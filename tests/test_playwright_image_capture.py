"""Tests for Playwright image capture functionality."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from io import BytesIO
from PIL import Image
from DownloadImagesOnPage.models import RenderedImage, ImageDimensions


@pytest.mark.asyncio
async def test_capture_rendered_images_returns_list():
    """Should return list of RenderedImage objects."""
    from DownloadImagesOnPage.fetcher import capture_rendered_images
    
    url = "https://example.com"
    
    # Create mock image data
    img = Image.new('RGB', (100, 200), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()
    
    # Mock Playwright objects
    mock_element = AsyncMock()
    mock_element.screenshot = AsyncMock(return_value=img_data)
    mock_element.get_attribute = AsyncMock(side_effect=lambda attr: {
        'src': 'https://example.com/test.jpg',
        'width': '100',
        'height': '200'
    }.get(attr))
    
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.nth = MagicMock(return_value=mock_element)
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_page.close = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    mock_context.set_default_timeout = MagicMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        images = await capture_rendered_images(url)
        
        assert isinstance(images, list)
        assert len(images) == 1
        assert isinstance(images[0], RenderedImage)
        mock_context.set_default_timeout.assert_called_once_with(5000)
        mock_page.set_default_timeout.assert_called_once_with(5000)


@pytest.mark.asyncio
async def test_capture_rendered_images_extracts_image_data():
    """Should extract image data from rendered page."""
    from DownloadImagesOnPage.fetcher import capture_rendered_images
    
    url = "https://example.com"
    
    # Create mock image data
    img = Image.new('RGB', (150, 250), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_data = img_bytes.getvalue()
    
    mock_element = AsyncMock()
    mock_element.screenshot = AsyncMock(return_value=img_data)
    mock_element.get_attribute = AsyncMock(side_effect=lambda attr: {
        'src': 'https://example.com/image.png',
        'width': '150',
        'height': '250'
    }.get(attr))
    
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(return_value=1)
    mock_locator.nth = MagicMock(return_value=mock_element)
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_page.close = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    mock_context.set_default_timeout = MagicMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        images = await capture_rendered_images(url)
        
        assert images[0].image_data == img_data
        assert images[0].original_url == 'https://example.com/image.png'
        assert images[0].dimensions.width == 150
        assert images[0].dimensions.height == 250
        mock_context.set_default_timeout.assert_called_once_with(5000)
        mock_page.set_default_timeout.assert_called_once_with(5000)


@pytest.mark.asyncio
async def test_capture_rendered_images_handles_multiple_images():
    """Should capture multiple images from the same page."""
    from DownloadImagesOnPage.fetcher import capture_rendered_images
    
    url = "https://example.com"
    
    # Create mock image data for multiple images
    img1_data = b"image1_data"
    img2_data = b"image2_data"
    
    mock_element1 = AsyncMock()
    mock_element1.screenshot = AsyncMock(return_value=img1_data)
    mock_element1.get_attribute = AsyncMock(side_effect=lambda attr: {
        'src': 'https://example.com/img1.jpg',
        'width': '100',
        'height': '100'
    }.get(attr))
    
    mock_element2 = AsyncMock()
    mock_element2.screenshot = AsyncMock(return_value=img2_data)
    mock_element2.get_attribute = AsyncMock(side_effect=lambda attr: {
        'src': 'https://example.com/img2.jpg',
        'width': '200',
        'height': '200'
    }.get(attr))
    
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(return_value=2)
    mock_locator.nth = MagicMock(side_effect=[mock_element1, mock_element2])
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_page.close = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    mock_context.set_default_timeout = MagicMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        images = await capture_rendered_images(url)
        
        assert len(images) == 2
        assert images[0].image_data == img1_data
        assert images[1].image_data == img2_data
        mock_context.set_default_timeout.assert_called_once_with(5000)
        mock_page.set_default_timeout.assert_called_once_with(5000)


@pytest.mark.asyncio
async def test_capture_rendered_images_skips_failed_screenshots():
    """Should skip images that fail to screenshot and continue."""
    from DownloadImagesOnPage.fetcher import capture_rendered_images
    
    url = "https://example.com"
    
    img_data = b"valid_image_data"
    
    # First element fails
    mock_element1 = AsyncMock()
    mock_element1.screenshot = AsyncMock(side_effect=Exception("Screenshot failed"))
    
    # Second element succeeds
    mock_element2 = AsyncMock()
    mock_element2.screenshot = AsyncMock(return_value=img_data)
    mock_element2.get_attribute = AsyncMock(side_effect=lambda attr: {
        'src': 'https://example.com/valid.jpg',
        'width': '100',
        'height': '100'
    }.get(attr))
    
    mock_locator = AsyncMock()
    mock_locator.count = AsyncMock(return_value=2)
    mock_locator.nth = MagicMock(side_effect=[mock_element1, mock_element2])
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.locator = MagicMock(return_value=mock_locator)
    mock_page.close = AsyncMock()
    mock_page.set_default_timeout = MagicMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    mock_context.set_default_timeout = MagicMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        images = await capture_rendered_images(url)
        
        # Should only return the successful image
        assert len(images) == 1
        assert images[0].image_data == img_data
        mock_context.set_default_timeout.assert_called_once_with(5000)
        mock_page.set_default_timeout.assert_called_once_with(5000)


def test_capture_rendered_images_sync_wrapper():
    """Synchronous wrapper should call async function correctly."""
    from DownloadImagesOnPage.fetcher import capture_rendered_images_sync
    
    url = "https://example.com"
    expected_images = [MagicMock()]
    
    with patch('DownloadImagesOnPage.fetcher.asyncio.run') as mock_run:
        def _run_and_close(coro):
            # Prevent un-awaited coroutine warnings in tests.
            coro.close()
            return expected_images

        mock_run.side_effect = _run_and_close
        
        images = capture_rendered_images_sync(url)
        
        assert images == expected_images
        mock_run.assert_called_once()
