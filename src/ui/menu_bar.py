from PyQt5.QtWidgets import QMenuBar, QMenu, QAction
from PyQt5.QtGui import QKeySequence

class MenuBar(QMenuBar):
    """Main menu bar for the application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the menu bar."""
        # File menu
        file_menu = self.addMenu("&File")
        
        self.open_file_action = QAction("&Open File...", self)
        self.open_file_action.setShortcut(QKeySequence.Open)
        
        self.open_url_action = QAction("Open &URL...", self)
        self.open_url_action.setShortcut("Ctrl+U")
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        
        file_menu.addAction(self.open_file_action)
        file_menu.addAction(self.open_url_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Playback menu
        playback_menu = self.addMenu("&Playback")
        
        self.play_action = QAction("&Play/Pause", self)
        self.play_action.setShortcut("Space")
        
        self.stop_action = QAction("&Stop", self)
        self.stop_action.setShortcut("S")
        
        playback_menu.addAction(self.play_action)
        playback_menu.addAction(self.stop_action)
        
        # View menu
        view_menu = self.addMenu("&View")
        
        self.fullscreen_action = QAction("&Fullscreen", self)
        self.fullscreen_action.setShortcut("F11")
        
        view_menu.addAction(self.fullscreen_action)
        
        # Help menu
        help_menu = self.addMenu("&Help")
        
        self.about_action = QAction("&About", self)
        self.shortcuts_action = QAction("Keyboard &Shortcuts", self)
        
        help_menu.addAction(self.about_action)
        help_menu.addAction(self.shortcuts_action)
