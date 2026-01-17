"""Tests for image downloader module."""
import pytest
from unittest.mock import Mock, patch
from io import BytesIO
import requests

from DownloadImagesOnPage.downloader import download_image
from DownloadImagesOnPage.exceptions import DownloadError


class TestDownloadImageSuccess:
    """Tests for successful image downloads."""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_returns_bytesio(self, mock_get):
        """Should return BytesIO stream with image data."""
        mock_response = Mock()
        mock_response.content = b"fake image data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        assert isinstance(result, BytesIO)
        assert result.read() == b"fake image data"
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_calls_requests_get(self, mock_get):
        """Should call requests.get with correct URL."""
        mock_response = Mock()
        mock_response.content = b"data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        download_image("https://example.com/photo.png")
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://example.com/photo.png"
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_uses_default_timeout(self, mock_get):
        """Should use default timeout of 10 seconds."""
        mock_response = Mock()
        mock_response.content = b"data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        download_image("https://example.com/image.jpg")
        
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == 10
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_uses_custom_timeout(self, mock_get):
        """Should use custom timeout when provided."""
        mock_response = Mock()
        mock_response.content = b"data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        download_image("https://example.com/image.jpg", timeout=30)
        
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == 30
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_checks_status_code(self, mock_get):
        """Should call raise_for_status to check HTTP status."""
        mock_response = Mock()
        mock_response.content = b"data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        download_image("https://example.com/image.jpg")
        
        mock_response.raise_for_status.assert_called_once()


class TestDownloadImageHttpErrors:
    """Tests for HTTP error handling."""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_404(self, mock_get):
        """Should raise DownloadError on 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        http_error = requests.HTTPError("404 Not Found")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/notfound.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/notfound.jpg"
        assert error.status_code == 404
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_500(self, mock_get):
        """Should raise DownloadError on 500 Internal Server Error."""
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = requests.HTTPError("500 Internal Server Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/image.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/image.jpg"
        assert error.status_code == 500
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_403(self, mock_get):
        """Should raise DownloadError on 403 Forbidden."""
        mock_response = Mock()
        mock_response.status_code = 403
        http_error = requests.HTTPError("403 Forbidden")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/forbidden.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/forbidden.jpg"
        assert error.status_code == 403


class TestDownloadImageNetworkErrors:
    """Tests for network error handling."""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_timeout(self, mock_get):
        """Should raise DownloadError on timeout."""
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/image.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/image.jpg"
        assert error.status_code is None
        assert "timeout" in str(error).lower()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_connection_error(self, mock_get):
        """Should raise DownloadError on connection error."""
        mock_get.side_effect = requests.ConnectionError("Failed to connect")
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/image.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/image.jpg"
        assert error.status_code is None
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_too_many_redirects(self, mock_get):
        """Should raise DownloadError on too many redirects."""
        mock_get.side_effect = requests.TooManyRedirects("Too many redirects")
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/image.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/image.jpg"
        assert "redirect" in str(error).lower()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_raises_on_generic_request_exception(self, mock_get):
        """Should raise DownloadError on generic request exception."""
        mock_get.side_effect = requests.RequestException("Unknown error")
        
        with pytest.raises(DownloadError) as exc_info:
            download_image("https://example.com/image.jpg")
        
        error = exc_info.value
        assert error.url == "https://example.com/image.jpg"


class TestDownloadImageEdgeCases:
    """Tests for edge cases."""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_handles_empty_response(self, mock_get):
        """Should handle empty response content."""
        mock_response = Mock()
        mock_response.content = b""
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/empty.jpg")
        
        assert isinstance(result, BytesIO)
        assert result.read() == b""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_handles_large_response(self, mock_get):
        """Should handle large image data."""
        large_data = b"x" * 1000000  # 1MB
        mock_response = Mock()
        mock_response.content = large_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/large.jpg")
        
        assert isinstance(result, BytesIO)
        assert len(result.read()) == 1000000
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    def test_download_image_returns_seekable_stream(self, mock_get):
        """Should return seekable BytesIO stream."""
        mock_response = Mock()
        mock_response.content = b"test data"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        # Should be able to seek
        result.seek(0)
        first_read = result.read()
        result.seek(0)
        second_read = result.read()
        
        assert first_read == second_read == b"test data"


class TestDownloadImageContentType:
    """Tests for Content-Type validation."""
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_accepts_image_jpeg(self, mock_logger, mock_get):
        """Should accept image/jpeg Content-Type without warning."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/jpeg'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_accepts_image_png(self, mock_logger, mock_get):
        """Should accept image/png Content-Type without warning."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/png'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.png")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_accepts_image_gif(self, mock_logger, mock_get):
        """Should accept image/gif Content-Type without warning."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/gif'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.gif")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_warns_on_text_html(self, mock_logger, mock_get):
        """Should warn but continue when Content-Type is text/html."""
        mock_response = Mock()
        mock_response.content = b"<html>Not an image</html>"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'text/html'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/page.html")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "text/html" in warning_message
        assert "https://example.com/page.html" in warning_message
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_warns_on_application_octet_stream(self, mock_logger, mock_get):
        """Should warn but continue when Content-Type is application/octet-stream."""
        mock_response = Mock()
        mock_response.content = b"binary data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/octet-stream'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/file.bin")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "application/octet-stream" in warning_message
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_warns_on_missing_content_type(self, mock_logger, mock_get):
        """Should warn but continue when Content-Type header is missing."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_called_once()
        warning_message = mock_logger.warning.call_args[0][0]
        assert "Content-Type" in warning_message or "content type" in warning_message.lower()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_accepts_image_webp(self, mock_logger, mock_get):
        """Should accept image/webp Content-Type without warning."""
        mock_response = Mock()
        mock_response.content = b"webp data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/webp'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.webp")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_accepts_image_svg_xml(self, mock_logger, mock_get):
        """Should accept image/svg+xml Content-Type without warning."""
        mock_response = Mock()
        mock_response.content = b"<svg></svg>"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/svg+xml'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.svg")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_handles_content_type_with_charset(self, mock_logger, mock_get):
        """Should handle Content-Type with charset parameter."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'image/jpeg; charset=utf-8'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
    
    @patch('DownloadImagesOnPage.downloader.requests.get')
    @patch('DownloadImagesOnPage.downloader.logger')
    def test_download_image_case_insensitive_content_type(self, mock_logger, mock_get):
        """Should handle Content-Type case-insensitively."""
        mock_response = Mock()
        mock_response.content = b"image data"
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'IMAGE/JPEG'}
        mock_get.return_value = mock_response
        
        result = download_image("https://example.com/image.jpg")
        
        assert isinstance(result, BytesIO)
        mock_logger.warning.assert_not_called()
