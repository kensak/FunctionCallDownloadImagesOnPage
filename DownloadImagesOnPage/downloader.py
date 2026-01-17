"""Image downloader module.

This module provides functionality to download image data from URLs.
"""
from io import BytesIO
import logging
import requests

from .exceptions import DownloadError

# Module logger
logger = logging.getLogger(__name__)


def download_image(url: str, timeout: int = 10) -> BytesIO:
    """Download image data from URL.
    
    Args:
        url: Image URL to download
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        BytesIO stream containing image data
    
    Raises:
        DownloadError: If download fails due to HTTP error, timeout, or network error
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Validate Content-Type (warning only, does not fail)
        content_type = response.headers.get('Content-Type', '').lower()
        if not content_type:
            logger.warning(f"No Content-Type header for URL: {url}")
        elif not content_type.startswith('image/'):
            logger.warning(f"Unexpected Content-Type '{content_type}' for URL: {url}")
        
        return BytesIO(response.content)
    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response else None
        raise DownloadError(
            url=url,
            status_code=status_code,
            message=f"HTTP error downloading image: {e}"
        )
    except requests.Timeout as e:
        raise DownloadError(
            url=url,
            status_code=None,
            message=f"Timeout downloading image: {e}"
        )
    except requests.ConnectionError as e:
        raise DownloadError(
            url=url,
            status_code=None,
            message=f"Connection error downloading image: {e}"
        )
    except requests.TooManyRedirects as e:
        raise DownloadError(
            url=url,
            status_code=None,
            message=f"Too many redirects: {e}"
        )
    except requests.RequestException as e:
        raise DownloadError(
            url=url,
            status_code=None,
            message=f"Request error downloading image: {e}"
        )
