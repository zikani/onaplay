from PyQt5.QtWidgets import (QWidget, QSizePolicy, QLabel, QVBoxLayout, 
                            QHBoxLayout, QGraphicsDropShadowEffect, QFrame,
                            QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QPixmap, QPen, QBrush

class VideoOverlay(QWidget):
    """Overlay widget that shows playback controls and info on top of video."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setObjectName("videoOverlay")
        
        # Fade in/out animation
        self.opacity_effect = self.graphicsEffect() or QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.opacity_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Setup UI
        self.setup_ui()
        self.hide_overlay()
    
    def setup_ui(self):
        """Initialize the overlay UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 40)
        
        # Top bar with title and controls
        top_bar = QWidget()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        self.title_label = QLabel("OnaPlay")
        self.title_label.setObjectName("titleLabel")
        
        top_layout.addWidget(self.title_label, 1)
        
        # Center container for play/pause button
        center_container = QWidget()
        center_container.setObjectName("centerContainer")
        center_layout = QHBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        self.play_button = QLabel()
        self.play_button.setObjectName("centerPlayButton")
        self.play_button.setFixedSize(80, 80)
        
        center_layout.addStretch()
        center_layout.addWidget(self.play_button)
        center_layout.addStretch()
        
        # Add to main layout
        layout.addWidget(top_bar)
        layout.addStretch()
        layout.addWidget(center_container)
        layout.addStretch()
    
    def show_overlay(self):
        """Show the overlay with fade in animation."""
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self.opacity_effect.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        self.show()
    
    def hide_overlay(self):
        """Hide the overlay with fade out animation."""
        self.opacity_animation.stop()
        self.opacity_animation.setStartValue(self.opacity_effect.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.opacity_animation.finished.connect(self.hide)
        self.opacity_animation.start()
    
    def update_play_state(self, is_playing):
        """Update the play/pause button state."""
        # This will be styled via CSS
        self.play_button.setProperty("playing", is_playing)
        self.play_button.style().unpolish(self.play_button)
        self.play_button.style().polish(self.play_button)


class VideoWidget(QWidget):
    """Main video display widget with overlay controls."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.setObjectName("videoWidget")
        
        # Set size policy to expanding in both directions
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        
        # Store aspect ratio (will be updated when video is loaded)
        self.aspect_ratio = 16.0 / 9.0  # Default 16:9
        
        # Create overlay
        self.overlay = VideoOverlay(self)
        
        # Setup mouse tracking for showing/hiding controls
        self.setMouseTracking(True)
        self._mouse_timer = QTimer(self)
        self._mouse_timer.setSingleShot(True)
        self._mouse_timer.timeout.connect(self.overlay.hide_overlay)
        self._last_mouse_pos = None
        
        # Show overlay initially
        self.overlay.show_overlay()
        self._mouse_timer.start(3000)  # Hide after 3 seconds
        
        # Disable focus to prevent stealing keyboard events
        self.setFocusPolicy(Qt.NoFocus)
        
    def keyPressEvent(self, event):
        """Forward key events to parent."""
        if self.parent():
            self.parent().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
            
    def focusInEvent(self, event):
        """Prevent focus stealing."""
        event.ignore()
        
    def focusOutEvent(self, event):
        """Prevent focus stealing."""
        event.ignore()
        
    def setFocus(self, *args, **kwargs):
        """Override to prevent focus stealing."""
        pass
        
    def focusNextPrevChild(self, next):
        """Override to prevent focus changes."""
        return False
    
    def resizeEvent(self, event):
        """Handle widget resize."""
        self.overlay.resize(self.size())
        super().resizeEvent(event)
    
    def set_aspect_ratio(self, width, height):
        """Set the aspect ratio of the video."""
        if width > 0 and height > 0:
            self.aspect_ratio = width / height
            self.update_geometry()
    
    def update_geometry(self):
        """Update the geometry to maintain aspect ratio."""
        if not self.parent() or not hasattr(self, 'aspect_ratio'):
            return
            
        parent_rect = self.parent().rect()
        if not parent_rect.isValid():
            return
            
        # Calculate target size maintaining aspect ratio
        target_width = parent_rect.width()
        target_height = int(target_width / self.aspect_ratio)
        
        # If the calculated height is larger than available, adjust width to fit height
        if target_height > parent_rect.height():
            target_height = parent_rect.height()
            target_width = int(target_height * self.aspect_ratio)
        
        # Center the widget
        x = (parent_rect.width() - target_width) // 2
        y = (parent_rect.height() - target_height) // 2
        
        self.setGeometry(x, y, target_width, target_height)
    
    def mouseMoveEvent(self, event):
        """Show controls on mouse movement."""
        current_pos = event.pos()
        if self._last_mouse_pos is None or (current_pos - self._last_mouse_pos).manhattanLength() > 3:
            self.overlay.show_overlay()
            self._mouse_timer.start(3000)  # Hide after 3 seconds of no movement
        self._last_mouse_pos = current_pos
        super().mouseMoveEvent(event)
    
    def enterEvent(self, event):
        """Show controls when mouse enters the widget."""
        self.overlay.show_overlay()
        self._mouse_timer.start(3000)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide controls when mouse leaves the widget."""
        self.overlay.hide_overlay()
        self._mouse_timer.stop()
        super().leaveEvent(event)
    
    def update_play_state(self, is_playing):
        """Update the play/pause state in the overlay."""
        self.overlay.update_play_state(is_playing)
    
    def get_video_sink(self):
        """Get the video sink for the media player."""
        return int(self.winId())  # Convert to int for VLC compatibility
