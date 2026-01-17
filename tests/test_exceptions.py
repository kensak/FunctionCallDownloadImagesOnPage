"""Tests for exception classes."""
import pytest
from pathlib import Path
from DownloadImagesOnPage.exceptions import (
    ImageDownloaderError,
    FetchError,
    DownloadError,
    FileWriteError,
)


class TestImageDownloaderError:
    """Tests for ImageDownloaderError base exception."""
    
    def test_base_exception_is_exception(self):
        """ImageDownloaderError should inherit from Exception."""
        assert issubclass(ImageDownloaderError, Exception)
    
    def test_base_exception_can_be_raised(self):
        """ImageDownloaderError should be raisable."""
        with pytest.raises(ImageDownloaderError):
            raise ImageDownloaderError("Test error")
    
    def test_base_exception_message(self):
        """ImageDownloaderError should preserve error message."""
        message = "Something went wrong"
        error = ImageDownloaderError(message)
        assert str(error) == message


class TestFetchError:
    """Tests for FetchError exception."""
    
    def test_fetch_error_inherits_from_base(self):
        """FetchError should inherit from ImageDownloaderError."""
        assert issubclass(FetchError, ImageDownloaderError)
    
    def test_fetch_error_has_url_attribute(self):
        """FetchError should have url attribute."""
        url = "https://example.com/page"
        error = FetchError(url, status_code=404)
        assert error.url == url
    
    def test_fetch_error_has_status_code_attribute(self):
        """FetchError should have status_code attribute."""
        error = FetchError("https://example.com", status_code=500)
        assert error.status_code == 500
    
    def test_fetch_error_with_message(self):
        """FetchError should support custom message."""
        url = "https://example.com"
        status_code = 404
        message = "Page not found"
        error = FetchError(url, status_code, message=message)
        
        assert error.url == url
        assert error.status_code == status_code
        assert message in str(error)
    
    def test_fetch_error_default_message(self):
        """FetchError should have default message format."""
        url = "https://example.com/test"
        status_code = 403
        error = FetchError(url, status_code)
        
        error_str = str(error)
        assert url in error_str
        assert "403" in error_str
    
    def test_fetch_error_without_status_code(self):
        """FetchError should work with status_code=None for network errors."""
        url = "https://example.com"
        error = FetchError(url, status_code=None, message="Connection timeout")
        
        assert error.url == url
        assert error.status_code is None
        assert "timeout" in str(error).lower()
    
    def test_fetch_error_can_be_caught_as_base(self):
        """FetchError should be catchable as ImageDownloaderError."""
        with pytest.raises(ImageDownloaderError):
            raise FetchError("https://test.com", 500)


class TestDownloadError:
    """Tests for DownloadError exception."""
    
    def test_download_error_inherits_from_base(self):
        """DownloadError should inherit from ImageDownloaderError."""
        assert issubclass(DownloadError, ImageDownloaderError)
    
    def test_download_error_has_url_attribute(self):
        """DownloadError should have url attribute."""
        url = "https://example.com/image.jpg"
        error = DownloadError(url)
        assert error.url == url
    
    def test_download_error_with_message(self):
        """DownloadError should support custom message."""
        url = "https://example.com/image.jpg"
        message = "Failed to download image"
        error = DownloadError(url, message=message)
        
        assert error.url == url
        assert message in str(error)
    
    def test_download_error_default_message(self):
        """DownloadError should have default message format."""
        url = "https://example.com/test.png"
        error = DownloadError(url)
        
        error_str = str(error)
        assert url in error_str
    
    def test_download_error_with_status_code(self):
        """DownloadError should support optional status_code."""
        url = "https://example.com/missing.jpg"
        error = DownloadError(url, message="404 Not Found")
        
        assert error.url == url
        assert "404" in str(error)
    
    def test_download_error_can_be_caught_as_base(self):
        """DownloadError should be catchable as ImageDownloaderError."""
        with pytest.raises(ImageDownloaderError):
            raise DownloadError("https://test.com/img.jpg")


class TestFileWriteError:
    """Tests for FileWriteError exception."""
    
    def test_file_write_error_inherits_from_base(self):
        """FileWriteError should inherit from ImageDownloaderError."""
        assert issubclass(FileWriteError, ImageDownloaderError)
    
    def test_file_write_error_has_path_attribute(self):
        """FileWriteError should have path attribute."""
        path = Path("/tmp/images/test.jpg")
        error = FileWriteError(path)
        assert error.path == path
    
    def test_file_write_error_with_message(self):
        """FileWriteError should support custom message."""
        path = Path("/tmp/test.jpg")
        message = "Permission denied"
        error = FileWriteError(path, message=message)
        
        assert error.path == path
        assert message in str(error)
    
    def test_file_write_error_default_message(self):
        """FileWriteError should have default message format."""
        path = Path("/tmp/output/image.jpg")
        error = FileWriteError(path)
        
        error_str = str(error)
        assert str(path) in error_str
    
    def test_file_write_error_with_permission_error(self):
        """FileWriteError should work with permission errors."""
        path = Path("/root/forbidden.jpg")
        error = FileWriteError(path, message="Permission denied")
        
        assert error.path == path
        assert "permission" in str(error).lower()
    
    def test_file_write_error_with_disk_full(self):
        """FileWriteError should work with disk full errors."""
        path = Path("/mnt/full/image.jpg")
        error = FileWriteError(path, message="No space left on device")
        
        assert error.path == path
        assert "space" in str(error).lower()
    
    def test_file_write_error_can_be_caught_as_base(self):
        """FileWriteError should be catchable as ImageDownloaderError."""
        with pytest.raises(ImageDownloaderError):
            raise FileWriteError(Path("/tmp/test.jpg"))


class TestExceptionHierarchy:
    """Tests for exception class hierarchy."""
    
    def test_all_exceptions_inherit_from_base(self):
        """All custom exceptions should inherit from ImageDownloaderError."""
        exceptions = [FetchError, DownloadError, FileWriteError]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, ImageDownloaderError)
    
    def test_catch_all_with_base_exception(self):
        """Base exception should catch all custom exceptions."""
        exceptions_to_raise = [
            FetchError("http://test.com", 404),
            DownloadError("http://test.com/img.jpg"),
            FileWriteError(Path("/tmp/test.jpg")),
        ]
        
        for exc in exceptions_to_raise:
            with pytest.raises(ImageDownloaderError):
                raise exc
    
    def test_exceptions_are_distinct(self):
        """Each exception should be a distinct type."""
        fetch_error = FetchError("http://test.com", 500)
        download_error = DownloadError("http://test.com/img.jpg")
        file_error = FileWriteError(Path("/tmp/test.jpg"))
        
        assert type(fetch_error) != type(download_error)
        assert type(download_error) != type(file_error)
        assert type(fetch_error) != type(file_error)
