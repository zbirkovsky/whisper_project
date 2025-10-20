"""
Compact floating overlay for audio recording
Similar to NVIDIA overlay - stays on top and can be dragged anywhere
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QTime, QPoint, Signal
from PySide6.QtGui import QPainter, QColor


class RecordingOverlay(QWidget):
    """Compact floating recording overlay that stays on top"""

    pause_clicked = Signal()
    stop_clicked = Signal()
    minimize_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_paused = False
        self.elapsed_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # For dragging
        self.drag_position = QPoint()
        self.is_dragging = False

        self.setup_ui()

    def setup_ui(self):
        """Setup the compact overlay UI"""
        # Window flags: frameless, stay on top, tool window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # Semi-transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Fixed compact size
        self.setFixedSize(280, 100)

        # Position in top-left corner of primary screen (multi-monitor friendly)
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(screen.left() + 20, screen.top() + 20)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container with background
        self.container = QWidget()
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 44, 52, 230);
                border-radius: 12px;
                border: 2px solid rgba(0, 120, 212, 150);
            }
        """)
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(6)

        # Header with REC indicator and minimize button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.rec_indicator = QLabel("● REC")
        self.rec_indicator.setStyleSheet("""
            QLabel {
                color: #dc3545;
                font-size: 13px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.rec_indicator)

        header_layout.addStretch()

        # Minimize button
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setFixedSize(24, 24)
        self.minimize_btn.setToolTip("Minimize to dialog")
        self.minimize_btn.clicked.connect(self.minimize_clicked.emit)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(108, 117, 125, 180);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(108, 117, 125, 255);
            }
        """)
        header_layout.addWidget(self.minimize_btn)

        container_layout.addLayout(header_layout)

        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
                background: transparent;
            }
        """)
        container_layout.addWidget(self.timer_label)

        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.pause_btn = QPushButton("⏸")
        self.pause_btn.setFixedSize(40, 32)
        self.pause_btn.setToolTip("Pause recording")
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 193, 7, 200);
                color: #212529;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(255, 193, 7, 255);
            }
        """)
        button_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(40, 32)
        self.stop_btn.setToolTip("Stop recording")
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(220, 53, 69, 200);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(220, 53, 69, 255);
            }
        """)
        button_layout.addWidget(self.stop_btn)

        button_layout.addStretch()

        # Drag hint label
        self.drag_hint = QLabel("⋮⋮")
        self.drag_hint.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 100);
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.drag_hint.setToolTip("Drag to move")
        button_layout.addWidget(self.drag_hint)

        container_layout.addLayout(button_layout)

        layout.addWidget(self.container)

    def start_recording(self):
        """Start the recording timer"""
        self.elapsed_time = 0
        self.is_paused = False
        self.timer.start(1000)
        self.rec_indicator.setVisible(True)
        self.update_pause_button()

    def on_pause_clicked(self):
        """Handle pause/resume button click"""
        self.is_paused = not self.is_paused

        if self.is_paused:
            self.timer.stop()
            self.rec_indicator.setText("⏸ PAUSED")
            self.rec_indicator.setStyleSheet("""
                QLabel {
                    color: #ffc107;
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                }
            """)
        else:
            self.timer.start(1000)
            self.rec_indicator.setText("● REC")
            self.rec_indicator.setStyleSheet("""
                QLabel {
                    color: #dc3545;
                    font-size: 13px;
                    font-weight: bold;
                    background: transparent;
                }
            """)

        self.update_pause_button()
        self.pause_clicked.emit()

    def update_pause_button(self):
        """Update pause button appearance"""
        if self.is_paused:
            self.pause_btn.setText("▶")
            self.pause_btn.setToolTip("Resume recording")
        else:
            self.pause_btn.setText("⏸")
            self.pause_btn.setToolTip("Pause recording")

    def stop_recording(self):
        """Stop the recording timer"""
        self.timer.stop()
        self.rec_indicator.setVisible(False)

    def update_timer(self):
        """Update the elapsed time display"""
        if not self.is_paused:
            self.elapsed_time += 1
            time = QTime(0, 0, 0).addSecs(self.elapsed_time)
            self.timer_label.setText(time.toString("HH:mm:ss"))

    def mousePressEvent(self, event):
        """Start dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle dragging"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Stop dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()

    def paintEvent(self, event):
        """Custom paint for shadow effect"""
        # Let the default painting happen
        super().paintEvent(event)
