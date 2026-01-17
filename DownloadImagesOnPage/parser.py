"""HTML parser module for extracting image URLs from HTML content."""
from bs4 import BeautifulSoup
from typing import List
from urllib.parse import urljoin, urlparse


# Supported image file extensions
SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}

# Invalid URL schemes to exclude
INVALID_SCHEMES = {'data', 'javascript', 'mailto'}


def extract_image_urls(html: str, base_url: str) -> List[str]:
    """
    HTMLから画像URLを抽出
    
    Args:
        html: HTMLテキスト
        base_url: 相対URL解決のためのベースURL
        
    Returns:
        画像URLのリスト（重複なし、絶対URL）
    """
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    img_tags = soup.find_all('img')
    
    urls = set()
    
    for img in img_tags:
        src = img.get('src')
        
        # Skip if no src attribute or empty
        if not src or not src.strip():
            continue
        
        # Parse URL to check scheme
        parsed = urlparse(src)
        
        # Skip invalid schemes
        if parsed.scheme in INVALID_SCHEMES:
            continue
        
        # Convert relative URL to absolute
        absolute_url = urljoin(base_url, src)
        
        # Check if URL has supported image extension
        parsed_absolute = urlparse(absolute_url)
        path = parsed_absolute.path.lower()
        
        # Extract extension from path (before query parameters)
        if '.' in path:
            extension = '.' + path.rsplit('.', 1)[-1].split('?')[0].split('#')[0]
            if extension in SUPPORTED_EXTENSIONS:
                urls.add(absolute_url)
    
    return list(urls)
