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
from transcription_app.utils.audio_processing import (
    calculate_and_apply_gain_boost,
    calculate_rms,
    stereo_to_mono,
    mix_audio_sources
)

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
        Get system default microphone device index

        Returns:
            Device index or None if not found
        """
        self._ensure_pyaudio()

        try:
            mic_info = self.p.get_default_input_device_info()
            logger.info(f"Using default microphone: {mic_info['name']} (index={mic_info['index']})")
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
            # Calculate expected chunks for debugging
            expected_chunks = int(
                self.config.sample_rate / self.config.chunk_size * self.duration
            )
            logger.info(f"Recording parameters: duration={self.duration}s, sample_rate={self.config.sample_rate}, chunk_size={self.config.chunk_size}")
            logger.info(f"Expected to record {expected_chunks} chunks ({self.duration}s)")

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
                # Get mic device info to determine channel count
                mic_info = p.get_device_info_by_index(self.mic_index)
                mic_channels = min(mic_info['maxInputChannels'], 2)  # Use up to 2 channels
                logger.info(f"Opening microphone stream (device {self.mic_index}, {mic_channels} channels)")
                stream_mic = p.open(
                    format=pyaudio.paInt16,
                    channels=mic_channels,
                    rate=self.config.sample_rate,
                    input=True,
                    frames_per_buffer=self.config.chunk_size,
                    input_device_index=self.mic_index
                )
                self.streams.append(('mic', stream_mic, mic_channels))

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
                    # Log every 100 chunks to track progress
                    if chunks_recorded % 100 == 0 and chunks_recorded > 0:
                        logger.debug(f"Recording progress: {chunks_recorded}/{num_chunks} chunks, is_cancelled={self.is_cancelled}")

                    # Read from all streams for this chunk
                    chunk_success = False
                    for name, stream, channels in self.streams:
                        try:
                            # Check if data is available before blocking read
                            # This prevents hanging on devices with noise gates (like NVIDIA Broadcast)
                            available = stream.get_read_available()

                            if available >= self.config.chunk_size:
                                # Enough data available, read it
                                data = stream.read(
                                    self.config.chunk_size,
                                    exception_on_overflow=False
                                )
                                frames[name].append(data)
                                chunk_success = True
                            elif available > 0:
                                # Some data available but less than chunk_size, read what's there
                                data = stream.read(
                                    available,
                                    exception_on_overflow=False
                                )
                                # Pad with zeros to maintain chunk size
                                padding = b'\x00' * (self.config.chunk_size * 2 * channels - len(data))
                                frames[name].append(data + padding)
                                chunk_success = True
                            else:
                                # No data available - skip this chunk to avoid choppy audio
                                # Only append silence occasionally to maintain timing
                                if chunks_recorded % 5 == 0:
                                    silence = b'\x00' * (self.config.chunk_size * 2 * channels)
                                    frames[name].append(silence)
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

                        # Small sleep to prevent CPU spinning when no audio data available
                        # Sleep for roughly the duration of one chunk
                        import time
                        time.sleep(self.config.chunk_size / self.config.sample_rate * 0.5)
            finally:
                # CRITICAL: Close streams immediately when loop exits (cancelled or complete)
                # This breaks out of any blocking stream.read() calls
                loop_exit_reason = "cancelled" if self.is_cancelled else "completed naturally"
                logger.info(f"Recording loop exited: reason={loop_exit_reason}, chunks_recorded={chunks_recorded}/{num_chunks}, is_cancelled={self.is_cancelled}")
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
        """Process and save recorded audio with downsampling to 16kHz for Whisper"""
        try:
            # Get target sample rate for Whisper (16kHz)
            target_rate = getattr(self.config, 'whisper_sample_rate', 16000)
            source_rate = self.config.sample_rate

            if self.record_mic and self.record_system and 'mic' in frames and 'system' in frames:
                # Mix both sources
                logger.info("Mixing microphone and system audio")
                sys_audio = np.frombuffer(b''.join(frames['system']), dtype='int16')
                mic_audio = np.frombuffer(b''.join(frames['mic']), dtype='int16')

                # Get the number of channels for mic stream
                mic_stream_info = next((s for s in self.streams if s[0] == 'mic'), None)
                mic_channels = mic_stream_info[2] if mic_stream_info else 1

                # Convert stereo system audio to mono (average L+R)
                sys_mono = stereo_to_mono(sys_audio)

                # Convert mic audio to mono if stereo
                if mic_channels == 2:
                    mic_mono = stereo_to_mono(mic_audio)
                else:
                    mic_mono = mic_audio

                # Check if system audio is mostly silence (RMS < 100)
                sys_rms = calculate_rms(sys_mono)
                mic_rms = calculate_rms(mic_mono)

                logger.info(f"Audio levels - Mic RMS: {mic_rms:.1f}, System RMS: {sys_rms:.1f}")

                # Apply moderate gain boost for low microphone levels
                # Target RMS should be at least 400 for good Whisper VAD detection
                mic_mono, boost_factor = calculate_and_apply_gain_boost(
                    mic_mono,
                    rms_threshold=self.config.mixed_rms_threshold,
                    target_rms=self.config.mixed_target_rms,
                    max_boost=self.config.mixed_max_boost,
                    rms_floor=self.config.rms_floor,
                    use_soft_clipping=self.config.mixed_use_soft_clipping
                )
                mic_rms = mic_rms * boost_factor  # Update RMS for mixing logic

                if sys_rms < 100:
                    # System audio is silent, use mic only
                    logger.info("System audio silent, using microphone only")
                    mixed = np.clip(mic_mono, -32767, 32766).astype('int16')
                else:
                    # Mix both sources with proper levels
                    logger.info(f"Mixing both sources (Mic: {mic_rms:.1f} RMS, System: {sys_rms:.1f} RMS)")
                    mixed = mix_audio_sources(
                        sys_mono,
                        mic_mono,
                        source1_gain=0.5,  # Reduce system audio
                        source2_gain=1.0
                    )

                # Downsample to target rate if needed
                if source_rate != target_rate:
                    logger.info(f"Downsampling audio from {source_rate}Hz to {target_rate}Hz")
                    mixed = self._downsample(mixed, source_rate, target_rate)

                # Save mono mixed audio
                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(target_rate)  # Use target rate for Whisper
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
                mic_audio = np.frombuffer(b''.join(frames['mic']), dtype='int16')

                # Get the number of channels for mic stream
                mic_stream_info = next((s for s in self.streams if s[0] == 'mic'), None)
                mic_channels = mic_stream_info[2] if mic_stream_info else 1

                mic_rms = calculate_rms(mic_audio)
                logger.info(f"Microphone audio - Channels: {mic_channels}, RMS: {mic_rms:.1f}")

                # Convert to mono if stereo
                if mic_channels == 2:
                    mic_mono = stereo_to_mono(mic_audio)
                else:
                    mic_mono = mic_audio

                # Boost microphone if too quiet (higher threshold for mic-only recording)
                mic_mono, _ = calculate_and_apply_gain_boost(
                    mic_mono,
                    rms_threshold=self.config.mic_only_rms_threshold,
                    target_rms=self.config.mic_only_target_rms,
                    max_boost=self.config.mic_only_max_boost,
                    rms_floor=self.config.rms_floor,
                    use_soft_clipping=self.config.mic_only_use_soft_clipping
                )

                mic_mono = np.clip(mic_mono, -32767, 32766).astype('int16')

                # Downsample to target rate if needed
                if source_rate != target_rate:
                    logger.info(f"Downsampling audio from {source_rate}Hz to {target_rate}Hz")
                    mic_mono = self._downsample(mic_mono, source_rate, target_rate)

                with wave.open(str(self.output_file), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(target_rate)  # Use target rate for Whisper
                    wf.writeframes(mic_mono.tobytes())

            else:
                raise ValueError("No audio data to save")

        except Exception as e:
            logger.error(f"Error saving audio: {e}", exc_info=True)
            raise

    @staticmethod
    def _downsample(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
        """
        Downsample audio from source_rate to target_rate using simple decimation

        Args:
            audio: Audio data as int16 numpy array
            source_rate: Source sample rate (e.g., 48000)
            target_rate: Target sample rate (e.g., 16000)

        Returns:
            Downsampled audio as int16 numpy array
        """
        if source_rate == target_rate:
            return audio

        # Calculate decimation factor (e.g., 48000/16000 = 3)
        decimation_factor = source_rate // target_rate

        if decimation_factor * target_rate != source_rate:
            logger.warning(f"Non-integer decimation factor: {source_rate}/{target_rate}")
            # Use scipy resample for non-integer ratios
            try:
                from scipy import signal
                num_samples = int(len(audio) * target_rate / source_rate)
                return signal.resample(audio, num_samples).astype('int16')
            except ImportError:
                logger.warning("scipy not available, using simple decimation")

        # Simple decimation: take every Nth sample
        return audio[::decimation_factor]

    def cancel(self):
        """Cancel recording"""
        import traceback
        logger.info("=" * 80)
        logger.info("CANCEL CALLED - Recording cancellation requested!")
        logger.info("=" * 80)
        # Log the call stack to see who called cancel
        logger.info("Cancel called from:")
        for line in traceback.format_stack()[:-1]:
            logger.info(line.strip())
        logger.info("=" * 80)

        self.is_cancelled = True

        # CRITICAL: Stop streams immediately to break out of blocking stream.read()
        logger.info(f"Stopping {len(self.streams)} audio streams to unblock read operations")
        for name, stream, _ in self.streams:
            try:
                stream.stop_stream()
                logger.info(f"Stopped {name} stream")
            except Exception as e:
                logger.warning(f"Error stopping {name} stream during cancellation: {e}")
