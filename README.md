# OnaPlay - A Modern Media Player

OnaPlay is a feature-rich, cross-platform media player built with Python and PyQt5, using VLC for robust media playback. It offers a sleek, modern interface with powerful playback controls and customization options.

## Features

- 🎬 **Wide Format Support**: Play virtually any video and audio format (powered by VLC)
- 🎨 **Modern UI**: Clean, dark-themed interface with intuitive controls
- 🎛️ **Advanced Playback**: Smooth seeking, frame-stepping, and playback speed control
- 🎚️ **Audio Controls**: Volume control, mute, and audio track selection
- ⏭️ **Playlist Management**: Create and manage playlists with drag-and-drop support
- ⌨️ **Keyboard Shortcuts**: Comprehensive keyboard controls for all functions
- 🖥️ **Fullscreen Mode**: Immersive viewing with auto-hiding controls
- 🔄 **Recent Files**: Quick access to recently played media
- 🎞️ **Thumbnail Previews**: Hover over timeline to see preview thumbnails

## Requirements

- Python 3.8 or higher
- VLC media player 3.0 or higher (for VLC Python bindings)
- PyQt5 5.15.0 or higher
- python-vlc 3.0.0 or higher
- Additional dependencies listed in `requirements.txt`

## Installation

### Windows
1. Install [VLC media player](https://www.videolan.org/vlc/)
2. Install Python 3.8+ from [python.org](https://www.python.org/downloads/)
3. Clone the repository:
   ```bash
   git clone https://github.com/zikani/onaplay.git
   cd onaplay
   ```
4. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install VLC and Python
brew install vlc python

# Clone and install
pip install -r requirements.txt
```

### Linux (Debian/Ubuntu)
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip python3-pyqt5 vlc

# Clone and install
pip install -r requirements.txt
```

## Usage

Start the application:
```bash
python main.py
```

### Opening Media
- **File Menu**: Select File > Open to browse for media files
- **Drag & Drop**: Drag files directly onto the player window
- **Command Line**: `python main.py path/to/your/media.mp4`

### Keyboard Shortcuts

#### Playback Controls
- **Space**: Play/Pause
- **S**: Stop
- **F**: Toggle fullscreen (also F11)
- **M**: Mute/Unmute
- **Ctrl+O**: Open file
- **Ctrl+Q**: Quit application

#### Navigation
- **Left/Right Arrows**: Seek -5/+5 seconds
- **Up/Down Arrows**: Volume up/down
- **Ctrl+Left/Right**: Skip to previous/next track
- **Home/End**: Jump to start/end of media

#### Playback Speed
- **+/-**: Increase/decrease playback speed
- **R**: Reset playback speed to 1.0x

### Mouse Controls
- **Double-click**: Toggle fullscreen
- **Wheel up/down**: Volume control
- **Click timeline**: Seek to position
- **Right-click**: Show context menu
- **Ctrl+U**: Open URL
- **Ctrl+Q**: Quit

## Project Structure

```
onaplay/
├── main.py                     # Application entry point
├── requirements.txt            # Project dependencies
├── README.md                   # This file
├── assets/                     # Static resources
│   ├── icons/                  # UI icons
│   └── styles/                 # QSS style sheets
└── src/                        # Source code
    ├── ui/                     # User interface components
    │   ├── main_window.py      # Main application window
    │   ├── video_widget.py     # Video display widget
    │   ├── control_bar.py      # Playback controls
    │   └── ...
    ├── core/                   # Core functionality
    │   ├── media_player.py     # Media playback engine (VLC wrapper)
    │   └── ...
    └── utils/                  # Utility functions
        ├── file_utils.py       # File operations
        └── ...
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

Please ensure your code follows the project's style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with ❤️ using Python, PyQt5, and VLC
- Inspired by vlc and other great media players
- Thanks to all contributors who helped improve this project
