"""HTML fetcher module for downloading HTML content from URLs."""
import asyncio
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


async def fetch_html_with_playwright(url: str, timeout: int = 30000) -> str:
    """
    Playwrightを使用してJavaScriptレンダリング後のHTMLコンテンツを取得
    
    Args:
        url: 取得するURL（HTTPまたはHTTPS）
        timeout: タイムアウト（ミリ秒、デフォルト: 30000ms = 30秒）
        
    Returns:
        レンダリング後のHTMLテキスト
        
    Raises:
        FetchError: ナビゲーションエラー、タイムアウト、その他のエラー
    """
    from playwright.async_api import async_playwright
    
    browser = None
    context = None
    page = None
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, wait_until="networkidle", timeout=timeout)
            html = await page.content()
            return html

    except TimeoutError as e:
        raise FetchError(url, None, message=f"Navigation timeout for {url}: {str(e)}")
    except Exception as e:
        raise FetchError(url, None, message=f"Playwright error for {url}: {str(e)}")
    finally:
        # Best-effort cleanup; don't mask original errors.
        if page:
            try:
                await page.close()
            except Exception:
                pass
        if context:
            try:
                await context.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass


def fetch_html_playwright(url: str, timeout: int = 30000) -> str:
    """
    Playwrightを使用してHTMLを取得する同期ラッパー
    
    Args:
        url: 取得するURL
        timeout: タイムアウト（ミリ秒）
        
    Returns:
        HTMLテキスト
        
    Raises:
        FetchError: 取得エラー
    """
    return asyncio.run(fetch_html_with_playwright(url, timeout))


async def capture_rendered_images(url: str, timeout: int = 10000) -> list:
    """
    Playwrightでページをレンダリングし、画像を直接キャプチャ
    
    Args:
        url: 取得するURL
        timeout: タイムアウト（ミリ秒）
        
    Returns:
        RenderedImageオブジェクトのリスト
        
    Raises:
        FetchError: ページ取得エラー
    """
    from playwright.async_api import async_playwright
    from DownloadImagesOnPage.models import RenderedImage, ImageDimensions
    from urllib.parse import urlparse, urljoin
    from pathlib import Path
    import logging
    
    logger = logging.getLogger(__name__)
    
    browser = None
    context = None
    page = None
    rendered_images = []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            # Ensure element operations do not fall back to Playwright's default 30s timeout.
            context.set_default_timeout(timeout)
            page = await context.new_page()
            page.set_default_timeout(timeout)

            # ページを読み込む
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            
            # 全ての<img>要素を取得
            img_locator = page.locator('img')
            img_count = await img_locator.count()
            
            logger.info(f"Found {img_count} image elements on page")
            
            # 各画像要素をスクリーンショット
            for i in range(img_count):
                try:
                    element = img_locator.nth(i)
                    
                    # src属性を取得
                    src = await element.get_attribute('src')
                    if not src:
                        logger.debug(f"Image {i+1}: No src attribute, skipping")
                        continue
                    
                    # 画像のスクリーンショットを撮る
                    screenshot_data = await element.screenshot(type='png', timeout=timeout)
                    
                    # 画像サイズを取得（width/height属性から、またはスクリーンショットから）
                    width_attr = await element.get_attribute('width')
                    height_attr = await element.get_attribute('height')
                    
                    if width_attr and height_attr:
                        try:
                            width = int(width_attr)
                            height = int(height_attr)
                        except ValueError:
                            # 属性から取得できない場合はスクリーンショットから取得
                            from PIL import Image
                            from io import BytesIO
                            img = Image.open(BytesIO(screenshot_data))
                            width, height = img.size
                    else:
                        # スクリーンショットから直接サイズを取得
                        from PIL import Image
                        from io import BytesIO
                        img = Image.open(BytesIO(screenshot_data))
                        width, height = img.size
                    
                    dimensions = ImageDimensions(width=width, height=height)
                    
                    # ファイル名を生成
                    parsed_url = urlparse(src)
                    filename = Path(parsed_url.path).name
                    if not filename or filename == '/':
                        filename = f"image_{i+1}.png"
                    
                    # 拡張子を.pngに統一（スクリーンショットはPNG形式）
                    filename = Path(filename).stem + '.png'
                    
                    rendered_image = RenderedImage(
                        image_data=screenshot_data,
                        original_url=src,
                        dimensions=dimensions,
                        filename=filename
                    )
                    
                    rendered_images.append(rendered_image)
                    logger.debug(f"Captured image {i+1}/{img_count}: {src} ({width}x{height})")
                    
                except Exception as e:
                    logger.warning(f"Failed to capture image {i+1}: {str(e)}")
                    continue
            
            return rendered_images
            
    except TimeoutError as e:
        raise FetchError(url, None, message=f"Navigation timeout for {url}: {str(e)}")
    except Exception as e:
        raise FetchError(url, None, message=f"Playwright error for {url}: {str(e)}")
    finally:
        # Best-effort cleanup; don't mask original errors.
        if page:
            try:
                await page.close()
            except Exception:
                pass
        if context:
            try:
                await context.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass


def capture_rendered_images_sync(url: str, timeout: int = 10000) -> list:
    """
    Playwrightで画像をキャプチャする同期ラッパー
    
    Args:
        url: 取得するURL
        timeout: タイムアウト（ミリ秒）
        
    Returns:
        RenderedImageオブジェクトのリスト
        
    Raises:
        FetchError: 取得エラー
    """
    return asyncio.run(capture_rendered_images(url, timeout))
