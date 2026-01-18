"""Tests for Playwright-based HTML fetcher."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from DownloadImagesOnPage.fetcher import fetch_html_with_playwright
from DownloadImagesOnPage.exceptions import FetchError


@pytest.mark.asyncio
async def test_fetch_html_with_playwright_success():
    """Playwright fetcher should successfully retrieve HTML content."""
    url = "https://example.com"
    expected_html = "<html><body><img src='test.jpg'/></body></html>"
    
    # Mock Playwright objects
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.content = AsyncMock(return_value=expected_html)
    mock_page.close = AsyncMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        html = await fetch_html_with_playwright(url)
        
        assert html == expected_html
        mock_page.goto.assert_awaited_once_with(url, wait_until="networkidle", timeout=30000)
        mock_page.content.assert_awaited_once()
        mock_page.close.assert_awaited_once()
        mock_context.close.assert_awaited_once()
        mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_html_with_playwright_timeout():
    """Playwright fetcher should raise FetchError on timeout."""
    url = "https://example.com"
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(side_effect=TimeoutError("Navigation timeout"))
    mock_page.close = AsyncMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        with pytest.raises(FetchError) as exc_info:
            await fetch_html_with_playwright(url)
        
        assert url in str(exc_info.value)
        assert "timeout" in str(exc_info.value).lower()
        mock_page.close.assert_awaited_once()
        mock_context.close.assert_awaited_once()
        mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_html_with_playwright_error():
    """Playwright fetcher should raise FetchError on navigation error."""
    url = "https://example.com"
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(side_effect=Exception("Network error"))
    mock_page.close = AsyncMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        with pytest.raises(FetchError) as exc_info:
            await fetch_html_with_playwright(url)
        
        assert url in str(exc_info.value)
        mock_page.close.assert_awaited_once()
        mock_context.close.assert_awaited_once()
        mock_browser.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_fetch_html_with_playwright_headless_mode():
    """Playwright fetcher should launch browser in headless mode by default."""
    url = "https://example.com"
    
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.content = AsyncMock(return_value="<html></html>")
    mock_page.close = AsyncMock()
    
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()
    
    mock_browser = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()
    
    mock_playwright = MagicMock()
    mock_playwright.chromium.launch = AsyncMock(return_value=mock_browser)
    
    with patch('playwright.async_api.async_playwright') as mock_async_playwright:
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright
        
        await fetch_html_with_playwright(url)
        
        mock_playwright.chromium.launch.assert_awaited_once_with(headless=True)


def test_fetch_html_with_playwright_sync_wrapper():
    """Synchronous wrapper should call async function correctly."""
    url = "https://example.com"
    expected_html = "<html><body>Test</body></html>"
    
    with patch('DownloadImagesOnPage.fetcher.asyncio.run') as mock_run:
        def _run_and_close(coro):
            # Prevent un-awaited coroutine warnings in tests.
            coro.close()
            return expected_html

        mock_run.side_effect = _run_and_close
        
        from DownloadImagesOnPage.fetcher import fetch_html_playwright
        html = fetch_html_playwright(url)
        
        assert html == expected_html
        mock_run.assert_called_once()
