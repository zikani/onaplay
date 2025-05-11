from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QStyle,
    QVBoxLayout, QSizePolicy, QToolButton, QFrame, QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QEvent
from PyQt5.QtGui import QIcon, QFont, QColor, QPainter, QPen, QLinearGradient
import os
import math
from src.utils.file_utils import get_asset_path

class TimelineSlider(QSlider):
    """Custom timeline slider with progress indicator."""
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setMouseTracking(True)
        self._progress = 0
        self._hover_pos = -1
        self._buffer = 0
        self.setCursor(Qt.PointingHandCursor)
    
    def set_progress(self, progress):
        """Set the progress percentage (0-100)."""
        self._progress = progress
        self.update()
    
    def set_buffer(self, buffer):
        """Set the buffer percentage (0-100)."""
        self._buffer = buffer
        self.update()
    
    def mouseMoveEvent(self, event):
        """Update hover position for tooltip."""
        self._hover_pos = event.pos().x()
        self.update()
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        """Reset hover position when leaving the slider."""
        self._hover_pos = -1
        self.update()
        super().leaveEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event for the timeline."""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        bg_rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(Qt.NoPen)
        
        # Draw buffer progress
        if self._buffer > 0:
            buffer_width = int(bg_rect.width() * (self._buffer / 100))
            buffer_rect = bg_rect.adjusted(0, 0, -bg_rect.width() + buffer_width, 0)
            painter.fillRect(buffer_rect, QColor(100, 100, 100, 150))
        
        # Draw progress
        if self._progress > 0:
            progress_width = int(bg_rect.width() * (self._progress / 100))
            progress_rect = bg_rect.adjusted(0, 0, -bg_rect.width() + progress_width, 0)
            
            # Gradient for progress
            gradient = QLinearGradient(progress_rect.topLeft(), progress_rect.topRight())
            gradient.setColorAt(0, QColor(0, 150, 255))
            gradient.setColorAt(1, QColor(0, 200, 255))
            painter.fillRect(progress_rect, gradient)
        
        # Draw hover indicator
        if self._hover_pos > 0 and self.underMouse():
            painter.setPen(QPen(Qt.white, 2))
            painter.drawLine(self._hover_pos, 0, self._hover_pos, self.height())
            
            # Draw time tooltip
            hover_time = int((self._hover_pos / self.width()) * self.maximum())
            time_text = self.format_time(hover_time)
            
            font_metrics = painter.fontMetrics()
            text_rect = font_metrics.boundingRect(time_text)
            text_rect.moveCenter(self.rect().center())
            
            tooltip_rect = text_rect.adjusted(-10, -5, 10, 5)
            tooltip_rect.moveTop(-25)
            tooltip_rect.moveLeft(self._hover_pos - tooltip_rect.width() // 2)
            
            # Keep tooltip within bounds
            if tooltip_rect.left() < 0:
                tooltip_rect.moveLeft(0)
            elif tooltip_rect.right() > self.width():
                tooltip_rect.moveRight(self.width())
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 0, 0, 200))
            painter.drawRoundedRect(tooltip_rect, 3, 3)
            
            painter.setPen(Qt.white)
            painter.drawText(tooltip_rect, Qt.AlignCenter, time_text)
    
    @staticmethod
    def format_time(milliseconds):
        """Format milliseconds to HH:MM:SS or MM:SS."""
        seconds = int(milliseconds / 1000)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"


class ControlBar(QWidget):
    """Control bar with media controls and timeline."""
    
    # Signals
    play_pressed = pyqtSignal()
    stop_pressed = pyqtSignal()
    seek_requested = pyqtSignal(int)  # Position in milliseconds
    volume_changed = pyqtSignal(int)   # Volume 0-100
    fullscreen_toggled = pyqtSignal()
    info_toggled = pyqtSignal()
    playlist_toggled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.duration = 0
        self.current_position = 0
        self._is_fullscreen = False
        self._auto_hide_timer = QTimer(self)
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self._auto_hide)
        self._is_mouse_over = False
        self.setup_ui()
        
        # Set up auto-hide timer
        self._auto_hide_timeout = 3000  # 3 seconds
        self._auto_hide_timer.start(self._auto_hide_timeout)
    
    def set_fullscreen_mode(self, is_fullscreen):
        """Update control bar style for fullscreen mode."""
        self._is_fullscreen = is_fullscreen
        if is_fullscreen:
            self.setStyleSheet("""
                QWidget#controlBar {
                    background-color: rgba(0, 0, 0, 200);
                    border: none;
                    border-top: 1px solid rgba(255, 255, 255, 50);
                    border-radius: 0;
                    padding: 5px 0;
                }
                QWidget#timelineContainer, QWidget#controlsContainer {
                    background-color: transparent;
                }
                QToolButton {
                    padding: 5px;
                    background: transparent;
                    border: none;
                }
                QToolButton:hover {
                    background: rgba(255, 255, 255, 30);
                    border-radius: 3px;
                }
            """)
            # In fullscreen, show the control bar initially
            self.show()
            self.raise_()
            self._start_auto_hide_timer()
        else:
            self.setStyleSheet("""
                QWidget#controlBar {
                    background-color: #262626;
                    border: none;
                    border-top: 1px solid rgba(255, 255, 255, 10);
                    border-radius: 0;
                    padding: 5px 0;
                }
                QToolButton {
                    padding: 5px;
                    background: transparent;
                    border: none;
                }
                QToolButton:hover {
                    background: rgba(255, 255, 255, 20);
                    border-radius: 3px;
                }
            """)
            self.show()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        self._is_mouse_over = True
        if self._is_fullscreen:
            self.show()
            self._auto_hide_timer.stop()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self._is_mouse_over = False
        if self._is_fullscreen and not self.underMouse():
            self._start_auto_hide_timer()
        super().leaveEvent(event)
    
    def _start_auto_hide_timer(self):
        """Start the auto-hide timer."""
        if self._is_fullscreen:
            self._auto_hide_timer.start(self._auto_hide_timeout)
    
    def _auto_hide(self):
        """Auto-hide the control bar in fullscreen mode."""
        if self._is_fullscreen and not self._is_mouse_over:
            # Only hide if the mouse is not over the control bar
            if not self.underMouse():
                self.hide()
            else:
                # If mouse is over the control bar, restart the timer
                self._start_auto_hide_timer()
    
    def showEvent(self, event):
        """Handle show event."""
        if self._is_fullscreen:
            self._start_auto_hide_timer()
        super().showEvent(event)
        
    def event(self, event):
        """Handle events for the control bar."""
        # Let the parent handle key events when we're hidden in fullscreen
        if self._is_fullscreen and not self.isVisible() and hasattr(event, 'type') and event.type() in [QEvent.KeyPress, QEvent.KeyRelease]:
            return False
        return super().event(event)
        
    def keyPressEvent(self, event):
        """Handle key press events."""
        # Let the parent handle all key events
        event.ignore()
        
    def keyReleaseEvent(self, event):
        """Handle key release events."""
        # Let the parent handle all key events
        event.ignore()
    
    def setup_ui(self):
        """Initialize the control bar UI."""
        self.setObjectName("controlBar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 15)
        layout.setSpacing(10)
        
        # Set initial style
        self.setStyleSheet("""
            QWidget#controlBar {
                background-color: #262626;
                border: none;
                border-top: 1px solid rgba(255, 255, 255, 10);
                border-radius: 0;
            }
            QWidget#timelineContainer, QWidget#controlsContainer {
                background-color: transparent;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255, 255, 255, 20);
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1e90ff;
                border-radius: 2px;
            }
        """)
        
        # Timeline container
        timeline_container = QWidget()
        timeline_container.setObjectName("timelineContainer")
        timeline_layout = QHBoxLayout(timeline_container)
        timeline_layout.setContentsMargins(0, 0, 0, 0)
        timeline_layout.setSpacing(10)
        
        # Current time
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("timeLabel")
        self.current_time_label.setMinimumWidth(40)
        
        # Timeline slider
        self.timeline = TimelineSlider()
        self.timeline.setObjectName("timelineSlider")
        self.timeline.setRange(0, 0)
        self.timeline.sliderMoved.connect(self.on_seek)
        
        # Duration
        self.duration_label = QLabel("00:00")
        self.duration_label.setObjectName("timeLabel")
        self.duration_label.setMinimumWidth(40)
        
        timeline_layout.addWidget(self.current_time_label)
        timeline_layout.addWidget(self.timeline, 1)
        timeline_layout.addWidget(self.duration_label)
        
        # Controls container
        controls_container = QWidget()
        controls_container.setObjectName("controlsContainer")
        controls_layout = QHBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)
        
        # Left controls
        left_controls = QWidget()
        left_layout = QHBoxLayout(left_controls)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Play/Pause button
        self.play_button = QPushButton()
        self.play_button.setObjectName("playButton")
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setFixedSize(36, 36)
        self.play_button.clicked.connect(self.on_play_pressed)
        
        # Stop button
        self.stop_button = QPushButton()
        self.stop_button.setObjectName("controlButton")
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.setFixedSize(32, 32)
        self.stop_button.clicked.connect(self.stop_pressed.emit)
        
        # Previous button
        self.prev_button = QPushButton()
        self.prev_button.setObjectName("controlButton")
        self.prev_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.prev_button.setFixedSize(32, 32)
        
        # Next button
        self.next_button = QPushButton()
        self.next_button.setObjectName("controlButton")
        self.next_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.next_button.setFixedSize(32, 32)
        
        left_layout.addWidget(self.prev_button)
        left_layout.addWidget(self.play_button)
        left_layout.addWidget(self.stop_button)
        left_layout.addWidget(self.next_button)
        
        # Center controls (empty for now, can add playback rate, etc.)
        center_controls = QWidget()
        center_layout = QHBoxLayout(center_controls)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Right controls
        right_controls = QWidget()
        right_layout = QHBoxLayout(right_controls)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Volume button
        self.volume_button = QPushButton()
        self.volume_button.setObjectName("controlButton")
        self.volume_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.volume_button.setFixedSize(32, 32)
        self.volume_button.clicked.connect(self.toggle_mute)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit(v))
        
        # Playlist button
        self.playlist_button = QPushButton()
        self.playlist_button.setObjectName("controlButton")
        self.playlist_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playlist_button.setFixedSize(32, 32)
        self.playlist_button.clicked.connect(self.playlist_toggled.emit)
        
        # Info button
        self.info_button = QPushButton()
        self.info_button.setObjectName("controlButton")
        self.info_button.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))
        self.info_button.setFixedSize(32, 32)
        self.info_button.clicked.connect(self.info_toggled.emit)
        
        # Fullscreen button
        self.fullscreen_button = QPushButton()
        self.fullscreen_button.setObjectName("controlButton")
        self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        self.fullscreen_button.setFixedSize(32, 32)
        self.fullscreen_button.clicked.connect(self.fullscreen_toggled.emit)
        
        right_layout.addWidget(self.volume_button)
        right_layout.addWidget(self.volume_slider)
        right_layout.addWidget(self.playlist_button)
        right_layout.addWidget(self.info_button)
        right_layout.addWidget(self.fullscreen_button)
        
        # Add all controls to main layout
        controls_layout.addWidget(left_controls, 1)
        controls_layout.addWidget(center_controls, 1)
        controls_layout.addWidget(right_controls, 1)
        
        # Add to main layout
        layout.addWidget(timeline_container)
        layout.addWidget(controls_container)
    
    def on_play_pressed(self):
        """Handle play/pause button press."""
        self.play_pressed.emit()
    
    def on_seek(self, position):
        """Handle timeline seek."""
        self.seek_requested.emit(position)
    
    def update_position(self, position, duration):
        """Update the timeline position and time labels."""
        self.current_position = position
        self.duration = duration if duration > 0 else 1  # Avoid division by zero
        
        if not self.timeline.isSliderDown():
            self.timeline.setValue(position)
        
        # Update timeline progress
        progress = (position / self.duration) * 100 if self.duration > 0 else 0
        self.timeline.set_progress(progress)
        
        # Update time labels
        self.current_time_label.setText(self.format_time(position))
        self.duration_label.setText(self.format_time(duration))
    
    def set_duration(self, duration):
        """Set the maximum duration of the timeline."""
        self.duration = duration
        self.timeline.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))
    
    def update_play_button(self, is_playing):
        """Update the play/pause button icon based on playback state."""
        self.is_playing = is_playing
        icon = self.style().standardIcon(
            QStyle.SP_MediaPause if is_playing else QStyle.SP_MediaPlay)
        self.play_button.setIcon(icon)
        
        # Update button style
        if is_playing:
            self.play_button.setObjectName("playButtonActive")
        else:
            self.play_button.setObjectName("playButton")
        self.play_button.style().unpolish(self.play_button)
        self.play_button.style().polish(self.play_button)
    
    def toggle_mute(self):
        """Toggle mute state of the volume."""
        if self.volume_slider.value() > 0:
            self.last_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
        else:
            self.volume_slider.setValue(self.last_volume if hasattr(self, 'last_volume') else 75)
    
    @staticmethod
    def format_time(milliseconds):
        """Format milliseconds to HH:MM:SS or MM:SS."""
        seconds = int(milliseconds / 1000)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
