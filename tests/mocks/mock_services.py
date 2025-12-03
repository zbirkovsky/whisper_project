"""
Mock service implementations for testing
"""
from pathlib import Path
from typing import Optional, List, Dict, Any
from unittest.mock import MagicMock


class MockConfigService:
    """Mock configuration service for testing"""

    def __init__(self, **overrides):
        self._app_dir = overrides.get('app_dir', Path('/tmp/cloudcall_test'))
        self._models_dir = overrides.get('models_dir', Path('/tmp/cloudcall_test/models'))
        self._recordings_dir = overrides.get('recordings_dir', Path('/tmp/cloudcall_test/recordings'))
        self._transcripts_dir = overrides.get('transcripts_dir', Path('/tmp/cloudcall_test/transcripts'))
        self._device = overrides.get('device', 'cpu')
        self._whisper_model = overrides.get('whisper_model', 'base')
        self._compute_type = overrides.get('compute_type', 'float32')
        self._batch_size = overrides.get('batch_size', 8)
        self._language = overrides.get('language', 'auto')
        self._sample_rate = overrides.get('sample_rate', 16000)
        self._chunk_size = overrides.get('chunk_size', 1024)
        self._diarization_enabled = overrides.get('diarization_enabled', False)
        self._hf_token = overrides.get('hf_token', '')
        self._min_speakers = overrides.get('min_speakers', 1)
        self._max_speakers = overrides.get('max_speakers', 10)
        self._rms_floor = overrides.get('rms_floor', 100.0)

    @property
    def app_dir(self) -> Path:
        return self._app_dir

    @property
    def models_dir(self) -> Path:
        return self._models_dir

    @property
    def recordings_dir(self) -> Path:
        return self._recordings_dir

    @property
    def transcripts_dir(self) -> Path:
        return self._transcripts_dir

    @property
    def device(self) -> str:
        return self._device

    @device.setter
    def device(self, value: str):
        self._device = value

    @property
    def whisper_model(self) -> str:
        return self._whisper_model

    @property
    def compute_type(self) -> str:
        return self._compute_type

    @compute_type.setter
    def compute_type(self, value: str):
        self._compute_type = value

    @property
    def batch_size(self) -> int:
        return self._batch_size

    @batch_size.setter
    def batch_size(self, value: int):
        self._batch_size = value

    @property
    def language(self) -> str:
        return self._language

    @property
    def sample_rate(self) -> int:
        return self._sample_rate

    @property
    def chunk_size(self) -> int:
        return self._chunk_size

    @property
    def diarization_enabled(self) -> bool:
        return self._diarization_enabled

    @property
    def hf_token(self) -> str:
        return self._hf_token

    @property
    def min_speakers(self) -> int:
        return self._min_speakers

    @property
    def max_speakers(self) -> int:
        return self._max_speakers

    @property
    def rms_floor(self) -> float:
        return self._rms_floor

    def validate_device(self) -> str:
        return self._device

    def get_cuda_available(self) -> bool:
        return False


class MockTranscriptionService:
    """Mock transcription service for testing"""

    def __init__(self):
        self.model_loaded = False
        self.current_preset = 'cpu_optimized'
        self.unload_called = False
        self.models_loaded_count = 0

    def ensure_models_loaded(self, language: Optional[str] = None) -> None:
        self.model_loaded = True
        self.models_loaded_count += 1

    def unload_models(self) -> None:
        self.model_loaded = False
        self.unload_called = True

    def apply_preset(self, preset_id: str, override_device: bool = False) -> None:
        self.current_preset = preset_id

    def get_model_info(self) -> Dict[str, Any]:
        return {
            'whisper_model': 'base',
            'device': 'cpu',
            'compute_type': 'float32',
            'model_loaded': self.model_loaded,
            'diarization_enabled': False
        }

    def get_engine(self):
        """Return mock engine for backward compatibility"""
        return MagicMock()


class MockAudioRecorderService:
    """Mock audio recorder service for testing"""

    def __init__(self):
        self.devices = [
            {'index': 0, 'name': 'Default Microphone', 'max_inputs': 2, 'max_outputs': 0, 'is_loopback': False},
            {'index': 1, 'name': 'Speakers (Loopback)', 'max_inputs': 2, 'max_outputs': 0, 'is_loopback': True},
        ]
        self.cleanup_called = False

    def list_devices(self) -> List[Dict[str, Any]]:
        return self.devices

    def get_loopback_device(self) -> Optional[int]:
        for device in self.devices:
            if device.get('is_loopback', False):
                return device['index']
        return None

    def get_default_microphone(self) -> Optional[int]:
        for device in self.devices:
            if not device.get('is_loopback', False) and device.get('max_inputs', 0) > 0:
                return device['index']
        return None

    def cleanup(self) -> None:
        self.cleanup_called = True

    def get_recorder(self):
        """Return self for backward compatibility"""
        return self


class MockExportService:
    """Mock export service for testing"""

    def __init__(self):
        self.export_called = False
        self.exported_files: List[Path] = []

    def export(
        self,
        result: Dict[str, Any],
        output_path: Path,
        format_id: Optional[str] = None
    ) -> bool:
        self.export_called = True
        self.exported_files.append(output_path)
        return True

    def export_multiple(
        self,
        result: Dict[str, Any],
        base_path: Path,
        format_ids: List[str]
    ) -> Dict[str, bool]:
        results = {}
        for fmt in format_ids:
            output_path = base_path.with_suffix(f'.{fmt}')
            results[fmt] = self.export(result, output_path, fmt)
        return results

    def available_formats(self) -> Dict[str, str]:
        return {
            'txt': 'Plain Text',
            'srt': 'SRT Subtitles',
            'vtt': 'WebVTT Subtitles',
            'json': 'JSON',
            'md': 'Markdown'
        }
