"""
Drag-and-drop zone widget for audio files
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont


class DropZoneWidget(QWidget):
    """Drag-and-drop zone for audio files"""

    files_dropped = Signal(list)  # Emits list of file paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Icon label (using Unicode icons)
        self.icon_label = QLabel("🎵")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        self.icon_label.setFont(icon_font)
        layout.addWidget(self.icon_label)

        # Main text label
        self.label = QLabel("Drop Audio Files Here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        main_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        self.label.setFont(main_font)
        layout.addWidget(self.label)

        # Subtitle label
        self.subtitle = QLabel("or click 'Open Files' to browse\n\nSupported: MP3, WAV, M4A, FLAC, MP4, OGG, WMA, AAC")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        subtitle_font = QFont("Segoe UI", 11)
        self.subtitle.setFont(subtitle_font)
        layout.addWidget(self.subtitle)

        # Apply initial styling
        self.apply_normal_style()

        # Set minimum size
        self.setMinimumHeight(200)

    def apply_normal_style(self):
        """Apply normal state styling"""
        self.setStyleSheet("""
            DropZoneWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 3px dashed #adb5bd;
                border-radius: 12px;
            }
        """)
        self.icon_label.setStyleSheet("color: #6c757d;")
        self.label.setStyleSheet("color: #212529;")
        self.subtitle.setStyleSheet("color: #6c757d;")

    def apply_hover_style(self):
        """Apply hover state styling"""
        self.setStyleSheet("""
            DropZoneWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4edff, stop:1 #b8e0ff);
                border: 3px solid #0078d4;
                border-radius: 12px;
            }
        """)
        self.icon_label.setStyleSheet("color: #0078d4;")
        self.label.setStyleSheet("color: #0078d4;")
        self.subtitle.setStyleSheet("color: #106ebe;")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.apply_hover_style()

    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.apply_normal_style()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop event"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.apply_normal_style()

        # Emit signal with file paths
        if files:
            self.files_dropped.emit(files)
