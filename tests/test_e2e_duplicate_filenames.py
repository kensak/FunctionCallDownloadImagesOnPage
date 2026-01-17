"""E2E tests for duplicate filename handling scenarios.

These tests verify that duplicate filenames are handled correctly
with sequential numbering while preserving extensions.

Run with: pytest tests/test_e2e_duplicate_filenames.py -v
"""
import logging
import sys
from io import BytesIO
from pathlib import Path
from unittest.mock import patch, Mock
import pytest


class TestE2EWithDuplicateFilenames:
    """E2E tests for duplicate filename handling."""
    
    def test_duplicate_filenames_with_sequential_numbers(self, tmp_path, caplog, monkeypatch):
        """Should add sequential numbers to duplicate filenames."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        # Three images with the same filename
        urls_list = [
            "https://example.com/image.jpg",
            "https://different.com/image.jpg",
            "https://another.com/image.jpg",
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir)
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        # Should save 3 files with unique names
        saved_files = sorted([f.name for f in output_dir.glob("*")])
        assert len(saved_files) == 3
        
        # Check that sequential numbers were added
        assert "image.jpg" in saved_files
        assert "image_1.jpg" in saved_files
        assert "image_2.jpg" in saved_files
        
        log_text = caplog.text
        assert "3 succeeded" in log_text
    
    def test_duplicate_filenames_preserve_extensions(self, tmp_path, caplog, monkeypatch):
        """Should preserve file extensions when handling duplicates."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/photo.png",
            "https://different.com/photo.png",
            "https://example.com/photo.jpg",  # Different extension
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir)
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        saved_files = sorted([f.name for f in output_dir.glob("*")])
        assert len(saved_files) == 3
        
        # .png files should have sequential numbers
        assert "photo.png" in saved_files
        assert "photo_1.png" in saved_files
        
        # .jpg file should not conflict (different extension)
        assert "photo.jpg" in saved_files
    
    def test_duplicate_filenames_with_many_conflicts(self, tmp_path, caplog, monkeypatch):
        """Should handle many duplicate filenames correctly."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        # Five images with the same filename
        urls_list = [
            f"https://site{i}.com/test.jpg" for i in range(5)
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir)
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        saved_files = sorted([f.name for f in output_dir.glob("*")])
        assert len(saved_files) == 5
        
        # Check sequential numbering
        assert "test.jpg" in saved_files
        assert "test_1.jpg" in saved_files
        assert "test_2.jpg" in saved_files
        assert "test_3.jpg" in saved_files
        assert "test_4.jpg" in saved_files
        
        log_text = caplog.text
        assert "5 succeeded" in log_text
    
    def test_duplicate_filenames_with_mixed_names(self, tmp_path, caplog, monkeypatch):
        """Should handle mixed filenames with some duplicates."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        
        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"
        
        urls_list = [
            "https://example.com/photo1.jpg",
            "https://example.com/photo2.jpg",
            "https://different.com/photo1.jpg",  # Duplicate
            "https://example.com/photo3.jpg",
            "https://another.com/photo1.jpg",    # Another duplicate
        ]
        
        def mock_extract(html, base_url):
            return urls_list
        
        def mock_download(url, headers=None, timeout=30):
            return BytesIO(b"fake_image_data")
        
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'fetch_html', mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'extract_image_urls', mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, 'download_image', mock_download)
        
        test_args = [
            "DownloadImagesOnPage",
            "https://example.com",
            str(output_dir)
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main
            exit_code = main()
        
        assert exit_code == 0
        
        saved_files = sorted([f.name for f in output_dir.glob("*")])
        assert len(saved_files) == 5
        
        # photo1.jpg should have duplicates with sequential numbers
        assert "photo1.jpg" in saved_files
        assert "photo1_1.jpg" in saved_files
        assert "photo1_2.jpg" in saved_files
        
        # photo2 and photo3 should be unique
        assert "photo2.jpg" in saved_files
        assert "photo3.jpg" in saved_files
