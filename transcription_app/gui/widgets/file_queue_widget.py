"""
Enhanced file queue widget with progress bars and controls
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
from transcription_app.gui.styles import AnimationHelper


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
        """Setup the UI for this file item"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            FileQueueItem {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 2px;
                padding: 8px;
            }
            FileQueueItem:hover {
                border-color: #0078d4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Top row: filename and controls
        top_row = QHBoxLayout()

        # File icon and name
        self.name_label = QLabel(self.file_id)
        self.name_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        top_row.addWidget(self.name_label)

        top_row.addStretch()

        # Status label
        self.status_label = QLabel("Waiting...")
        self.status_label.setStyleSheet("color: #666;")
        top_row.addWidget(self.status_label)

        # Cancel button
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(24, 24)
        self.cancel_btn.setToolTip("Cancel transcription")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #666;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                color: #d13438;
            }
        """)
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.file_id))
        top_row.addWidget(self.cancel_btn)

        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Bottom row: file info
        info_row = QHBoxLayout()

        # File size (if we can get it)
        try:
            file_size = Path(self.file_path).stat().st_size
            size_str = self._format_size(file_size)
            self.size_label = QLabel(size_str)
        except:
            self.size_label = QLabel("Unknown size")

        self.size_label.setStyleSheet("color: #999; font-size: 10px;")
        info_row.addWidget(self.size_label)

        info_row.addStretch()

        # Percentage label
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("color: #666; font-size: 10px;")
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

        # Change colors based on status
        if percentage == 100:
            self.status_label.setStyleSheet("color: #107c10; font-weight: bold;")
            self.cancel_btn.setVisible(False)
        elif "error" in status.lower():
            self.status_label.setStyleSheet("color: #d13438; font-weight: bold;")
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #e0e0e0;
                    border-radius: 3px;
                    text-align: center;
                    background-color: #f5f5f5;
                }
                QProgressBar::chunk {
                    background-color: #d13438;
                    border-radius: 2px;
                }
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
