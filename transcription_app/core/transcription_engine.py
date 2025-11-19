"""
Transcription engine integrating WhisperX and Pyannote
Provides GPU-accelerated speech-to-text with speaker diarization
"""
import gc
from pathlib import Path
from typing import Optional, Dict, Any
from PySide6.QtCore import QObject, Signal, QThread

try:
    import whisperx
    import torch
except ImportError as e:
    raise ImportError(
        "WhisperX and PyTorch are required. "
        "Install with: pip install whisperx torch"
    ) from e

from transcription_app.utils.logger import get_logger
from transcription_app.utils.language_detector import get_best_model_for_language
from transcription_app.utils.quality_presets import get_preset

logger = get_logger(__name__)


class TranscriptionEngine(QObject):
    """Manages transcription models and processing"""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.model = None
        self.current_model_name = None  # Track which model is loaded
        self.diarize_model = None
        self.device = config.validate_device()
        self.compute_type = config.compute_type

        logger.info(
            f"TranscriptionEngine initialized: device={self.device}, "
            f"compute_type={self.compute_type}, model={config.whisper_model}"
        )

    def apply_preset(self, preset_id: str, override_device: bool = False):
        """
        Apply a quality preset to the transcription engine

        Args:
            preset_id: ID of the preset to apply (e.g., "gpu_balanced", "cpu_optimized")
            override_device: Whether to override the device setting from the preset
        """
        preset = get_preset(preset_id)
        logger.info(f"Applying quality preset: {preset.name} ({preset_id})")

        # Update device if override is enabled
        if override_device and preset.device != self.device:
            logger.info(f"Overriding device: {self.device} -> {preset.device}")
            self.device = preset.device
            self.config.device = preset.device
            # Model will need to be reloaded
            if self.model is not None:
                logger.info("Unloading model due to device change")
                self.unload_models()

        # Update compute type
        if preset.compute_type != self.compute_type:
            logger.info(f"Updating compute type: {self.compute_type} -> {preset.compute_type}")
            self.compute_type = preset.compute_type
            self.config.compute_type = preset.compute_type
            # Model will need to be reloaded
            if self.model is not None:
                logger.info("Unloading model due to compute type change")
                self.unload_models()

        # Update batch size
        if preset.batch_size != self.config.batch_size:
            logger.info(f"Updating batch size: {self.config.batch_size} -> {preset.batch_size}")
            self.config.batch_size = preset.batch_size

        logger.info(f"Preset applied: {preset.name}")

    def ensure_models_loaded(self, language: Optional[str] = None):
        """
        Load Whisper model if not already loaded, or switch to language-specific model

        Args:
            language: Language code (cs, en, auto) to select appropriate model
        """
        # Determine which model to use
        if language and language != "auto":
            desired_model = get_best_model_for_language(language)
        else:
            desired_model = self.config.whisper_model

        # Check if we need to switch models
        if self.model is not None and self.current_model_name == desired_model:
            logger.debug(f"Model {desired_model} already loaded")
            return

        # Unload current model if switching
        if self.model is not None and self.current_model_name != desired_model:
            logger.info(f"Switching from {self.current_model_name} to {desired_model}")
            self.unload_models()

        logger.info(f"Loading Whisper model: {desired_model}")

        try:
            # Set environment variable to allow downloads
            import os
            os.environ['HF_HUB_OFFLINE'] = '0'

            # High-quality ASR options to prevent hallucinations and improve accuracy
            asr_options = {
                # Anti-hallucination settings (CRITICAL)
                "condition_on_previous_text": False,     # Prevent hallucination chaining
                "repetition_penalty": 1.2,               # Penalize repetitive text (>1 = less repetition)
                "no_repeat_ngram_size": 3,               # Block 3-word phrase loops

                # Quality & retry settings
                "temperatures": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],  # Temperature fallback on failure
                "no_speech_threshold": 0.6,              # Treat as silence if prob > 0.6
                "compression_ratio_threshold": 2.4,      # Reject if compression ratio > 2.4
                "log_prob_threshold": -1.0,              # Reject if avg log prob < -1.0

                # Context for better accuracy
                "initial_prompt": "This is a professional conversation in clear English. Transcribe exactly what is said, including filler words like um and uh.",
            }

            # VAD options with reduced thresholds to catch full words
            vad_options = {
                "chunk_size": 30,
                "vad_onset": 0.300,      # Reduced from 0.500 - catch word starts
                "vad_offset": 0.200,     # Reduced from 0.363 - catch word endings
            }

            logger.info(f"ASR options: {asr_options}")
            logger.info(f"VAD options: {vad_options}")

            # Try loading with retries for HuggingFace server errors
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.model = whisperx.load_model(
                        desired_model,
                        device=self.device,
                        compute_type=self.compute_type,
                        download_root=str(self.config.models_dir),
                        vad_method="silero",        # Use Silero VAD for compatibility
                        asr_options=asr_options,    # Quality settings
                        vad_options=vad_options,    # Better speech detection
                        language="en",              # Force English
                    )
                    self.current_model_name = desired_model
                    logger.info(f"Whisper model loaded successfully: {desired_model}")
                    break
                except Exception as e:
                    if attempt < max_retries - 1 and "500" in str(e):
                        logger.warning(f"HuggingFace server error, retrying... (attempt {attempt + 1}/{max_retries})")
                        import time
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                    else:
                        raise
        except Exception as e:
            error_msg = str(e)
            if "500" in error_msg:
                logger.error("HuggingFace servers are experiencing issues. Please try again in a few minutes.")
                raise Exception(
                    "HuggingFace servers are temporarily down. Please try again in a few minutes.\n"
                    "This is a temporary server issue, not a problem with the application."
                )
            else:
                logger.error(f"Failed to load Whisper model: {e}", exc_info=True)
                raise

    def unload_models(self):
        """Unload models to free memory"""
        logger.info("Unloading models")

        if self.model is not None:
            del self.model
            self.model = None

        if self.diarize_model is not None:
            del self.diarize_model
            self.diarize_model = None

        # Force garbage collection
        gc.collect()
        if self.device == "cuda":
            torch.cuda.empty_cache()

        logger.info("Models unloaded")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            'whisper_model': self.config.whisper_model,
            'device': self.device,
            'compute_type': self.compute_type,
            'model_loaded': self.model is not None,
            'diarization_enabled': self.config.diarization_enabled
        }


class TranscriptionWorker(QThread):
    """Worker thread for transcription processing"""

    # Signals
    progress_updated = Signal(int, str)  # percentage, status message
    transcription_complete = Signal(dict)  # result dict
    error_occurred = Signal(str)  # error message

    def __init__(
        self,
        engine: TranscriptionEngine,
        audio_file: Path,
        enable_diarization: bool = True,
        language: Optional[str] = None
    ):
        super().__init__()
        self.engine = engine
        self.audio_file = Path(audio_file)
        self.enable_diarization = enable_diarization and engine.config.diarization_enabled
        self.language = language or engine.config.language
        self.is_cancelled = False

        logger.info(
            f"TranscriptionWorker initialized: file={audio_file}, "
            f"diarization={self.enable_diarization}, language={self.language}"
        )

    def run(self):
        """Execute transcription in background thread"""
        try:
            # Load models (with language-specific model selection)
            self.progress_updated.emit(5, "Loading models...")
            self.engine.ensure_models_loaded(self.language)

            if self.is_cancelled:
                return

            # Load audio
            self.progress_updated.emit(10, "Loading audio file...")
            logger.info(f"Loading audio: {self.audio_file}")
            try:
                audio = whisperx.load_audio(str(self.audio_file))
            except FileNotFoundError as e:
                # This usually means FFmpeg is not installed
                error_msg = (
                    "FFmpeg is required but not found on your system.\n\n"
                    "Please install FFmpeg:\n"
                    "1. Download from: https://ffmpeg.org/download.html\n"
                    "   Or use winget: winget install ffmpeg\n"
                    "2. Add FFmpeg to your system PATH\n"
                    "3. Restart the application\n\n"
                    f"Technical details: {str(e)}"
                )
                logger.error(f"FFmpeg not found: {e}")
                raise FileNotFoundError(error_msg) from e

            if self.is_cancelled:
                return

            # Transcribe
            self.progress_updated.emit(20, "Transcribing audio...")
            logger.info("Starting transcription")

            # Handle language parameter - WhisperX has limited API
            transcribe_options = {
                'batch_size': self.engine.config.batch_size,
            }
            if self.language != "auto":
                transcribe_options['language'] = self.language

            logger.info(f"Transcription options: {transcribe_options}")

            result = self.engine.model.transcribe(
                audio,
                **transcribe_options
            )

            detected_language = result.get("language", "unknown")
            logger.info(f"Transcription complete. Detected language: {detected_language}")

            if self.is_cancelled:
                return

            # Align whisper output for better timestamps
            self.progress_updated.emit(60, "Aligning transcription...")
            logger.info("Aligning transcription")

            try:
                model_a, metadata = whisperx.load_align_model(
                    language_code=detected_language,
                    device=self.engine.device
                )
                result = whisperx.align(
                    result["segments"],
                    model_a,
                    metadata,
                    audio,
                    self.engine.device,
                    return_char_alignments=False
                )

                # Cleanup alignment model
                del model_a
                gc.collect()

                logger.info("Alignment complete")
            except Exception as e:
                logger.warning(f"Alignment failed, continuing without: {e}")

            if self.is_cancelled:
                return

            # Speaker diarization
            if self.enable_diarization and self.engine.config.hf_token:
                self.progress_updated.emit(80, "Identifying speakers...")
                logger.info("Starting speaker diarization")

                try:
                    diarize_model = whisperx.DiarizationPipeline(
                        use_auth_token=self.engine.config.hf_token,
                        device=self.engine.device
                    )
                    diarize_segments = diarize_model(
                        audio,
                        min_speakers=self.engine.config.min_speakers,
                        max_speakers=self.engine.config.max_speakers
                    )
                    result = whisperx.assign_word_speakers(diarize_segments, result)

                    # Cleanup diarization model
                    del diarize_model
                    gc.collect()

                    logger.info("Speaker diarization complete")
                except Exception as e:
                    logger.warning(f"Diarization failed, continuing without: {e}")
            elif self.enable_diarization:
                logger.warning("Diarization enabled but HF token not provided")

            # Add metadata
            result['file_path'] = str(self.audio_file)
            result['file_name'] = self.audio_file.name
            result['language'] = detected_language

            self.progress_updated.emit(100, "Complete!")
            logger.info("Transcription pipeline complete")
            self.transcription_complete.emit(result)

        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.error_occurred.emit(error_msg)

        finally:
            # Cleanup
            gc.collect()
            if self.engine.device == "cuda":
                torch.cuda.empty_cache()

    def cancel(self):
        """Cancel transcription"""
        logger.info("Cancelling transcription")
        self.is_cancelled = True


def format_transcript_text(result: Dict[str, Any], include_timestamps: bool = True) -> str:
    """
    Format transcription result as plain text

    Args:
        result: Transcription result dictionary
        include_timestamps: Whether to include timestamps

    Returns:
        Formatted text string
    """
    lines = []

    # Add header
    file_name = result.get('file_name', 'Unknown')
    language = result.get('language', 'unknown')
    lines.append(f"=== Transcription: {file_name} ===")
    lines.append(f"Language: {language}")
    lines.append("")

    # Format segments
    for segment in result.get('segments', []):
        speaker = segment.get('speaker', 'Unknown')
        start = segment.get('start', 0)
        text_content = segment.get('text', '').strip()

        if include_timestamps:
            timestamp = f"[{start:.2f}s]"
            lines.append(f"{timestamp} {speaker}: {text_content}")
        else:
            lines.append(f"{speaker}: {text_content}")

    return '\n'.join(lines)


def format_transcript_srt(result: Dict[str, Any]) -> str:
    """
    Format transcription result as SRT subtitle file

    Args:
        result: Transcription result dictionary

    Returns:
        SRT formatted string
    """
    lines = []
    subtitle_index = 1

    for segment in result.get('segments', []):
        start = segment.get('start', 0)
        end = segment.get('end', start + 1)
        text_content = segment.get('text', '').strip()
        speaker = segment.get('speaker', '')

        # Format timestamps as SRT time format (HH:MM:SS,mmm)
        start_time = _format_srt_time(start)
        end_time = _format_srt_time(end)

        # Add speaker prefix if available
        if speaker:
            text_content = f"{speaker}: {text_content}"

        lines.append(str(subtitle_index))
        lines.append(f"{start_time} --> {end_time}")
        lines.append(text_content)
        lines.append("")  # Blank line between subtitles

        subtitle_index += 1

    return '\n'.join(lines)


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
