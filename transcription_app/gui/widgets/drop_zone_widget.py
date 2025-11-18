"""
Drag-and-drop zone widget for audio files with modern 2025 design
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from transcription_app.gui.styles.stylesheet_manager import SPACING, RADIUS, TYPOGRAPHY, StyleSheetManager, Theme


class DropZoneWidget(QWidget):
    """Drag-and-drop zone for audio files"""

    files_dropped = Signal(list)  # Emits list of file paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        # Get theme from parent's style manager if available
        self.current_theme = Theme.DARK  # Default
        if hasattr(parent, 'style_manager'):
            self.current_theme = parent.style_manager.current_theme
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface with compact professional spacing"""
        layout = QVBoxLayout(self)
        # Use compact spacing tokens (base = 12px)
        spacing = int(SPACING['base'].replace('px', ''))
        layout.setContentsMargins(spacing, spacing, spacing, spacing)
        layout.setSpacing(int(SPACING['xs'].replace('px', '')))  # 2px between elements - very compact

        # Icon label - smaller, cleaner
        self.icon_label = QLabel("📁")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(20)  # Much smaller for compact design
        self.icon_label.setFont(icon_font)
        layout.addWidget(self.icon_label)

        # Main text label - compact and readable
        self.label = QLabel("Drop Audio Files Here")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 16px;
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        layout.addWidget(self.label)

        # Subtitle label - very compact
        self.subtitle = QLabel("MP3, WAV, M4A, FLAC, MP4...")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 11px;
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)
        layout.addWidget(self.subtitle)

        # Apply initial styling
        self.apply_normal_style()

        # Set minimum size - very compact
        self.setMinimumHeight(80)

    def get_theme_colors(self):
        """Get colors for current theme"""
        sm = StyleSheetManager(self.current_theme)
        palette = sm._palette
        return {
            'bg_normal': palette.surface_2,
            'bg_hover': palette.surface_3,
            'border_normal': palette.neutral_500,
            'border_hover': palette.primary_500,
            'icon_normal': palette.neutral_300,
            'icon_hover': palette.primary_500,
            'text_normal': palette.text_primary,
            'text_hover': palette.primary_50,
            'subtitle_normal': palette.text_secondary,
            'subtitle_hover': palette.primary_500,
        }

    def apply_normal_style(self):
        """Apply normal state styling - theme aware"""
        colors = self.get_theme_colors()
        self.setStyleSheet(f"""
            DropZoneWidget {{
                background-color: {colors['bg_normal']};
                border: 2px dashed {colors['border_normal']};
                border-radius: {RADIUS['md']};
            }}
        """)
        self.icon_label.setStyleSheet(f"color: {colors['icon_normal']};")
        self.label.setStyleSheet(f"""
            color: {colors['text_normal']};
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 16px;
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        self.subtitle.setStyleSheet(f"""
            color: {colors['subtitle_normal']};
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 11px;
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)

    def apply_hover_style(self):
        """Apply hover state styling - theme aware"""
        colors = self.get_theme_colors()
        self.setStyleSheet(f"""
            DropZoneWidget {{
                background-color: {colors['bg_hover']};
                border: 2px solid {colors['border_hover']};
                border-radius: {RADIUS['md']};
            }}
        """)
        self.icon_label.setStyleSheet(f"color: {colors['icon_hover']};")
        self.label.setStyleSheet(f"""
            color: {colors['text_hover']};
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 16px;
            font-weight: {TYPOGRAPHY['weight_semibold']};
        """)
        self.subtitle.setStyleSheet(f"""
            color: {colors['subtitle_hover']};
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: 11px;
            font-weight: {TYPOGRAPHY['weight_regular']};
        """)

    def update_theme(self, theme: Theme):
        """Update widget theme"""
        self.current_theme = theme
        self.apply_normal_style()

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
