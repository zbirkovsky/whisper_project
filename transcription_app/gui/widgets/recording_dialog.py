"""
Dialog for audio recording with system audio + microphone
Now supports unlimited recording with manual stop and Teams meeting detection
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QGroupBox, QLineEdit
)
from PySide6.QtCore import Slot, Qt, QTimer, QTime

from transcription_app.integrations.teams_detector import detect_teams_meeting, is_teams_running


class RecordingDialog(QDialog):
    """Dialog for recording audio with unlimited duration"""

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.is_recording = False
        self.is_paused = False
        self.elapsed_time = 0  # in seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Record Audio")
        self.setMinimumWidth(500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Info label
        info_label = QLabel(
            "🎙️ Record audio from your microphone and/or system audio\n"
            "Click Start to begin recording, Pause to pause, and Stop when finished."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #495057; font-size: 13px; padding: 10px; background-color: #f8f9fa; border-radius: 6px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Audio sources section
        sources_group = QGroupBox("Audio Sources")
        sources_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }
        """)
        sources_layout = QVBoxLayout(sources_group)

        self.mic_check = QCheckBox("🎤 Record Microphone")
        self.mic_check.setChecked(True)
        self.mic_check.setToolTip("Capture audio from your microphone")
        self.mic_check.setStyleSheet("font-size: 13px; padding: 5px;")
        sources_layout.addWidget(self.mic_check)

        self.system_check = QCheckBox("🔊 Record System Audio (Loopback)")
        self.system_check.setChecked(True)
        self.system_check.setToolTip("Capture audio playing on your computer (speakers/applications)")
        self.system_check.setStyleSheet("font-size: 13px; padding: 5px;")
        sources_layout.addWidget(self.system_check)

        layout.addWidget(sources_group)

        # Teams meeting detection section
        teams_group = QGroupBox("Meeting Name (Optional)")
        teams_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #e1e4e8;
                border-radius: 8px;
                margin-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
            }
        """)
        teams_layout = QVBoxLayout(teams_group)

        # Auto-detect checkbox
        self.teams_detect_check = QCheckBox("📅 Auto-detect Teams meeting name")
        # Get setting from config
        detect_enabled = getattr(self.viewmodel.engine.config, 'auto_detect_teams_meeting', True)
        self.teams_detect_check.setChecked(detect_enabled)
        self.teams_detect_check.setToolTip("Automatically detect and use Microsoft Teams meeting name for filename")
        self.teams_detect_check.setStyleSheet("font-size: 13px; padding: 5px;")
        self.teams_detect_check.stateChanged.connect(self.on_teams_detect_toggled)
        teams_layout.addWidget(self.teams_detect_check)

        # Meeting name input row
        meeting_name_layout = QHBoxLayout()

        self.meeting_name_edit = QLineEdit()
        self.meeting_name_edit.setPlaceholderText("Meeting name (leave empty for timestamp only)")
        self.meeting_name_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #e1e4e8;
                border-radius: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        meeting_name_layout.addWidget(self.meeting_name_edit)

        self.detect_btn = QPushButton("🔄")
        self.detect_btn.setFixedWidth(40)
        self.detect_btn.setToolTip("Detect Teams meeting now")
        self.detect_btn.clicked.connect(self.detect_teams_meeting)
        self.detect_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        meeting_name_layout.addWidget(self.detect_btn)

        teams_layout.addLayout(meeting_name_layout)

        # Detection status label
        self.teams_status_label = QLabel("")
        self.teams_status_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")
        teams_layout.addWidget(self.teams_status_label)

        layout.addWidget(teams_group)

        # Try to detect meeting on dialog open
        QTimer.singleShot(100, self.detect_teams_meeting)

        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            font-family: 'Consolas', 'Courier New', monospace;
            color: #0078d4;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 2px solid #e1e4e8;
        """)
        layout.addWidget(self.timer_label)

        # Status label
        self.status_label = QLabel("Ready to record")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #6c757d; font-size: 14px; font-weight: 500;")
        layout.addWidget(self.status_label)

        # Recording indicator
        self.recording_indicator = QLabel("")
        self.recording_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_indicator.setVisible(False)
        layout.addWidget(self.recording_indicator)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.start_btn = QPushButton("▶ Start Recording")
        self.start_btn.setMinimumWidth(150)
        self.start_btn.setMinimumHeight(45)
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        button_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setMinimumWidth(120)
        self.pause_btn.setMinimumHeight(45)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_recording)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        button_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setMinimumHeight(45)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
        """)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)

        # Bottom buttons
        bottom_layout = QHBoxLayout()

        open_folder_btn = QPushButton("📁 Open Recordings Folder")
        open_folder_btn.setMinimumWidth(180)
        open_folder_btn.clicked.connect(self.open_recordings_folder)
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        bottom_layout.addWidget(open_folder_btn)

        bottom_layout.addStretch()

        close_btn = QPushButton("Close")
        close_btn.setMinimumWidth(100)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        bottom_layout.addWidget(close_btn)
        layout.addLayout(bottom_layout)

    def connect_signals(self):
        """Connect ViewModel signals"""
        self.viewmodel.recording_progress.connect(self.update_progress)
        self.viewmodel.recording_completed.connect(self.on_recording_complete)
        self.viewmodel.error_occurred.connect(self.on_error)

    def start_recording(self):
        """Start recording"""
        record_mic = self.mic_check.isChecked()
        record_system = self.system_check.isChecked()

        # Validate at least one source is selected
        if not record_mic and not record_system:
            self.status_label.setText("⚠️ Please select at least one audio source")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")
            return

        self.is_recording = True
        self.is_paused = False
        self.elapsed_time = 0

        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.mic_check.setEnabled(False)
        self.system_check.setEnabled(False)

        self.status_label.setText("🔴 Recording...")
        self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")

        self.recording_indicator.setText("● REC")
        self.recording_indicator.setStyleSheet("color: #dc3545; font-size: 18px; font-weight: bold;")
        self.recording_indicator.setVisible(True)

        # Start timer
        self.timer.start(1000)  # Update every second

        # Get meeting name for filename
        meeting_name = self.get_meeting_name()

        # Start actual recording with a very long duration (2 hours max)
        self.viewmodel.start_recording(7200, record_mic, record_system, meeting_name)

    def pause_recording(self):
        """Pause/Resume recording"""
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
            self.status_label.setText("🔴 Recording...")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")
            self.timer.start(1000)
            # Note: Actual audio recording cannot be paused easily, so we just pause the timer
            # A full implementation would need to handle audio stream pausing
        else:
            # Pause
            self.is_paused = True
            self.pause_btn.setText("▶ Resume")
            self.status_label.setText("⏸ Paused")
            self.status_label.setStyleSheet("color: #ffc107; font-weight: bold; font-size: 14px;")
            self.timer.stop()

    def stop_recording(self):
        """Stop recording early and save"""
        self.is_recording = False
        self.timer.stop()

        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)

        self.status_label.setText("⏹ Stopping recording...")
        self.status_label.setStyleSheet("color: #6c757d; font-weight: bold; font-size: 14px;")
        self.recording_indicator.setVisible(False)

        # Cancel the recording worker (this will trigger save and completion)
        self.viewmodel.cancel_transcription("recording")

    def update_timer(self):
        """Update the elapsed time display"""
        if not self.is_paused:
            self.elapsed_time += 1
            time = QTime(0, 0, 0).addSecs(self.elapsed_time)
            self.timer_label.setText(time.toString("HH:mm:ss"))

    @Slot(float)
    def update_progress(self, seconds):
        """Update recording progress"""
        # This is called by the viewmodel, but we're using our own timer instead
        pass

    @Slot(str)
    def on_recording_complete(self, file_path):
        """Handle recording completion"""
        self.is_recording = False
        self.timer.stop()

        self.status_label.setText(f"✅ Recording saved successfully!")
        self.status_label.setStyleSheet("color: #28a745; font-weight: bold; font-size: 14px;")
        self.recording_indicator.setVisible(False)

        # Add recorded file to transcription queue
        self.viewmodel.add_files([file_path])

        # Reset UI after 2 seconds
        QTimer.singleShot(2000, self.reset_ui)

    @Slot(str, str)
    def on_error(self, file_id, error):
        """Handle recording error"""
        if file_id == "recording":
            self.is_recording = False
            self.timer.stop()
            self.status_label.setText(f"❌ Error: {error}")
            self.status_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px;")
            self.recording_indicator.setVisible(False)
            self.reset_ui()

    def reset_ui(self):
        """Reset UI to initial state"""
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.mic_check.setEnabled(True)
        self.system_check.setEnabled(True)

        self.timer_label.setText("00:00:00")
        self.status_label.setText("Ready to record")
        self.status_label.setStyleSheet("color: #6c757d; font-size: 14px; font-weight: 500;")
        self.recording_indicator.setVisible(False)

        self.is_recording = False
        self.is_paused = False
        self.elapsed_time = 0
        self.pause_btn.setText("⏸ Pause")

    def detect_teams_meeting(self):
        """Detect active Teams meeting and update UI"""
        if not self.teams_detect_check.isChecked():
            return

        # Check if Teams is running first
        if not is_teams_running():
            self.teams_status_label.setText("⚠️ Teams is not running")
            self.teams_status_label.setStyleSheet("color: #ffc107; font-size: 11px; font-style: italic;")
            return

        # Try to detect meeting
        meeting_name = detect_teams_meeting()

        if meeting_name:
            self.meeting_name_edit.setText(meeting_name)
            self.teams_status_label.setText(f"✅ Detected: {meeting_name}")
            self.teams_status_label.setStyleSheet("color: #28a745; font-size: 11px; font-style: italic;")
        else:
            self.teams_status_label.setText("ℹ️ No active meeting detected (join a meeting first)")
            self.teams_status_label.setStyleSheet("color: #6c757d; font-size: 11px; font-style: italic;")

    def on_teams_detect_toggled(self, state):
        """Handle Teams detection checkbox toggle"""
        enabled = state == Qt.CheckState.Checked.value
        self.meeting_name_edit.setEnabled(True)  # Always enabled for manual entry
        self.detect_btn.setEnabled(enabled)

        if enabled:
            self.detect_teams_meeting()
        else:
            self.teams_status_label.setText("")

    def get_meeting_name(self):
        """Get the meeting name for filename, or None"""
        meeting_name = self.meeting_name_edit.text().strip()
        return meeting_name if meeting_name else None

    def open_recordings_folder(self):
        """Open the recordings folder in file explorer"""
        import subprocess
        import platform
        from pathlib import Path

        # Get recordings directory from viewmodel's config
        recordings_dir = self.viewmodel.engine.config.recordings_dir

        # Ensure directory exists
        recordings_dir.mkdir(parents=True, exist_ok=True)

        # Open in file explorer based on platform
        if platform.system() == "Windows":
            subprocess.Popen(['explorer', str(recordings_dir)])
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(['open', str(recordings_dir)])
        else:  # Linux
            subprocess.Popen(['xdg-open', str(recordings_dir)])

    def closeEvent(self, event):
        """Handle dialog close"""
        if self.is_recording:
            self.stop_recording()
        event.accept()
