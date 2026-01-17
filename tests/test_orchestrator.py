"""Tests for download orchestrator module."""
import pytest
from unittest.mock import Mock, patch, call
from io import BytesIO
from pathlib import Path

from DownloadImagesOnPage.orchestrator import run_download
from DownloadImagesOnPage.models import CLIConfig, DownloadResult, DownloadStatus, ImageDimensions
from DownloadImagesOnPage.exceptions import FetchError, DownloadError


class TestRunDownloadBasic:
    """Tests for basic run_download functionality."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.generate_unique_filename')
    @patch('DownloadImagesOnPage.orchestrator.save_image')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    def test_run_download_success_single_image(
        self, mock_dimensions, mock_save, mock_unique_filename, 
        mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should successfully download a single image."""
        # Setup mocks
        mock_fetch.return_value = "<html><img src='image.jpg'/></html>"
        mock_extract.return_value = ["https://example.com/image.jpg"]
        mock_download.return_value = BytesIO(b"fake image data")
        mock_check_size.return_value = True
        mock_unique_filename.return_value = Path("/output/image.jpg")
        mock_dimensions.return_value = ImageDimensions(800, 600)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            min_width=None,
            min_height=None,
            verbose=False
        )
        
        result = run_download(config)
        
        assert isinstance(result, DownloadResult)
        assert result.success_count == 1
        assert result.failed_count == 0
        assert result.filtered_count == 0
        assert result.total_count == 1
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.generate_unique_filename')
    @patch('DownloadImagesOnPage.orchestrator.save_image')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    def test_run_download_multiple_images(
        self, mock_dimensions, mock_save, mock_unique_filename, 
        mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should successfully download multiple images."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.png",
            "https://example.com/img3.gif"
        ]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = True
        mock_unique_filename.side_effect = [
            Path("/output/img1.jpg"),
            Path("/output/img2.png"),
            Path("/output/img3.gif")
        ]
        mock_dimensions.return_value = ImageDimensions(800, 600)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        result = run_download(config)
        
        assert result.success_count == 3
        assert result.total_count == 3
        assert mock_download.call_count == 3
        assert mock_save.call_count == 3


class TestRunDownloadHTMLFetchError:
    """Tests for HTML fetch error handling."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    def test_run_download_fetch_error_raises(self, mock_fetch):
        """Should raise FetchError when HTML fetch fails."""
        mock_fetch.side_effect = FetchError(
            url="https://example.com",
            status_code=404,
            message="Not found"
        )
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        with pytest.raises(FetchError):
            run_download(config)
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    def test_run_download_fetch_network_error(self, mock_fetch):
        """Should raise FetchError on network errors."""
        mock_fetch.side_effect = FetchError(
            url="https://example.com",
            status_code=None,
            message="Connection timeout"
        )
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        with pytest.raises(FetchError):
            run_download(config)


class TestRunDownloadImageFailures:
    """Tests for individual image download failures."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    def test_run_download_continues_after_failed_image(
        self, mock_download, mock_extract, mock_fetch
    ):
        """Should continue downloading after one image fails."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg"
        ]
        # First image fails, second succeeds
        mock_download.side_effect = [
            DownloadError(url="https://example.com/img1.jpg", status_code=404),
            BytesIO(b"data")
        ]
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        # Should not raise, but continue processing
        with patch('DownloadImagesOnPage.orchestrator.check_image_size', return_value=True):
            with patch('DownloadImagesOnPage.orchestrator.generate_unique_filename'):
                with patch('DownloadImagesOnPage.orchestrator.save_image'):
                    with patch('DownloadImagesOnPage.orchestrator.get_image_dimensions'):
                        result = run_download(config)
        
        assert result.failed_count == 1
        assert result.success_count == 1
        assert result.total_count == 2


class TestRunDownloadSizeFiltering:
    """Tests for size filtering functionality."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    def test_run_download_filters_small_images(
        self, mock_dimensions, mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should filter out images that don't meet size criteria."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            "https://example.com/small.jpg",
            "https://example.com/large.jpg"
        ]
        mock_download.return_value = BytesIO(b"data")
        # First image filtered, second passes
        mock_check_size.side_effect = [False, True]
        mock_dimensions.return_value = ImageDimensions(100, 100)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            min_width=500,
            min_height=500
        )
        
        with patch('DownloadImagesOnPage.orchestrator.generate_unique_filename'):
            with patch('DownloadImagesOnPage.orchestrator.save_image'):
                result = run_download(config)
        
        assert result.filtered_count == 1
        assert result.success_count == 1
        assert result.total_count == 2
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    def test_run_download_no_filtering_when_no_size_specified(
        self, mock_dimensions, mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should not filter when no size constraints specified."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ["https://example.com/image.jpg"]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = True
        mock_dimensions.return_value = ImageDimensions(50, 50)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            min_width=None,
            min_height=None
        )
        
        with patch('DownloadImagesOnPage.orchestrator.generate_unique_filename'):
            with patch('DownloadImagesOnPage.orchestrator.save_image'):
                result = run_download(config)
        
        assert result.filtered_count == 0
        assert result.success_count == 1


class TestRunDownloadNoImages:
    """Tests for cases with no images found."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    def test_run_download_no_images_found(self, mock_extract, mock_fetch):
        """Should return empty result when no images found."""
        mock_fetch.return_value = "<html><p>No images here</p></html>"
        mock_extract.return_value = []
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        result = run_download(config)
        
        assert result.total_count == 0
        assert result.success_count == 0
        assert result.failed_count == 0
        assert result.filtered_count == 0


class TestRunDownloadProgressAndLogging:
    """Tests for progress display and logging."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.generate_unique_filename')
    @patch('DownloadImagesOnPage.orchestrator.save_image')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    @patch('DownloadImagesOnPage.orchestrator.logger')
    def test_run_download_logs_progress(
        self, mock_logger, mock_dimensions, mock_save, mock_unique_filename,
        mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should log progress during download."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            "https://example.com/img1.jpg",
            "https://example.com/img2.jpg"
        ]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = True
        mock_unique_filename.side_effect = [Path("/output/img1.jpg"), Path("/output/img2.jpg")]
        mock_dimensions.return_value = ImageDimensions(800, 600)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            verbose=False
        )
        
        run_download(config)
        
        # Should log progress info (not checking exact text)
        assert mock_logger.info.call_count >= 2
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.logger')
    def test_run_download_logs_failures(
        self, mock_logger, mock_download, mock_extract, mock_fetch
    ):
        """Should log warning when image download fails."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ["https://example.com/img.jpg"]
        mock_download.side_effect = DownloadError(
            url="https://example.com/img.jpg",
            status_code=404
        )
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        result = run_download(config)
        
        # Should log warning about failure
        assert mock_logger.warning.call_count >= 1
        assert result.failed_count == 1
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    @patch('DownloadImagesOnPage.orchestrator.logger')
    def test_run_download_logs_filtered_images(
        self, mock_logger, mock_dimensions, mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should log info when image is filtered."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ["https://example.com/small.jpg"]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = False
        mock_dimensions.return_value = ImageDimensions(100, 100)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            min_width=500,
            min_height=500
        )
        
        result = run_download(config)
        
        # Should log info about filtered image
        assert mock_logger.info.call_count >= 1
        assert result.filtered_count == 1
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.generate_unique_filename')
    @patch('DownloadImagesOnPage.orchestrator.save_image')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    @patch('DownloadImagesOnPage.orchestrator.logger')
    def test_run_download_verbose_logging(
        self, mock_logger, mock_dimensions, mock_save, mock_unique_filename,
        mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should log detailed info in verbose mode."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = ["https://example.com/img.jpg"]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = True
        mock_unique_filename.return_value = Path("/output/img.jpg")
        mock_dimensions.return_value = ImageDimensions(800, 600)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            verbose=True
        )
        
        run_download(config)
        
        # Verbose mode should log more details
        # At least: progress + success details
        assert mock_logger.info.call_count >= 2


class TestRunDownloadUniqueFilenames:
    """Tests for unique filename generation."""
    
    @patch('DownloadImagesOnPage.orchestrator.fetch_html')
    @patch('DownloadImagesOnPage.orchestrator.extract_image_urls')
    @patch('DownloadImagesOnPage.orchestrator.download_image')
    @patch('DownloadImagesOnPage.orchestrator.check_image_size')
    @patch('DownloadImagesOnPage.orchestrator.generate_unique_filename')
    @patch('DownloadImagesOnPage.orchestrator.save_image')
    @patch('DownloadImagesOnPage.orchestrator.get_image_dimensions')
    def test_run_download_generates_unique_filenames(
        self, mock_dimensions, mock_save, mock_unique_filename,
        mock_check_size, mock_download, mock_extract, mock_fetch
    ):
        """Should generate unique filenames for each image."""
        mock_fetch.return_value = "<html></html>"
        mock_extract.return_value = [
            "https://example.com/image.jpg",
            "https://another.com/image.jpg"
        ]
        mock_download.return_value = BytesIO(b"data")
        mock_check_size.return_value = True
        mock_unique_filename.side_effect = [
            Path("/output/image.jpg"),
            Path("/output/image_1.jpg")
        ]
        mock_dimensions.return_value = ImageDimensions(800, 600)
        
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        
        result = run_download(config)
        
        assert mock_unique_filename.call_count == 2
        assert result.success_count == 2
