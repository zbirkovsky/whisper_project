"""
Service interfaces and protocols for dependency injection
Defines contracts that services must implement
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any


class IConfigService(ABC):
    """Configuration service interface"""

    @property
    @abstractmethod
    def app_dir(self) -> Path:
        """Application data directory"""
        pass

    @property
    @abstractmethod
    def models_dir(self) -> Path:
        """Models storage directory"""
        pass

    @property
    @abstractmethod
    def recordings_dir(self) -> Path:
        """Recordings storage directory"""
        pass

    @property
    @abstractmethod
    def transcripts_dir(self) -> Path:
        """Transcripts export directory"""
        pass

    @property
    @abstractmethod
    def device(self) -> str:
        """Compute device (cuda/cpu)"""
        pass

    @property
    @abstractmethod
    def whisper_model(self) -> str:
        """Whisper model name"""
        pass

    @abstractmethod
    def validate_device(self) -> str:
        """Validate and return appropriate device"""
        pass


class IAudioRecorderService(ABC):
    """Audio recorder service interface"""

    @abstractmethod
    def list_devices(self) -> List[Dict[str, Any]]:
        """Get list of available audio devices"""
        pass

    @abstractmethod
    def get_loopback_device(self) -> Optional[int]:
        """Get system audio loopback device index"""
        pass

    @abstractmethod
    def get_default_microphone(self) -> Optional[int]:
        """Get default microphone device index"""
        pass

    @abstractmethod
    def cleanup(self):
        """Cleanup audio resources"""
        pass


class ITranscriptionService(ABC):
    """Transcription service interface"""

    @abstractmethod
    def ensure_models_loaded(self, language: Optional[str] = None):
        """Load transcription models if not already loaded"""
        pass

    @abstractmethod
    def unload_models(self):
        """Unload models to free memory"""
        pass

    @abstractmethod
    def apply_preset(self, preset_id: str, override_device: bool = False):
        """Apply quality preset"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        pass


class IExportService(ABC):
    """Transcript export service interface"""

    @abstractmethod
    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        format_id: Optional[str] = None
    ) -> bool:
        """Export transcription result to file"""
        pass

    @abstractmethod
    def export_multiple(
        self,
        result: Dict[str, Any],
        base_path: Path,
        format_ids: List[str]
    ) -> Dict[str, bool]:
        """Export transcript to multiple formats"""
        pass

    @abstractmethod
    def available_formats(self) -> Dict[str, str]:
        """Get available export formats"""
        pass


class IAudioFormatService(ABC):
    """Audio format handling service interface"""

    @abstractmethod
    def get_handler(self, file_path: Path) -> Optional[Any]:
        """Get appropriate format handler for file"""
        pass

    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Get list of all supported extensions"""
        pass


class IStyleService(ABC):
    """UI style management service interface"""

    @abstractmethod
    def get_stylesheet(self) -> str:
        """Get current stylesheet"""
        pass

    @abstractmethod
    def set_theme(self, theme: Any):
        """Set UI theme"""
        pass
