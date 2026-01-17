"""End-to-end tests for the image downloader CLI.

These tests verify the complete workflow from command-line invocation
to file system output.
"""
import logging
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, Mock
import pytest


class TestBasicDownloadScenario:
    """E2E tests for basic download scenarios."""
    
    def test_basic_download_with_mock_http(self, tmp_path, caplog, monkeypatch):
        """Should complete a full download workflow with mocked HTTP."""
        output_dir = tmp_path / "output"
        
        # Patch orchestrator-level references (stable even if modules were imported earlier)
        import DownloadImagesOnPage.orchestrator
        
        # Create mock functions
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        def mock_extract(html, base_url):
            return [
                "https://example.com/img1.jpg",
                "https://example.com/img2.png",
            ]
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        # Apply patches
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        # Set sys.argv
        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Verify the output
        assert output_dir.exists()
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 2
        
        log_text = caplog.text
        assert "Download complete" in log_text or "succeeded" in log_text
    
    def test_basic_download_verifies_file_names(self, tmp_path, caplog, monkeypatch):
        """Should save images with correct filenames derived from URLs."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        def mock_extract(html, base_url):
            return [
                "https://example.com/photo.jpg",
                "https://example.com/image.png",
            ]
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()

        assert exit_code == 0

        # Check that files are saved (filenames may be sanitized/unique)
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 2
        
        # Check that we have .jpg and .png files
        extensions = {f.suffix for f in saved_files}
        assert '.jpg' in extensions or '.png' in extensions
    
    def test_basic_download_displays_progress(self, tmp_path, caplog, monkeypatch):
        """Should display progress during download."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        def mock_extract(html, base_url):
            return [
                "https://example.com/img1.jpg",
                "https://example.com/img2.png",
            ]
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            main()
        
        log_text = caplog.text
        
        # Should show processing messages
        assert "Processing" in log_text or "Downloaded" in log_text or "Success" in log_text
    
    def test_basic_download_displays_summary(self, tmp_path, caplog, monkeypatch):
        """Should display summary after download."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        def mock_extract(html, base_url):
            return [
                "https://example.com/img1.jpg",
                "https://example.com/img2.png",
            ]
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            main()
        
        log_text = caplog.text
        
        # Verify summary
        assert "complete" in log_text.lower() or "succeeded" in log_text.lower()
        assert "2" in log_text  # Should report 2 successful downloads
    
    def test_basic_download_with_no_images(self, tmp_path, caplog, monkeypatch):
        """Should handle pages with no images gracefully."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html><p>No images here</p></html>"
        
        def mock_extract(html, base_url):
            return []
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        
        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Should create directory
        assert output_dir.exists()
        
        log_text = caplog.text
        assert "0" in log_text or "Found 0" in log_text


class TestE2EWithVerboseMode:
    """E2E tests for verbose mode output."""
    
    def test_verbose_mode_displays_detailed_info(self, tmp_path, caplog, monkeypatch):
        """Should display detailed information in verbose mode."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        import DownloadImagesOnPage.filter
        from DownloadImagesOnPage.models import ImageDimensions
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        def mock_extract(html, base_url):
            return ["https://example.com/test-image.jpg"]
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        def mock_dims(image_data):
            return ImageDimensions(800, 600)
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        monkeypatch.setattr(DownloadImagesOnPage.filter, 'get_image_dimensions', mock_dims)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'get_image_dimensions', mock_dims)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir),
            "--verbose"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.DEBUG):  # Verbose uses DEBUG level
            from DownloadImagesOnPage.main import main
            main()
        
        log_text = caplog.text
        
        # Verbose mode should show detailed information about downloads
        # Check for various indicators that details were logged
        assert "Success:" in log_text or "Downloaded:" in log_text
        assert ".jpg" in log_text  # Should mention file extension

