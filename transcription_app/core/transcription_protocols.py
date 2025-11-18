"""
Transcription engine protocols and abstractions
Allows pluggable transcription backends (WhisperX, OpenAI, Azure, etc.)
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class TranscriptionOptions:
    """Configuration options for transcription"""
    language: Optional[str] = None  # Language code or "auto"
    enable_diarization: bool = True  # Speaker identification
    batch_size: int = 16
    compute_type: str = "float16"  # Precision: float32, float16, int8
    device: str = "cuda"  # Device: cuda, cpu
    min_speakers: Optional[int] = None
    max_speakers: Optional[int] = None


@dataclass
class TranscriptionResult:
    """Standardized transcription result"""
    text: str  # Full transcript text
    segments: list[Dict[str, Any]]  # Timestamped segments
    language: str  # Detected language
    file_path: str  # Source audio file
    file_name: str  # Source filename
    metadata: Dict[str, Any]  # Additional metadata (confidence, etc.)


class TranscriptionEngineProtocol(ABC):
    """Abstract protocol for transcription engines"""

    @abstractmethod
    def initialize(self, config: Any) -> bool:
        """
        Initialize the transcription engine

        Args:
            config: Configuration object

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if engine is available and ready

        Returns:
            True if engine can be used
        """
        pass

    @abstractmethod
    def load_model(self, model_name: str, **kwargs) -> bool:
        """
        Load transcription model

        Args:
            model_name: Model identifier
            **kwargs: Engine-specific parameters

        Returns:
            True if model loaded successfully
        """
        pass

    @abstractmethod
    def unload_model(self):
        """Unload model to free resources"""
        pass

    @abstractmethod
    def transcribe(
        self,
        audio_file: Path,
        options: TranscriptionOptions,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio file

        Args:
            audio_file: Path to audio file
            options: Transcription options
            progress_callback: Optional callback(percentage, status_message)

        Returns:
            TranscriptionResult object

        Raises:
            TranscriptionError: If transcription fails
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes

        Returns:
            List of language codes (e.g., ['en', 'cs', 'es'])
        """
        pass

    @abstractmethod
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get engine information

        Returns:
            Dictionary with engine name, version, capabilities, etc.
        """
        pass


class TranscriptionError(Exception):
    """Base exception for transcription errors"""
    pass


class ModelNotLoadedError(TranscriptionError):
    """Raised when trying to transcribe without loaded model"""
    pass


class UnsupportedLanguageError(TranscriptionError):
    """Raised when requested language is not supported"""
    pass


class TranscriptionEngineRegistry:
    """Registry for transcription engines"""

    def __init__(self):
        self.engines: Dict[str, TranscriptionEngineProtocol] = {}
        self.default_engine: Optional[str] = None

    def register(self, engine_id: str, engine: TranscriptionEngineProtocol, set_as_default: bool = False):
        """
        Register a transcription engine

        Args:
            engine_id: Unique identifier for engine
            engine: Engine instance
            set_as_default: Set as default engine
        """
        self.engines[engine_id] = engine
        logger.info(f"Registered transcription engine: {engine_id}")

        if set_as_default or self.default_engine is None:
            self.default_engine = engine_id
            logger.info(f"Default engine set to: {engine_id}")

    def get_engine(self, engine_id: Optional[str] = None) -> Optional[TranscriptionEngineProtocol]:
        """
        Get transcription engine

        Args:
            engine_id: Engine identifier (uses default if None)

        Returns:
            Engine instance or None
        """
        if engine_id is None:
            engine_id = self.default_engine

        return self.engines.get(engine_id)

    def available_engines(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available engines and their info

        Returns:
            Dictionary mapping engine_id to engine_info
        """
        return {
            engine_id: engine.get_engine_info()
            for engine_id, engine in self.engines.items()
            if engine.is_available()
        }


# Global registry instance
_transcription_registry: Optional[TranscriptionEngineRegistry] = None


def get_transcription_engine_registry() -> TranscriptionEngineRegistry:
    """Get or create global transcription engine registry"""
    global _transcription_registry
    if _transcription_registry is None:
        _transcription_registry = TranscriptionEngineRegistry()
    return _transcription_registry
