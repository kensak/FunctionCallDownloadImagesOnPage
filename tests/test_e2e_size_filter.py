"""E2E tests for size filtering scenarios.

These tests must be run separately from other E2E tests to avoid module caching issues.
Run with: pytest tests/test_e2e_size_filter.py -v
"""
import logging
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, Mock
import pytest


class TestE2EWithSizeFiltering:
    """E2E tests for size filtering scenarios."""
    
    def test_size_filter_with_min_width_only(self, tmp_path, caplog, monkeypatch):
        """Should filter images based on minimum width."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        import DownloadImagesOnPage.filter
        from DownloadImagesOnPage.models import ImageDimensions
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/large.jpg",   # 1000x500 - should pass
            "https://example.com/small.jpg",   # 200x300 - should be filtered
            "https://example.com/medium.jpg",  # 600x400 - should pass
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        # Create dimension mapping based on URL
        dimensions_map = {
            "https://example.com/large.jpg": ImageDimensions(1000, 500),
            "https://example.com/small.jpg": ImageDimensions(200, 300),
            "https://example.com/medium.jpg": ImageDimensions(600, 400),
        }
        
        call_index = [0]
        
        def mock_dims(image_data):
            # Return dimensions based on which URL was processed
            url = urls_list[call_index[0] % len(urls_list)]
            call_index[0] += 1
            return dimensions_map[url]
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        monkeypatch.setattr(DownloadImagesOnPage.filter, 'get_image_dimensions', mock_dims)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'get_image_dimensions', mock_dims)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir),
            "--min-width", "500"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Should save only 2 images (large and medium)
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 2
        
        log_text = caplog.text
        # Should report 2 succeeded, 0 failed, 1 filtered
        assert "2 succeeded" in log_text
        assert "1 filtered" in log_text
    
    def test_size_filter_with_min_height_only(self, tmp_path, caplog, monkeypatch):
        """Should filter images based on minimum height."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        import DownloadImagesOnPage.filter
        from DownloadImagesOnPage.models import ImageDimensions
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/tall.jpg",    # 400x800 - should pass
            "https://example.com/short.jpg",   # 500x150 - should be filtered
            "https://example.com/medium.jpg",  # 300x400 - should pass
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        dimensions_map = {
            "https://example.com/tall.jpg": ImageDimensions(400, 800),
            "https://example.com/short.jpg": ImageDimensions(500, 150),
            "https://example.com/medium.jpg": ImageDimensions(300, 400),
        }
        
        call_index = [0]
        
        def mock_dims(image_data):
            url = urls_list[call_index[0] % len(urls_list)]
            call_index[0] += 1
            return dimensions_map[url]
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        monkeypatch.setattr(DownloadImagesOnPage.filter, 'get_image_dimensions', mock_dims)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'get_image_dimensions', mock_dims)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir),
            "--min-height", "350"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Should save only 2 images (tall and medium)
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 2
        
        log_text = caplog.text
        assert "2 succeeded" in log_text
        assert "1 filtered" in log_text
    
    def test_size_filter_with_both_dimensions(self, tmp_path, caplog, monkeypatch):
        """Should filter images based on both width and height."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        import DownloadImagesOnPage.filter
        from DownloadImagesOnPage.models import ImageDimensions
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/large.jpg",   # 1000x800 - should pass both
            "https://example.com/wide.jpg",    # 800x200 - width ok, height fail
            "https://example.com/tall.jpg",    # 200x800 - width fail, height ok
            "https://example.com/small.jpg",   # 200x200 - both fail
            "https://example.com/ok.jpg",      # 600x600 - should pass both
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        dimensions_map = {
            "https://example.com/large.jpg": ImageDimensions(1000, 800),
            "https://example.com/wide.jpg": ImageDimensions(800, 200),
            "https://example.com/tall.jpg": ImageDimensions(200, 800),
            "https://example.com/small.jpg": ImageDimensions(200, 200),
            "https://example.com/ok.jpg": ImageDimensions(600, 600),
        }
        
        call_index = [0]
        
        def mock_dims(image_data):
            url = urls_list[call_index[0] % len(urls_list)]
            call_index[0] += 1
            return dimensions_map[url]
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        monkeypatch.setattr(DownloadImagesOnPage.filter, 'get_image_dimensions', mock_dims)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'get_image_dimensions', mock_dims)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir),
            "--min-width", "500",
            "--min-height", "500"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Should save only 2 images (large and ok)
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 2
        
        log_text = caplog.text
        assert "2 succeeded" in log_text
        assert "3 filtered" in log_text
    
    def test_size_filter_all_images_filtered(self, tmp_path, caplog, monkeypatch):
        """Should handle case where all images are filtered."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        import DownloadImagesOnPage.filter
        from DownloadImagesOnPage.models import ImageDimensions
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/small1.jpg",
            "https://example.com/small2.jpg",
            "https://example.com/small3.jpg",
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        def mock_dims(image_data):
            # All images are small
            return ImageDimensions(100, 100)
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        monkeypatch.setattr(DownloadImagesOnPage.filter, 'get_image_dimensions', mock_dims)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'get_image_dimensions', mock_dims)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir),
            "--min-width", "500",
            "--min-height", "500"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # No images should be saved
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 0
        
        log_text = caplog.text
        assert "0 succeeded" in log_text
        assert "3 filtered" in log_text
