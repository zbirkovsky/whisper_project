"""
Enhanced transcript display widget with syntax highlighting and search
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QCheckBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QTextCursor, QSyntaxHighlighter


class TranscriptHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for transcript text"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_formats()

    def setup_formats(self):
        """Setup text formats for different elements"""
        # Timestamp format [00:15.23]
        self.timestamp_format = QTextCharFormat()
        self.timestamp_format.setForeground(QColor("#0078d4"))
        self.timestamp_format.setFontWeight(QFont.Weight.Bold)

        # Speaker format Speaker 1:
        self.speaker_format = QTextCharFormat()
        self.speaker_format.setForeground(QColor("#107c10"))
        self.speaker_format.setFontWeight(QFont.Weight.Bold)

        # Header format ===
        self.header_format = QTextCharFormat()
        self.header_format.setForeground(QColor("#666"))
        self.header_format.setFontWeight(QFont.Weight.Bold)

        # Language format
        self.language_format = QTextCharFormat()
        self.language_format.setForeground(QColor("#999"))

    def highlightBlock(self, text):
        """Highlight a block of text"""
        # Highlight timestamps [XX:XX.XX]
        import re

        # Timestamps
        for match in re.finditer(r'\[\d+:\d+\.\d+s?\]', text):
            self.setFormat(match.start(), match.end() - match.start(), self.timestamp_format)

        # Speakers (Speaker X: or SPEAKER_XX:)
        for match in re.finditer(r'(Speaker \d+|SPEAKER_\d+):', text):
            self.setFormat(match.start(), match.end() - match.start(), self.speaker_format)

        # Headers (=== ... ===)
        for match in re.finditer(r'=== .+ ===', text):
            self.setFormat(match.start(), match.end() - match.start(), self.header_format)

        # Language line
        if text.startswith('Language:'):
            self.setFormat(0, len(text), self.language_format)


class TranscriptWidget(QWidget):
    """Enhanced transcript display with search and highlighting"""

    copy_segment = Signal(str)  # Emits segment text to copy

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_search_index = -1
        self.search_results = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Header with title and controls
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("Transcript")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Copy button
        self.copy_btn = QPushButton("Copy All")
        self.copy_btn.setToolTip("Copy transcript to clipboard")
        self.copy_btn.clicked.connect(self.copy_all)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 12px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        header_layout.addWidget(self.copy_btn)

        layout.addWidget(header)

        # Search bar
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(8, 0, 8, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in transcript...")
        self.search_input.textChanged.connect(self.search_text)
        self.search_input.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_input)

        self.search_prev_btn = QPushButton("◄")
        self.search_prev_btn.setFixedWidth(30)
        self.search_prev_btn.setToolTip("Previous match")
        self.search_prev_btn.clicked.connect(self.find_previous)
        search_layout.addWidget(self.search_prev_btn)

        self.search_next_btn = QPushButton("►")
        self.search_next_btn.setFixedWidth(30)
        self.search_next_btn.setToolTip("Next match")
        self.search_next_btn.clicked.connect(self.find_next)
        search_layout.addWidget(self.search_next_btn)

        self.search_count_label = QLabel("")
        self.search_count_label.setStyleSheet("color: #666; font-size: 10px;")
        search_layout.addWidget(self.search_count_label)

        # Case sensitive checkbox
        self.case_sensitive_check = QCheckBox("Aa")
        self.case_sensitive_check.setToolTip("Case sensitive")
        self.case_sensitive_check.stateChanged.connect(self.search_text)
        search_layout.addWidget(self.case_sensitive_check)

        layout.addWidget(search_widget)

        # Text display
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setPlaceholderText(
            "Transcription results will appear here...\n\n"
            "• Timestamps are highlighted in blue\n"
            "• Speaker labels are highlighted in green\n"
            "• Use search to find specific words\n"
            "• Copy button to copy full transcript"
        )

        # Apply syntax highlighter
        self.highlighter = TranscriptHighlighter(self.text_edit.document())

        layout.addWidget(self.text_edit)

    def set_text(self, text: str):
        """Set transcript text"""
        self.text_edit.setPlainText(text)
        self.search_text()  # Re-run search if any

    def append_text(self, text: str):
        """Append text to transcript"""
        self.text_edit.append(text)

    def clear(self):
        """Clear transcript"""
        self.text_edit.clear()
        self.search_input.clear()
        self.search_results = []
        self.current_search_index = -1
        self.search_count_label.setText("")

    def copy_all(self):
        """Copy all transcript text to clipboard"""
        from PySide6.QtWidgets import QApplication
        text = self.text_edit.toPlainText()
        QApplication.clipboard().setText(text)
        self.search_count_label.setText("Copied!")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.search_count_label.setText(""))

    def search_text(self):
        """Search for text in transcript"""
        search_term = self.search_input.text()

        # Clear previous highlights
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        fmt = QTextCharFormat()
        cursor.setCharFormat(fmt)
        cursor.clearSelection()

        self.search_results = []
        self.current_search_index = -1

        if not search_term:
            self.search_count_label.setText("")
            return

        # Find all occurrences
        flags = QTextCursor.FindFlag(0)
        if self.case_sensitive_check.isChecked():
            flags |= QTextCursor.FindFlag.FindCaseSensitively

        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)

        # Highlight format
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("#fff59d"))

        count = 0
        while True:
            cursor = self.text_edit.document().find(search_term, cursor, flags)
            if cursor.isNull():
                break

            # Store position
            self.search_results.append(cursor.position())

            # Highlight
            cursor.mergeCharFormat(highlight_format)
            count += 1

        if count > 0:
            self.search_count_label.setText(f"{count} matches")
            self.current_search_index = 0
            self.highlight_current_match()
        else:
            self.search_count_label.setText("No matches")

    def find_next(self):
        """Find next match"""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index + 1) % len(self.search_results)
        self.highlight_current_match()

    def find_previous(self):
        """Find previous match"""
        if not self.search_results:
            return

        self.current_search_index = (self.current_search_index - 1) % len(self.search_results)
        self.highlight_current_match()

    def highlight_current_match(self):
        """Highlight the current search match"""
        if not self.search_results or self.current_search_index < 0:
            return

        position = self.search_results[self.current_search_index]

        # Move cursor to position
        cursor = self.text_edit.textCursor()
        cursor.setPosition(position - len(self.search_input.text()))
        cursor.movePosition(
            QTextCursor.MoveOperation.Right,
            QTextCursor.MoveMode.KeepAnchor,
            len(self.search_input.text())
        )

        # Set as current match (different color)
        current_format = QTextCharFormat()
        current_format.setBackground(QColor("#ff9800"))
        cursor.mergeCharFormat(current_format)

        # Scroll to match
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

        # Update counter
        self.search_count_label.setText(
            f"{self.current_search_index + 1} of {len(self.search_results)}"
        )
