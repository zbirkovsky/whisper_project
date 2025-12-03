"""
Tests for the transcription engine
"""
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest


class TestTranscriptionEngine:
    """Tests for TranscriptionEngine class"""

    def test_engine_initialization(self, mock_config):
        """Test engine initializes with correct settings"""
        with patch('transcription_app.core.transcription_engine.whisperx'):
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False
                mock_torch.cuda.empty_cache = MagicMock()

                from transcription_app.core.transcription_engine import TranscriptionEngine

                engine = TranscriptionEngine(mock_config)

                assert engine.device == 'cpu'
                assert engine.model is None
                assert engine.current_preset == 'cpu_optimized'

    def test_apply_preset_changes_settings(self, mock_config):
        """Test applying preset changes engine settings"""
        with patch('transcription_app.core.transcription_engine.whisperx'):
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False
                mock_torch.cuda.empty_cache = MagicMock()

                from transcription_app.core.transcription_engine import TranscriptionEngine

                engine = TranscriptionEngine(mock_config)

                # Apply a preset
                engine.apply_preset('cpu_optimized')

                assert engine.current_preset == 'cpu_optimized'
                assert engine.asr_options is not None
                assert engine.vad_options is not None

    def test_unload_models_clears_memory(self, mock_config):
        """Test unloading models clears GPU memory"""
        with patch('transcription_app.core.transcription_engine.whisperx'):
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False
                mock_torch.cuda.empty_cache = MagicMock()

                from transcription_app.core.transcription_engine import TranscriptionEngine

                engine = TranscriptionEngine(mock_config)
                engine.model = MagicMock()
                engine.diarize_model = MagicMock()

                engine.unload_models()

                assert engine.model is None
                assert engine.diarize_model is None

    def test_get_model_info(self, mock_config):
        """Test getting model information"""
        with patch('transcription_app.core.transcription_engine.whisperx'):
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False

                from transcription_app.core.transcription_engine import TranscriptionEngine

                engine = TranscriptionEngine(mock_config)
                info = engine.get_model_info()

                assert 'whisper_model' in info
                assert 'device' in info
                assert 'model_loaded' in info
                assert info['model_loaded'] == False


class TestTranscriptionWorker:
    """Tests for TranscriptionWorker class"""

    def test_worker_cancel_sets_flag(self, mock_config):
        """Test cancelling worker sets is_cancelled flag"""
        with patch('transcription_app.core.transcription_engine.whisperx'):
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False
                mock_torch.cuda.empty_cache = MagicMock()

                from transcription_app.core.transcription_engine import (
                    TranscriptionEngine,
                    TranscriptionWorker
                )

                engine = TranscriptionEngine(mock_config)
                worker = TranscriptionWorker(
                    engine,
                    Path('/tmp/test.wav'),
                    enable_diarization=False,
                    language='en'
                )

                worker.cancel()

                assert worker.is_cancelled == True


class TestFormatFunctions:
    """Tests for transcript formatting functions"""

    def test_format_transcript_text_with_timestamps(self, sample_transcription_result):
        """Test formatting transcript with timestamps"""
        from transcription_app.core.transcription_engine import format_transcript_text

        result = format_transcript_text(sample_transcription_result, include_timestamps=True)

        assert 'test_audio.wav' in result
        assert 'Language: en' in result
        assert 'SPEAKER_00' in result
        assert 'Hello, this is a test.' in result

    def test_format_transcript_text_without_timestamps(self, sample_transcription_result):
        """Test formatting transcript without timestamps"""
        from transcription_app.core.transcription_engine import format_transcript_text

        result = format_transcript_text(sample_transcription_result, include_timestamps=False)

        assert 'Hello, this is a test.' in result
        # Timestamps should not be present
        assert '[0.00s]' not in result

    def test_format_transcript_srt(self, sample_transcription_result):
        """Test SRT format generation"""
        from transcription_app.core.transcription_engine import format_transcript_srt

        result = format_transcript_srt(sample_transcription_result)

        # Should have subtitle indices
        assert '1\n' in result
        assert '2\n' in result

        # Should have timestamp arrows
        assert '-->' in result

        # Should have text content
        assert 'Hello, this is a test.' in result

    def test_srt_time_formatting(self):
        """Test SRT time format conversion"""
        from transcription_app.core.transcription_engine import _format_srt_time

        # Test basic seconds
        assert _format_srt_time(0) == '00:00:00,000'
        assert _format_srt_time(1.5) == '00:00:01,500'

        # Test minutes
        assert _format_srt_time(65.123) == '00:01:05,123'

        # Test hours
        assert _format_srt_time(3661.5) == '01:01:01,500'


class TestLanguageModelSelection:
    """Tests for language-specific model selection"""

    def test_model_selection_for_czech(self, mock_config):
        """Test Czech language uses Czech-specific model"""
        with patch('transcription_app.core.transcription_engine.whisperx') as mock_whisperx:
            with patch('transcription_app.core.transcription_engine.torch') as mock_torch:
                mock_torch.cuda.is_available.return_value = False
                mock_torch.cuda.empty_cache = MagicMock()
                mock_whisperx.load_model.return_value = MagicMock()

                from transcription_app.core.transcription_engine import TranscriptionEngine
                from transcription_app.utils.language_detector import get_best_model_for_language

                # Mock the language detector
                with patch('transcription_app.core.transcription_engine.get_best_model_for_language') as mock_get_model:
                    mock_get_model.return_value = 'whisper-large-v3-czech-cv13-ct2'

                    engine = TranscriptionEngine(mock_config)
                    engine.ensure_models_loaded('cs')

                    # Should have called load_model with Czech model
                    mock_whisperx.load_model.assert_called()
                    call_args = mock_whisperx.load_model.call_args
                    assert 'czech' in call_args[0][0] or engine.current_model_name == 'whisper-large-v3-czech-cv13-ct2'
