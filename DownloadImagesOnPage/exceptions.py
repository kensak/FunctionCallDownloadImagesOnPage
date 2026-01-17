"""Exception classes for image downloader.

This module defines a hierarchy of custom exceptions used throughout the application.
All exceptions inherit from the base ImageDownloaderError class, allowing for
convenient catch-all error handling while still maintaining specific error types.

Exception Hierarchy:
    ImageDownloaderError (base)
    ├── FetchError (HTML fetch failures)
    ├── DownloadError (image download failures)
    └── FileWriteError (file write failures)
"""
from pathlib import Path
from typing import Optional


class ImageDownloaderError(Exception):
    """基底例外クラス - すべてのダウンローダー例外の親クラス.
    
    This is the base class for all custom exceptions in the image downloader.
    Use this for catch-all error handling when you want to catch any
    application-specific error.
    
    Example:
        try:
            # Some operation
            pass
        except ImageDownloaderError as e:
            # Handle any downloader-related error
            print(f"Error: {e}")
    """
    pass


class FetchError(ImageDownloaderError):
    """HTML取得エラー.
    
    Raised when fetching HTML content from a URL fails. This can be due to
    HTTP errors (404, 500, etc.) or network errors (timeout, DNS failure, etc.).
    
    Attributes:
        url: 取得に失敗したURL
        status_code: HTTPステータスコード（ネットワークエラーの場合はNone）
        message: エラーメッセージ
    
    Example:
        raise FetchError("https://example.com", 404)
        raise FetchError("https://example.com", None, message="Connection timeout")
    """
    
    def __init__(
        self,
        url: str,
        status_code: Optional[int],
        message: Optional[str] = None
    ):
        """Initialize FetchError.
        
        Args:
            url: 取得に失敗したURL
            status_code: HTTPステータスコード（ネットワークエラーの場合はNone）
            message: カスタムエラーメッセージ（省略時は自動生成）
        """
        self.url = url
        self.status_code = status_code
        
        if message:
            self.message = message
        elif status_code is not None:
            self.message = f"Failed to fetch HTML from {url} (HTTP {status_code})"
        else:
            self.message = f"Failed to fetch HTML from {url} (Network error)"
        
        super().__init__(self.message)


class DownloadError(ImageDownloaderError):
    """画像ダウンロードエラー.
    
    Raised when downloading an image from a URL fails. This can be due to
    HTTP errors, network issues, or invalid image data.
    
    Attributes:
        url: ダウンロードに失敗した画像URL
        status_code: HTTPステータスコード（ネットワークエラーの場合はNone）
        message: エラーメッセージ
    
    Example:
        raise DownloadError("https://example.com/image.jpg", status_code=404)
        raise DownloadError("https://example.com/image.jpg", message="Connection timeout")
    """
    
    def __init__(
        self,
        url: str,
        status_code: Optional[int] = None,
        message: Optional[str] = None
    ):
        """Initialize DownloadError.
        
        Args:
            url: ダウンロードに失敗した画像URL
            status_code: HTTPステータスコード（ネットワークエラーの場合はNone）
            message: カスタムエラーメッセージ（省略時は自動生成）
        """
        self.url = url
        self.status_code = status_code
        
        if message:
            self.message = message
        elif status_code is not None:
            self.message = f"Failed to download image from {url} (HTTP {status_code})"
        else:
            self.message = f"Failed to download image from {url} (Network error)"
        
        super().__init__(self.message)


class FileWriteError(ImageDownloaderError):
    """ファイル書き込みエラー.
    
    Raised when writing a file to disk fails. This can be due to permission
    errors, disk full errors, or invalid file paths.
    
    Attributes:
        path: 書き込みに失敗したファイルパス
        message: エラーメッセージ
    
    Example:
        raise FileWriteError(Path("/tmp/image.jpg"))
        raise FileWriteError(Path("/root/image.jpg"), message="Permission denied")
    """
    
    def __init__(self, path: Path, message: Optional[str] = None):
        """Initialize FileWriteError.
        
        Args:
            path: 書き込みに失敗したファイルパス
            message: カスタムエラーメッセージ（省略時は自動生成）
        """
        self.path = path
        
        if message:
            self.message = message
        else:
            self.message = f"Failed to write file to {path}"
        
        super().__init__(self.message)
