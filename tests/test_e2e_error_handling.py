"""E2E tests for error handling scenarios.

These tests verify that the application continues processing when some images
fail to download, and that the final summary reports correct failure counts.

Run with: pytest tests/test_e2e_error_handling.py -v
"""

import logging
import sys
from io import BytesIO


class TestE2EErrorHandling:
    def test_mixed_404_and_invalid_url_continue_and_report_failures(self, tmp_path, caplog, monkeypatch):
        """Should skip failed images and report failure count in summary."""
        output_dir = tmp_path / "output"

        import DownloadImagesOnPage.orchestrator
        from DownloadImagesOnPage.exceptions import DownloadError

        ok_url = "https://example.com/ok.jpg"
        not_found_url = "https://example.com/missing.jpg"
        invalid_url = "https://invalid-host.example/img.jpg"

        def mock_fetch(url, headers=None, timeout=30):
            return "<html></html>"

        def mock_extract(html, base_url):
            # Intentionally include URLs that will fail to download.
            return [ok_url, not_found_url, invalid_url]

        def mock_download(url, headers=None, timeout=30):
            if url == ok_url:
                return BytesIO(b"fake_image_data")
            if url == not_found_url:
                raise DownloadError(url=url, status_code=404)
            raise DownloadError(url=url, status_code=None, message="Invalid URL")

        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, "fetch_html", mock_fetch)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, "extract_image_urls", mock_extract)
        monkeypatch.setattr(DownloadImagesOnPage.orchestrator, "download_image", mock_download)

        test_args = ["DownloadImagesOnPage", "https://example.com", str(output_dir)]
        monkeypatch.setattr(sys, "argv", test_args)

        with caplog.at_level(logging.INFO):
            from DownloadImagesOnPage.main import main

            exit_code = main()

        assert exit_code == 0

        # Only the successful image should be saved.
        saved_files = list(output_dir.glob("*"))
        assert len(saved_files) == 1

        log_text = caplog.text
        # Should have logged failures and still completed.
        assert "Failed to download" in log_text
        assert "Download complete" in log_text
        assert "1 succeeded" in log_text
        assert "2 failed" in log_text
