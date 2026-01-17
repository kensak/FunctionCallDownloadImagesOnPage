"""Tests for HTML fetcher module."""
import pytest
from unittest.mock import Mock, patch
import requests

from DownloadImagesOnPage.fetcher import fetch_html
from DownloadImagesOnPage.exceptions import FetchError


class TestFetchHtmlSuccess:
    """Tests for successful HTML fetching."""
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_returns_text(self, mock_get):
        """Should return HTML text from successful request."""
        mock_response = Mock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        assert result == "<html><body>Test</body></html>"
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_calls_raise_for_status(self, mock_get):
        """Should call raise_for_status to check HTTP errors."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        fetch_html("https://example.com")
        
        mock_response.raise_for_status.assert_called_once()
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_uses_custom_timeout(self, mock_get):
        """Should use custom timeout when provided."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        fetch_html("https://example.com", timeout=30)
        
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == 30
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_uses_default_timeout(self, mock_get):
        """Should use default timeout of 10 seconds."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        fetch_html("https://example.com")
        
        call_args = mock_get.call_args
        assert call_args[1]['timeout'] == 10
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_sets_user_agent(self, mock_get):
        """Should set User-Agent header."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_get.return_value = mock_response
        
        fetch_html("https://example.com")
        
        call_args = mock_get.call_args
        headers = call_args[1].get('headers', {})
        assert 'User-Agent' in headers
        assert len(headers['User-Agent']) > 0
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_supports_http(self, mock_get):
        """Should support HTTP protocol."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_html("http://example.com")
        
        assert result == "<html></html>"
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_supports_https(self, mock_get):
        """Should support HTTPS protocol."""
        mock_response = Mock()
        mock_response.text = "<html></html>"
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        assert result == "<html></html>"


class TestFetchHtmlHttpErrors:
    """Tests for HTTP error handling."""
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_404(self, mock_get):
        """Should raise FetchError on 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        http_error = requests.HTTPError("404 Not Found")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com/notfound")
        
        error = exc_info.value
        assert error.url == "https://example.com/notfound"
        assert error.status_code == 404
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_500(self, mock_get):
        """Should raise FetchError on 500."""
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = requests.HTTPError("500 Internal Server Error")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.status_code == 500
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_403(self, mock_get):
        """Should raise FetchError on 403 Forbidden."""
        mock_response = Mock()
        mock_response.status_code = 403
        http_error = requests.HTTPError("403 Forbidden")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.status_code == 403


class TestFetchHtmlNetworkErrors:
    """Tests for network error handling."""
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_timeout(self, mock_get):
        """Should raise FetchError on timeout."""
        mock_get.side_effect = requests.Timeout("Connection timeout")
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.url == "https://example.com"
        assert error.status_code is None
        assert "timeout" in str(error).lower()
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_connection_error(self, mock_get):
        """Should raise FetchError on connection error."""
        mock_get.side_effect = requests.ConnectionError("Failed to connect")
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.url == "https://example.com"
        assert error.status_code is None
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_too_many_redirects(self, mock_get):
        """Should raise FetchError on too many redirects."""
        mock_get.side_effect = requests.TooManyRedirects("Too many redirects")
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.url == "https://example.com"
        assert "redirect" in str(error).lower()
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_raises_on_generic_request_exception(self, mock_get):
        """Should raise FetchError on generic request exception."""
        mock_get.side_effect = requests.RequestException("Unknown error")
        
        with pytest.raises(FetchError) as exc_info:
            fetch_html("https://example.com")
        
        error = exc_info.value
        assert error.url == "https://example.com"


class TestFetchHtmlEdgeCases:
    """Tests for edge cases."""
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_handles_empty_response(self, mock_get):
        """Should handle empty HTML response."""
        mock_response = Mock()
        mock_response.text = ""
        mock_get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        assert result == ""
    
    @patch('DownloadImagesOnPage.fetcher.requests.get')
    def test_fetch_html_handles_large_response(self, mock_get):
        """Should handle large HTML response."""
        mock_response = Mock()
        mock_response.text = "<html>" + "x" * 1000000 + "</html>"
        mock_get.return_value = mock_response
        
        result = fetch_html("https://example.com")
        
        assert len(result) > 1000000
