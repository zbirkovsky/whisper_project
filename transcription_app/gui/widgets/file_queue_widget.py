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
from transcription_app.gui.styles.stylesheet_manager import SPACING, RADIUS, TYPOGRAPHY, StyleSheetManager, Theme


class FileQueueItem(QFrame):
    """Individual file item with progress bar and controls"""

    cancel_clicked = Signal(str)  # file_id
    remove_clicked = Signal(str)  # file_id

    def __init__(self, file_id: str, file_path: str, parent=None):
        super().__init__(parent)
        self.file_id = file_id
        self.file_path = file_path
        self._progress_animation = None
        self.current_theme = Theme.DARK  # Default
        if hasattr(parent, 'current_theme'):
            self.current_theme = parent.current_theme
        self.setup_ui()

    def _get_colors(self):
        """Get theme-aware colors"""
        sm = StyleSheetManager(self.current_theme)
        p = sm._palette
        return {
            'card_bg': p.surface_1,
            'card_hover': p.surface_2,
            'border': p.neutral_600,
            'border_hover': p.primary_500,
            'text_primary': p.text_primary,
            'text_secondary': p.text_secondary,
            'text_muted': p.neutral_300,
            'progress_bg': p.neutral_600,
            'progress_fill': p.primary_500,
            'progress_fill_end': p.primary_300,
            'success': p.success_main,
            'error': p.error_main,
        }

    def _apply_card_style(self):
        """Apply card styling"""
        c = self._get_colors()
        self.setStyleSheet(f"""
            FileQueueItem {{
                background-color: {c['card_bg']};
                border: 2px solid {c['border']};
                border-radius: {RADIUS['md']};
                margin: {SPACING['xs']};
                padding: {SPACING['md']};
            }}
            FileQueueItem:hover {{
                border-color: {c['border_hover']};
                background-color: {c['card_hover']};
            }}
        """)

    def _apply_label_styles(self):
        """Apply styles to all labels"""
        c = self._get_colors()
        self.name_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_base']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {c['text_primary']};
        """)
        self.status_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: {c['text_secondary']};
        """)
        self.size_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_xs']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: {c['text_muted']};
        """)
        self.percent_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_mono']};
            font-size: {TYPOGRAPHY['size_xs']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            color: {c['progress_fill']};
        """)

    def _apply_button_style(self):
        """Apply cancel button style"""
        c = self._get_colors()
        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: {c['text_muted']};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {c['error']};
                color: white;
            }}
        """)

    def _apply_progress_style(self):
        """Apply progress bar style"""
        c = self._get_colors()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: {RADIUS['sm']};
                background-color: {c['progress_bg']};
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {c['progress_fill']}, stop:1 {c['progress_fill_end']});
                border-radius: {RADIUS['sm']};
            }}
        """)

    def setup_ui(self):
        """Setup the UI for this file item - theme aware"""
        self.setFrameShape(QFrame.Shape.StyledPanel)

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

        # File icon and name
        self.name_label = QLabel(self.file_id)
        top_row.addWidget(self.name_label)

        top_row.addStretch()

        # Status label
        self.status_label = QLabel("Waiting...")
        top_row.addWidget(self.status_label)

        # Cancel button
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(24, 24)
        self.cancel_btn.setToolTip("Cancel transcription")
        self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.file_id))
        top_row.addWidget(self.cancel_btn)

        layout.addLayout(top_row)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

        # Bottom row: file info
        info_row = QHBoxLayout()

        # File size
        try:
            file_size = Path(self.file_path).stat().st_size
            size_str = self._format_size(file_size)
            self.size_label = QLabel(size_str)
        except:
            self.size_label = QLabel("Unknown size")

        info_row.addWidget(self.size_label)

        info_row.addStretch()

        # Percentage label
        self.percent_label = QLabel("0%")
        info_row.addWidget(self.percent_label)

        layout.addLayout(info_row)

        # Apply all theme-aware styles
        self._apply_card_style()
        self._apply_label_styles()
        self._apply_button_style()
        self._apply_progress_style()

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
        c = self._get_colors()
        if percentage == 100:
            self.status_label.setStyleSheet(f"""
                font-family: {TYPOGRAPHY['font_primary']};
                font-size: {TYPOGRAPHY['size_sm']};
                font-weight: {TYPOGRAPHY['weight_semibold']};
                color: {c['success']};
            """)
            self.cancel_btn.setVisible(False)
        elif "error" in status.lower():
            self.status_label.setStyleSheet(f"""
                font-family: {TYPOGRAPHY['font_primary']};
                font-size: {TYPOGRAPHY['size_sm']};
                font-weight: {TYPOGRAPHY['weight_semibold']};
                color: {c['error']};
            """)
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    border-radius: {RADIUS['sm']};
                    background-color: {c['progress_bg']};
                }}
                QProgressBar::chunk {{
                    background-color: {c['error']};
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

    def update_theme(self, theme: Theme):
        """Update widget theme"""
        self.current_theme = theme
        self._apply_card_style()
        self._apply_label_styles()
        self._apply_button_style()
        self._apply_progress_style()

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
        self.current_theme = Theme.DARK  # Default
        if hasattr(parent, 'style_manager'):
            self.current_theme = parent.style_manager.current_theme
        self.setup_ui()

    def _get_colors(self):
        """Get theme-aware colors"""
        sm = StyleSheetManager(self.current_theme)
        p = sm._palette
        return {
            'bg': p.background,
            'text_primary': p.text_primary,
            'text_secondary': p.text_secondary,
        }

    def _apply_widget_style(self):
        """Apply theme-aware widget style"""
        c = self._get_colors()
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['bg']};
            }}
        """)

    def _apply_header_style(self):
        """Apply header styling"""
        c = self._get_colors()
        self.header.setStyleSheet(f"background-color: {c['bg']};")
        self.title.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_lg']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {c['text_primary']};
        """)
        self.count_label.setStyleSheet(f"""
            font-family: {TYPOGRAPHY['font_primary']};
            font-size: {TYPOGRAPHY['size_sm']};
            font-weight: {TYPOGRAPHY['weight_regular']};
            color: {c['text_secondary']};
        """)

    def _apply_scroll_style(self):
        """Apply scroll area styling"""
        c = self._get_colors()
        self.scroll.setStyleSheet(f"""
            QScrollArea {{
                background-color: {c['bg']};
                border: none;
            }}
        """)
        self.container.setStyleSheet(f"background-color: {c['bg']};")

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header - compact professional styling
        self.header = QWidget()
        header_layout = QHBoxLayout(self.header)
        # Compact header padding (4px = sm)
        padding = int(SPACING['sm'].replace('px', ''))
        header_layout.setContentsMargins(padding * 2, padding, padding * 2, padding)

        self.title = QLabel("File Queue")
        header_layout.addWidget(self.title)

        header_layout.addStretch()

        self.count_label = QLabel("0 files")
        header_layout.addWidget(self.count_label)

        layout.addWidget(self.header)

        # Scroll area for items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container for file items - compact spacing
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        # Use xs spacing (2px) for very compact layout
        compact_spacing = int(SPACING['xs'].replace('px', ''))
        self.container_layout.setSpacing(compact_spacing)
        self.container_layout.setContentsMargins(compact_spacing, compact_spacing, compact_spacing, compact_spacing)
        self.container_layout.addStretch()

        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        # Apply theme-aware styles
        self._apply_widget_style()
        self._apply_header_style()
        self._apply_scroll_style()

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

    def update_theme(self, theme: Theme):
        """Update widget theme"""
        self.current_theme = theme
        self._apply_widget_style()
        self._apply_header_style()
        self._apply_scroll_style()
        # Update all file items
        for item in self.file_items.values():
            item.update_theme(theme)

    def clear(self):
        """Clear all items"""
        for file_id in list(self.file_items.keys()):
            self._remove_item(file_id)
