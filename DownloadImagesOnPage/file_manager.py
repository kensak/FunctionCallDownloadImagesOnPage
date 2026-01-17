"""File manager module.

This module provides functionality for file system operations including
directory management, unique filename generation, and file writing.
"""
from pathlib import Path
from io import BytesIO

from .exceptions import FileWriteError


def ensure_directory(directory: Path) -> None:
    """Ensure directory exists, creating it if necessary.
    
    Args:
        directory: Directory path to ensure exists
        
    Raises:
        FileWriteError: If directory creation fails due to permission error,
                       OSError, or if path exists as a file
    """
    try:
        # Check if path exists as a file (not directory)
        if directory.exists() and not directory.is_dir():
            raise FileWriteError(
                path=directory,
                message=f"Path exists as a file, not a directory: {directory}"
            )
        
        # Create directory with parents if needed
        directory.mkdir(parents=True, exist_ok=True)
        
    except PermissionError as e:
        raise FileWriteError(
            path=directory,
            message=f"Permission denied creating directory: {directory} - {e}"
        )
    except OSError as e:
        # Check if it's because the path exists as a file
        if directory.exists() and not directory.is_dir():
            raise FileWriteError(
                path=directory,
                message=f"Path exists as a file, not a directory: {directory}"
            )
        raise FileWriteError(
            path=directory,
            message=f"Failed to create directory: {directory} - {e}"
        )


def generate_unique_filename(directory: Path, filename: str) -> Path:
    """Generate unique filename in directory, avoiding conflicts.
    
    If a file with the given name already exists, appends a numeric suffix
    (_1, _2, _3, etc.) to make it unique. Preserves the file extension.
    
    Args:
        directory: Directory where file will be saved
        filename: Original filename
        
    Returns:
        Path object with unique filename (may have numeric suffix if needed)
    """
    file_path = directory / filename
    
    # If no conflict, return original path
    if not file_path.exists():
        return file_path
    
    # Extract stem (name without extension) and suffix (extension)
    stem = file_path.stem
    suffix = file_path.suffix
    
    # Try numbered suffixes until we find one that doesn't exist
    counter = 1
    while True:
        new_filename = f"{stem}_{counter}{suffix}"
        new_path = directory / new_filename
        
        if not new_path.exists():
            return new_path
        
        counter += 1


def save_image(image_data: BytesIO, file_path: Path) -> None:
    """Save image data to file.
    
    Args:
        image_data: BytesIO stream containing image data
        file_path: Path where file should be saved
        
    Raises:
        FileWriteError: If file write fails due to permission error,
                       OSError, or IOError
    """
    try:
        # Get all bytes from BytesIO stream
        image_bytes = image_data.getvalue()
        
        # Write bytes to file
        file_path.write_bytes(image_bytes)
        
    except PermissionError as e:
        raise FileWriteError(
            path=file_path,
            message=f"Permission denied writing file: {file_path} - {e}"
        )
    except IOError as e:
        raise FileWriteError(
            path=file_path,
            message=f"I/O error writing file: {file_path} - {e}"
        )
    except OSError as e:
        raise FileWriteError(
            path=file_path,
            message=f"Failed to write file: {file_path} - {e}"
        )


