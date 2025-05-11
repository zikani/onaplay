import os
import vlc
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, QUrl
from PyQt5.QtWidgets import QApplication

from src.utils.file_utils import get_asset_path

class MediaPlayer(QObject):
    """
    Media player using VLC backend with enhanced features and UI integration.
    """
    
    # Signals
    position_changed = pyqtSignal(int, int)    # position, duration
    duration_changed = pyqtSignal(int)          # duration
    state_changed = pyqtSignal(bool)            # is_playing
    media_changed = pyqtSignal(dict)            # media information dict
    error_occurred = pyqtSignal(str)            # error_message
    volume_changed = pyqtSignal(int)            # volume (0-100)
    playback_finished = pyqtSignal()           # when media finishes playing
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create VLC instance with optimizations
        vlc_args = [
            '--no-xlib',  # No Xlib support (faster on Linux)
            '--no-video-title-show',  # Don't show video title on top of the video
            '--quiet',  # No console output
            '--no-stats',  # No statistics
            '--no-video-on-top',  # Don't force video on top
        ]
        
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        
        # Current media info
        self.current_media = None
        self._volume = 75  # Default volume
        self._is_muted = False
        self._last_volume = self._volume
        
        # Setup timer for position updates
        self.timer = QTimer(self)
        self.timer.setInterval(200)  # Update every 200ms
        self.timer.timeout.connect(self.update_position)
        
        # Connect VLC events
        self.event_manager = self.player.event_manager()
        self.setup_vlc_events()
        
        # Set initial volume
        self.set_volume(self._volume)
    
    def setup_vlc_events(self):
        """Connect VLC event callbacks."""
        events = [
            (vlc.EventType.MediaPlayerTimeChanged, self.on_time_changed),
            (vlc.EventType.MediaPlayerPositionChanged, self.on_position_changed),
            (vlc.EventType.MediaPlayerLengthChanged, self.on_length_changed),
            (vlc.EventType.MediaPlayerPlaying, self.on_playing),
            (vlc.EventType.MediaPlayerPaused, self.on_paused),
            (vlc.EventType.MediaPlayerStopped, self.on_stopped),
            (vlc.EventType.MediaPlayerEndReached, self.on_ended),
            (vlc.EventType.MediaPlayerEncounteredError, self.on_error),
            (vlc.EventType.MediaPlayerVout, self.on_vout),
        ]
        
        for event_type, callback in events:
            try:
                self.event_manager.event_attach(event_type, callback)
            except Exception as e:
                print(f"Failed to attach event {event_type}: {e}")
    
    def cleanup(self):
        """Clean up resources."""
        self.timer.stop()
        self.stop()
        self.player.release()
        self.instance.release()
    
    def set_video_widget(self, video_widget):
        """
        Set the video widget for the player.
        
        Args:
            video_widget: QWidget or similar object with winId() method
        """
        if video_widget is None:
            return
            
        try:
            if hasattr(video_widget, 'winId'):
                # Windows
                self.player.set_hwnd(int(video_widget.winId()))
            elif hasattr(video_widget, 'window'):
                # Linux/Unix with X11
                self.player.set_xwindow(video_widget.window().winId())
            else:
                print("Unsupported video widget type")
        except Exception as e:
            self.error_occurred.emit(f"Failed to set video widget: {str(e)}")
    
    def load(self, media_path):
        """
        Load a media file or URL.
        
        Args:
            media_path: Path to media file or URL
        """
        if not media_path:
            return
            
        try:
            self.stop()
            
            # Convert to file URI if it's a local file
            if os.path.exists(media_path):
                media_path = QUrl.fromLocalFile(media_path).toString()
            
            # Create and configure media
            media = self.instance.media_new(media_path)
            media.parse_with_options(vlc.MediaParseFlag.network, 0)
            
            # Set media
            self.player.set_media(media)
            self.current_media = media_path
            
            # Start playback
            if self.player.play() == -1:
                raise Exception("Failed to play media")
                
            # Wait a moment for media to start and get metadata
            QApplication.processEvents()
            
            # Get and emit media info
            media_info = self.get_media_info()
            self.media_changed.emit(media_info)
            
            self.timer.start()
            
        except Exception as e:
            error_msg = f"Failed to load media: {str(e)}"
            self.error_occurred.emit(error_msg)
            print(error_msg)
    
    def get_media_info(self):
        """Get detailed information about the current media."""
        if not self.current_media:
            return {}
            
        media = self.player.get_media()
        if not media:
            return {}
            
        # Get basic file info
        file_path = self.current_media
        if file_path.startswith('file://'):
            file_path = QUrl(file_path).toLocalFile()
            
        file_size = 0
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            
        # Get media tracks info
        media.parse()
        tracks = media.tracks_get()
        
        video_track = None
        audio_track = None
        
        for track in tracks:
            if track.contents.i_codec == vlc.FourCC('h264') or track.contents.i_codec == vlc.FourCC('avc1'):
                video_track = track
            elif track.contents.i_codec in [vlc.FourCC('mp4a'), vlc.FourCC('aac ')]:
                audio_track = track
        
        # Format file size
        def format_size(size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} TB"
            
        # Get resolution if video track exists
        resolution = "-"
        fps = "-"
        if video_track:
            width = video_track.contents.u.video.i_width
            height = video_track.contents.u.video.i_height
            resolution = f"{width}×{height}"
            fps_num = video_track.contents.u.video.i_frame_rate_num
            fps_den = video_track.contents.u.video.i_frame_rate_den
            if fps_den > 0:
                fps = f"{fps_num / fps_den:.2f}"
        
        # Get audio info if audio track exists
        audio_info = "-"
        if audio_track:
            channels = audio_track.contents.audio.i_channels
            rate = audio_track.contents.audio.i_rate // 1000  # Convert to kHz
            audio_info = f"{channels} channels, {rate} kHz"
        
        # Get codec info
        video_codec = "-"
        if video_track:
            codec_name = vlc.fourcc_get_string(video_track.contents.i_codec) or "Unknown"
            video_codec = f"{codec_name} ({video_track.contents.i_codec:08x})"
        
        info = {
            'file': os.path.basename(file_path),
            'path': file_path,
            'size': format_size(file_size) if file_size > 0 else "-",
            'duration': self.player.get_length(),
            'format': media.get_mrl().split('.')[-1].upper() if '.' in media.get_mrl() else "-",
            'resolution': resolution,
            'fps': fps,
            'video_codec': video_codec,
            'audio': audio_info,
            'bitrate': f"{media.get_mrl()}",  # This is a placeholder, VLC doesn't expose bitrate directly
            'title': media.get_meta(vlc.Meta.Title) or os.path.basename(file_path),
            'artist': media.get_meta(vlc.Meta.Artist) or 'Unknown',
            'album': media.get_meta(vlc.Meta.Album) or 'Unknown',
            'genre': media.get_meta(vlc.Meta.Genre) or 'Unknown',
        }
        
        return info
    
    def play_pause(self):
        """Toggle between play and pause."""
        if not self.player.get_media():
            return
            
        if self.player.is_playing():
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start or resume playback."""
        if not self.player.get_media():
            return
            
        if self.player.play() == -1:
            self.error_occurred.emit("Failed to start playback")
            return
            
        self.timer.start()
    
    def pause(self):
        """Pause playback."""
        self.player.pause()
    
    def stop(self):
        """Stop playback and reset position."""
        self.player.stop()
        self.timer.stop()
        self.position_changed.emit(0, 0)
    
    def seek(self, position):
        """
        Seek to a specific position in the media.
        
        Args:
            position (int): Position in milliseconds
        """
        if not self.player.get_media():
            return
            
        duration = self.player.get_length()
        if duration <= 0:
            return
            
        # Ensure position is within bounds
        position = max(0, min(position, duration))
        self.player.set_time(position)
    
    def seek_relative(self, offset_ms):
        """Seek relative to current position."""
        if not self.player.get_media():
            return
            
        current = self.player.get_time()
        duration = self.player.get_length()
        new_pos = max(0, min(current + offset_ms, duration))
        self.seek(new_pos)
    
    # Volume control methods
    def set_volume(self, volume):
        """
        Set the volume level.
        
        Args:
            volume (int): Volume level (0-100)
        """
        volume = max(0, min(100, volume))
        self._volume = volume
        
        if not self._is_muted:
            self.player.audio_set_volume(volume)
            self.volume_changed.emit(volume)
    
    def get_volume(self):
        """Get the current volume level (0-100)."""
        return self._volume
    
    def mute(self, mute=True):
        """Mute or unmute the audio."""
        if mute and not self._is_muted:
            self._last_volume = self._volume
            self.player.audio_set_volume(0)
            self._is_muted = True
        elif not mute and self._is_muted:
            self.player.audio_set_volume(self._last_volume)
            self._volume = self._last_volume
            self._is_muted = False
            self.volume_changed.emit(self._volume)
    
    def toggle_mute(self):
        """Toggle mute state."""
        self.mute(not self._is_muted)
    
    # Playback information
    def get_time(self):
        """Get current position in milliseconds."""
        return self.player.get_time()
    
    def get_duration(self):
        """Get total duration in milliseconds."""
        return self.player.get_length()
    
    def is_playing(self):
        """Check if media is currently playing."""
        return self.player.is_playing()
    
    # Timer callback
    def update_position(self):
        """Update position and duration through signals."""
        if not self.player.get_media():
            return
            
        position = self.player.get_time()
        duration = self.player.get_length()
        
        if position < 0 or duration <= 0:
            return
            
        self.position_changed.emit(position, duration)
    
    # VLC event handlers
    def on_time_changed(self, event):
        """Handle time change event from VLC."""
        QApplication.processEvents()
    
    def on_position_changed(self, event):
        """Handle position change event from VLC."""
        pass
    
    def on_length_changed(self, event):
        """Handle duration change event from VLC."""
        duration = self.player.get_length()
        if duration > 0:
            self.duration_changed.emit(duration)
    
    def on_playing(self, event):
        """Handle playback started event."""
        self.state_changed.emit(True)
        
        # Emit duration when playback starts
        duration = self.player.get_length()
        if duration > 0:
            self.duration_changed.emit(duration)
    
    def on_paused(self, event):
        """Handle playback paused event."""
        self.state_changed.emit(False)
    
    def on_stopped(self, event):
        """Handle playback stopped event."""
        self.timer.stop()
        self.state_changed.emit(False)
    
    def on_ended(self, event):
        """Handle playback finished event."""
        self.timer.stop()
        self.state_changed.emit(False)
        self.playback_finished.emit()
    
    def on_error(self, event):
        """Handle playback error event."""
        error_msg = "An error occurred during playback"
        self.error_occurred.emit(error_msg)
        print(f"VLC Error: {error_msg}")
    
    def on_vout(self, event):
        """Handle video output event."""
        pass
