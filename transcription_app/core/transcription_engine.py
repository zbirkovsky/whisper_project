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

logger = get_logger(__name__)


class TranscriptionEngine(QObject):
    """Manages transcription models and processing"""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.model = None
        self.diarize_model = None
        self.device = config.validate_device()
        self.compute_type = config.compute_type

        logger.info(
            f"TranscriptionEngine initialized: device={self.device}, "
            f"compute_type={self.compute_type}, model={config.whisper_model}"
        )

    def ensure_models_loaded(self):
        """Load Whisper model if not already loaded"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.config.whisper_model}")

            try:
                # Set environment variable to allow downloads
                import os
                os.environ['HF_HUB_OFFLINE'] = '0'

                # Try loading with retries for HuggingFace server errors
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.model = whisperx.load_model(
                            self.config.whisper_model,
                            device=self.device,
                            compute_type=self.compute_type,
                            download_root=str(self.config.models_dir)
                        )
                        logger.info("Whisper model loaded successfully")
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
            # Load models
            self.progress_updated.emit(5, "Loading models...")
            self.engine.ensure_models_loaded()

            if self.is_cancelled:
                return

            # Load audio
            self.progress_updated.emit(10, "Loading audio file...")
            logger.info(f"Loading audio: {self.audio_file}")
            audio = whisperx.load_audio(str(self.audio_file))

            if self.is_cancelled:
                return

            # Transcribe
            self.progress_updated.emit(20, "Transcribing audio...")
            logger.info("Starting transcription")

            # Handle language parameter
            transcribe_options = {
                'batch_size': self.engine.config.batch_size
            }
            if self.language != "auto":
                transcribe_options['language'] = self.language

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
