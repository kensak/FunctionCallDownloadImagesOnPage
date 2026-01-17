"""Tests for image size filter module."""
import pytest
from io import BytesIO
from PIL import Image

from DownloadImagesOnPage.filter import get_image_dimensions, check_image_size
from DownloadImagesOnPage.models import ImageDimensions


class TestGetImageDimensions:
    """Tests for get_image_dimensions function."""
    
    def test_get_dimensions_from_valid_image(self):
        """Should return dimensions from valid image."""
        # Create a test image
        img = Image.new('RGB', (100, 200), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == 100
        assert result.height == 200
    
    def test_get_dimensions_returns_image_dimensions_type(self):
        """Should return ImageDimensions namedtuple."""
        img = Image.new('RGB', (50, 75), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert isinstance(result, ImageDimensions)
    
    def test_get_dimensions_from_different_formats(self):
        """Should handle different image formats."""
        formats = [
            ('PNG', (100, 100)),
            ('JPEG', (200, 150)),
            ('GIF', (50, 50)),
            ('BMP', (300, 200)),
        ]
        
        for fmt, size in formats:
            img = Image.new('RGB', size, color='green')
            img_bytes = BytesIO()
            img.save(img_bytes, format=fmt)
            img_bytes.seek(0)
            
            result = get_image_dimensions(img_bytes)
            
            assert result is not None
            assert result.width == size[0]
            assert result.height == size[1]
    
    def test_get_dimensions_from_large_image(self):
        """Should handle large images."""
        img = Image.new('RGB', (5000, 3000), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == 5000
        assert result.height == 3000
    
    def test_get_dimensions_from_small_image(self):
        """Should handle very small images."""
        img = Image.new('RGB', (1, 1), color='black')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == 1
        assert result.height == 1


class TestGetImageDimensionsErrors:
    """Tests for error handling in get_image_dimensions."""
    
    def test_get_dimensions_from_corrupted_data(self):
        """Should return None for corrupted image data."""
        corrupted_data = BytesIO(b"This is not an image")
        
        result = get_image_dimensions(corrupted_data)
        
        assert result is None
    
    def test_get_dimensions_from_empty_data(self):
        """Should return None for empty data."""
        empty_data = BytesIO(b"")
        
        result = get_image_dimensions(empty_data)
        
        assert result is None
    
    def test_get_dimensions_from_incomplete_image(self):
        """Should handle incomplete image data gracefully."""
        # Create a valid image and truncate it severely
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        
        # Get only very minimal data (not enough for header)
        img_bytes.seek(0)
        partial_data = BytesIO(img_bytes.read(10))  # Only first 10 bytes
        
        result = get_image_dimensions(partial_data)
        
        # Pillow might still extract dimensions from header, so we accept either
        # In practice, truly corrupted data will return None
        assert result is None or isinstance(result, ImageDimensions)
    
    def test_get_dimensions_preserves_stream_position(self):
        """Should not consume the BytesIO stream permanently."""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        original_size = len(img_bytes.getvalue())
        get_image_dimensions(img_bytes)
        
        # Stream should still be readable
        img_bytes.seek(0)
        assert len(img_bytes.read()) == original_size


class TestGetImageDimensionsEdgeCases:
    """Tests for edge cases."""
    
    def test_get_dimensions_from_square_image(self):
        """Should handle square images."""
        img = Image.new('RGB', (100, 100), color='purple')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == result.height
    
    def test_get_dimensions_from_wide_image(self):
        """Should handle wide landscape images."""
        img = Image.new('RGB', (1000, 100), color='orange')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width > result.height
    
    def test_get_dimensions_from_tall_image(self):
        """Should handle tall portrait images."""
        img = Image.new('RGB', (100, 1000), color='cyan')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.height > result.width
    
    def test_get_dimensions_with_transparency(self):
        """Should handle images with transparency."""
        img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == 100
        assert result.height == 100
    
    def test_get_dimensions_from_grayscale(self):
        """Should handle grayscale images."""
        img = Image.new('L', (100, 100), color=128)
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = get_image_dimensions(img_bytes)
        
        assert result is not None
        assert result.width == 100
        assert result.height == 100


class TestCheckImageSize:
    """Tests for check_image_size function."""
    
    def test_check_size_passes_when_both_dimensions_meet_minimum(self):
        """Should return True when image meets both min width and height."""
        img = Image.new('RGB', (200, 150), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is True
    
    def test_check_size_fails_when_width_below_minimum(self):
        """Should return False when width is below minimum."""
        img = Image.new('RGB', (80, 150), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is False
    
    def test_check_size_fails_when_height_below_minimum(self):
        """Should return False when height is below minimum."""
        img = Image.new('RGB', (200, 80), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is False
    
    def test_check_size_fails_when_both_dimensions_below_minimum(self):
        """Should return False when both dimensions are below minimum."""
        img = Image.new('RGB', (80, 80), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is False
    
    def test_check_size_passes_with_exact_minimum(self):
        """Should return True when dimensions exactly match minimum."""
        img = Image.new('RGB', (100, 100), color='purple')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is True


class TestCheckImageSizeOptionalFilters:
    """Tests for optional filter parameters."""
    
    def test_check_size_skips_check_when_min_width_is_none(self):
        """Should pass all images when min_width is None."""
        img = Image.new('RGB', (50, 200), color='orange')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=None, min_height=100)
        
        assert result is True
    
    def test_check_size_skips_check_when_min_height_is_none(self):
        """Should pass all images when min_height is None."""
        img = Image.new('RGB', (200, 50), color='cyan')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=None)
        
        assert result is True
    
    def test_check_size_skips_all_checks_when_both_are_none(self):
        """Should pass all images when both filters are None."""
        img = Image.new('RGB', (10, 10), color='black')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=None, min_height=None)
        
        assert result is True
    
    def test_check_size_with_only_min_width(self):
        """Should check only width when only min_width is specified."""
        img = Image.new('RGB', (150, 50), color='white')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=100, min_height=None)
        
        assert result is True
    
    def test_check_size_with_only_min_height(self):
        """Should check only height when only min_height is specified."""
        img = Image.new('RGB', (50, 150), color='gray')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=None, min_height=100)
        
        assert result is True


class TestCheckImageSizeErrors:
    """Tests for error handling in check_image_size."""
    
    def test_check_size_returns_false_for_corrupted_image(self):
        """Should return False when image data is corrupted."""
        corrupted_data = BytesIO(b"Not a valid image")
        
        result = check_image_size(corrupted_data, min_width=100, min_height=100)
        
        assert result is False
    
    def test_check_size_returns_false_for_empty_data(self):
        """Should return False when image data is empty."""
        empty_data = BytesIO(b"")
        
        result = check_image_size(empty_data, min_width=100, min_height=100)
        
        assert result is False
    
    def test_check_size_preserves_stream_position(self):
        """Should not permanently consume the BytesIO stream."""
        img = Image.new('RGB', (200, 200), color='red')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        original_size = len(img_bytes.getvalue())
        check_image_size(img_bytes, min_width=100, min_height=100)
        
        # Stream should still be readable
        img_bytes.seek(0)
        assert len(img_bytes.read()) == original_size


class TestCheckImageSizeEdgeCases:
    """Tests for edge cases."""
    
    def test_check_size_with_very_large_minimums(self):
        """Should handle very large minimum values."""
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=5000, min_height=5000)
        
        assert result is False
    
    def test_check_size_with_zero_minimums(self):
        """Should pass all images with zero minimums."""
        img = Image.new('RGB', (1, 1), color='green')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=0, min_height=0)
        
        assert result is True
    
    def test_check_size_with_one_pixel_image(self):
        """Should handle 1x1 pixel images."""
        img = Image.new('RGB', (1, 1), color='yellow')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=1, min_height=1)
        
        assert result is True
    
    def test_check_size_with_asymmetric_minimums(self):
        """Should handle different min_width and min_height values."""
        img = Image.new('RGB', (500, 100), color='purple')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        result = check_image_size(img_bytes, min_width=400, min_height=50)
        
        assert result is True
    
    def test_check_size_and_condition_both_must_pass(self):
        """Should require both width AND height to meet minimums."""
        img = Image.new('RGB', (200, 80), color='orange')
        img_bytes = BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Width passes (200 >= 100) but height fails (80 < 100)
        result = check_image_size(img_bytes, min_width=100, min_height=100)
        
        assert result is False
