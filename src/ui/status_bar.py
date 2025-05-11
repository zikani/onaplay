from PyQt5.QtWidgets import QStatusBar, QLabel

class StatusBar(QStatusBar):
    """Status bar for displaying messages and status information."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the status bar."""
        # Create status labels
        self.status_label = QLabel("Ready")
        self.media_info_label = QLabel("")
        self.media_info_label.setVisible(False)
        
        # Add permanent widgets to the right
        self.addPermanentWidget(self.media_info_label)
        
        # Add main status label
        self.addWidget(self.status_label)
    
    def show_message(self, message, timeout=3000):
        """Show a temporary status message."""
        self.showMessage(message, timeout)
    
    def set_media_info(self, info_text):
        """Set media information text (e.g., codec, resolution)."""
        if info_text:
            self.media_info_label.setText(info_text)
            self.media_info_label.setVisible(True)
        else:
            self.media_info_label.setVisible(False)
    
    def clear_media_info(self):
        """Clear media information."""
        self.media_info_label.clear()
        self.media_info_label.setVisible(False)
