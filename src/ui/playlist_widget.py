from PyQt5.QtWidgets import (
    QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os

class PlaylistWidget(QWidget):
    """Playlist widget for managing media files."""
    
    # Signals
    item_double_clicked = pyqtSignal(str)  # Emitted when an item is double-clicked
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the playlist UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create playlist view
        self.playlist_view = QListWidget()
        self.playlist_view.setAlternatingRowColors(True)
        self.playlist_view.setSelectionMode(QListWidget.SingleSelection)
        self.playlist_view.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.playlist_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.playlist_view.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.playlist_view)
    
    def add_media(self, file_path):
        """Add a media file to the playlist."""
        if not os.path.exists(file_path):
            return
            
        item = QListWidgetItem(os.path.basename(file_path))
        item.setData(Qt.UserRole, file_path)  # Store full path
        self.playlist_view.addItem(item)
    
    def add_media_list(self, file_paths):
        """Add multiple media files to the playlist."""
        for file_path in file_paths:
            self.add_media(file_path)
    
    def clear_playlist(self):
        """Clear the playlist."""
        self.playlist_view.clear()
    
    def get_current_media(self):
        """Get the currently selected media file path."""
        current_item = self.playlist_view.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def on_item_double_clicked(self, item):
        """Handle double-click on playlist item."""
        file_path = item.data(Qt.UserRole)
        self.item_double_clicked.emit(file_path)
    
    def show_context_menu(self, position):
        """Show context menu for playlist items."""
        menu = QMenu()
        
        remove_action = QAction("Remove from playlist", self)
        remove_action.triggered.connect(self.remove_selected_item)
        
        clear_action = QAction("Clear playlist", self)
        clear_action.triggered.connect(self.clear_playlist)
        
        menu.addAction(remove_action)
        menu.addSeparator()
        menu.addAction(clear_action)
        
        menu.exec_(self.playlist_view.viewport().mapToGlobal(position))
    
    def remove_selected_item(self):
        """Remove the currently selected item from the playlist."""
        current_row = self.playlist_view.currentRow()
        if current_row >= 0:
            self.playlist_view.takeItem(current_row)
