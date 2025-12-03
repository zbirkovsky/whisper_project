"""
Real-time transcription display widget
Shows live translations as they are processed during recording
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QFrame
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont

from transcription_app.gui.styles.stylesheet_manager import StyleSheetManager, Theme
from transcription_app.utils.logger import get_logger

logger = get_logger(__name__)


class RealtimeDisplayWidget(QWidget):
    """Widget for displaying real-time transcription and translation"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Theme support
        self.current_theme = Theme.DARK
        if hasattr(parent, 'style_manager'):
            self.current_theme = parent.style_manager.current_theme

        self.setup_ui()
        self.setVisible(False)  # Hidden by default

    def _get_colors(self):
        """Get theme-aware colors"""
        sm = StyleSheetManager(self.current_theme)
        p = sm._palette
        return {
            'bg': p.background,
            'surface_1': p.surface_1,
            'surface_2': p.surface_2,
            'text_primary': p.text_primary,
            'text_secondary': p.text_secondary,
            'border': p.border,
            'warning_main': p.warning_main,
            'warning_light': p.warning_light,
            'success': p.success_main,
        }

    def setup_ui(self):
        """Setup the real-time display UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        c = self._get_colors()

        # Widget styling
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['surface_1']};
                border: 2px solid {c['warning_main']};
                border-radius: 8px;
            }}
        """)

        # Header
        header = QLabel("⚡ Live Translation (English)")
        header.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 700;
            color: {c['warning_main']};
            padding: 0;
            background: transparent;
            border: none;
        """)
        layout.addWidget(header)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(f"background-color: {c['border']}; max-height: 1px; border: none;")
        layout.addWidget(separator)

        # Real-time text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Listening... translations will appear here as you speak")

        # Monospace font for better readability
        font = QFont("Consolas", 11)
        self.text_display.setFont(font)

        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: {c['surface_2']};
                color: {c['text_primary']};
                border: 1px solid {c['border']};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        layout.addWidget(self.text_display)

        # Status label
        self.status_label = QLabel("Waiting for audio...")
        self.status_label.setStyleSheet(f"""
            font-size: 11px;
            font-style: italic;
            color: {c['text_secondary']};
            background: transparent;
            border: none;
            padding: 0;
        """)
        layout.addWidget(self.status_label)

    @Slot()
    def clear(self):
        """Clear the display"""
        self.text_display.clear()
        self.status_label.setText("Waiting for audio...")

    @Slot(str, str, float)
    def add_translation(self, original_text: str, translated_text: str, timestamp: float):
        """
        Add a new translation to the display

        Args:
            original_text: Original transcribed text
            translated_text: Translated text
            timestamp: Timestamp in seconds
        """
        # Format timestamp as MM:SS
        minutes = int(timestamp // 60)
        seconds = int(timestamp % 60)
        time_str = f"[{minutes:02d}:{seconds:02d}]"

        # Add to display (translation only, as per user preference)
        current_text = self.text_display.toPlainText()
        if current_text:
            new_text = f"{current_text}\n\n{time_str} {translated_text}"
        else:
            new_text = f"{time_str} {translated_text}"

        self.text_display.setPlainText(new_text)

        # Scroll to bottom
        scrollbar = self.text_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        # Update status
        self.status_label.setText(f"Last update: {time_str}")

        logger.debug(f"Added translation at {time_str}: {translated_text[:50]}...")

    @Slot()
    def show_display(self):
        """Show the display widget"""
        self.clear()
        self.setVisible(True)
        logger.info("Real-time display shown")

    @Slot()
    def hide_display(self):
        """Hide the display widget"""
        self.setVisible(False)
        logger.info("Real-time display hidden")
