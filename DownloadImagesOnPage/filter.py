"""Image size filter module for checking image dimensions."""
from io import BytesIO
from typing import Optional
import logging
from PIL import Image, UnidentifiedImageError

from DownloadImagesOnPage.models import ImageDimensions


logger = logging.getLogger(__name__)


def get_image_dimensions(image_data: BytesIO) -> Optional[ImageDimensions]:
    """
    画像データから寸法を取得
    
    Args:
        image_data: 画像のバイトストリーム
        
    Returns:
        画像寸法、取得失敗時はNone
    """
    try:
        # Save current position
        original_position = image_data.tell()
        
        # Open image and get dimensions
        img = Image.open(image_data)
        width, height = img.size
        
        # Reset stream position
        image_data.seek(original_position)
        
        return ImageDimensions(width=width, height=height)
    except (UnidentifiedImageError, OSError, ValueError) as e:
        # Return None for any image processing errors
        return None
    except Exception:
        # Catch any other unexpected errors
        return None


def check_image_size(
    image_data: BytesIO,
    min_width: Optional[int],
    min_height: Optional[int],
    max_width: Optional[int],
    max_height: Optional[int]
) -> bool:
    """
    画像が最小サイズ条件を満たすかチェック
    
    Args:
        image_data: 画像のバイトストリーム
        min_width: 最小幅（Noneの場合はチェックしない）
        min_height: 最小高さ（Noneの場合はチェックしない）
        max_width: 最大幅（Noneの場合はチェックしない）
        max_height: 最大高さ（Noneの場合はチェックしない）
    Returns:
        True: 条件を満たす、False: 条件を満たさない
    """
    # If both filters are None, pass all images
    if min_width is None and min_height is None and max_width is None and max_height is None:
        return True
    
    # Get image dimensions
    dimensions = get_image_dimensions(image_data)
    
    # If failed to get dimensions, log warning and return False
    if dimensions is None:
        logger.warning("Failed to get image dimensions, filtering out image")
        return False
    
    # Check width if min_width is specified
    if min_width is not None and dimensions.width < min_width:
        return False
    
    # Check height if min_height is specified
    if min_height is not None and dimensions.height < min_height:
        return False

    # Check width if max_width is specified
    if max_width is not None and dimensions.width > max_width:
        return False

    # Check height if max_height is specified
    if max_height is not None and dimensions.height > max_height:
        return False
    
    return True
