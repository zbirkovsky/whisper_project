"""
Tests for the TranscriptionViewModel
"""
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestTranscriptionViewModel:
    """Tests for TranscriptionViewModel class"""

    def test_viewmodel_initialization(self):
        """Test viewmodel initializes correctly"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        assert vm.engine == mock_engine
        assert vm.recorder == mock_recorder
        assert len(vm.active_workers) == 0
        assert len(vm.queue) == 0
        assert vm.is_processing == False

    def test_add_valid_files(self, temp_dir):
        """Test adding valid audio files"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        # Create test files
        test_file = temp_dir / 'test.mp3'
        test_file.touch()

        # Track emitted signals
        files_added = []
        vm.files_added.connect(files_added.append)

        # Add files
        with patch.object(vm, 'process_next'):  # Prevent actual processing
            vm.add_files([str(test_file)])

        assert len(files_added) == 1
        assert str(test_file) in files_added[0]

    def test_add_invalid_files(self, temp_dir):
        """Test adding invalid files are filtered out"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        # Create test file with invalid extension
        test_file = temp_dir / 'test.xyz'
        test_file.touch()

        files_added = []
        vm.files_added.connect(files_added.append)

        vm.add_files([str(test_file)])

        assert len(files_added) == 0

    def test_add_nonexistent_files(self):
        """Test adding nonexistent files are filtered out"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        files_added = []
        vm.files_added.connect(files_added.append)

        vm.add_files(['/nonexistent/path/file.mp3'])

        assert len(files_added) == 0

    def test_cancel_transcription(self):
        """Test cancelling transcription"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        # Add a mock worker
        mock_worker = MagicMock()
        vm.active_workers['test.mp3'] = mock_worker

        vm.cancel_transcription('test.mp3')

        mock_worker.cancel.assert_called_once()

    def test_cancel_all(self):
        """Test cancelling all workers"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        # Add multiple mock workers
        mock_worker1 = MagicMock()
        mock_worker2 = MagicMock()
        vm.active_workers['test1.mp3'] = mock_worker1
        vm.active_workers['test2.mp3'] = mock_worker2

        vm.cancel_all()

        mock_worker1.cancel.assert_called_once()
        mock_worker2.cancel.assert_called_once()
        mock_worker1.wait.assert_called_once()
        mock_worker2.wait.assert_called_once()
        assert len(vm.active_workers) == 0

    def test_cleanup(self):
        """Test cleanup method"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        vm.cleanup()

        mock_recorder.cleanup.assert_called_once()

    def test_process_next_when_queue_empty(self):
        """Test process_next does nothing when queue is empty"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)

        # Should not raise
        vm.process_next()

        assert vm.is_processing == False

    def test_process_next_skips_when_processing(self, temp_dir):
        """Test process_next skips when already processing"""
        from transcription_app.viewmodels.transcription_vm import TranscriptionViewModel

        mock_engine = MagicMock()
        mock_recorder = MagicMock()

        vm = TranscriptionViewModel(mock_engine, mock_recorder)
        vm.is_processing = True

        # Add something to queue
        vm.queue.append(str(temp_dir / 'test.mp3'))

        vm.process_next()

        # Queue should still have item
        assert len(vm.queue) == 1


class TestSanitizeFilename:
    """Tests for filename sanitization"""

    def test_sanitize_removes_invalid_chars(self):
        """Test that invalid Windows characters are removed/replaced"""
        from transcription_app.viewmodels.transcription_vm import sanitize_filename

        # Test various invalid characters
        assert '<' not in sanitize_filename('test<file')
        assert '>' not in sanitize_filename('test>file')
        assert ':' not in sanitize_filename('test:file') or '-' in sanitize_filename('test:file')
        assert '"' not in sanitize_filename('test"file')
        assert '/' not in sanitize_filename('test/file') or '-' in sanitize_filename('test/file')
        assert '\\' not in sanitize_filename('test\\file') or '-' in sanitize_filename('test\\file')
        assert '|' not in sanitize_filename('test|file') or '-' in sanitize_filename('test|file')
        assert '?' not in sanitize_filename('test?file')
        assert '*' not in sanitize_filename('test*file')

    def test_sanitize_replaces_dashes(self):
        """Test that em-dashes and en-dashes are replaced with hyphens"""
        from transcription_app.viewmodels.transcription_vm import sanitize_filename

        result = sanitize_filename('meeting—name–here')
        assert '—' not in result  # em-dash
        assert '–' not in result  # en-dash
        assert '-' in result

    def test_sanitize_strips_leading_trailing(self):
        """Test that leading/trailing spaces and periods are stripped"""
        from transcription_app.viewmodels.transcription_vm import sanitize_filename

        assert sanitize_filename('  test  ') == 'test'
        assert sanitize_filename('..test..') == 'test'
        assert sanitize_filename('. test .') == 'test'

    def test_sanitize_collapses_whitespace(self):
        """Test that multiple spaces are collapsed"""
        from transcription_app.viewmodels.transcription_vm import sanitize_filename

        result = sanitize_filename('test    multiple   spaces')
        assert '    ' not in result
        assert 'test multiple spaces' == result

    def test_sanitize_collapses_hyphens(self):
        """Test that multiple hyphens are collapsed"""
        from transcription_app.viewmodels.transcription_vm import sanitize_filename

        result = sanitize_filename('test---multiple---hyphens')
        assert '---' not in result
