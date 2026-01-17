"""HTML fetcher module for downloading HTML content from URLs."""
import requests
from typing import Optional

from DownloadImagesOnPage.exceptions import FetchError


def fetch_html(url: str, timeout: int = 10) -> str:
    """
    URLからHTMLコンテンツを取得
    
    Args:
        url: 取得するURL（HTTPまたはHTTPS）
        timeout: タイムアウト秒数（デフォルト: 10秒）
        
    Returns:
        HTMLテキスト
        
    Raises:
        FetchError: HTTP エラー、タイムアウト、ネットワークエラー
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.HTTPError as e:
        status_code: Optional[int] = None
        if hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
        raise FetchError(url, status_code, message=f"HTTP error {status_code}: {str(e)}")
    except requests.Timeout as e:
        raise FetchError(url, None, message=f"Connection timeout: {str(e)}")
    except requests.ConnectionError as e:
        raise FetchError(url, None, message=f"Connection error: {str(e)}")
    except requests.TooManyRedirects as e:
        raise FetchError(url, None, message=f"Too many redirects: {str(e)}")
    except requests.RequestException as e:
        raise FetchError(url, None, message=f"Request failed: {str(e)}")
