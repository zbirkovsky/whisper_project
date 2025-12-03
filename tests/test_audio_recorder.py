"""
Tests for the audio recorder module
"""
from unittest.mock import patch, MagicMock
from pathlib import Path

import pytest


class TestAudioRecorder:
    """Tests for AudioRecorder class"""

    def test_list_devices(self):
        """Test listing audio devices"""
        with patch('transcription_app.core.audio_recorder.pyaudio') as mock_pyaudio:
            mock_pa_instance = MagicMock()
            mock_pa_instance.get_device_count.return_value = 2
            mock_pa_instance.get_device_info_by_index.side_effect = [
                {
                    'index': 0,
                    'name': 'Microphone',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 0,
                    'isLoopbackDevice': False,
                    'defaultSampleRate': 44100
                },
                {
                    'index': 1,
                    'name': 'Speakers (Loopback)',
                    'maxInputChannels': 2,
                    'maxOutputChannels': 0,
                    'isLoopbackDevice': True,
                    'defaultSampleRate': 48000
                }
            ]
            mock_pyaudio.PyAudio.return_value = mock_pa_instance

            from transcription_app.core.audio_recorder import AudioRecorder

            mock_config = MagicMock()
            recorder = AudioRecorder(mock_config)
            devices = recorder.list_devices()

            assert len(devices) == 2
            assert devices[0]['name'] == 'Microphone'
            assert devices[1]['is_loopback'] == True

    def test_get_default_microphone(self):
        """Test getting default microphone"""
        with patch('transcription_app.core.audio_recorder.pyaudio') as mock_pyaudio:
            mock_pa_instance = MagicMock()
            mock_pa_instance.get_default_input_device_info.return_value = {
                'index': 0,
                'name': 'Default Mic'
            }
            mock_pyaudio.PyAudio.return_value = mock_pa_instance

            from transcription_app.core.audio_recorder import AudioRecorder

            mock_config = MagicMock()
            recorder = AudioRecorder(mock_config)
            mic_index = recorder.get_default_microphone()

            assert mic_index == 0

    def test_get_default_microphone_handles_error(self):
        """Test getting default microphone handles errors"""
        with patch('transcription_app.core.audio_recorder.pyaudio') as mock_pyaudio:
            mock_pa_instance = MagicMock()
            mock_pa_instance.get_default_input_device_info.side_effect = Exception('No device')
            mock_pyaudio.PyAudio.return_value = mock_pa_instance

            from transcription_app.core.audio_recorder import AudioRecorder

            mock_config = MagicMock()
            recorder = AudioRecorder(mock_config)
            mic_index = recorder.get_default_microphone()

            assert mic_index is None

    def test_cleanup(self):
        """Test cleanup terminates PyAudio"""
        with patch('transcription_app.core.audio_recorder.pyaudio') as mock_pyaudio:
            mock_pa_instance = MagicMock()
            mock_pyaudio.PyAudio.return_value = mock_pa_instance

            from transcription_app.core.audio_recorder import AudioRecorder

            mock_config = MagicMock()
            recorder = AudioRecorder(mock_config)
            recorder._ensure_pyaudio()  # Initialize PyAudio

            recorder.cleanup()

            mock_pa_instance.terminate.assert_called_once()
            assert recorder.p is None


class TestRecordingWorker:
    """Tests for RecordingWorker class"""

    def test_worker_initialization(self, temp_dir):
        """Test worker initializes correctly"""
        with patch('transcription_app.core.audio_recorder.pyaudio'):
            from transcription_app.core.audio_recorder import RecordingWorker

            mock_config = MagicMock()
            mock_config.sample_rate = 16000
            mock_config.chunk_size = 1024

            output_file = temp_dir / 'test_recording.wav'
            worker = RecordingWorker(
                config=mock_config,
                duration=10,
                output_file=output_file,
                record_mic=True,
                record_system=False
            )

            assert worker.duration == 10
            assert worker.record_mic == True
            assert worker.record_system == False
            assert worker.is_cancelled == False

    def test_worker_cancel(self, temp_dir):
        """Test worker cancellation"""
        with patch('transcription_app.core.audio_recorder.pyaudio'):
            from transcription_app.core.audio_recorder import RecordingWorker

            mock_config = MagicMock()
            mock_config.sample_rate = 16000
            mock_config.chunk_size = 1024

            output_file = temp_dir / 'test_recording.wav'
            worker = RecordingWorker(
                config=mock_config,
                duration=10,
                output_file=output_file
            )

            worker.cancel()

            assert worker.is_cancelled == True

    def test_downsample_integer_ratio(self):
        """Test downsampling with integer ratio (48000 -> 16000)"""
        import numpy as np
        from transcription_app.core.audio_recorder import RecordingWorker

        # Create test audio at 48kHz
        source_rate = 48000
        target_rate = 16000
        duration = 0.1  # 100ms
        source_samples = int(source_rate * duration)

        audio = np.arange(source_samples, dtype=np.int16)
        result = RecordingWorker._downsample(audio, source_rate, target_rate)

        expected_samples = int(target_rate * duration)
        assert len(result) == expected_samples

    def test_downsample_same_rate(self):
        """Test downsampling when rates are the same"""
        import numpy as np
        from transcription_app.core.audio_recorder import RecordingWorker

        audio = np.arange(1600, dtype=np.int16)
        result = RecordingWorker._downsample(audio, 16000, 16000)

        assert len(result) == len(audio)
        assert np.array_equal(result, audio)


class TestAudioProcessing:
    """Tests for audio processing utilities"""

    def test_stereo_to_mono(self):
        """Test stereo to mono conversion"""
        import numpy as np
        from transcription_app.utils.audio_processing import stereo_to_mono

        # Create stereo audio (interleaved L, R, L, R, ...)
        stereo = np.array([100, 200, 300, 400, 500, 600], dtype=np.int16)
        mono = stereo_to_mono(stereo)

        # Should average left and right channels
        expected_length = len(stereo) // 2
        assert len(mono) == expected_length

    def test_calculate_rms(self):
        """Test RMS calculation"""
        import numpy as np
        from transcription_app.utils.audio_processing import calculate_rms

        # Silence should have RMS of 0
        silence = np.zeros(1000, dtype=np.int16)
        assert calculate_rms(silence) == 0

        # Constant value should have predictable RMS
        constant = np.full(1000, 1000, dtype=np.int16)
        rms = calculate_rms(constant)
        assert rms == pytest.approx(1000, abs=1)
