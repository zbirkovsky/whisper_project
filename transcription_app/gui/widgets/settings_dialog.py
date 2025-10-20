"""
Settings dialog for application configuration
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QFormLayout, QLineEdit, QFileDialog, QTabWidget, QWidget
)
from PySide6.QtCore import Qt, Signal


class SettingsDialog(QDialog):
    """Dialog for application settings"""

    settings_changed = Signal(dict)  # Emits new settings

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.settings = {}
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Setup the UI"""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)

        # Tabs for different setting categories
        tabs = QTabWidget()

        # Transcription tab
        trans_tab = self.create_transcription_tab()
        tabs.addTab(trans_tab, "Transcription")

        # Audio tab
        audio_tab = self.create_audio_tab()
        tabs.addTab(audio_tab, "Audio Recording")

        # Advanced tab
        advanced_tab = self.create_advanced_tab()
        tabs.addTab(advanced_tab, "Advanced")

        layout.addWidget(tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        button_layout.addWidget(apply_btn)

        layout.addLayout(button_layout)

    def create_transcription_tab(self):
        """Create transcription settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Model settings group
        model_group = QGroupBox("Whisper Model")
        model_layout = QFormLayout(model_group)

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "tiny (39MB - Fastest)",
            "base (74MB - Recommended)",
            "small (244MB - Better accuracy)",
            "medium (769MB - High accuracy)",
            "large-v2 (1.5GB - Best accuracy)",
            "large-v3 (1.5GB - Latest)"
        ])
        model_layout.addRow("Model Size:", self.model_combo)

        self.device_combo = QComboBox()
        self.device_combo.addItems(["cuda", "cpu"])
        model_layout.addRow("Device:", self.device_combo)

        self.compute_combo = QComboBox()
        self.compute_combo.addItems(["float16", "int8", "float32"])
        model_layout.addRow("Compute Type:", self.compute_combo)

        self.batch_spin = QSpinBox()
        self.batch_spin.setRange(1, 64)
        self.batch_spin.setValue(16)
        model_layout.addRow("Batch Size:", self.batch_spin)

        layout.addWidget(model_group)

        # Diarization settings group
        diarization_group = QGroupBox("Speaker Diarization")
        diarization_layout = QFormLayout(diarization_group)

        self.diarization_check = QCheckBox("Enable speaker diarization")
        self.diarization_check.setChecked(True)
        diarization_layout.addRow(self.diarization_check)

        self.min_speakers_spin = QSpinBox()
        self.min_speakers_spin.setRange(1, 20)
        self.min_speakers_spin.setValue(1)
        diarization_layout.addRow("Min Speakers:", self.min_speakers_spin)

        self.max_speakers_spin = QSpinBox()
        self.max_speakers_spin.setRange(1, 20)
        self.max_speakers_spin.setValue(10)
        diarization_layout.addRow("Max Speakers:", self.max_speakers_spin)

        self.hf_token_edit = QLineEdit()
        self.hf_token_edit.setPlaceholderText("Enter HuggingFace token...")
        self.hf_token_edit.setEchoMode(QLineEdit.EchoMode.Password)
        diarization_layout.addRow("HF Token:", self.hf_token_edit)

        layout.addWidget(diarization_group)

        # Language settings
        language_group = QGroupBox("Language")
        language_layout = QFormLayout(language_group)

        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "auto (Auto-detect)",
            "en (English)",
            "es (Spanish)",
            "fr (French)",
            "de (German)",
            "it (Italian)",
            "pt (Portuguese)",
            "pl (Polish)",
            "tr (Turkish)",
            "ru (Russian)",
            "nl (Dutch)",
            "cs (Czech)",
            "ar (Arabic)",
            "zh (Chinese)",
            "ja (Japanese)",
            "ko (Korean)"
        ])
        language_layout.addRow("Language:", self.language_combo)

        layout.addWidget(language_group)

        layout.addStretch()
        return widget

    def create_audio_tab(self):
        """Create audio settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Recording settings
        recording_group = QGroupBox("Recording Settings")
        recording_layout = QFormLayout(recording_group)

        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(["16000", "22050", "44100", "48000"])
        self.sample_rate_combo.setCurrentText("48000")
        recording_layout.addRow("Sample Rate:", self.sample_rate_combo)

        self.channels_spin = QSpinBox()
        self.channels_spin.setRange(1, 2)
        self.channels_spin.setValue(2)
        recording_layout.addRow("Channels:", self.channels_spin)

        self.chunk_size_spin = QSpinBox()
        self.chunk_size_spin.setRange(128, 2048)
        self.chunk_size_spin.setValue(512)
        self.chunk_size_spin.setSingleStep(128)
        recording_layout.addRow("Chunk Size:", self.chunk_size_spin)

        layout.addWidget(recording_group)
        layout.addStretch()
        return widget

    def create_advanced_tab(self):
        """Create advanced settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Paths group
        paths_group = QGroupBox("Paths")
        paths_layout = QFormLayout(paths_group)

        # Models directory
        models_layout = QHBoxLayout()
        self.models_dir_edit = QLineEdit()
        self.models_dir_edit.setText(str(self.config.models_dir))
        models_layout.addWidget(self.models_dir_edit)

        browse_models_btn = QPushButton("Browse...")
        browse_models_btn.clicked.connect(self.browse_models_dir)
        models_layout.addWidget(browse_models_btn)

        paths_layout.addRow("Models Directory:", models_layout)

        # Recordings directory
        recordings_layout = QHBoxLayout()
        self.recordings_dir_edit = QLineEdit()
        self.recordings_dir_edit.setText(str(self.config.recordings_dir))
        recordings_layout.addWidget(self.recordings_dir_edit)

        browse_recordings_btn = QPushButton("Browse...")
        browse_recordings_btn.clicked.connect(self.browse_recordings_dir)
        recordings_layout.addWidget(browse_recordings_btn)

        paths_layout.addRow("Recordings Directory:", recordings_layout)

        layout.addWidget(paths_group)

        # Logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)

        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.log_level_combo.setCurrentText("INFO")
        logging_layout.addRow("Log Level:", self.log_level_combo)

        self.log_size_spin = QSpinBox()
        self.log_size_spin.setRange(1, 100)
        self.log_size_spin.setValue(10)
        self.log_size_spin.setSuffix(" MB")
        logging_layout.addRow("Max Log Size:", self.log_size_spin)

        layout.addWidget(logging_group)

        layout.addStretch()
        return widget

    def load_settings(self):
        """Load current settings from config"""
        # Transcription
        model_map = {
            "tiny": 0, "base": 1, "small": 2,
            "medium": 3, "large-v2": 4, "large-v3": 5
        }
        self.model_combo.setCurrentIndex(model_map.get(self.config.whisper_model, 1))

        self.device_combo.setCurrentText(self.config.device)
        self.compute_combo.setCurrentText(self.config.compute_type)
        self.batch_spin.setValue(self.config.batch_size)

        # Diarization
        self.diarization_check.setChecked(self.config.diarization_enabled)
        self.min_speakers_spin.setValue(self.config.min_speakers)
        self.max_speakers_spin.setValue(self.config.max_speakers)
        if self.config.hf_token:
            self.hf_token_edit.setText(self.config.hf_token)

        # Language
        lang_map = {
            "auto": 0, "en": 1, "es": 2, "fr": 3, "de": 4,
            "it": 5, "pt": 6, "pl": 7, "tr": 8, "ru": 9,
            "nl": 10, "cs": 11, "ar": 12, "zh": 13, "ja": 14, "ko": 15
        }
        self.language_combo.setCurrentIndex(lang_map.get(self.config.language, 0))

        # Audio
        self.sample_rate_combo.setCurrentText(str(self.config.sample_rate))
        self.channels_spin.setValue(self.config.channels)
        self.chunk_size_spin.setValue(self.config.chunk_size)

        # Advanced
        self.log_level_combo.setCurrentText(self.config.log_level)
        self.log_size_spin.setValue(self.config.max_log_size_mb)

    def get_settings(self):
        """Get current settings from UI"""
        model_names = ["tiny", "base", "small", "medium", "large-v2", "large-v3"]
        languages = ["auto", "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "ko"]

        return {
            # Transcription
            "whisper_model": model_names[self.model_combo.currentIndex()],
            "device": self.device_combo.currentText(),
            "compute_type": self.compute_combo.currentText(),
            "batch_size": self.batch_spin.value(),

            # Diarization
            "diarization_enabled": self.diarization_check.isChecked(),
            "min_speakers": self.min_speakers_spin.value(),
            "max_speakers": self.max_speakers_spin.value(),
            "hf_token": self.hf_token_edit.text(),

            # Language
            "language": languages[self.language_combo.currentIndex()],

            # Audio
            "sample_rate": int(self.sample_rate_combo.currentText()),
            "channels": self.channels_spin.value(),
            "chunk_size": self.chunk_size_spin.value(),

            # Advanced
            "models_dir": self.models_dir_edit.text(),
            "recordings_dir": self.recordings_dir_edit.text(),
            "log_level": self.log_level_combo.currentText(),
            "max_log_size_mb": self.log_size_spin.value(),
        }

    def browse_models_dir(self):
        """Browse for models directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Models Directory",
            str(self.config.models_dir)
        )
        if directory:
            self.models_dir_edit.setText(directory)

    def browse_recordings_dir(self):
        """Browse for recordings directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Recordings Directory",
            str(self.config.recordings_dir)
        )
        if directory:
            self.recordings_dir_edit.setText(directory)

    def apply_settings(self):
        """Apply settings without closing"""
        self.settings = self.get_settings()
        self.settings_changed.emit(self.settings)

    def save_settings(self):
        """Save settings and close"""
        self.apply_settings()
        self.accept()
