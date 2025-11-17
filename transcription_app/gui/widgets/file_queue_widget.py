"""
Enhanced file queue widget with modern card styling and controls
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from transcription_app.gui.styles import AnimationHelper
from transcription_app.gui.styles.stylesheet_manager import SPACING, RADIUS, TYPOGRAPHY


class FileQueueItem(QFrame):
    """Individual file item with progress bar and controls"""

    cancel_clicked = Signal(str)  # file_id
    remove_clicked = Signal(str)  # file_id

    def __init__(self, file_id: str, file_path: str, parent=None):
        super().__init__(parent)
        self.file_id = file_id
        self.file_path = file_path
        self._progress_animation = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI for this file item with modern card styling"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        # Modern card with subtle shadow and hover effect
        self.setStyleSheet(f"""
            FileQueueItem {{
                background-color: #FFFFFF;  /* surface_1 */
                border: 1px solid #E0E0E0;  /* neutral_300 */
                border-radius: {RADIUS['md']};
                margin: {SPACING['xs']};
                padding: {SPACING['md']};
            }}
            FileQueueItem:hover {{
                border-color: #2196F3;  /* primary_500 */
                background-color: #FAFAFA;  /* surface_1 hover */
            }}
        """)

        layout = QVBoxLayout(self)
        # Use design tokens for spacing
        layout.setSpacing(int(SPACING['sm'].replace('px', '')))
        layout.setContentsMargins(
            int(SPACING['md'].replace('px', '')),
            int(SPACING['md'].replace('px', '')),
            int(SPACING['md'].replace('px', '')),
            int(SPACING['md'].replace('px', ''))
        )

        # Top row: filename and controls
        top_row = QHBoxLayout()

        # File icon and name - modern typography
        self.name_label = QLabel(self.file_id)
        self.name_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_base']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: #212121;  /* neutral_900 */
        """)
        top_row.addWidget(self.name_label)

        top_row.addStretch()

        # Status label - modern typography
        self.status_label = QLabel("Waiting...")
        self.status_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: #757575;  /* neutral_600 */
        """)
        top_row.addWidget(self.status_label)

        # Cancel button - modern circular button
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(28, 28)
        self.cancel_btn.setToolTip("Cancel transcription")
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 14px;  /* Circle */
                color: #757575;  /* neutral_600 */
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #FFEBEE;  /* error_light */
                color: #F44336;  /* error_main */
            }}
        """)
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.file_id))
        top_row.addWidget(self.cancel_btn)

        layout.addLayout(top_row)

        # Progress bar - modern thin design
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)  # Hide text for cleaner look
        self.progress_bar.setFixedHeight(8)  # Thin modern progress bar
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: {RADIUS['sm']};
                background-color: #E0E0E0;  /* neutral_300 */
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1E88E5, stop:1 #2196F3);  /* primary gradient */
                border-radius: {RADIUS['sm']};
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Bottom row: file info
        info_row = QHBoxLayout()

        # File size (if we can get it) - modern typography
        try:
            file_size = Path(self.file_path).stat().st_size
            size_str = self._format_size(file_size)
            self.size_label = QLabel(size_str)
        except:
            self.size_label = QLabel("Unknown size")

        self.size_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_xs']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: #9E9E9E;  /* neutral_500 */
        """)
        info_row.addWidget(self.size_label)

        info_row.addStretch()

        # Percentage label - modern typography
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_mono']};  /* Monospace for numbers */
            font-size: {TYPOGRAPHY['size_xs']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            color: #757575;  /* neutral_600 */
        """)
        info_row.addWidget(self.percent_label)

        layout.addLayout(info_row)

    def update_progress(self, percentage: int, status: str):
        """Update progress bar and status with smooth animation"""
        # Animate progress bar changes
        current_value = self.progress_bar.value()
        if percentage != current_value:
            # Stop any existing animation
            if self._progress_animation:
                self._progress_animation.stop()

            # Create smooth progress animation
            self._progress_animation = QPropertyAnimation(self.progress_bar, b"value")
            self._progress_animation.setDuration(AnimationHelper.DURATION_NORMAL)
            self._progress_animation.setStartValue(current_value)
            self._progress_animation.setEndValue(percentage)
            self._progress_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._progress_animation.start()

        self.status_label.setText(status)
        self.percent_label.setText(f"{percentage}%")

        # Change colors based on status using semantic colors
        if percentage == 100:
            self.status_label.setStyleSheet(f"""
                font-family: {TYPOGRAPHY['font_primary']};
                font-size: {TYPOGRAPHY['size_sm']};
                font-weight: {TYPOGRAPHY['weight_semibold']};
                color: #4CAF50;  /* success_main */
            """)
            self.cancel_btn.setVisible(False)
        elif "error" in status.lower():
            self.status_label.setStyleSheet(f"""
                font-family: {TYPOGRAPHY['font_primary']};
                font-size: {TYPOGRAPHY['size_sm']};
                font-weight: {TYPOGRAPHY['weight_semibold']};
                color: #F44336;  /* error_main */
            """)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: {RADIUS['sm']};
                    background-color: #E0E0E0;
                }}
                QProgressBar::chunk {{
                    background-color: #F44336;  /* error_main */
                    border-radius: {RADIUS['sm']};
                }}
            """)

    def mark_complete(self):
        """Mark as complete"""
        self.update_progress(100, "Complete!")
        self.cancel_btn.setVisible(False)

    def mark_error(self, error: str):
        """Mark as error"""
        self.update_progress(0, f"Error: {error[:50]}")
        self.cancel_btn.setText("✕")
        self.cancel_btn.setToolTip("Remove from list")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(lambda: self.remove_clicked.emit(self.file_id))

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class FileQueueWidget(QWidget):
    """Widget to display file queue with progress"""

    cancel_file = Signal(str)  # file_id
    remove_file = Signal(str)  # file_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_items = {}  # file_id -> FileQueueItem
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 8, 8, 8)

        title = QLabel("File Queue")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_layout.addWidget(title)

        header_layout.addStretch()

        self.count_label = QLabel("0 files")
        self.count_label.setStyleSheet("color: #666;")
        header_layout.addWidget(self.count_label)

        layout.addWidget(header)

        # Scroll area for items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container for file items
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setSpacing(4)
        self.container_layout.setContentsMargins(4, 4, 4, 4)
        self.container_layout.addStretch()

        scroll.setWidget(self.container)
        layout.addWidget(scroll)

    def add_file(self, file_id: str, file_path: str):
        """Add a file to the queue"""
        if file_id in self.file_items:
            return

        item = FileQueueItem(file_id, file_path)
        item.cancel_clicked.connect(self.cancel_file.emit)
        item.remove_clicked.connect(self._remove_item)

        # Insert before stretch
        self.container_layout.insertWidget(
            self.container_layout.count() - 1,
            item
        )

        self.file_items[file_id] = item
        self._update_count()

    def update_progress(self, file_id: str, percentage: int, status: str):
        """Update progress for a file"""
        if file_id in self.file_items:
            self.file_items[file_id].update_progress(percentage, status)

    def mark_complete(self, file_id: str):
        """Mark file as complete"""
        if file_id in self.file_items:
            self.file_items[file_id].mark_complete()

    def mark_error(self, file_id: str, error: str):
        """Mark file as error"""
        if file_id in self.file_items:
            self.file_items[file_id].mark_error(error)

    def _remove_item(self, file_id: str):
        """Remove item from queue"""
        if file_id in self.file_items:
            item = self.file_items[file_id]
            self.container_layout.removeWidget(item)
            item.deleteLater()
            del self.file_items[file_id]
            self._update_count()
            self.remove_file.emit(file_id)

    def _update_count(self):
        """Update file count label"""
        count = len(self.file_items)
        self.count_label.setText(f"{count} file{'s' if count != 1 else ''}")

    def clear(self):
        """Clear all items"""
        for file_id in list(self.file_items.keys()):
            self._remove_item(file_id)
