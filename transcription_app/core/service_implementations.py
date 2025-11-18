"""
Service implementations that wrap existing components
Provides DI-friendly wrappers for legacy code
"""
from pathlib import Path
from typing import Optional, List, Dict, Any

from transcription_app.core.services import (
    IConfigService,
    IAudioRecorderService,
    ITranscriptionService,
    IExportService,
    IAudioFormatService
)
from transcription_app.utils.config import AppConfig
from transcription_app.core.audio_recorder import AudioRecorder
from transcription_app.core.transcription_engine import TranscriptionEngine
from transcription_app.core.transcript_exporter import TranscriptExporter
from transcription_app.core.audio_formats import AudioFormatRegistry


class ConfigService(IConfigService):
    """Configuration service wrapper"""

    def __init__(self, config: AppConfig):
        self._config = config

    @property
    def app_dir(self) -> Path:
        return self._config.app_dir

    @property
    def models_dir(self) -> Path:
        return self._config.models_dir

    @property
    def recordings_dir(self) -> Path:
        return self._config.recordings_dir

    @property
    def transcripts_dir(self) -> Path:
        return self._config.transcripts_dir

    @property
    def device(self) -> str:
        return self._config.device

    @property
    def whisper_model(self) -> str:
        return self._config.whisper_model

    def validate_device(self) -> str:
        return self._config.validate_device()

    # Allow direct access to underlying config for backward compatibility
    def get_config(self) -> AppConfig:
        return self._config


class AudioRecorderService(IAudioRecorderService):
    """Audio recorder service wrapper"""

    def __init__(self, config: AppConfig):
        self._recorder = AudioRecorder(config)

    def list_devices(self) -> List[Dict[str, Any]]:
        return self._recorder.list_devices()

    def get_loopback_device(self) -> Optional[int]:
        return self._recorder.get_loopback_device()

    def get_default_microphone(self) -> Optional[int]:
        return self._recorder.get_default_microphone()

    def cleanup(self):
        self._recorder.cleanup()

    # Provide access to underlying recorder for advanced use
    def get_recorder(self) -> AudioRecorder:
        return self._recorder


class TranscriptionService(ITranscriptionService):
    """Transcription service wrapper"""

    def __init__(self, config: AppConfig):
        self._engine = TranscriptionEngine(config)

    def ensure_models_loaded(self, language: Optional[str] = None):
        self._engine.ensure_models_loaded(language)

    def unload_models(self):
        self._engine.unload_models()

    def apply_preset(self, preset_id: str, override_device: bool = False):
        self._engine.apply_preset(preset_id, override_device)

    def get_model_info(self) -> Dict[str, Any]:
        return self._engine.get_model_info()

    # Provide access to underlying engine
    def get_engine(self) -> TranscriptionEngine:
        return self._engine


class ExportService(IExportService):
    """Export service wrapper"""

    def __init__(self):
        self._exporter = TranscriptExporter()

    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        format_id: Optional[str] = None
    ) -> bool:
        return self._exporter.export(result, output_path, format_id)

    def export_multiple(
        self,
        result: Dict[str, Any],
        base_path: Path,
        format_ids: List[str]
    ) -> Dict[str, bool]:
        return self._exporter.export_multiple(result, base_path, format_ids)

    def available_formats(self) -> Dict[str, str]:
        return self._exporter.available_formats()

    # Provide access to underlying exporter
    def get_exporter(self) -> TranscriptExporter:
        return self._exporter


class AudioFormatService(IAudioFormatService):
    """Audio format service wrapper"""

    def __init__(self, registry: AudioFormatRegistry):
        self._registry = registry

    def get_handler(self, file_path: Path) -> Optional[Any]:
        return self._registry.get_handler(file_path)

    def supported_extensions(self) -> List[str]:
        return self._registry.supported_extensions()

    # Provide access to underlying registry
    def get_registry(self) -> AudioFormatRegistry:
        return self._registry
