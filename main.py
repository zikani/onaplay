import sys
import os
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow
from src.core.media_player import MediaPlayer
from src.utils.file_utils import get_asset_path

def show_splash_screen():
    """Show a splash screen while the application is loading."""
    splash_pix = QPixmap(get_asset_path("images/splash.png"))
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    QApplication.processEvents()
    return splash

def setup_application():
    """Set up the QApplication with the correct settings."""
    try:
        # Enable high DPI scaling
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("OnaPlay")
        app.setApplicationDisplayName("OnaPlay")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("OnaPlay")
        
        # Set application icon
        icon_path = r"C:\Users\goon\Documents\New folder (10)\onaplay\assets\icons\app_icon.ico"
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")
            # Try alternative paths
            alt_paths = [
                r"C:\Users\goon\Documents\New folder (10)\onaplay\assets\icons\app_icon_256.png",
                r"C:\Users\goon\Documents\New folder (10)\onaplay\assets\icons\app_icon_128.png",
                r"C:\Users\goon\Documents\New folder (10)\onaplay\assets\icons\app_icon_64.png",
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    app.setWindowIcon(QIcon(path))
                    print(f"Using alternative icon: {path}")
                    break
        
        # Set application style
        app.setStyle("Fusion")
        
        # Load and apply stylesheet
        style_path = r"C:\Users\goon\Documents\New folder (10)\onaplay\assets\styles\dark_theme.qss"
        if os.path.exists(style_path):
            try:
                with open(style_path, "r") as f:
                    app.setStyleSheet(f.read())
            except Exception as e:
                print(f"Error loading stylesheet: {e}")
        else:
            print(f"Stylesheet not found at {style_path}")
        
        return app
    except Exception as e:
        print(f"Error in setup_application: {e}")
        raise

def handle_exception(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions with a user-friendly message."""
    # Format the error message
    error_msg = f"""
    An unhandled exception occurred:
    
    Type: {exc_type.__name__}
    Message: {str(exc_value)}
    
    Traceback:
    {''.join(traceback.format_tb(exc_traceback))}
    """
    
    # Print to console
    print(error_msg, file=sys.stderr)
    
    # Show error dialog if possible
    app = QApplication.instance()
    if app and QApplication.startingUp() == False and QApplication.topLevelWidgets():
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
            "The application may not function correctly.\n"
            "Please check the console for more details."
        )
    
    return True  # Prevent default exception hook

def main():
    """Main application entry point."""
    # Set up exception handling first
    sys.excepthook = handle_exception
    
    try:
        print("Starting OnaPlay...")
        
        # Set up and show splash screen
        app = setup_application()
        splash = show_splash_screen()
        
        # Create main window
        window = MainWindow()
        
        # Close splash and show main window
        splash.finish(window)
        
        # Ensure window is properly shown and focused
        window.setWindowState(Qt.WindowActive)
        window.show()
        window.raise_()
        window.activateWindow()
        window.setFocus()
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            file_path = sys.argv[1]
            if os.path.exists(file_path):
                window.open_file(file_path)
        
        print("Application started successfully")
        
        # Run application
        sys.exit(app.exec_())
        
    except Exception as e:
        handle_exception(type(e), e, e.__traceback__)
        return 1

if __name__ == "__main__":
    main()
