"""Integration tests for Playwright functionality."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from DownloadImagesOnPage.orchestrator import run_download
from DownloadImagesOnPage.models import CLIConfig


class TestPlaywrightIntegration:
    """Tests for Playwright integration in the orchestrator."""
    
    def test_orchestrator_uses_playwright_when_flag_is_true(self, tmp_path):
        """Orchestrator should use capture_rendered_images_sync when use_playwright=True."""
        from DownloadImagesOnPage.models import RenderedImage, ImageDimensions
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=tmp_path,
            use_playwright=True,
            verbose=False
        )
        
        # Mock rendered images
        rendered_images = [
            RenderedImage(
                image_data=b"test_image_data",
                original_url="https://example.com/test.jpg",
                dimensions=ImageDimensions(width=200, height=300),
                filename="test.png"
            )
        ]
        
        with patch('DownloadImagesOnPage.orchestrator.capture_rendered_images_sync') as mock_capture:
            with patch('DownloadImagesOnPage.orchestrator.fetch_html') as mock_requests:
                with patch('DownloadImagesOnPage.orchestrator.save_image'):
                    mock_capture.return_value = rendered_images
                    
                    result = run_download(config)
                    
                    # Should call Playwright capture function
                    mock_capture.assert_called_once_with(config.url)
                    # Should NOT call requests fetcher
                    mock_requests.assert_not_called()
                    # Should have processed 1 image
                    assert result.total_count == 1
    
    def test_orchestrator_uses_requests_when_flag_is_false(self, tmp_path):
        """Orchestrator should use fetch_html when use_playwright=False."""
        config = CLIConfig(
            url="https://example.com",
            output_dir=tmp_path,
            use_playwright=False,
            verbose=False
        )
        
        html = '<html><body><img src="https://example.com/test.jpg"/></body></html>'
        
        with patch('DownloadImagesOnPage.orchestrator.fetch_html_playwright') as mock_playwright:
            with patch('DownloadImagesOnPage.orchestrator.fetch_html') as mock_requests:
                with patch('DownloadImagesOnPage.orchestrator.download_image'):
                    with patch('DownloadImagesOnPage.orchestrator.save_image'):
                        mock_requests.return_value = html
                        
                        result = run_download(config)
                        
                        # Should call requests fetcher
                        mock_requests.assert_called_once_with(config.url)
                        # Should NOT call Playwright capture
                        mock_playwright.assert_not_called()
    
    def test_orchestrator_extracts_js_rendered_images(self, tmp_path):
        """Orchestrator should process multiple rendered images."""
        from DownloadImagesOnPage.models import RenderedImage, ImageDimensions
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=tmp_path,
            use_playwright=True,
            verbose=False
        )
        
        # Mock multiple rendered images
        rendered_images = [
            RenderedImage(
                image_data=b"static_image_data",
                original_url="https://example.com/static.jpg",
                dimensions=ImageDimensions(width=200, height=300),
                filename="static.png"
            ),
            RenderedImage(
                image_data=b"dynamic1_image_data",
                original_url="https://example.com/dynamic1.jpg",
                dimensions=ImageDimensions(width=250, height=350),
                filename="dynamic1.png"
            ),
            RenderedImage(
                image_data=b"dynamic2_image_data",
                original_url="https://example.com/dynamic2.jpg",
                dimensions=ImageDimensions(width=300, height=400),
                filename="dynamic2.png"
            )
        ]
        
        saved_files = []
        
        def mock_save(image_data, path):
            saved_files.append(path.name)
        
        with patch('DownloadImagesOnPage.orchestrator.capture_rendered_images_sync') as mock_capture:
            with patch('DownloadImagesOnPage.orchestrator.save_image', side_effect=mock_save):
                mock_capture.return_value = rendered_images
                
                result = run_download(config)
                
                # Should process all 3 images
                assert len(saved_files) == 3
                assert "static.png" in saved_files
                assert "dynamic1.png" in saved_files
                assert "dynamic2.png" in saved_files
                assert result.total_count == 3
                assert result.success_count == 3


class TestPlaywrightRealWorld:
    """Real-world tests using actual websites."""
    
    @pytest.mark.slow
    def test_playwright_renders_wikipedia_page(self, tmp_path):
        """Playwright should render Wikipedia page and extract more images than static HTML."""
        url = "https://ja.wikipedia.org/wiki/%E3%82%A8%E3%83%83%E3%83%95%E3%82%A7%E3%83%AB%E5%A1%94"
        
        # Test with regular requests
        config_requests = CLIConfig(
            url=url,
            output_dir=tmp_path / "requests",
            use_playwright=False,
            verbose=True
        )
        
        # Test with Playwright
        config_playwright = CLIConfig(
            url=url,
            output_dir=tmp_path / "playwright",
            use_playwright=True,
            verbose=True
        )
        
        from DownloadImagesOnPage.fetcher import fetch_html, fetch_html_playwright
        from DownloadImagesOnPage.parser import extract_image_urls
        
        # Get HTML with both methods
        html_requests = fetch_html(url)
        html_playwright = fetch_html_playwright(url)
        
        # Extract image URLs
        images_requests = extract_image_urls(html_requests, url)
        images_playwright = extract_image_urls(html_playwright, url)
        
        print(f"\nImages found with requests: {len(images_requests)}")
        print(f"Images found with Playwright: {len(images_playwright)}")
        
        # Playwright should find at least as many images as requests
        assert len(images_playwright) >= len(images_requests)
        
        # Both should find some images
        assert len(images_requests) > 0
        assert len(images_playwright) > 0
    
    @pytest.mark.slow
    def test_playwright_full_download_workflow(self, tmp_path):
        """Full download workflow with Playwright on Wikipedia."""
        url = "https://ja.wikipedia.org/wiki/%E3%82%A8%E3%83%83%E3%83%95%E3%82%A7%E3%83%AB%E5%A1%94"
        
        config = CLIConfig(
            url=url,
            output_dir=tmp_path,
            min_width=100,  # Filter out very small icons
            use_playwright=True,
            verbose=True
        )
        
        result = run_download(config)
        
        print(f"\nDownload result:")
        print(f"  Total: {result.total_count}")
        print(f"  Success: {result.success_count}")
        print(f"  Failed: {result.failed_count}")
        print(f"  Filtered: {result.filtered_count}")
        
        # Should find and process some images
        assert result.total_count > 0
        
        # Wikipedia may block downloads (403), so we just verify the workflow runs
        # The important part is that Playwright successfully rendered and extracted images
        assert result.total_count >= 40  # Page content may vary slightly over time
