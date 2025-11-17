"""
Drag-and-drop zone widget for audio files with modern 2025 design
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from transcription_app.gui.styles.stylesheet_manager import SPACING, RADIUS, TYPOGRAPHY


class DropZoneWidget(QWidget):
    """Drag-and-drop zone for audio files"""

    files_dropped = Signal(list)  # Emits list of file paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface with compact professional spacing"""
        layout = QVBoxLayout(self)
        # Use compact spacing tokens (base = 12px)
        spacing = int(SPACING['base'].replace('px', ''))
        layout.setContentsMargins(spacing, spacing, spacing, spacing)
        layout.setSpacing(int(SPACING['sm'].replace('px', '')))  # 4px between elements

        # Icon label (using Unicode icons) - compact size
        self.icon_label = QLabel("🎵")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(32)  # Reduced from 48
        self.icon_label.setFont(icon_font)
        layout.addWidget(self.icon_label)

        # Main text label - using typography tokens
        self.label = QLabel("Drop Audio Files Here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        # Use 2xl size (24px) with semibold weight
        self.label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_2xl']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        layout.addWidget(self.label)

        # Subtitle label - using typography tokens
        self.subtitle = QLabel("or click 'Open Files' to browse\n\nSupported: MP3, WAV, M4A, FLAC, MP4, OGG, WMA, AAC")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)
        layout.addWidget(self.subtitle)

        # Apply initial styling
        self.apply_normal_style()

        # Set minimum size - compact professional design
        self.setMinimumHeight(120)

    def apply_normal_style(self):
        """Apply normal state styling with modern design"""
        # Modern flat design with subtle border and clean background
        self.setStyleSheet(f"""
            DropZoneWidget {{
                background-color: #FAFAFA;  /* neutral_50 light */
                border: 2px dashed #BDBDBD;  /* neutral_400 */
                border-radius: {RADIUS['lg']};
            }}
        """)
        self.icon_label.setStyleSheet("color: #9E9E9E;")  # neutral_500
        self.label.setStyleSheet(f"""
            color: #212121;  /* neutral_900 */
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_2xl']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        self.subtitle.setStyleSheet(f"""
            color: #757575;  /* neutral_600 */
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)

    def apply_hover_style(self):
        """Apply hover state styling with modern design"""
        # Modern hover with primary color accent
        self.setStyleSheet(f"""
            DropZoneWidget {{
                background-color: #E3F2FD;  /* primary_50 - light blue tint */
                border: 2px solid #2196F3;  /* primary_500 */
                border-radius: {RADIUS['lg']};
            }}
        """)
        self.icon_label.setStyleSheet("color: #2196F3;")  # primary_500
        self.label.setStyleSheet(f"""
            color: #1976D2;  /* primary_700 */
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_2xl']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        self.subtitle.setStyleSheet(f"""
            color: #1E88E5;  /* primary_600 */
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)

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
