import os
from pathlib import Path

def get_asset_path(relative_path):
    """
    Get the absolute path to an asset file.
    
    Args:
        relative_path (str): Relative path from the assets directory
        
    Returns:
        str: Absolute path to the asset file
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Navigate up to the project root and then to the assets directory
    assets_dir = os.path.join(current_dir, "..", "..", "assets")
    return os.path.join(assets_dir, relative_path)

def is_supported_media_file(file_path):
    """
    Check if a file has a supported media extension.
    
    Args:
        file_path (str): Path to the file to check
        
    Returns:
        bool: True if the file has a supported extension, False otherwise
    """
    supported_extensions = {
        # Video formats
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v',
        # Audio formats
        '.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma'
    }
    
    _, ext = os.path.splitext(file_path)
    return ext.lower() in supported_extensions

def get_file_info(file_path):
    """
    Get basic information about a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        dict: Dictionary containing file information (size, modification time, etc.)
    """
    if not os.path.exists(file_path):
        return None
        
    file_stat = os.stat(file_path)
    
    return {
        'path': file_path,
        'name': os.path.basename(file_path),
        'size': file_stat.st_size,
        'created': file_stat.st_ctime,
        'modified': file_stat.st_mtime,
        'is_dir': os.path.isdir(file_path)
    }
