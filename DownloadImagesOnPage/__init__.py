"""Image Downloader - Download all images from a webpage."""

from .models import (
    CLIConfig,
    ImageDimensions,
    DownloadStatus,
    ImageDownloadRecord,
    DownloadResult,
)
from .exceptions import (
    ImageDownloaderError,
    FetchError,
    DownloadError,
    FileWriteError,
)
from .cli import parse_arguments

__version__ = "0.1.0"

__all__ = [
    "CLIConfig",
    "ImageDimensions",
    "DownloadStatus",
    "ImageDownloadRecord",
    "DownloadResult",
    "ImageDownloaderError",
    "FetchError",
    "DownloadError",
    "FileWriteError",
    "parse_arguments",
]
