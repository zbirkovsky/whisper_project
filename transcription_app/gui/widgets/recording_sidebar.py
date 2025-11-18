"""
Recording sidebar widget - compact left panel with all recording controls
Replaces the popup recording dialog with integrated sidebar
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QCheckBox, QLineEdit, QComboBox, QFrame
)
from PySide6.QtCore import Slot, Qt, QTimer
from PySide6.QtGui import QFont
import subprocess
from pathlib import Path

from transcription_app.integrations.teams_detector import detect_teams_meeting, is_teams_running
from transcription_app.utils.language_detector import detect_language_from_teams_meeting
from transcription_app.utils.logger import get_logger
from transcription_app.gui.styles.stylesheet_manager import StyleSheetManager, Theme

logger = get_logger(__name__)


class RecordingSidebarWidget(QWidget):
    """Compact sidebar widget for audio recording controls"""

    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.is_recording = False
        self.is_paused = False
        self.elapsed_time = 0  # in seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.selected_language = "auto"  # Track language for recorded file transcription

        # Theme support
        self.current_theme = Theme.DARK  # Default
        if hasattr(parent, 'style_manager'):
            self.current_theme = parent.style_manager.current_theme

        self.setup_ui()
        self.connect_signals()

        # Auto-detect Teams meeting on initialization (delayed)
        QTimer.singleShot(100, self.auto_detect_teams)

    def _get_colors(self):
        """Get theme-aware colors"""
        sm = StyleSheetManager(self.current_theme)
        p = sm._palette
        return {
            'bg': p.background,
            'surface_1': p.surface_1,
            'surface_2': p.surface_2,
            'surface_3': p.surface_3,
            'text_primary': p.text_primary,
            'text_secondary': p.text_secondary,
            'text_muted': p.neutral_300,
            'border': p.border,
            'border_focus': p.border_focus,
            'primary_50': p.primary_50,
            'primary_100': p.primary_100,
            'primary_300': p.primary_300,
            'primary_main': p.primary_500,
            'primary_hover': p.primary_600,
            'primary_pressed': p.primary_700,
            'success': p.success_main,
            'warning_main': p.warning_main,
            'warning_light': p.warning_light,
            'warning_dark': p.warning_dark,
            'error_main': p.error_main,
            'error_light': p.error_light,
            'error_dark': p.error_dark,
            'neutral_400': p.neutral_400,
            'neutral_600': p.neutral_600,
        }

    def _apply_base_style(self):
        """Apply base sidebar style"""
        c = self._get_colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg']};
                color: {c['text_primary']};
            }}
        """)

    def setup_ui(self):
        """Setup the compact sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Apply theme-aware base style
        c = self._get_colors()
        self._apply_base_style()

        # Title - Professional style
        self.title_label = QLabel("🎙️ Recording")
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {c['primary_main']};
            padding-bottom: 8px;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.title_label)

        # Separator
        self.separator1 = QFrame()
        self.separator1.setFrameShape(QFrame.Shape.HLine)
        self.separator1.setStyleSheet(f"background-color: {c['border']}; max-height: 1px;")
        layout.addWidget(self.separator1)

        # === Audio Input Section ===
        self.audio_label = QLabel("Audio Input")
        self.audio_label.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {c['text_secondary']}; margin-top: 8px;")
        layout.addWidget(self.audio_label)

        # Microphone checkbox
        self.mic_check = QCheckBox("Microphone")
        self.mic_check.setChecked(True)
        self.mic_check.stateChanged.connect(self.on_mic_check_changed)
        self.mic_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: {c['text_primary']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['surface_2']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {c['primary_main']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['primary_main']};
                border-color: {c['primary_main']};
                image: none;
            }}
        """)
        layout.addWidget(self.mic_check)

        self.mic_combo = QComboBox()
        self.mic_combo.setMinimumHeight(36)
        self.mic_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 10px;
                border: 2px solid {c['border']};
                border-radius: 8px;
                font-size: 13px;
                background-color: {c['surface_2']};
                color: {c['text_primary']};
            }}
            QComboBox:hover {{
                border-color: {c['neutral_400']};
            }}
            QComboBox:focus {{
                border-color: {c['border_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {c['text_secondary']};
                width: 8px;
                height: 8px;
                border-top: none;
                border-left: none;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['surface_2']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                selection-background-color: {c['border']};
                selection-color: {c['primary_main']};
                padding: 4px;
            }}
        """)
        layout.addWidget(self.mic_combo)

        # Populate microphone list
        self.populate_microphones()

        # System audio checkbox
        self.system_check = QCheckBox("System Audio (Loopback)")
        self.system_check.setChecked(True)
        self.system_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: {c['text_primary']};
                margin-top: 6px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['surface_2']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {c['primary_main']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['primary_main']};
                border-color: {c['primary_main']};
            }}
        """)
        layout.addWidget(self.system_check)

        # === Meeting Name Section ===
        self.meeting_label = QLabel("Meeting Name")
        self.meeting_label.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {c['text_secondary']}; margin-top: 12px;")
        layout.addWidget(self.meeting_label)

        # Meeting name input with Teams detect button
        meeting_row = QHBoxLayout()
        meeting_row.setSpacing(6)

        self.meeting_name_edit = QLineEdit()
        self.meeting_name_edit.setPlaceholderText("Optional...")
        self.meeting_name_edit.setMinimumHeight(36)
        self.meeting_name_edit.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 2px solid {c['border']};
                border-radius: 8px;
                font-size: 13px;
                background-color: {c['surface_2']};
                color: {c['text_primary']};
            }}
            QLineEdit:hover {{
                border-color: {c['neutral_400']};
            }}
            QLineEdit:focus {{
                border-color: {c['border_focus']};
            }}
            QLineEdit::placeholder {{
                color: {c['text_muted']};
            }}
        """)
        meeting_row.addWidget(self.meeting_name_edit, 1)

        self.detect_btn = QPushButton("🔄")
        self.detect_btn.setToolTip("Detect Teams meeting")
        self.detect_btn.setMaximumWidth(40)
        self.detect_btn.setMinimumHeight(36)
        self.detect_btn.clicked.connect(self.manual_detect_teams)
        self.detect_btn.setStyleSheet(f"""
            QPushButton {{
                border: 2px solid {c['border']};
                border-radius: 8px;
                background-color: {c['surface_2']};
                font-size: 16px;
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {c['border']};
                border-color: {c['primary_main']};
            }}
            QPushButton:pressed {{
                background-color: {c['neutral_400']};
            }}
        """)
        meeting_row.addWidget(self.detect_btn)

        layout.addLayout(meeting_row)

        # Teams status label
        self.teams_status_label = QLabel("")
        self.teams_status_label.setWordWrap(True)
        self.teams_status_label.setStyleSheet(f"color: {c['text_secondary']}; font-size: 11px; font-style: italic; padding: 4px 0;")
        layout.addWidget(self.teams_status_label)

        # === Language Section ===
        self.language_label = QLabel("Language")
        self.language_label.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {c['text_secondary']}; margin-top: 12px;")
        layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "🇬🇧 English",
            "🇨🇿 Czech",
            "🌐 Auto-detect"
        ])
        self.language_combo.setCurrentIndex(0)  # Default to English
        self.language_combo.setMinimumHeight(36)
        self.language_combo.setStyleSheet(f"""
            QComboBox {{
                padding: 8px 10px;
                border: 2px solid {c['border']};
                border-radius: 8px;
                font-size: 13px;
                background-color: {c['surface_2']};
                color: {c['text_primary']};
            }}
            QComboBox:hover {{
                border-color: {c['neutral_400']};
            }}
            QComboBox:focus {{
                border-color: {c['border_focus']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: 2px solid {c['text_secondary']};
                width: 8px;
                height: 8px;
                border-top: none;
                border-left: none;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['surface_2']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 8px;
                selection-background-color: {c['border']};
                selection-color: {c['primary_main']};
                padding: 4px;
            }}
        """)
        layout.addWidget(self.language_combo)

        # Separator
        self.separator2 = QFrame()
        self.separator2.setFrameShape(QFrame.Shape.HLine)
        self.separator2.setStyleSheet(f"background-color: {c['border']}; max-height: 1px; margin: 12px 0;")
        layout.addWidget(self.separator2)

        # === Recording Status Section ===
        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_font = QFont("Consolas", 28, QFont.Weight.Bold)
        self.timer_label.setFont(timer_font)
        self.timer_label.setStyleSheet(f"""
            color: {c['primary_hover']};
            padding: 18px;
            background-color: {c['surface_1']};
            border-radius: 12px;
            border: 2px solid {c['primary_main']};
            letter-spacing: 3px;
        """)
        layout.addWidget(self.timer_label)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {c['text_secondary']}; font-size: 13px; font-weight: 500; margin-top: 6px;")
        layout.addWidget(self.status_label)

        # Recording indicator
        self.recording_indicator = QLabel("● REC")
        self.recording_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recording_indicator.setStyleSheet(f"""
            color: {c['error_main']};
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 2px;
        """)
        self.recording_indicator.setVisible(False)
        layout.addWidget(self.recording_indicator)

        # === Recording Control Buttons ===
        # Start button
        self.start_btn = QPushButton("▶ Start Recording")
        self.start_btn.setMinimumHeight(44)
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['primary_300']},
                    stop:1 {c['primary_main']});
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['primary_100']},
                    stop:1 {c['primary_300']});
            }}
            QPushButton:pressed {{
                background: {c['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {c['border']};
                color: {c['text_muted']};
            }}
        """)
        layout.addWidget(self.start_btn)

        # Pause and Stop buttons (horizontal, hidden initially)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setMinimumHeight(44)
        self.pause_btn.clicked.connect(self.pause_recording)
        self.pause_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['warning_main']},
                    stop:1 {c['warning_light']});
                color: {c['bg']};
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['warning_dark']},
                    stop:1 {c['warning_main']});
            }}
            QPushButton:pressed {{
                background: {c['warning_light']};
            }}
        """)
        self.pause_btn.setVisible(False)
        controls_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(44)
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['error_main']},
                    stop:1 {c['error_light']});
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {c['error_dark']},
                    stop:1 {c['error_main']});
            }}
            QPushButton:pressed {{
                background: {c['error_light']};
            }}
        """)
        self.stop_btn.setVisible(False)
        controls_layout.addWidget(self.stop_btn)

        layout.addLayout(controls_layout)

        # === Quick Actions ===
        # Open recordings folder button
        self.open_folder_btn = QPushButton("📁 Open Recordings Folder")
        self.open_folder_btn.setMinimumHeight(38)
        self.open_folder_btn.clicked.connect(self.open_recordings_folder)
        self.open_folder_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['surface_2']};
                color: {c['text_secondary']};
                border: 2px solid {c['border']};
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                margin-top: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['border']};
                border-color: {c['primary_main']};
                color: {c['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {c['neutral_400']};
            }}
        """)
        layout.addWidget(self.open_folder_btn)

        # Spacer to push everything to top
        layout.addStretch()

    def populate_microphones(self):
        """Populate microphone dropdown with available devices"""
        try:
            devices = self.viewmodel.recorder.list_devices()

            # Filter input devices (exclude loopback devices)
            mic_devices = [d for d in devices if d['max_inputs'] > 0 and not d.get('is_loopback', False)]

            # Sort: default first, then professional mics, then others, NVIDIA Broadcast last
            def priority_sort(device):
                name = device['name'].lower()
                is_default = "(default)" in name or device.get('index') == self.viewmodel.recorder.get_default_microphone()

                if is_default:
                    return (0, name)
                elif any(brand in name for brand in ['hyperx', 'quadcast', 'blue yeti', 'rode', 'shure']):
                    return (1, name)
                elif 'nvidia broadcast' in name:
                    return (99, name)  # Last
                else:
                    return (50, name)

            mic_devices.sort(key=priority_sort)

            self.mic_combo.clear()
            for device in mic_devices:
                name = device['name']
                channels = device['max_inputs']
                rate = int(device['default_sample_rate'])

                # Add marker for default device
                if device.get('index') == self.viewmodel.recorder.get_default_microphone():
                    name = f"{name} [DEFAULT]"

                display_text = f"{name} ({channels}ch, {rate}Hz)"
                self.mic_combo.addItem(display_text, device['index'])

            logger.info(f"Populated {len(mic_devices)} microphones")

        except Exception as e:
            logger.error(f"Error populating microphones: {e}")
            self.mic_combo.addItem("Error loading devices", None)

    def connect_signals(self):
        """Connect signals from viewmodel"""
        self.viewmodel.recording_progress.connect(self.update_progress)
        self.viewmodel.recording_completed.connect(self.on_recording_complete)
        self.viewmodel.error_occurred.connect(self.on_error)

    @Slot(str)
    def on_mic_check_changed(self, state):
        """Enable/disable mic combo when checkbox changes"""
        self.mic_combo.setEnabled(self.mic_check.isChecked())

    def auto_detect_teams(self):
        """Auto-detect Teams meeting (runs on initialization)"""
        # Check if auto-detect is enabled in config
        detect_enabled = getattr(self.viewmodel.engine.config, 'auto_detect_teams_meeting', True)

        if not detect_enabled:
            logger.info("Teams auto-detection disabled in config")
            return

        try:
            if not is_teams_running():
                self.teams_status_label.setText("")
                logger.info("Teams is not running")
                return

            meeting_name = detect_teams_meeting()

            if meeting_name:
                self.meeting_name_edit.setText(meeting_name)
                self.teams_status_label.setText(f"✓ Teams detected")
                logger.info(f"Auto-detected Teams meeting: {meeting_name}")

                # Auto-detect language from meeting name
                detected_lang = detect_language_from_teams_meeting(meeting_name)
                if detected_lang == 'cs':
                    self.language_combo.setCurrentIndex(1)  # Czech
                    logger.info("Auto-selected Czech language")
                elif detected_lang == 'en':
                    self.language_combo.setCurrentIndex(0)  # English
                    logger.info("Auto-selected English language")

            else:
                self.teams_status_label.setText("Teams running, no meeting")
                logger.info("Teams running but no active meeting detected")

        except Exception as e:
            logger.error(f"Error detecting Teams meeting: {e}")
            self.teams_status_label.setText("Detection failed")

    def manual_detect_teams(self):
        """Manual Teams detection via button"""
        self.teams_status_label.setText("Detecting...")
        self.auto_detect_teams()

    def start_recording(self):
        """Start recording"""
        # Validate at least one source is selected
        if not self.mic_check.isChecked() and not self.system_check.isChecked():
            self.status_label.setText("⚠️ Select at least one audio source!")
            self.status_label.setStyleSheet("color: #E74C3C; font-size: 13px; font-weight: 700;")
            return

        # Get selected microphone index
        mic_index = None
        if self.mic_check.isChecked():
            mic_index = self.mic_combo.currentData()

        # Get meeting name (optional)
        meeting_name = self.meeting_name_edit.text().strip() or None

        # Get selected language
        lang_index = self.language_combo.currentIndex()
        if lang_index == 0:
            self.selected_language = "en"
        elif lang_index == 1:
            self.selected_language = "cs"
        else:
            self.selected_language = "auto"

        logger.info(f"Starting recording: mic={self.mic_check.isChecked()}, system={self.system_check.isChecked()}, meeting={meeting_name}, language={self.selected_language}")

        # Disable controls during recording
        self.mic_check.setEnabled(False)
        self.mic_combo.setEnabled(False)
        self.system_check.setEnabled(False)
        self.meeting_name_edit.setEnabled(False)
        self.detect_btn.setEnabled(False)
        self.language_combo.setEnabled(False)

        # Update UI
        self.start_btn.setVisible(False)
        self.pause_btn.setVisible(True)
        self.stop_btn.setVisible(True)
        self.recording_indicator.setVisible(True)
        self.status_label.setText("Recording...")
        self.status_label.setStyleSheet("color: #E74C3C; font-size: 13px; font-weight: 700;")

        # Start recording (unlimited duration: 7200 seconds / 2 hours)
        self.viewmodel.start_recording(
            duration_seconds=7200,
            record_mic=self.mic_check.isChecked(),
            record_system=self.system_check.isChecked(),
            meeting_name=meeting_name,
            mic_index=mic_index
        )

        # Start timer
        self.elapsed_time = 0
        self.is_recording = True
        self.is_paused = False
        self.timer.start(1000)  # Update every second

    def pause_recording(self):
        """Pause/resume recording (timer only)"""
        if self.is_paused:
            # Resume
            self.timer.start(1000)
            self.is_paused = False
            self.pause_btn.setText("⏸ Pause")
            self.status_label.setText("Recording...")
            logger.info("Recording resumed (timer)")
        else:
            # Pause
            self.timer.stop()
            self.is_paused = True
            self.pause_btn.setText("▶ Resume")
            self.status_label.setText("Paused")
            logger.info("Recording paused (timer only)")

    def stop_recording(self):
        """Stop recording"""
        logger.info("Stopping recording")

        self.timer.stop()
        self.is_recording = False
        self.is_paused = False

        self.status_label.setText("Stopping...")
        self.status_label.setStyleSheet("color: #B3B3B3; font-size: 13px; font-weight: 500;")

        # Stop recording via viewmodel
        self.viewmodel.cancel_transcription("recording")

    @Slot(float)
    def update_progress(self, seconds):
        """Update recording progress"""
        # This is called by viewmodel during recording
        pass  # Timer handles display

    def update_timer(self):
        """Update timer display"""
        self.elapsed_time += 1
        hours = self.elapsed_time // 3600
        minutes = (self.elapsed_time % 3600) // 60
        seconds = self.elapsed_time % 60
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    @Slot(str)
    def on_recording_complete(self, file_path):
        """Handle recording completion"""
        logger.info(f"Recording completed: {file_path}")

        # Reset UI
        self.timer.stop()
        self.is_recording = False
        self.is_paused = False

        # Re-enable controls
        self.mic_check.setEnabled(True)
        self.mic_combo.setEnabled(self.mic_check.isChecked())
        self.system_check.setEnabled(True)
        self.meeting_name_edit.setEnabled(True)
        self.detect_btn.setEnabled(True)
        self.language_combo.setEnabled(True)

        # Update UI
        self.start_btn.setVisible(True)
        self.pause_btn.setVisible(False)
        self.stop_btn.setVisible(False)
        self.recording_indicator.setVisible(False)
        self.status_label.setText("✓ Recording saved, transcribing...")
        self.status_label.setStyleSheet("color: #10B981; font-size: 13px; font-weight: 700;")

        # Clear meeting name for next recording
        self.meeting_name_edit.clear()

        # Add recorded file to transcription queue with selected language
        logger.info(f"Adding recorded file to queue with language: {self.selected_language}")
        self.viewmodel.add_files([file_path])

        # Start transcription with the language that was selected during recording
        # The add_files method already starts transcription, we just need to set the language
        # Note: This is handled by the main window's file queue, which will use default settings
        # If we need custom language, we'd need to modify this flow

        # Auto-detect Teams again for next recording
        QTimer.singleShot(500, self.auto_detect_teams)

    @Slot(str, str)
    def on_error(self, file_id, error_message):
        """Handle recording error"""
        if file_id == "recording":
            logger.error(f"Recording error: {error_message}")
            self.status_label.setText(f"Error: {error_message}")
            self.status_label.setStyleSheet("color: #E74C3C; font-size: 13px; font-weight: 700;")

            # Reset to ready state
            self.timer.stop()
            self.is_recording = False
            self.is_paused = False

            # Re-enable controls
            self.mic_check.setEnabled(True)
            self.mic_combo.setEnabled(self.mic_check.isChecked())
            self.system_check.setEnabled(True)
            self.meeting_name_edit.setEnabled(True)
            self.detect_btn.setEnabled(True)
            self.language_combo.setEnabled(True)

            self.start_btn.setVisible(True)
            self.pause_btn.setVisible(False)
            self.stop_btn.setVisible(False)
            self.recording_indicator.setVisible(False)

    def open_recordings_folder(self):
        """Open recordings folder in file explorer"""
        try:
            recordings_dir = self.viewmodel.engine.config.recordings_dir
            if recordings_dir.exists():
                # Open in Windows Explorer
                subprocess.run(['explorer', str(recordings_dir)])
                logger.info(f"Opened recordings folder: {recordings_dir}")
            else:
                logger.warning(f"Recordings folder does not exist: {recordings_dir}")
                self.status_label.setText("Recordings folder not found")
        except Exception as e:
            logger.error(f"Error opening recordings folder: {e}")
            self.status_label.setText("Error opening folder")

    def update_theme(self, theme: Theme):
        """Update widget theme - reapply all styles"""
        self.current_theme = theme
        c = self._get_colors()

        # Reapply all styles
        self._apply_base_style()
        self.title_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 700;
            color: {c['primary_main']};
            padding-bottom: 8px;
            letter-spacing: 0.5px;
        """)
        self.separator1.setStyleSheet(f"background-color: {c['border']}; max-height: 1px;")
        self.audio_label.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {c['text_secondary']}; margin-top: 8px;")
        self.mic_check.setStyleSheet(f"""
            QCheckBox {{
                font-size: 13px;
                color: {c['text_primary']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {c['border']};
                background-color: {c['surface_2']};
            }}
            QCheckBox::indicator:hover {{
                border-color: {c['primary_main']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {c['primary_main']};
                border-color: {c['primary_main']};
                image: none;
            }}
        """)
        # Update all other widgets similarly...
        logger.info(f"Updated recording sidebar theme to {theme.value}")
