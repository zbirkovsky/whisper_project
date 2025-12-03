"""
Pytest configuration and fixtures for CloudCall Transcription tests
"""
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.mocks import (
    MockConfigService,
    MockTranscriptionService,
    MockAudioRecorderService,
    MockExportService,
)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration service"""
    return MockConfigService(
        app_dir=temp_dir / 'app',
        models_dir=temp_dir / 'models',
        recordings_dir=temp_dir / 'recordings',
        transcripts_dir=temp_dir / 'transcripts',
    )


@pytest.fixture
def mock_transcription_service():
    """Create a mock transcription service"""
    return MockTranscriptionService()


@pytest.fixture
def mock_audio_recorder_service():
    """Create a mock audio recorder service"""
    return MockAudioRecorderService()


@pytest.fixture
def mock_export_service():
    """Create a mock export service"""
    return MockExportService()


@pytest.fixture
def sample_transcription_result() -> Dict[str, Any]:
    """Create a sample transcription result for testing"""
    return {
        'file_path': '/tmp/test_audio.wav',
        'file_name': 'test_audio.wav',
        'language': 'en',
        'segments': [
            {
                'start': 0.0,
                'end': 2.5,
                'text': 'Hello, this is a test.',
                'speaker': 'SPEAKER_00'
            },
            {
                'start': 2.5,
                'end': 5.0,
                'text': 'Testing the transcription system.',
                'speaker': 'SPEAKER_01'
            },
            {
                'start': 5.0,
                'end': 7.5,
                'text': 'Everything should work correctly.',
                'speaker': 'SPEAKER_00'
            },
        ]
    }


@pytest.fixture
def sample_audio_bytes():
    """Create sample audio bytes for testing"""
    import numpy as np
    # Generate 1 second of silence at 16kHz
    silence = np.zeros(16000, dtype=np.int16)
    return silence.tobytes()


@pytest.fixture
def mock_torch():
    """Mock torch module for tests that don't need GPU"""
    with patch.dict('sys.modules', {'torch': MagicMock()}):
        mock = sys.modules['torch']
        mock.cuda.is_available.return_value = False
        mock.cuda.empty_cache = MagicMock()
        yield mock


@pytest.fixture
def mock_whisperx():
    """Mock whisperx module for tests"""
    with patch.dict('sys.modules', {'whisperx': MagicMock()}):
        mock = sys.modules['whisperx']
        mock.load_model.return_value = MagicMock()
        mock.load_audio.return_value = MagicMock()
        yield mock


# Environment setup
@pytest.fixture(autouse=True)
def setup_test_environment(temp_dir):
    """Setup test environment for each test"""
    # Ensure temp directories exist
    (temp_dir / 'app').mkdir(parents=True, exist_ok=True)
    (temp_dir / 'models').mkdir(parents=True, exist_ok=True)
    (temp_dir / 'recordings').mkdir(parents=True, exist_ok=True)
    (temp_dir / 'transcripts').mkdir(parents=True, exist_ok=True)
    yield


# Skip markers
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU"
    )
