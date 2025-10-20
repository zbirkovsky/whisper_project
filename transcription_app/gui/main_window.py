"""
Main application window with Fluent Design-inspired UI
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QStatusBar, QSplitter,
    QListWidget, QFileDialog, QListWidgetItem, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QAction, QKeySequence

from transcription_app.gui.widgets.drop_zone_widget import DropZoneWidget
from transcription_app.gui.widgets.recording_dialog import RecordingDialog
from transcription_app.gui.widgets.file_queue_widget import FileQueueWidget
from transcription_app.gui.widgets.settings_dialog import SettingsDialog
from transcription_app.gui.widgets.transcript_widget import TranscriptWidget
from transcription_app.gui.styles import StyleSheetManager, Theme, get_icon_manager, AnimationHelper
from transcription_app.core.transcription_engine import format_transcript_text, format_transcript_srt
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, viewmodel, config):
        super().__init__()
        self.viewmodel = viewmodel
        self.config = config
        self.file_items = {}  # Maps file_id to QListWidgetItem
        self.file_progress = {}  # Maps file_id to QProgressBar
        self.current_result = None  # Store current transcription result
        self.style_manager = StyleSheetManager(Theme.LIGHT)
        self.icon_manager = get_icon_manager()
        self.setup_ui()
        self.connect_signals()
        logger.info("MainWindow initialized")

    def setup_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("CloudCall Transcription")
        self.setMinimumSize(1000, 700)

        # Menu bar
        self.create_menu_bar()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Command bar
        command_bar = self.create_command_bar()
        main_layout.addWidget(command_bar)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Drop zone
        self.drop_zone = DropZoneWidget()
        splitter.addWidget(self.drop_zone)

        # Enhanced file queue
        self.file_queue = FileQueueWidget()
        self.file_queue.cancel_file.connect(self.cancel_file)
        self.file_queue.remove_file.connect(self.remove_file)
        self.file_queue.setMinimumHeight(320)  # Show at least 3 items
        splitter.addWidget(self.file_queue)

        # Transcript display - enhanced widget with syntax highlighting and search
        self.transcript_text = TranscriptWidget()
        splitter.addWidget(self.transcript_text)

        splitter.setSizes([150, 320, 350])
        main_layout.addWidget(splitter)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Drop audio files or click 'Open Files'")

        # Apply stylesheet from StyleSheet Manager
        self.setStyleSheet(self.style_manager.get_stylesheet())

    def create_menu_bar(self):
        """Create menu bar with File/Edit/View/Help menus"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Files...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.setStatusTip("Open audio files for transcription")
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

        record_action = QAction("&Record Audio...", self)
        record_action.setShortcut(QKeySequence("Ctrl+R"))
        record_action.setStatusTip("Record audio from microphone and/or system")
        record_action.triggered.connect(self.start_recording)
        file_menu.addAction(record_action)

        file_menu.addSeparator()

        save_txt_action = QAction("Save as &TXT...", self)
        save_txt_action.setShortcut(QKeySequence("Ctrl+T"))
        save_txt_action.setStatusTip("Save transcript as plain text")
        save_txt_action.triggered.connect(lambda: self.save_transcript('txt'))
        file_menu.addAction(save_txt_action)

        save_srt_action = QAction("Save as &SRT...", self)
        save_srt_action.setShortcut(QKeySequence("Ctrl+S"))
        save_srt_action.setStatusTip("Save transcript as SRT subtitle file")
        save_srt_action.triggered.connect(lambda: self.save_transcript('srt'))
        file_menu.addAction(save_srt_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        copy_action = QAction("&Copy Transcript", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setStatusTip("Copy transcript to clipboard")
        copy_action.triggered.connect(self.copy_transcript)
        edit_menu.addAction(copy_action)

        clear_action = QAction("C&lear Transcript", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.setStatusTip("Clear transcript display")
        clear_action.triggered.connect(self.clear_transcript)
        edit_menu.addAction(clear_action)

        edit_menu.addSeparator()

        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence.StandardKey.Preferences)
        settings_action.setStatusTip("Open settings dialog")
        settings_action.triggered.connect(self.open_settings)
        edit_menu.addAction(settings_action)

        # View Menu
        view_menu = menubar.addMenu("&View")

        self.queue_visible_action = QAction("Show File &Queue", self)
        self.queue_visible_action.setCheckable(True)
        self.queue_visible_action.setChecked(True)
        self.queue_visible_action.setStatusTip("Toggle file queue visibility")
        self.queue_visible_action.triggered.connect(self.toggle_queue_visibility)
        view_menu.addAction(self.queue_visible_action)

        self.dropzone_visible_action = QAction("Show &Drop Zone", self)
        self.dropzone_visible_action.setCheckable(True)
        self.dropzone_visible_action.setChecked(True)
        self.dropzone_visible_action.setStatusTip("Toggle drop zone visibility")
        self.dropzone_visible_action.triggered.connect(self.toggle_dropzone_visibility)
        view_menu.addAction(self.dropzone_visible_action)

        view_menu.addSeparator()

        self.dark_mode_action = QAction("&Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(False)
        self.dark_mode_action.setShortcut(QKeySequence("Ctrl+D"))
        self.dark_mode_action.setStatusTip("Toggle dark mode theme")
        self.dark_mode_action.triggered.connect(self.toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        docs_action = QAction("&Documentation", self)
        docs_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        docs_action.setStatusTip("Open documentation")
        docs_action.triggered.connect(self.open_documentation)
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_command_bar(self):
        """Create command bar with primary actions"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        btn_open = QPushButton(self.icon_manager.get_button_icon('folder-open'), " Open Files")
        btn_open.setToolTip("Select audio files to transcribe")
        btn_open.clicked.connect(self.open_files)
        layout.addWidget(btn_open)

        btn_record = QPushButton(self.icon_manager.get_button_icon('record'), " Record Audio")
        btn_record.setToolTip("Record audio from microphone and/or system")
        btn_record.clicked.connect(self.start_recording)
        layout.addWidget(btn_record)

        btn_save_txt = QPushButton(self.icon_manager.get_button_icon('text'), " Save as TXT")
        btn_save_txt.setToolTip("Save transcript as plain text")
        btn_save_txt.clicked.connect(lambda: self.save_transcript('txt'))
        layout.addWidget(btn_save_txt)

        btn_save_srt = QPushButton(self.icon_manager.get_button_icon('subtitle'), " Save as SRT")
        btn_save_srt.setToolTip("Save transcript as SRT subtitle file")
        btn_save_srt.clicked.connect(lambda: self.save_transcript('srt'))
        layout.addWidget(btn_save_srt)

        layout.addStretch()

        btn_clear = QPushButton(self.icon_manager.get_button_icon('clear'), " Clear")
        btn_clear.setToolTip("Clear transcript display")
        btn_clear.clicked.connect(self.clear_transcript)
        layout.addWidget(btn_clear)

        btn_settings = QPushButton(self.icon_manager.get_button_icon('settings'), " Settings")
        btn_settings.setToolTip("Open settings dialog")
        btn_settings.clicked.connect(self.open_settings)
        layout.addWidget(btn_settings)

        return widget

    def connect_signals(self):
        """Connect ViewModel signals to UI updates"""
        self.viewmodel.files_added.connect(self.on_files_added)
        self.viewmodel.progress_changed.connect(self.update_progress)
        self.viewmodel.transcription_completed.connect(self.display_transcript)
        self.viewmodel.error_occurred.connect(self.show_error)
        self.drop_zone.files_dropped.connect(self.viewmodel.add_files)

    def open_files(self):
        """Open file dialog to select audio files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            str(Path.home()),
            "Audio Files (*.mp3 *.wav *.m4a *.flac *.mp4 *.ogg *.wma *.aac);;All Files (*.*)"
        )
        if files:
            logger.info(f"User selected {len(files)} files")
            self.viewmodel.add_files(files)

    @Slot(list)
    def on_files_added(self, files):
        """Handle files added to queue"""
        for file_path in files:
            file_id = Path(file_path).name

            # Add to enhanced queue widget
            self.file_queue.add_file(file_id, file_path)

            # Auto-start transcription
            logger.info(f"Starting transcription for: {file_id}")
            self.viewmodel.start_transcription(file_path)

        self.status_bar.showMessage(f"Added {len(files)} file(s) to queue")

    @Slot(str, int, str)
    def update_progress(self, file_id, percentage, status):
        """Update progress for file"""
        self.file_queue.update_progress(file_id, percentage, status)
        self.status_bar.showMessage(f"{file_id}: {status} ({percentage}%)")

    @Slot(str, dict)
    def display_transcript(self, file_id, result):
        """Display transcription result"""
        logger.info(f"Displaying transcript for: {file_id}")

        # Store current result
        self.current_result = result

        # Update queue widget
        self.file_queue.mark_complete(file_id)

        # Format and display transcript
        transcript_text = format_transcript_text(result, include_timestamps=True)
        self.transcript_text.set_text(transcript_text)

        # Auto-save transcript to configured transcripts directory
        try:
            file_name = result.get('file_name', file_id)
            base_name = Path(file_name).stem

            # Save as TXT
            txt_path = self.config.transcripts_dir / f"{base_name}_transcript.txt"
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(transcript_text)
            logger.info(f"Auto-saved transcript to: {txt_path}")

            # Save as SRT
            srt_path = self.config.transcripts_dir / f"{base_name}.srt"
            srt_content = format_transcript_srt(result)
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
            logger.info(f"Auto-saved SRT to: {srt_path}")
        except Exception as e:
            logger.error(f"Failed to auto-save transcript: {e}")

        # Update status
        num_segments = len(result.get('segments', []))
        language = result.get('language', 'unknown')
        self.status_bar.showMessage(
            f"Completed: {file_id} ({num_segments} segments, language: {language}) - Saved to {self.config.transcripts_dir}"
        )

    @Slot(str, str)
    def show_error(self, file_id, error):
        """Display error message"""
        logger.error(f"Error for {file_id}: {error}")

        # Update queue widget
        self.file_queue.mark_error(file_id, error)

        # Display in transcript area
        self.transcript_text.append_text(f"\n=== ERROR ({file_id}) ===\n{error}\n")

        self.status_bar.showMessage(f"Error: {error}")

    def cancel_file(self, file_id: str):
        """Cancel transcription for a file"""
        logger.info(f"Cancelling transcription for: {file_id}")
        self.viewmodel.cancel_transcription(file_id)
        self.status_bar.showMessage(f"Cancelled: {file_id}")

    def remove_file(self, file_id: str):
        """Remove file from queue"""
        logger.info(f"Removed from queue: {file_id}")
        self.status_bar.showMessage(f"Removed: {file_id}")

    def start_recording(self):
        """Show recording dialog"""
        logger.info("Opening recording dialog")
        dialog = RecordingDialog(self.viewmodel, self)
        dialog.exec()

    def save_transcript(self, format_type='txt'):
        """Save transcript to file"""
        if not self.current_result:
            self.status_bar.showMessage("No transcript available to save")
            return

        file_name = self.current_result.get('file_name', 'transcript')
        base_name = Path(file_name).stem

        if format_type == 'txt':
            default_path = Path.home() / f"{base_name}_transcript.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Transcript",
                str(default_path),
                "Text Files (*.txt)"
            )
            if file_path:
                content = format_transcript_text(self.current_result, include_timestamps=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Saved transcript to: {file_path}")
                self.status_bar.showMessage(f"Saved to {file_path}")

        elif format_type == 'srt':
            default_path = Path.home() / f"{base_name}.srt"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save SRT Subtitles",
                str(default_path),
                "SRT Files (*.srt)"
            )
            if file_path:
                content = format_transcript_srt(self.current_result)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Saved SRT to: {file_path}")
                self.status_bar.showMessage(f"Saved to {file_path}")

    def clear_transcript(self):
        """Clear transcript display"""
        self.transcript_text.clear()
        self.current_result = None
        logger.info("Cleared transcript display")

    def open_settings(self):
        """Open settings dialog"""
        logger.info("Opening settings dialog")
        dialog = SettingsDialog(self.config, self)
        dialog.settings_changed.connect(self.apply_new_settings)
        dialog.exec()

    def apply_new_settings(self, settings: dict):
        """Apply new settings"""
        logger.info(f"Applying new settings: {settings}")
        # Update config object
        for key, value in settings.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        self.status_bar.showMessage("Settings applied successfully! Restart for some changes to take effect.")

    def copy_transcript(self):
        """Copy transcript to clipboard"""
        from PySide6.QtWidgets import QApplication
        text = self.transcript_text.text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("Transcript copied to clipboard")
        else:
            self.status_bar.showMessage("No transcript to copy")

    def toggle_queue_visibility(self):
        """Toggle file queue visibility"""
        self.file_queue.setVisible(self.queue_visible_action.isChecked())
        logger.info(f"File queue visibility: {self.queue_visible_action.isChecked()}")

    def toggle_dropzone_visibility(self):
        """Toggle drop zone visibility"""
        self.drop_zone.setVisible(self.dropzone_visible_action.isChecked())
        logger.info(f"Drop zone visibility: {self.dropzone_visible_action.isChecked()}")

    def toggle_dark_mode(self):
        """Toggle dark mode theme"""
        if self.dark_mode_action.isChecked():
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_dark_mode(self):
        """Apply dark mode theme"""
        self.style_manager.set_theme(Theme.DARK)
        self.setStyleSheet(self.style_manager.get_stylesheet())
        self.status_bar.showMessage("Dark mode enabled")
        logger.info("Dark mode enabled")

    def apply_light_mode(self):
        """Apply light mode theme"""
        self.style_manager.set_theme(Theme.LIGHT)
        self.setStyleSheet(self.style_manager.get_stylesheet())
        self.status_bar.showMessage("Light mode enabled")
        logger.info("Light mode enabled")

    def open_documentation(self):
        """Open documentation in default browser"""
        import webbrowser
        from pathlib import Path

        # Try to open README.md if it exists
        readme_path = Path(__file__).parent.parent.parent / "README.md"
        if readme_path.exists():
            webbrowser.open(readme_path.as_uri())
            self.status_bar.showMessage("Opening documentation...")
        else:
            QMessageBox.information(
                self,
                "Documentation",
                "Documentation is located in README.md in the project folder."
            )

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>CloudCall Transcription</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Description:</b> Professional audio transcription application with speaker diarization.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>WhisperX for accurate speech-to-text transcription</li>
            <li>Pyannote.audio for speaker diarization</li>
            <li>Support for multiple audio/video formats</li>
            <li>Real-time audio recording with system audio capture</li>
            <li>Export to TXT and SRT subtitle formats</li>
            <li>GPU acceleration support</li>
        </ul>
        <br>
        <p><b>Technologies:</b> PySide6, WhisperX, PyTorch, Pyannote.audio, PyAudioWPatch</p>
        <p><b>License:</b> MIT</p>
        """

        QMessageBox.about(self, "About CloudCall Transcription", about_text)

    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        logger.info("Main window shown")

    def closeEvent(self, event):
        """Handle window close event"""
        logger.info("Application closing")
        self.viewmodel.cleanup()
        event.accept()
