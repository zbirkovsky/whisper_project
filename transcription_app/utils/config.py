"""
Application configuration using Pydantic
Supports both .env files and settings.toml
"""
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
    recordings_dir: Path = Field(
        default_factory=lambda: Path.home() / '.cloudcall' / 'recordings',
        description="Audio recordings storage directory"
    )
    transcripts_dir: Path = Field(
        default_factory=lambda: Path.home() / '.cloudcall' / 'transcripts',
        description="Transcripts export directory"
    )

    # Transcription settings
    whisper_model: str = Field(
        default="large-v3",
        description="Whisper model size: tiny, base, small, medium, large-v2, large-v3"
    )
    compute_type: str = Field(
        default="float16",
        description="Computation precision: float16 for GPU, int8 for CPU, float32 for compatibility"
    )
    batch_size: int = Field(
        default=16,
        description="Batch size for transcription"
    )
    device: str = Field(
        default="cuda",
        description="Device to use: cuda for GPU acceleration or cpu for CPU-only"
    )
    language: str = Field(
        default="auto",
        description="Language code for transcription (auto for auto-detect)"
    )

    # Language-specific models for optimal quality
    model_czech: str = Field(
        default="whisper-large-v3-czech-cv13-ct2",
        description="Model to use for Czech language"
    )
    model_english: str = Field(
        default="large-v3-turbo",
        description="Model to use for English language"
    )
    model_fallback: str = Field(
        default="large-v3",
        description="Fallback model when language is unknown"
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
        default=2048,
        description="Audio chunk size for recording (larger = better quality, less crackling)"
    )
    audio_format: str = Field(
        default="int16",
        description="Audio format"
    )

    # Audio gain boost settings
    mixed_rms_threshold: float = Field(default=500.0)
    mixed_target_rms: float = Field(default=400.0)
    mixed_max_boost: float = Field(default=2.5)
    mixed_use_soft_clipping: bool = Field(default=True)
    mic_only_rms_threshold: float = Field(default=1000.0)
    mic_only_target_rms: float = Field(default=2000.0)
    mic_only_max_boost: float = Field(default=3.0)
    mic_only_use_soft_clipping: bool = Field(default=False)
    rms_floor: float = Field(default=100.0)

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
    auto_detect_teams_meeting: bool = Field(
        default=True,
        description="Automatically detect Teams meeting names for recordings"
    )

    # UI dimensions and layout
    window_min_width: int = Field(default=1100)
    window_min_height: int = Field(default=600)
    sidebar_min_width: int = Field(default=200)
    sidebar_max_width: int = Field(default=350)
    file_queue_min_height: int = Field(default=100)
    vertical_splitter_sizes: list[int] = Field(default=[60, 120, 520])
    horizontal_splitter_sizes: list[int] = Field(default=[250, 650])

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
        # Resolve relative to the project root (3 levels up from utils/config.py)
        project_root = Path(__file__).parent.parent.parent
        settings_file = project_root / 'config' / 'settings.toml'
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
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

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
        """Validate and return the appropriate device, adjusting compute_type if needed"""
        if self.device == "cuda" and not self.get_cuda_available():
            print("Warning: CUDA not available, falling back to CPU")
            # Also adjust compute_type for CPU
            if self.compute_type == "float16":
                self.compute_type = "float32"
                print("Info: Adjusted compute_type to float32 for CPU")
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
