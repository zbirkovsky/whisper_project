"""
ViewModel for transcription operations
Bridges GUI and business logic using MVVM pattern
"""
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot

from transcription_app.core.transcription_engine import TranscriptionWorker
from transcription_app.core.audio_recorder import RecordingWorker
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class TranscriptionViewModel(QObject):
    """ViewModel for main transcription functionality"""

    # Signals for View binding
    files_added = Signal(list)  # List of file paths added
    progress_changed = Signal(str, int, str)  # file_id, percentage, status
    transcription_completed = Signal(str, dict)  # file_id, result
    error_occurred = Signal(str, str)  # file_id, error_message
    recording_progress = Signal(float)  # seconds recorded
    recording_completed = Signal(str)  # file path

    def __init__(self, transcription_engine, audio_recorder):
        super().__init__()
        self.engine = transcription_engine
        self.recorder = audio_recorder
        self.active_workers: Dict[str, Any] = {}
        self.file_queue = []

        logger.info("TranscriptionViewModel initialized")

    @Slot(list)
    def add_files(self, file_paths: list):
        """
        Add files to transcription queue

        Args:
            file_paths: List of file paths to add
        """
        valid_extensions = {'.mp3', '.wav', '.m4a', '.flac', '.mp4', '.ogg', '.wma', '.aac'}
        valid_files = [
            f for f in file_paths
            if Path(f).suffix.lower() in valid_extensions and Path(f).exists()
        ]

        if valid_files:
            logger.info(f"Adding {len(valid_files)} files to queue")
            self.file_queue.extend(valid_files)
            self.files_added.emit(valid_files)
        else:
            logger.warning(f"No valid files found in: {file_paths}")

    @Slot(str)
    @Slot(str, bool)
    def start_transcription(self, file_path: str, enable_diarization: bool = True):
        """
        Start transcription for a specific file

        Args:
            file_path: Path to audio file
            enable_diarization: Whether to enable speaker diarization
        """
        file_id = str(Path(file_path).name)
        logger.info(f"Starting transcription for: {file_id}")

        worker = TranscriptionWorker(
            self.engine,
            file_path,
            enable_diarization=enable_diarization
        )

        # Connect signals
        worker.progress_updated.connect(
            lambda pct, msg: self._on_progress_updated(file_id, pct, msg)
        )
        worker.transcription_complete.connect(
            lambda result: self._on_transcription_complete(file_id, result)
        )
        worker.error_occurred.connect(
            lambda error: self._on_error_occurred(file_id, error)
        )

        self.active_workers[file_id] = worker
        worker.start()

    def _on_progress_updated(self, file_id: str, percentage: int, status: str):
        """Handle progress update from worker"""
        logger.debug(f"{file_id}: {percentage}% - {status}")
        self.progress_changed.emit(file_id, percentage, status)

    def _on_transcription_complete(self, file_id: str, result: dict):
        """Handle transcription completion"""
        logger.info(f"Transcription complete for: {file_id}")
        self.transcription_completed.emit(file_id, result)

        # Cleanup worker
        if file_id in self.active_workers:
            del self.active_workers[file_id]

    def _on_error_occurred(self, file_id: str, error: str):
        """Handle error from worker"""
        logger.error(f"Error transcribing {file_id}: {error}")
        self.error_occurred.emit(file_id, error)

        # Cleanup worker
        if file_id in self.active_workers:
            del self.active_workers[file_id]

    @Slot(int, bool, bool)
    @Slot(int, bool, bool, str)
    def start_recording(
        self,
        duration_seconds: int,
        record_mic: bool = True,
        record_system: bool = True,
        meeting_name: str = None
    ):
        """
        Start audio recording

        Args:
            duration_seconds: Recording duration in seconds
            record_mic: Whether to record microphone
            record_system: Whether to record system audio
            meeting_name: Optional meeting name for filename
        """
        logger.info(
            f"Starting recording: {duration_seconds}s, "
            f"mic={record_mic}, system={record_system}, meeting={meeting_name}"
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate filename with meeting name if provided
        if meeting_name:
            filename = f"Teams_{meeting_name}_{timestamp}.wav"
        else:
            filename = f"recording_{timestamp}.wav"

        output_file = self.engine.config.recordings_dir / filename

        mic_index = self.recorder.get_default_microphone() if record_mic else None
        loopback_index = self.recorder.get_loopback_device() if record_system else None

        worker = RecordingWorker(
            self.engine.config,
            duration_seconds,
            output_file,
            record_mic,
            record_system,
            mic_index,
            loopback_index
        )

        # Connect signals
        worker.progress_updated.connect(self.recording_progress.emit)
        worker.recording_complete.connect(self._on_recording_complete)
        worker.error_occurred.connect(
            lambda error: self.error_occurred.emit("recording", error)
        )

        self.active_workers['recording'] = worker
        worker.start()

    def _on_recording_complete(self, file_path: str):
        """Handle recording completion"""
        logger.info(f"Recording complete: {file_path}")
        self.recording_completed.emit(file_path)

        # Cleanup worker
        if 'recording' in self.active_workers:
            del self.active_workers['recording']

    @Slot(str)
    def cancel_transcription(self, file_id: str):
        """
        Cancel ongoing transcription

        Args:
            file_id: ID of file to cancel
        """
        if file_id in self.active_workers:
            logger.info(f"Cancelling transcription: {file_id}")
            worker = self.active_workers[file_id]
            worker.cancel()
            # Don't wait() - let worker complete async and emit signals
            # Keep in active_workers so completion handler can clean up properly

    def cancel_all(self):
        """Cancel all active workers"""
        logger.info("Cancelling all active workers")
        for file_id, worker in list(self.active_workers.items()):
            worker.cancel()
            worker.wait()
        self.active_workers.clear()

    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up TranscriptionViewModel")
        self.cancel_all()
        self.recorder.cleanup()
