"""
Application configuration using Pydantic
Supports both .env files and settings.toml
"""
import os
import toml
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration with environment variable support"""

    # Application paths
    app_dir: Path = Field(
        default_factory=lambda: Path.home() / '.cloudcall',
        description="Application data directory"
    )
    models_dir: Path = Field(
        default_factory=lambda: Path.home() / '.cloudcall' / 'models',
        description="Models storage directory"
    )

    # Transcription settings
    whisper_model: str = Field(
        default="base",
        description="Whisper model size: tiny, base, small, medium, large-v2, large-v3"
    )
    compute_type: str = Field(
        default="float16",
        description="Computation precision: float16, int8, float32"
    )
    batch_size: int = Field(
        default=16,
        description="Batch size for transcription"
    )
    device: str = Field(
        default="cuda",
        description="Device to use: cuda or cpu"
    )
    language: str = Field(
        default="auto",
        description="Language code for transcription (auto for auto-detect)"
    )

    # Audio recording settings
    sample_rate: int = Field(
        default=48000,
        description="Audio sample rate in Hz"
    )
    channels: int = Field(
        default=2,
        description="Number of audio channels"
    )
    chunk_size: int = Field(
        default=512,
        description="Audio chunk size for recording"
    )
    audio_format: str = Field(
        default="int16",
        description="Audio format"
    )

    # Diarization settings
    diarization_enabled: bool = Field(
        default=True,
        description="Enable speaker diarization"
    )
    min_speakers: int = Field(
        default=1,
        description="Minimum number of speakers"
    )
    max_speakers: int = Field(
        default=10,
        description="Maximum number of speakers"
    )
    hf_token: str = Field(
        default="",
        description="HuggingFace authentication token for Pyannote"
    )

    # UI settings
    theme: str = Field(
        default="auto",
        description="UI theme: auto, light, dark"
    )
    window_width: int = Field(
        default=1000,
        description="Default window width"
    )
    window_height: int = Field(
        default=700,
        description="Default window height"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
    )
    log_file: Path = Field(
        default_factory=lambda: Path.home() / '.cloudcall' / 'app.log',
        description="Log file path"
    )
    max_log_size_mb: int = Field(
        default=10,
        description="Maximum log file size in MB"
    )
    backup_count: int = Field(
        default=5,
        description="Number of log backup files to keep"
    )

    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='CLOUDCALL_',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )

    def __init__(self, **kwargs):
        # First try to load from settings.toml if it exists
        settings_file = Path('config/settings.toml')
        toml_config = {}

        if settings_file.exists():
            try:
                toml_data = toml.load(settings_file)
                # Flatten TOML structure
                for section, values in toml_data.items():
                    if isinstance(values, dict):
                        toml_config.update(values)
            except Exception as e:
                print(f"Warning: Could not load settings.toml: {e}")

        # Merge TOML config with kwargs (kwargs take precedence)
        merged_config = {**toml_config, **kwargs}

        super().__init__(**merged_config)

        # Ensure directories exist
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Convert log file path to absolute if relative
        if not self.log_file.is_absolute():
            self.log_file = self.app_dir / self.log_file.name

    def get_cuda_available(self) -> bool:
        """Check if CUDA is available"""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False

    def validate_device(self) -> str:
        """Validate and return the appropriate device"""
        if self.device == "cuda" and not self.get_cuda_available():
            print("Warning: CUDA not available, falling back to CPU")
            return "cpu"
        return self.device

    def get_max_log_bytes(self) -> int:
        """Get maximum log file size in bytes"""
        return self.max_log_size_mb * 1024 * 1024


# Global config instance
_config_instance: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance


def reload_config() -> AppConfig:
    """Reload configuration from files"""
    global _config_instance
    _config_instance = AppConfig()
    return _config_instance
