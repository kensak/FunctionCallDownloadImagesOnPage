"""Tests for data models."""
import pytest
from pathlib import Path
from dataclasses import FrozenInstanceError
from DownloadImagesOnPage.models import (
    CLIConfig,
    ImageDimensions,
    DownloadStatus,
    ImageDownloadRecord,
    DownloadResult,
)


class TestCLIConfig:
    """Tests for CLIConfig dataclass."""
    
    def test_cli_config_creation_with_required_fields(self):
        """CLIConfig should be created with required fields."""
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/tmp/images")
        )
        
        assert config.url == "https://example.com"
        assert config.output_dir == Path("/tmp/images")
        assert config.min_width is None
        assert config.min_height is None
        assert config.verbose is False
    
    def test_cli_config_creation_with_all_fields(self):
        """CLIConfig should be created with all optional fields."""
        config = CLIConfig(
            url="https://example.com/page",
            output_dir=Path("/downloads"),
            min_width=800,
            min_height=600,
            verbose=True
        )
        
        assert config.url == "https://example.com/page"
        assert config.output_dir == Path("/downloads")
        assert config.min_width == 800
        assert config.min_height == 600
        assert config.verbose is True
    
    def test_cli_config_type_hints(self):
        """CLIConfig should have proper type hints."""
        from typing import get_type_hints
        
        hints = get_type_hints(CLIConfig)
        
        assert hints['url'] == str
        assert hints['output_dir'] == Path
        # Optional[int] appears as Union[int, None] in type hints
        assert 'min_width' in hints
        assert 'min_height' in hints
        assert hints['verbose'] == bool
    
    def test_cli_config_is_frozen(self):
        """CLIConfig should be immutable (frozen)."""
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/tmp")
        )
        
        with pytest.raises(FrozenInstanceError):
            config.url = "https://different.com"


class TestImageDimensions:
    """Tests for ImageDimensions namedtuple."""
    
    def test_image_dimensions_creation(self):
        """ImageDimensions should be created with width and height."""
        dims = ImageDimensions(width=1920, height=1080)
        
        assert dims.width == 1920
        assert dims.height == 1080
    
    def test_image_dimensions_is_namedtuple(self):
        """ImageDimensions should be a namedtuple."""
        dims = ImageDimensions(800, 600)
        
        # namedtuples support tuple unpacking
        width, height = dims
        assert width == 800
        assert height == 600
    
    def test_image_dimensions_immutable(self):
        """ImageDimensions should be immutable."""
        dims = ImageDimensions(1024, 768)
        
        with pytest.raises(AttributeError):
            dims.width = 2048
    
    def test_image_dimensions_equality(self):
        """ImageDimensions should support equality comparison."""
        dims1 = ImageDimensions(800, 600)
        dims2 = ImageDimensions(800, 600)
        dims3 = ImageDimensions(1024, 768)
        
        assert dims1 == dims2
        assert dims1 != dims3


class TestDownloadStatus:
    """Tests for DownloadStatus enum."""
    
    def test_download_status_has_success(self):
        """DownloadStatus should have SUCCESS member."""
        assert hasattr(DownloadStatus, 'SUCCESS')
        assert DownloadStatus.SUCCESS.name == 'SUCCESS'
    
    def test_download_status_has_failed(self):
        """DownloadStatus should have FAILED member."""
        assert hasattr(DownloadStatus, 'FAILED')
        assert DownloadStatus.FAILED.name == 'FAILED'
    
    def test_download_status_has_filtered(self):
        """DownloadStatus should have FILTERED member."""
        assert hasattr(DownloadStatus, 'FILTERED')
        assert DownloadStatus.FILTERED.name == 'FILTERED'
    
    def test_download_status_only_three_members(self):
        """DownloadStatus should have exactly three members."""
        assert len(DownloadStatus) == 3
    
    def test_download_status_comparison(self):
        """DownloadStatus members should be comparable for equality."""
        status1 = DownloadStatus.SUCCESS
        status2 = DownloadStatus.SUCCESS
        status3 = DownloadStatus.FAILED
        
        assert status1 == status2
        assert status1 != status3


class TestImageDownloadRecord:
    """Tests for ImageDownloadRecord dataclass."""
    
    def test_image_download_record_creation_success(self):
        """ImageDownloadRecord should be created for successful download."""
        record = ImageDownloadRecord(
            url="https://example.com/image.jpg",
            status=DownloadStatus.SUCCESS,
            file_path=Path("/tmp/image.jpg"),
            dimensions=ImageDimensions(800, 600)
        )
        
        assert record.url == "https://example.com/image.jpg"
        assert record.status == DownloadStatus.SUCCESS
        assert record.file_path == Path("/tmp/image.jpg")
        assert record.dimensions == ImageDimensions(800, 600)
        assert record.error_message is None
    
    def test_image_download_record_creation_failed(self):
        """ImageDownloadRecord should be created for failed download."""
        record = ImageDownloadRecord(
            url="https://example.com/missing.jpg",
            status=DownloadStatus.FAILED,
            error_message="404 Not Found"
        )
        
        assert record.url == "https://example.com/missing.jpg"
        assert record.status == DownloadStatus.FAILED
        assert record.file_path is None
        assert record.dimensions is None
        assert record.error_message == "404 Not Found"
    
    def test_image_download_record_creation_filtered(self):
        """ImageDownloadRecord should be created for filtered image."""
        record = ImageDownloadRecord(
            url="https://example.com/small.jpg",
            status=DownloadStatus.FILTERED,
            dimensions=ImageDimensions(100, 100),
            error_message="Image too small: 100x100 (min: 800x600)"
        )
        
        assert record.url == "https://example.com/small.jpg"
        assert record.status == DownloadStatus.FILTERED
        assert record.file_path is None
        assert record.dimensions == ImageDimensions(100, 100)
        assert "too small" in record.error_message
    
    def test_image_download_record_type_hints(self):
        """ImageDownloadRecord should have proper type hints."""
        from typing import get_type_hints
        
        hints = get_type_hints(ImageDownloadRecord)
        
        assert hints['url'] == str
        assert hints['status'] == DownloadStatus
        # Optional types appear as Union in type hints
        assert 'file_path' in hints
        assert 'dimensions' in hints
        assert 'error_message' in hints


class TestDownloadResult:
    """Tests for DownloadResult dataclass."""
    
    def test_download_result_creation(self):
        """DownloadResult should be created with all counts."""
        result = DownloadResult(
            success_count=15,
            failed_count=2,
            filtered_count=3,
            total_count=20
        )
        
        assert result.success_count == 15
        assert result.failed_count == 2
        assert result.filtered_count == 3
        assert result.total_count == 20
    
    def test_download_result_all_success(self):
        """DownloadResult should handle all successful downloads."""
        result = DownloadResult(
            success_count=10,
            failed_count=0,
            filtered_count=0,
            total_count=10
        )
        
        assert result.success_count == 10
        assert result.failed_count == 0
        assert result.filtered_count == 0
        assert result.total_count == 10
    
    def test_download_result_type_hints(self):
        """DownloadResult should have proper type hints."""
        from typing import get_type_hints
        
        hints = get_type_hints(DownloadResult)
        
        assert hints['success_count'] == int
        assert hints['failed_count'] == int
        assert hints['filtered_count'] == int
        assert hints['total_count'] == int
    
    def test_download_result_equality(self):
        """DownloadResult should support equality comparison."""
        result1 = DownloadResult(10, 2, 1, 13)
        result2 = DownloadResult(10, 2, 1, 13)
        result3 = DownloadResult(5, 1, 0, 6)
        
        assert result1 == result2
        assert result1 != result3
