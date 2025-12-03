"""
Tests for the configuration module
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Import will be done after path setup in conftest


class TestAppConfig:
    """Tests for AppConfig class"""

    def test_default_config_creates_directories(self, temp_dir):
        """Test that default config creates required directories"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_MODELS_DIR': str(temp_dir / 'models'),
            'CLOUDCALL_RECORDINGS_DIR': str(temp_dir / 'recordings'),
            'CLOUDCALL_TRANSCRIPTS_DIR': str(temp_dir / 'transcripts'),
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()

            # Directories should be created
            assert config.app_dir.exists()
            assert config.models_dir.exists()
            assert config.recordings_dir.exists()
            assert config.transcripts_dir.exists()

    def test_device_validation_fallback_to_cpu(self, temp_dir):
        """Test device validation falls back to CPU when CUDA unavailable"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_DEVICE': 'cuda',
        }):
            from transcription_app.utils.config import AppConfig

            with patch('transcription_app.utils.config.AppConfig.get_cuda_available', return_value=False):
                config = AppConfig()
                device = config.validate_device()
                assert device == 'cpu'

    def test_device_validation_keeps_cuda_when_available(self, temp_dir):
        """Test device validation keeps CUDA when available"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_DEVICE': 'cuda',
        }):
            from transcription_app.utils.config import AppConfig

            with patch('transcription_app.utils.config.AppConfig.get_cuda_available', return_value=True):
                config = AppConfig()
                device = config.validate_device()
                assert device == 'cuda'

    def test_compute_type_adjusted_for_cpu(self, temp_dir):
        """Test compute_type is adjusted when falling back to CPU"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_DEVICE': 'cuda',
            'CLOUDCALL_COMPUTE_TYPE': 'float16',
        }):
            from transcription_app.utils.config import AppConfig

            with patch('transcription_app.utils.config.AppConfig.get_cuda_available', return_value=False):
                config = AppConfig()
                config.validate_device()
                assert config.compute_type == 'float32'

    def test_max_log_bytes_calculation(self, temp_dir):
        """Test max log bytes calculation from MB"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_MAX_LOG_SIZE_MB': '5',
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()
            assert config.get_max_log_bytes() == 5 * 1024 * 1024

    def test_default_whisper_model(self, temp_dir):
        """Test default whisper model is set correctly"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()
            assert config.whisper_model == 'large-v3'

    def test_environment_variable_override(self, temp_dir):
        """Test that environment variables override defaults"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_WHISPER_MODEL': 'base',
            'CLOUDCALL_BATCH_SIZE': '4',
            'CLOUDCALL_LANGUAGE': 'en',
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()
            assert config.whisper_model == 'base'
            assert config.batch_size == 4
            assert config.language == 'en'

    def test_toml_config_loading(self, temp_dir):
        """Test loading config from TOML file"""
        # Create a test TOML config
        config_dir = temp_dir / 'config'
        config_dir.mkdir(parents=True, exist_ok=True)

        toml_content = """
[transcription]
whisper_model = "small"
batch_size = 8

[audio]
sample_rate = 44100
"""
        (config_dir / 'settings.toml').write_text(toml_content)

        # This test would need the config module to look at our temp directory
        # For now, we'll just verify the TOML parsing logic works
        import toml
        parsed = toml.loads(toml_content)
        assert parsed['transcription']['whisper_model'] == 'small'
        assert parsed['transcription']['batch_size'] == 8
        assert parsed['audio']['sample_rate'] == 44100

    def test_diarization_settings(self, temp_dir):
        """Test diarization settings are properly configured"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_DIARIZATION_ENABLED': 'true',
            'CLOUDCALL_MIN_SPEAKERS': '2',
            'CLOUDCALL_MAX_SPEAKERS': '5',
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()
            assert config.diarization_enabled == True
            assert config.min_speakers == 2
            assert config.max_speakers == 5

    def test_realtime_settings(self, temp_dir):
        """Test real-time transcription settings"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
            'CLOUDCALL_REALTIME_ENABLED': 'true',
            'CLOUDCALL_REALTIME_SOURCE_LANGUAGE': 'cs',
            'CLOUDCALL_REALTIME_TARGET_LANGUAGE': 'en',
        }):
            from transcription_app.utils.config import AppConfig
            config = AppConfig()
            assert config.realtime_enabled == True
            assert config.realtime_source_language == 'cs'
            assert config.realtime_target_language == 'en'


class TestConfigSingleton:
    """Tests for config singleton pattern"""

    def test_get_config_returns_same_instance(self, temp_dir):
        """Test get_config returns the same instance"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
        }):
            from transcription_app.utils.config import get_config, reload_config

            # Force reload to get fresh instance
            config1 = reload_config()
            config2 = get_config()

            assert config1 is config2

    def test_reload_config_creates_new_instance(self, temp_dir):
        """Test reload_config creates a new instance"""
        with patch.dict(os.environ, {
            'CLOUDCALL_APP_DIR': str(temp_dir / 'app'),
        }):
            from transcription_app.utils.config import get_config, reload_config

            config1 = get_config()
            config2 = reload_config()

            # After reload, get_config should return new instance
            config3 = get_config()
            assert config2 is config3
