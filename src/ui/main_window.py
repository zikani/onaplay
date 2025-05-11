from PyQt5.QtCore import Qt, QPoint, QUrl, QEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QMessageBox, QLabel, QListWidget, QListWidgetItem,
                            QSlider, QPushButton, QFrame, QSplitter, QScrollArea, QComboBox, QSizePolicy,
                            QLineEdit, QSpinBox)
from .control_bar import ControlBar
from .video_widget import VideoWidget
from src.core.media_player import MediaPlayer
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint, QUrl
from PyQt5.QtGui import QIcon, QPalette, QColor, QFont, QFontDatabase, QPixmap, QLinearGradient, QGradient
import os
import traceback

from src.core.media_player import MediaPlayer
from src.ui.video_widget import VideoWidget
from src.ui.control_bar import ControlBar
from src.ui.playlist_widget import PlaylistWidget
from src.ui.menu_bar import MenuBar
from src.ui.status_bar import StatusBar
from src.utils.file_utils import get_asset_path

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setObjectName("titleBar")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 0, 15, 0)
        
        # Title
        self.title = QLabel("OnaPlay")
        self.title.setObjectName("titleLabel")
        
        # Only add window controls if this is the main window
        if parent and isinstance(parent, QMainWindow):
            # Window controls
            self.minimize_btn = QPushButton("−")
            self.maximize_btn = QPushButton("□")
            self.close_btn = QPushButton("×")
            
            # Style window controls
            for btn in [self.minimize_btn, self.maximize_btn, self.close_btn]:
                btn.setFixedSize(18, 18)
                btn.setStyleSheet("""
                    QPushButton {
                        border: none;
                        background: transparent;
                        color: #e0e0e0;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: rgba(255, 255, 255, 0.1);
                        border-radius: 9px;
                    }
                """)
            
            # Add window controls to layout
            self.layout.addStretch()
            self.layout.addWidget(self.minimize_btn)
            self.layout.addWidget(self.maximize_btn)
            self.layout.addWidget(self.close_btn)
            
            # Connect signals
            self.minimize_btn.clicked.connect(self.parent.showMinimized)
            self.maximize_btn.clicked.connect(self.toggle_maximize)
            self.close_btn.clicked.connect(self.parent.close)
        else:
            # For non-main windows, just add a close button if needed
            self.close_btn = QPushButton("×")
            self.close_btn.setFixedSize(18, 18)
            self.close_btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: transparent;
                    color: #e0e0e0;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 9px;
                }
            """)
            self.layout.addStretch()
            self.layout.addWidget(self.close_btn)
            self.close_btn.clicked.connect(self.parent.close if self.parent else None)
        
        # For window dragging
        self.start = QPoint(0, 0)
        self.pressing = False
    
    def toggle_maximize(self):
        if hasattr(self, 'parent') and self.parent:
            if self.parent.isMaximized():
                self.parent.showNormal()
            else:
                self.parent.showMaximized()
    
    def mousePressEvent(self, event):
        if hasattr(self, 'parent') and self.parent and isinstance(self.parent, QMainWindow):
            self.start = self.mapToGlobal(event.pos())
            self.pressing = True
    
    def mouseMoveEvent(self, event):
        if hasattr(self, 'parent') and self.parent and self.pressing and isinstance(self.parent, QMainWindow):
            if self.parent.isMaximized():
                self.parent.showNormal()
            self.parent.move(self.parent.pos() + self.mapToGlobal(event.pos()) - self.start)
            self.start = self.mapToGlobal(event.pos())
    
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'parent') and self.parent and isinstance(self.parent, QMainWindow):
            self.pressing = False


class MainWindow(QMainWindow):
    def showEvent(self, event):
        print(f"MainWindow show event triggered. Window visible: {self.isVisible()}")
        super().showEvent(event)
        print(f"After showEvent. Window visible: {self.isVisible()}")
    
    def paintEvent(self, event):
        print(f"MainWindow paint event. Visible: {self.isVisible()}, Size: {self.size()}")
        super().paintEvent(event)
    
    def __init__(self):
        try:
            super().__init__()
            print("Initializing MainWindow...")
            
            # Set focus policy to ensure we can receive keyboard events
            self.setFocusPolicy(Qt.StrongFocus)
            
            # Install event filter to capture key events globally
            QApplication.instance().installEventFilter(self)
            
            # Ensure we can receive keyboard events
            self.setAttribute(Qt.WA_KeyCompression, False)
            self.setFocus()
            
            # Debug information
            primary_screen = QApplication.primaryScreen()
            print(f"Primary screen: {primary_screen.name() if primary_screen else 'None'}")
            print(f"Screens available: {[screen.name() for screen in QApplication.screens()]}")
            
            # Set window properties with default flags
            self.setWindowTitle("OnaPlay")
            
            # Set window size
            self.setMinimumSize(1200, 700)
            self.resize(1280, 800)
            
            # Set window style
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                
                QWidget {
                    color: #ffffff;
                    font-family: Arial, sans-serif;
                }
            """)
            
            # Load and apply stylesheet
            self.load_stylesheet()
            
            # Create main container
            self.main_widget = QWidget()
            self.main_layout = QVBoxLayout(self.main_widget)
            self.main_layout.setContentsMargins(0, 0, 0, 0)
            self.main_layout.setSpacing(0)
            self.setCentralWidget(self.main_widget)
            
            # Add menu bar
            self.menu_bar = self.menuBar()
            
            # Create menus
            self.setup_menus()
            
            # Add title bar
            self.title_bar = TitleBar(self)
            self.main_layout.addWidget(self.title_bar)
            
            # Set window icon
            icon_path = get_asset_path("icons/app_icon.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            
            # Initialize media player
            print("Initializing media player...")
            self.media_player = MediaPlayer()
            
            # Initialize UI components
            print("Setting up UI...")
            self.setup_ui()
            
            # Connect signals
            print("Setting up connections...")
            self.setup_connections()
            
            print("MainWindow initialized successfully")
            
            # Show window
            self.show()
        except Exception as e:
            print(f"Error initializing MainWindow: {str(e)}")
            traceback.print_exc()
            raise
    
    def load_stylesheet(self):
        """Load and apply the stylesheet."""
        style_path = get_asset_path("styles/dark_theme.qss")
        print(f"Loading stylesheet from: {style_path}")
        if os.path.exists(style_path):
            try:
                with open(style_path, 'r') as f:
                    style = f.read()
                    print(f"Stylesheet loaded successfully, length: {len(style)} characters")
                    self.setStyleSheet(style)
            except Exception as e:
                print(f"Error loading stylesheet: {e}")
        else:
            print("Stylesheet file not found")
    
    def setup_ui(self):
        """Initialize the main window UI components."""
        try:
            print("Setting up main UI...")
            
            # Create main content area
            self.content_widget = QWidget()
            self.content_widget.setObjectName("contentWidget")
            self.content_layout = QHBoxLayout(self.content_widget)
            self.content_layout.setContentsMargins(10, 0, 10, 10)
            self.content_layout.setSpacing(10)
            
            # Create video and controls container
            self.video_container = QWidget()
            self.video_layout = QVBoxLayout(self.video_container)
            self.video_layout.setContentsMargins(0, 0, 0, 0)
            self.video_layout.setSpacing(10)
            
            # Create video area
            self.video_widget = VideoWidget()
            self.video_widget.setObjectName("videoContainer")
            self.media_player.set_video_widget(self.video_widget)
            
            # Create control bar
            self.control_bar = ControlBar()
            
            # Create info panel (hidden by default)
            self.info_panel = self.create_info_panel()
            self.info_visible = False
            self.info_panel.hide()  # Hide by default
            
            # Add widgets to video container
            self.video_layout.addWidget(self.video_widget, 1)
            self.video_layout.addWidget(self.control_bar)
            
            # Create splitter for video and playlist
            self.splitter = QSplitter(Qt.Horizontal)
            
            # Create playlist
            self.playlist_widget = self.create_playlist()
            
            # Add widgets to splitter
            self.splitter.addWidget(self.video_container)
            self.splitter.addWidget(self.playlist_widget)
            self.splitter.setStretchFactor(0, 3)
            self.splitter.setStretchFactor(1, 1)
            
            # Add splitter to content layout
            self.content_layout.addWidget(self.splitter, 1)
            
            # Hide playlist by default
            self.playlist_visible = False
            self.toggle_playlist_visibility()
            
            # Add content to main layout
            self.main_layout.addWidget(self.content_widget, 1)
            
            print("UI setup completed")
            
        except Exception as e:
            print(f"Error setting up UI: {str(e)}")
            traceback.print_exc()
            raise
    
    def create_playlist(self):
        """Create the playlist widget."""
        playlist = QWidget()
        playlist.setObjectName("playlistPanel")
        playlist.setWindowFlags(Qt.Widget)  # Ensure it's just a widget, not a window
        layout = QVBoxLayout(playlist)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Playlist header - simplified without window controls
        header = QWidget()
        header.setObjectName("playlistHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 5, 15, 5)  # Adjusted margins
        
        title = QLabel("Playlist")
        title.setObjectName("playlistTitle")  # Changed from titleLabel to avoid conflicts
        
        search_btn = QPushButton("🔍")
        search_btn.setFlat(True)
        search_btn.setFixedSize(24, 24)
        search_btn.setObjectName("playlistSearchBtn")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(search_btn)
        
        # Playlist tools
        tools = QWidget()
        tools.setObjectName("playlistTools")
        tools_layout = QHBoxLayout(tools)
        tools_layout.setContentsMargins(10, 5, 10, 5)
        tools_layout.setSpacing(5)
        
        # Add tool buttons
        for icon in ["+", "-", "▶", "⏹", "⏭"]:
            btn = QPushButton(icon)
            btn.setFixedSize(24, 24)
            tools_layout.addWidget(btn)
        
        # Playlist content
        self.playlist = QListWidget()
        self.playlist.setObjectName("playlist")
        self.playlist.setAlternatingRowColors(True)
        self.playlist.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        
        # Add sample items
        for i in range(10):
            item = QListWidgetItem(f"Media File {i+1}.mp4")
            item.setData(Qt.UserRole, f"path/to/media_{i+1}.mp4")
            self.playlist.addItem(item)
        
        # Add widgets to layout
        layout.addWidget(header)
        layout.addWidget(tools)
        layout.addWidget(self.playlist)
        
        return playlist
    
    def create_info_panel(self):
        """Create the information panel."""
        panel = QWidget()
        panel.setObjectName("infoPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Tabs
        tabs = QWidget()
        tabs.setObjectName("infoTabs")
        tabs_layout = QHBoxLayout(tabs)
        tabs_layout.setContentsMargins(5, 5, 5, 5)
        tabs_layout.setSpacing(5)
        
        active_tab = QPushButton("Info")
        active_tab.setObjectName("activeTab")
        
        for tab in ["Format", "Audio", "Video", "Statistics"]:
            btn = QPushButton(tab)
            btn.setObjectName("inactiveTab")
            tabs_layout.addWidget(btn)
        
        tabs_layout.insertWidget(0, active_tab)
        
        # Info content
        self.info_content = QWidget()
        content_layout = QVBoxLayout(self.info_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # File info - will be updated when media is loaded
        self.media_info = {
            'file': ("File:", "No file loaded"),
            'size': ("Size:", "-"),
            'duration': ("Duration:", "-"),
            'format': ("Format:", "-"),
            'resolution': ("Resolution:", "-"),
            'fps': ("Frame rate:", "-"),
            'video_codec': ("Video codec:", "-"),
            'audio': ("Audio:", "-"),
            'bitrate': ("Bitrate:", "-"),
            'path': ("Path:", "-")
        }
        
        self.info_widgets = {}
        
        for key, (label, value) in self.media_info.items():
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            label_widget = QLabel(label)
            value_widget = QLabel(value)
            value_widget.setWordWrap(True)
            
            row_layout.addWidget(label_widget, 1)
            row_layout.addWidget(value_widget, 3)
            
            content_layout.addWidget(row)
            self.info_widgets[key] = value_widget
        
        content_layout.addStretch()
        
        # Add widgets to layout
        layout.addWidget(tabs)
        layout.addWidget(self.info_content, 1)
        
        # Connect media player signals
        if hasattr(self, 'media_player'):
            self.media_player.media_changed.connect(self.update_media_info)
            self.media_player.media_changed.connect(self.on_media_changed)
        
        return panel
        
    def on_media_changed(self, media_info):
        """Handle when media changes and update the UI accordingly."""
        # Update window title with media name if available
        title = media_info.get('title', 'OnaPlay')
        if title and title != 'OnaPlay':
            self.setWindowTitle(f"OnaPlay - {title}")
            
        # Update video aspect ratio if resolution is available
        if 'resolution' in media_info and 'x' in media_info['resolution']:
            try:
                width, height = map(int, media_info['resolution'].split('x'))
                self.video_widget.set_aspect_ratio(width, height)
            except (ValueError, AttributeError):
                pass  # Use default aspect ratio if resolution parsing fails
            
    def update_media_info(self, media_info):
        """Update the media information display."""
        if not hasattr(self, 'info_widgets') or not self.info_widgets:
            return
            
        # Update each field if it exists in the provided media_info
        for key, value_widget in self.info_widgets.items():
            if key in media_info and media_info[key]:
                value_widget.setText(str(media_info[key]))
        
        # Special handling for duration formatting
        if 'duration' in media_info and media_info['duration']:
            try:
                duration_sec = int(media_info['duration']) // 1000
                hours = duration_sec // 3600
                minutes = (duration_sec % 3600) // 60
                seconds = duration_sec % 60
                formatted_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.info_widgets['duration'].setText(formatted_duration)
            except (ValueError, TypeError):
                pass
                
        # Update status bar with basic media info
        if hasattr(self, 'status_bar'):
            status_text = []
            if 'resolution' in media_info:
                status_text.append(f"{media_info['resolution']}")
            if 'fps' in media_info and media_info['fps'] != '-':
                status_text.append(f"{media_info['fps']} fps")
            if 'audio' in media_info and media_info['audio'] != '-':
                status_text.append(media_info['audio'])
                
            if status_text:
                self.status_bar.show_message(" | ".join(status_text))
    
    def setup_menus(self):
        """Set up the application menus."""
        # Create File menu
        file_menu = self.menu_bar.addMenu("&File")
        
        # Add actions to File menu
        self.open_file_action = file_menu.addAction("&Open File...")
        self.open_file_action.setShortcut("Ctrl+O")
        self.open_url_action = file_menu.addAction("Open &URL...")
        self.open_url_action.setShortcut("Ctrl+U")
        file_menu.addSeparator()
        self.exit_action = file_menu.addAction("E&xit")
        self.exit_action.setShortcut("Alt+F4")
        
        # Create View menu
        view_menu = self.menu_bar.addMenu("&View")
        self.toggle_playlist_action = view_menu.addAction("Show &Playlist")
        self.toggle_playlist_action.setCheckable(True)
        self.toggle_playlist_action.setChecked(False)
        self.toggle_playlist_action.triggered.connect(self.toggle_playlist_visibility)
    
    def setup_connections(self):
        """Connect signals and slots."""
        try:
            print("Setting up connections...")
            
            # Connect control bar signals
            self.control_bar.play_pressed.connect(self.media_player.play_pause)
            self.control_bar.stop_pressed.connect(self.media_player.stop)
            self.control_bar.volume_changed.connect(self.media_player.set_volume)
            self.control_bar.seek_requested.connect(self.media_player.seek)
            self.control_bar.info_toggled.connect(self.toggle_info_panel)
            self.control_bar.playlist_toggled.connect(self.toggle_playlist_visibility)
            
            # Connect media player signals
            self.media_player.position_changed.connect(self.control_bar.update_position)
            self.media_player.duration_changed.connect(self.control_bar.set_duration)
            self.media_player.state_changed.connect(self.control_bar.update_play_button)
            
            # Connect playlist signals
            self.playlist.itemDoubleClicked.connect(self.playlist_item_double_clicked)
            
            # Connect menu actions
            self.open_file_action.triggered.connect(self.open_file)
            self.open_url_action.triggered.connect(self.open_url)
            self.exit_action.triggered.connect(self.close)
            
            print("Connections set up successfully")
            
        except Exception as e:
            print(f"Error setting up connections: {str(e)}")
            traceback.print_exc()
    
    def playlist_item_double_clicked(self, item):
        """Handle double click on playlist item."""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.media_player.load(file_path)
            self.media_player.play()
    
    def open_file(self):
        """Open a file dialog to select media files."""
        try:
            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setNameFilter("Media Files (*.mp4 *.avi *.mkv *.mp3 *.wav)")
            
            if file_dialog.exec_():
                file_paths = file_dialog.selectedFiles()
                if file_paths:
                    self.media_player.load(file_paths[0])
                    
                    # Add to playlist if not already there
                    for path in file_paths:
                        exists = False
                        for i in range(self.playlist.count()):
                            if self.playlist.item(i).data(Qt.UserRole) == path:
                                exists = True
                                break
                        
                        if not exists:
                            item = QListWidgetItem(os.path.basename(path))
                            item.setData(Qt.UserRole, path)
                            self.playlist.addItem(item)
        
        except Exception as e:
            print(f"Error opening file: {str(e)}")
            traceback.print_exc()
    
    def open_url(self):
        """Open a dialog to enter a media URL."""
        try:
            from PyQt5.QtWidgets import QInputDialog
            
            url, ok = QInputDialog.getText(
                self, 
                "Open URL", 
                "Enter media URL:", 
                text="https://"
            )
            
            if ok and url:
                self.media_player.load(url)
                
                # Add to playlist
                item = QListWidgetItem(url)
                item.setData(Qt.UserRole, url)
                self.playlist.addItem(item)
        
        except Exception as e:
            print(f"Error opening URL: {str(e)}")
            traceback.print_exc()
    
    def toggle_playlist_visibility(self):
        """Toggle the visibility of the playlist."""
        self.playlist_visible = not self.playlist_visible
        self.playlist_widget.setVisible(self.playlist_visible)
        self.toggle_playlist_action.setChecked(self.playlist_visible)
    
    def toggle_info_panel(self):
        """Toggle the visibility of the info panel."""
        self.info_visible = not self.info_visible
        if self.info_visible:
            self.info_panel.show()
            self.video_layout.addWidget(self.info_panel)
        else:
            self.info_panel.hide()
            self.info_panel.setParent(None)
        
        # Adjust splitter sizes when showing/hiding
        if self.playlist_visible:
            sizes = self.splitter.sizes()
            total = sum(sizes) if sizes else self.width()
            self.splitter.setSizes([int(total * 0.75), int(total * 0.25)])
    
    def closeEvent(self, event):
        """Handle window close event."""
        try:
            # Save window state
            # TODO: Save window geometry, playlist, etc.
            
            # Clean up resources
            self.media_player.cleanup()
            event.accept()
            
        except Exception as e:
            print(f"Error during close: {str(e)}")
            traceback.print_exc()
            event.accept()
    
    def eventFilter(self, obj, event):
        """Global event filter to handle key events."""
        if event.type() == QEvent.KeyPress:
            # Don't handle key events when a text input widget has focus
            if isinstance(obj, (QLineEdit, QComboBox)):
                return super().eventFilter(obj, event)
                
            key = event.key()
            
            # Space: Play/Pause
            if key == Qt.Key_Space and not isinstance(obj, QLineEdit):
                self.media_player.play_pause()
                return True
                
            # Left/Right arrows: Seek backward/forward 5 seconds
            if key == Qt.Key_Left and not isinstance(obj, (QLineEdit, QSpinBox, QComboBox)):
                self.media_player.seek(self.media_player.get_time() - 5000)  # Rewind 5s
                return True
            if key == Qt.Key_Right and not isinstance(obj, (QLineEdit, QSpinBox, QComboBox)):
                self.media_player.seek(self.media_player.get_time() + 5000)  # Forward 5s
                return True
                
            # Up/Down arrows: Volume up/down
            if key == Qt.Key_Up and not isinstance(obj, (QLineEdit, QSpinBox, QComboBox)):
                current_vol = self.media_player.get_volume()
                self.media_player.set_volume(min(100, current_vol + 5))
                return True
            if key == Qt.Key_Down and not isinstance(obj, (QLineEdit, QSpinBox, QComboBox)):
                current_vol = self.media_player.get_volume()
                self.media_player.set_volume(max(0, current_vol - 5))
                return True
                
            # F: Toggle fullscreen
            if key == Qt.Key_F and not isinstance(obj, QLineEdit):
                self.toggle_fullscreen()
                return True
                
            # M: Mute/unmute
            if key == Qt.Key_M and not isinstance(obj, QLineEdit):
                self.media_player.toggle_mute()
                return True
                
            # L: Toggle playlist
            if key == Qt.Key_L and not isinstance(obj, QLineEdit):
                self.toggle_playlist_visibility()
                return True
                
            # I: Toggle info panel
            if key == Qt.Key_I and not isinstance(obj, QLineEdit):
                self.toggle_info_panel()
                return True
                
            # Escape: Exit fullscreen
            if key == Qt.Key_Escape and self.isFullScreen():
                self.showNormal()
                return True
                
        # Let other events be handled normally
        return super().eventFilter(obj, event)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            # Restore normal window state
            self.showNormal()
            self.menuBar().show()
            self.title_bar.show()
            self.control_bar.set_fullscreen_mode(False)
            self.video_container.layout().setContentsMargins(0, 0, 0, 0)
            # Ensure control bar is visible when exiting fullscreen
            self.control_bar.show()
            self.control_bar.raise_()
        else:
            # Hide UI elements in fullscreen
            self.menuBar().hide()
            self.title_bar.hide()
            self.control_bar.set_fullscreen_mode(True)
            self.video_container.layout().setContentsMargins(0, 0, 0, 0)
            self.showFullScreen()
            # Show control bar when entering fullscreen
            self.control_bar.show()
            self.control_bar.raise_()
            self.control_bar._start_auto_hide_timer()
            
        # Update video widget geometry after toggling fullscreen
        QTimer.singleShot(100, self._update_video_geometry)
    
    def eventFilter(self, obj, event):
        """Global event filter to handle key events and mouse movements in fullscreen."""
        # Handle mouse movements in fullscreen
        if event.type() == QEvent.MouseMove and self.isFullScreen():
            # Show control bar if mouse is near the bottom of the screen
            mouse_pos = event.pos()
            if mouse_pos.y() >= self.height() - 100:  # 100px from bottom
                self.control_bar.show()
                self.control_bar.raise_()
                self.control_bar._start_auto_hide_timer()
            # Hide control bar if mouse is near the top of the screen
            elif mouse_pos.y() <= 20 and not self.control_bar.underMouse():
                self.control_bar.hide()
        
        # Handle key events
        if event.type() == QEvent.KeyPress:
            # Don't handle key events when a text input widget has focus
            if isinstance(obj, (QLineEdit, QComboBox, QSpinBox)):
                return super().eventFilter(obj, event)
            
            # Only process key events for the main window, video widget, or control bar
            if obj not in [self, self.video_widget, self.control_bar]:
                return super().eventFilter(obj, event)
            
            # Don't process key events with modifiers (like Ctrl+Left, etc.)
            if event.modifiers() != Qt.NoModifier:
                return super().eventFilter(obj, event)
                
            key = event.key()
            
            # Space: Play/Pause
            if key == Qt.Key_Space:
                self.media_player.play_pause()
                # Show control bar when using space to play/pause
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                return True
            
            # F key or F11: Toggle fullscreen
            if key in (Qt.Key_F, Qt.Key_F11):
                self.toggle_fullscreen()
                return True
                
            # Left/Right arrows: Seek backward/forward 5 seconds
            if key == Qt.Key_Left:
                self.media_player.seek(self.media_player.get_time() - 5000)  # Rewind 5s
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                event.accept()
                return True
                
            if key == Qt.Key_Right:
                self.media_player.seek(self.media_player.get_time() + 5000)  # Forward 5s
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                event.accept()
                return True
                
            # Up/Down arrows: Volume up/down
            if key == Qt.Key_Up:
                current_vol = self.media_player.get_volume()
                self.media_player.set_volume(min(100, current_vol + 5))
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                event.accept()
                return True
                
            if key == Qt.Key_Down:
                current_vol = self.media_player.get_volume()
                self.media_player.set_volume(max(0, current_vol - 5))
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                event.accept()
                return True
                
            # M key: Toggle mute
            if key == Qt.Key_M:
                self.media_player.toggle_mute()
                if self.isFullScreen():
                    self.control_bar.show()
                    self.control_bar.raise_()
                    self.control_bar._start_auto_hide_timer()
                return True
                
            # F: Toggle fullscreen
            if key == Qt.Key_F and not isinstance(obj, QLineEdit):
                self.toggle_fullscreen()
                return True
                
            # M: Mute/unmute
            if key == Qt.Key_M and not isinstance(obj, QLineEdit):
                self.media_player.toggle_mute()
                return True
                
            # L: Toggle playlist
            if key == Qt.Key_L and not isinstance(obj, QLineEdit):
                self.toggle_playlist_visibility()
                return True
                
            # I: Toggle info panel
            if key == Qt.Key_I and not isinstance(obj, QLineEdit):
                self.toggle_info_panel()
                return True
                
            # Escape: Exit fullscreen
            if key == Qt.Key_Escape and self.isFullScreen():
                self.showNormal()
                return True
        
        return super().eventFilter(obj, event)
    
    def _update_video_geometry(self):
        """Update video widget geometry to maintain aspect ratio."""
        if hasattr(self, 'video_widget'):
            self.video_widget.update_geometry()
    
    def resizeEvent(self, event):
        """Handle window resize event."""
        super().resizeEvent(event)
        self._update_video_geometry()
