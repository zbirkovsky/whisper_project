"""
Audio recording with simultaneous microphone and system audio capture
Uses PyAudioWPatch for WASAPI loopback support on Windows
"""
import wave
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from PySide6.QtCore import QObject, Signal, QThread

try:
    import pyaudiowpatch as pyaudio
except ImportError:
    import pyaudio

from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class AudioRecorder(QObject):
    """Handles audio recording from microphone and system audio"""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.p: Optional[pyaudio.PyAudio] = None

    def _ensure_pyaudio(self):
        """Ensure PyAudio instance is initialized"""
        if self.p is None:
            self.p = pyaudio.PyAudio()

    def list_devices(self) -> List[Dict[str, any]]:
        """Get list of available audio devices"""
        self._ensure_pyaudio()

        devices = []
        for i in range(self.p.get_device_count()):
            try:
                info = self.p.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': info['name'],
                    'max_inputs': info['maxInputChannels'],
                    'max_outputs': info['maxOutputChannels'],
                    'is_loopback': info.get('isLoopbackDevice', False),
                    'default_sample_rate': info.get('defaultSampleRate', 0)
                })
            except Exception as e:
                logger.warning(f"Error reading device {i}: {e}")

        return devices

    def get_loopback_device(self) -> Optional[int]:
        """
        Get system audio loopback device index

        Returns:
            Device index or None if not found
        """
        self._ensure_pyaudio()

        try:
            # Get WASAPI host API
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = self.p.get_device_info_by_index(
                wasapi_info["defaultOutputDevice"]
            )

            # Check if default device is already loopback
            if not default_speakers.get("isLoopbackDevice", False):
                # Find corresponding loopback device
                for loopback in self.p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        logger.info(f"Found loopback device: {loopback['name']}")
                        return loopback["index"]

            logger.info(f"Using loopback device: {default_speakers['name']}")
            return default_speakers["index"]

        except Exception as e:
            logger.error(f"Error getting loopback device: {e}")
            return None

    def get_default_microphone(self) -> Optional[int]:
        """
        Get default microphone device index

        Returns:
            Device index or None if not found
        """
        self._ensure_pyaudio()

        try:
            mic_info = self.p.get_default_input_device_info()
            logger.info(f"Default microphone: {mic_info['name']}")
            return mic_info['index']
        except Exception as e:
            logger.error(f"Error getting default microphone: {e}")
            return None

    def cleanup(self):
        """Cleanup PyAudio resources"""
        if self.p is not None:
            self.p.terminate()
            self.p = None


class RecordingWorker(QThread):
    """Worker thread for audio recording"""

    # Signals
    progress_updated = Signal(float)  # seconds recorded
    recording_complete = Signal(str)  # output file path
    error_occurred = Signal(str)  # error message

    def __init__(
        self,
        config,
        duration: int,
        output_file: Path,
        record_mic: bool = True,
        record_system: bool = True,
        mic_index: Optional[int] = None,
        loopback_index: Optional[int] = None
    ):
        super().__init__()
        self.config = config
        self.duration = duration
        self.output_file = Path(output_file)
        self.record_mic = record_mic
        self.record_system = record_system
        self.mic_index = mic_index
        self.loopback_index = loopback_index
        self.is_cancelled = False
        self.streams = []  # Keep reference to streams for cancellation

        logger.info(
            f"RecordingWorker initialized: duration={duration}s, "
            f"mic={record_mic}, system={record_system}"
        )

    def run(self):
        """Execute recording in background thread"""
        p = pyaudio.PyAudio()

        try:
            # Open streams
            self.streams = []

            if self.record_system and self.loopback_index is not None:
                logger.info(f"Opening system audio stream (device {self.loopback_index})")
                stream_sys = p.open(
                    format=pyaudio.paInt16,
                    channels=2,
                    rate=self.config.sample_rate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size,
                    input_device_index=self.loopback_index
                )
                self.streams.append(('system', stream_sys, 2))

            if self.record_mic and self.mic_index is not None:
                logger.info(f"Opening microphone stream (device {self.mic_index})")
                stream_mic = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=self.config.sample_rate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size,
                    input_device_index=self.mic_index
                )
                self.streams.append(('mic', stream_mic, 1))

            if not self.streams:
                raise ValueError("No audio streams available")

            # Record audio
            frames = {name: [] for name, _, _ in self.streams}
            num_chunks = int(
                self.config.sample_rate / self.config.chunk_size * self.duration
            )

            logger.info(f"Starting recording for {self.duration} seconds ({num_chunks} chunks)")

            chunks_recorded = 0
            try:
                while chunks_recorded < num_chunks and not self.is_cancelled:
                    # Read from all streams for this chunk
                    chunk_success = False
                    for name, stream, channels in self.streams:
                        try:
                            # Read one chunk of audio data
                            data = stream.read(
                                self.config.chunk_size,
                                exception_on_overflow=False
                            )
                            frames[name].append(data)
                            chunk_success = True
                        except Exception as e:
                            logger.warning(f"Error reading from {name} stream: {e}")
                            # Continue recording even if one stream fails
                            continue

                    if chunk_success:
                        chunks_recorded += 1

                        # Update progress every 10 chunks to reduce overhead
                        if chunks_recorded % 10 == 0:
                            elapsed = chunks_recorded * self.config.chunk_size / self.config.sample_rate
                            self.progress_updated.emit(elapsed)
            finally:
                # CRITICAL: Close streams immediately when loop exits (cancelled or complete)
                # This breaks out of any blocking stream.read() calls
                logger.info(f"Recording loop finished after {chunks_recorded} chunks ({chunks_recorded * self.config.chunk_size / self.config.sample_rate:.2f} seconds), closing streams...")
            # Close streams
            for name, stream, _ in self.streams:
                try:
                    if stream.is_active():
                        stream.stop_stream()
                    stream.close()
                    logger.info(f"Closed {name} stream")
                except Exception as e:
                    logger.error(f"Error closing {name} stream: {e}")

            # Process and save audio (even if cancelled - save what we recorded)
            # Check if we have any frames to save
            has_data = any(len(frame_list) > 0 for frame_list in frames.values())
            logger.info(f"Checking if we have data to save... has_data={has_data}")
            if has_data:
                logger.info("Saving audio...")
                self._save_audio(frames)
                logger.info(f"Recording complete: {self.output_file}")
                self.recording_complete.emit(str(self.output_file))
            else:
                logger.warning("No audio data recorded")
                self.error_occurred.emit("No audio data was recorded")

        except Exception as e:
            error_msg = f"Recording error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

        finally:
            p.terminate()

    def _save_audio(self, frames: Dict[str, List[bytes]]):
        """Process and save recorded audio"""
        try:
            if self.record_mic and self.record_system and 'mic' in frames and 'system' in frames:
                # Mix both sources
                logger.info("Mixing microphone and system audio")
                sys_audio = np.frombuffer(b''.join(frames['system']), dtype='int16')
                mic_audio = np.frombuffer(b''.join(frames['mic']), dtype='int16')

                # Convert stereo system audio to mono (average L+R)
                sys_mono = np.array([sys_audio[::2], sys_audio[1::2]]).mean(axis=0)

                # Normalize volumes before mixing
                sys_mono = sys_mono * 0.7  # Reduce system audio volume
                mic_audio = mic_audio * 1.0  # Keep mic at full volume

                # Mix
                min_len = min(len(sys_mono), len(mic_audio))
                mixed = sys_mono[:min_len] + mic_audio[:min_len]
                mixed = np.clip(mixed, -32767, 32766).astype('int16')

                # Save mono mixed audio
                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.config.sample_rate)
                    wf.writeframes(mixed.tobytes())

            elif self.record_system and 'system' in frames:
                # Save system audio only
                logger.info("Saving system audio only")
                sys_audio = b''.join(frames['system'])
                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(2)
                    wf.setsampwidth(2)
                    wf.setframerate(self.config.sample_rate)
                    wf.writeframes(sys_audio)

            elif self.record_mic and 'mic' in frames:
                # Save mic audio only
                logger.info("Saving microphone audio only")
                mic_audio = b''.join(frames['mic'])
                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.config.sample_rate)
                    wf.writeframes(mic_audio)

            else:
                raise ValueError("No audio data to save")

        except Exception as e:
            logger.error(f"Error saving audio: {e}", exc_info=True)
            raise

    def cancel(self):
        """Cancel recording"""
        logger.info("Cancelling recording")
        self.is_cancelled = True

        # CRITICAL: Stop streams immediately to break out of blocking stream.read()
        logger.info(f"Stopping {len(self.streams)} audio streams to unblock read operations")
        for name, stream, _ in self.streams:
            try:
                stream.stop_stream()
                logger.info(f"Stopped {name} stream")
            except Exception as e:
                logger.warning(f"Error stopping {name} stream during cancellation: {e}")
