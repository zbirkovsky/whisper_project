"""
Real-time transcription with translation
Processes audio chunks as they're recorded and provides live translation
Uses background thread to avoid blocking the UI
"""
import numpy as np
import tempfile
import wave
import threading
import queue
from pathlib import Path
from typing import Optional
from PySide6.QtCore import QObject, Signal, QThread

try:
    import whisperx
except ImportError as e:
    raise ImportError("WhisperX is required for real-time transcription") from e

from transcription_app.utils.logger import get_logger
from transcription_app.utils.translator import TranslationService

logger = get_logger(__name__)


class RealtimeProcessingWorker(QThread):
    """
    Background worker thread for processing audio chunks
    Prevents UI blocking during transcription and translation
    """

    # Signals to communicate back to main thread
    transcription_ready = Signal(str, str, float)  # original, translated, timestamp
    error_occurred = Signal(str)

    def __init__(self, engine, translator, source_language: str, target_language: str):
        super().__init__()
        self.engine = engine
        self.translator = translator
        self.source_language = source_language
        self.target_language = target_language
        self.sample_rate = 16000

        # Real-time optimized settings from config
        self.realtime_model = getattr(engine.config, 'realtime_model', 'large-v3-turbo')
        self.realtime_batch_size = getattr(engine.config, 'realtime_batch_size', 4)

        # Thread-safe queue for audio chunks
        self.audio_queue: queue.Queue = queue.Queue()
        self.is_running = False
        self.total_processed_duration = 0.0
        self._realtime_model_loaded = False

    def run(self):
        """Main processing loop - runs in background thread"""
        self.is_running = True
        logger.info("RealtimeProcessingWorker started")

        while self.is_running:
            try:
                # Wait for audio data with timeout to check is_running
                try:
                    audio_data, duration = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if audio_data is None:  # Poison pill to stop
                    break

                self._process_audio(audio_data, duration)

            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)
                self.error_occurred.emit(f"Processing error: {str(e)}")

        logger.info("RealtimeProcessingWorker stopped")

    def stop(self):
        """Signal the worker to stop"""
        self.is_running = False
        # Send poison pill to unblock queue
        self.audio_queue.put((None, 0))

    def add_audio(self, audio: np.ndarray, duration: float):
        """Add audio data to processing queue (thread-safe)"""
        if self.is_running:
            self.audio_queue.put((audio.copy(), duration))

    def _is_speech_present(self, audio: np.ndarray, threshold: float = 500.0) -> bool:
        """
        Simple VAD: check if audio contains speech based on RMS level

        Args:
            audio: Audio samples as int16
            threshold: RMS threshold for speech detection

        Returns:
            True if speech is likely present
        """
        if len(audio) == 0:
            return False
        # Calculate RMS (root mean square) energy
        rms = np.sqrt(np.mean(audio.astype(np.float32) ** 2))
        return rms > threshold

    def _process_audio(self, audio: np.ndarray, duration: float):
        """Process a single audio chunk"""
        tmp_path: Optional[Path] = None
        try:
            # Quick VAD check - skip silent audio for faster response
            if not self._is_speech_present(audio):
                logger.debug(f"[RT Worker] Skipping silent audio chunk ({duration:.2f}s)")
                self.total_processed_duration += duration
                return

            logger.debug(f"[RT Worker] Processing audio: {len(audio)} samples, {duration:.2f}s")

            # Save to temporary WAV file (WhisperX needs a file)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)

                with wave.open(str(tmp_path), 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio.tobytes())

            # Transcribe using existing engine

            # Ensure model is loaded (may take time on first call)
            self.engine.ensure_models_loaded(self.source_language)

            # Load and transcribe audio
            audio_whisperx = whisperx.load_audio(str(tmp_path))

            # Build transcription options - optimized for real-time speed
            transcribe_options = {
                'batch_size': self.realtime_batch_size,  # Smaller batch for faster processing
                'task': 'transcribe',  # Explicitly set task to avoid token misinterpretation
            }

            # Add language if specified (must be valid ISO 639-1 code)
            if self.source_language and self.source_language != "auto":
                transcribe_options['language'] = self.source_language

            # Speed optimizations for real-time mode (override preset options)
            # These settings prioritize speed over maximum accuracy
            realtime_asr_options = {
                'beam_size': 1,  # Greedy decoding is fastest
                'best_of': 1,   # No sampling variations
                'patience': 1.0,  # No extended beam search
                'compression_ratio_threshold': 2.4,
                'condition_on_previous_text': False,  # Faster, less context dependency
            }

            # Merge ASR options from quality preset, but let realtime options override
            if self.engine.asr_options:
                # Don't let preset override task
                preset_options = {k: v for k, v in self.engine.asr_options.items() if k != 'task'}
                transcribe_options.update(preset_options)

            # Apply real-time speed optimizations last (highest priority)
            transcribe_options.update(realtime_asr_options)

            # Transcribe
            logger.debug(f"[RT Worker] Transcribing with batch_size={transcribe_options.get('batch_size')}")
            result = self.engine.model.transcribe(
                audio_whisperx,
                **transcribe_options
            )

            # Extract text from segments
            segments = result.get('segments', [])
            if segments:
                # Combine all segment texts
                original_text = ' '.join([seg.get('text', '').strip() for seg in segments])

                if original_text:
                    # Translate to target language
                    detected_language = result.get('language', self.source_language)

                    if detected_language != self.target_language:
                        translated_text = self.translator.translate(
                            original_text,
                            source_language=detected_language,
                            target_language=self.target_language
                        )
                        logger.info(f"[RT] {detected_language}: '{original_text[:50]}...' -> '{translated_text[:50]}...'")
                    else:
                        translated_text = original_text
                        logger.info(f"[RT] {detected_language}: '{original_text[:80]}...'")

                    # Emit transcription with translation
                    timestamp = self.total_processed_duration
                    self.transcription_ready.emit(original_text, translated_text, timestamp)

            # Update total processed duration
            self.total_processed_duration += duration

        except Exception as e:
            error_msg = f"Real-time transcription error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

        finally:
            # Always cleanup temp file if it was created
            if tmp_path is not None and tmp_path.exists():
                try:
                    tmp_path.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file {tmp_path}: {cleanup_error}")


class RealtimeTranscriptionEngine(QObject):
    """
    Handles real-time transcription and translation of audio chunks
    Designed to work alongside audio recording for live transcription
    Uses background thread to prevent UI blocking
    """

    # Signals
    transcription_ready = Signal(str, str, float)  # original_text, translated_text, timestamp
    error_occurred = Signal(str)  # error_message

    def __init__(self, transcription_engine, source_language: str = "auto", target_language: str = "en"):
        """
        Initialize real-time transcription engine

        Args:
            transcription_engine: Main TranscriptionEngine instance (reuses loaded models)
            source_language: Source language for transcription ('auto', 'vi', 'en', etc.)
            target_language: Target language for translation ('en', 'vi', etc.)
        """
        super().__init__()
        self.engine = transcription_engine
        self.source_language = source_language
        self.target_language = target_language
        self.translator = TranslationService(target_language=target_language)

        # Buffer for accumulating audio chunks
        self.audio_buffer = []
        self.buffer_duration = 0.0  # seconds
        self.chunk_duration_target = getattr(
            self.engine.config, 'realtime_chunk_duration', 10.0
        )  # Use config or default
        self.sample_rate = 16000  # Whisper expects 16kHz

        self.is_active = False
        self.worker: Optional[RealtimeProcessingWorker] = None

        logger.info(
            f"RealtimeTranscriptionEngine initialized: "
            f"source={source_language}, target={target_language}, "
            f"chunk_duration={self.chunk_duration_target}s"
        )

    def start(self):
        """Start real-time transcription"""
        self.is_active = True
        self.audio_buffer = []
        self.buffer_duration = 0.0

        # Create and start worker thread
        self.worker = RealtimeProcessingWorker(
            self.engine,
            self.translator,
            self.source_language,
            self.target_language
        )
        # Forward signals from worker
        self.worker.transcription_ready.connect(self.transcription_ready.emit)
        self.worker.error_occurred.connect(self.error_occurred.emit)
        self.worker.start()

        logger.info("Real-time transcription started with background worker")

    def stop(self):
        """Stop real-time transcription and process remaining buffer"""
        self.is_active = False

        # Process any remaining audio in buffer
        if self.audio_buffer and self.worker:
            logger.info("Processing final audio buffer")
            audio = np.concatenate(self.audio_buffer)
            self.worker.add_audio(audio, self.buffer_duration)

        # Stop worker thread
        if self.worker:
            self.worker.stop()
            self.worker.wait(5000)  # Wait up to 5 seconds
            self.worker = None

        self.audio_buffer = []
        self.buffer_duration = 0.0
        logger.info("Real-time transcription stopped")

    def add_audio_chunk(self, audio_data: bytes, sample_rate: int = 16000):
        """
        Add audio chunk to buffer for processing

        Args:
            audio_data: Raw audio bytes (int16)
            sample_rate: Sample rate of audio data
        """
        if not self.is_active or not self.worker:
            return

        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Handle stereo audio - convert to mono by averaging channels
        if len(audio_array) > 0:
            # Check if stereo (even number of samples)
            # Stereo audio is interleaved: L R L R L R...
            # If we have stereo, convert to mono
            if hasattr(self, '_is_stereo') and self._is_stereo:
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
            elif len(audio_array) % 2 == 0 and sample_rate >= 44100:
                # Assume stereo for high sample rates with even samples
                # First chunk detection
                self._is_stereo = True
                audio_array = audio_array.reshape(-1, 2).mean(axis=1).astype(np.int16)
                logger.info(f"Detected stereo audio, converting to mono")

        # Resample if needed (Whisper expects 16kHz)
        if sample_rate != self.sample_rate:
            audio_array = self._resample(audio_array, sample_rate, self.sample_rate)

        # Add to buffer
        self.audio_buffer.append(audio_array)

        # Update buffer duration
        chunk_duration = len(audio_array) / self.sample_rate
        self.buffer_duration += chunk_duration

        # Log progress periodically (reduced frequency for speed)
        if len(self.audio_buffer) % 100 == 0:
            logger.debug(f"Realtime buffer: {self.buffer_duration:.1f}s / {self.chunk_duration_target}s")

        # Process if buffer is full - send to worker thread
        if self.buffer_duration >= self.chunk_duration_target:
            logger.info(f"Buffer full ({self.buffer_duration:.2f}s), sending to worker for transcription...")
            audio = np.concatenate(self.audio_buffer)
            self.worker.add_audio(audio, self.buffer_duration)

            # Clear buffer
            self.audio_buffer = []
            self.buffer_duration = 0.0

    @staticmethod
    def _resample(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
        """
        Resample audio to target rate

        Args:
            audio: Audio data as int16 numpy array
            source_rate: Source sample rate
            target_rate: Target sample rate

        Returns:
            Resampled audio as int16 numpy array
        """
        if source_rate == target_rate:
            return audio

        # Calculate decimation factor
        decimation_factor = source_rate // target_rate

        if decimation_factor * target_rate == source_rate:
            # Simple decimation
            return audio[::decimation_factor]
        else:
            # Use scipy if available for non-integer ratios
            try:
                from scipy import signal
                num_samples = int(len(audio) * target_rate / source_rate)
                return signal.resample(audio, num_samples).astype('int16')
            except ImportError:
                logger.warning("scipy not available, using simple decimation")
                return audio[::decimation_factor]
