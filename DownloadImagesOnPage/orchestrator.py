"""Download orchestrator module.

This module coordinates the entire download workflow by integrating
all components: HTML fetching, image parsing, filtering, downloading,
and file management.
"""
import logging
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from .models import CLIConfig, DownloadResult, DownloadStatus, ImageDownloadRecord, ImageDimensions
from .fetcher import fetch_html, fetch_html_playwright, capture_rendered_images_sync
from .parser import extract_image_urls
from .downloader import download_image
from .filter import check_image_size, get_image_dimensions
from .file_manager import generate_unique_filename, save_image
from .exceptions import DownloadError, FileWriteError
from io import BytesIO

# Module logger
logger = logging.getLogger(__name__)


def run_download(config: CLIConfig) -> DownloadResult:
    """Run the complete download workflow.
    
    Args:
        config: CLI configuration with URL, output directory, and filters
        
    Returns:
        DownloadResult with summary statistics
        
    Raises:
        FetchError: If HTML fetch fails (fatal error)
    """
    # Playwrightモードの場合は別のワークフロー
    if config.use_playwright:
        return run_download_with_playwright(config)
    
    # Step 1: Fetch HTML (fatal error if fails)
    logger.info(f"Fetching HTML from {config.url}")
    html = fetch_html(config.url)
    
    # Step 2: Extract image URLs
    logger.info("Parsing HTML for image URLs")
    image_urls = extract_image_urls(html, config.url)
    
    total_count = len(image_urls)
    logger.info(f"Found {total_count} image(s)")
    
    if total_count == 0:
        return DownloadResult(
            success_count=0,
            failed_count=0,
            filtered_count=0,
            total_count=0
        )
    
    # Step 3: Process each image
    success_count = 0
    failed_count = 0
    filtered_count = 0
    
    for index, url in enumerate(image_urls, start=1):
        # Progress display
        logger.info(f"Processing {index}/{total_count}: {url}")
        
        try:
            # Download image
            image_data = download_image(url)
            
            # Check size filter
            if config.min_width is not None or config.min_height is not None or \
                config.max_width is not None or config.max_height is not None:
                passes_filter = check_image_size(image_data, config.min_width, config.min_height, config.max_width, config.max_height)
                
                if not passes_filter:
                    # Get dimensions for logging
                    dimensions = get_image_dimensions(image_data)
                    if dimensions:
                        logger.info(
                            f"Filtered out: {url} "
                            f"(size: {dimensions.width}x{dimensions.height}, "
                            f"required: {config.min_width or '*'}x{config.min_height or '*'}, "
                            f"max: {config.max_width or '*'}x{config.max_height or '*'})"
                        )
                    else:
                        logger.info(f"Filtered out: {url} (unable to determine size)")
                    filtered_count += 1
                    continue
            
            # Get dimensions for verbose logging
            dimensions = get_image_dimensions(image_data)
            
            # Generate filename from URL
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename:
                filename = f"image_{index}.jpg"
            
            # Generate unique filename
            unique_path = generate_unique_filename(config.output_dir, filename)
            
            # Save image
            save_image(image_data, unique_path)
            
            success_count += 1
            
            if config.verbose:
                if dimensions:
                    logger.info(
                        f"Success: {url} -> {unique_path} "
                        f"({dimensions.width}x{dimensions.height})"
                    )
                else:
                    logger.info(f"Success: {url} -> {unique_path}")
            else:
                logger.info(f"Downloaded: {unique_path.name}")
            
        except DownloadError as e:
            logger.warning(f"Failed to download: {url} - {e}")
            failed_count += 1
            continue
        except FileWriteError as e:
            logger.warning(f"Failed to save: {url} - {e}")
            failed_count += 1
            continue
        except Exception as e:
            logger.warning(f"Unexpected error for {url}: {e}")
            failed_count += 1
            continue
    
    # Step 4: Return summary
    result = DownloadResult(
        success_count=success_count,
        failed_count=failed_count,
        filtered_count=filtered_count,
        total_count=total_count
    )
    
    logger.info(
        f"Download complete: {success_count} succeeded, "
        f"{failed_count} failed, {filtered_count} filtered"
    )
    
    return result


def run_download_with_playwright(config: CLIConfig) -> DownloadResult:
    """Playwrightを使用してレンダリングされた画像を直接保存するワークフロー.
    
    Args:
        config: CLI configuration with URL, output directory, and filters
        
    Returns:
        DownloadResult with summary statistics
        
    Raises:
        FetchError: If page fetch fails (fatal error)
    """
    # Step 1: Playwrightで画像をキャプチャ
    logger.info(f"Capturing rendered images from {config.url} using Playwright")
    rendered_images = capture_rendered_images_sync(config.url)
    
    total_count = len(rendered_images)
    logger.info(f"Captured {total_count} rendered image(s)")
    
    if total_count == 0:
        return DownloadResult(
            success_count=0,
            failed_count=0,
            filtered_count=0,
            total_count=0
        )
    
    # Step 2: 各画像を処理
    success_count = 0
    failed_count = 0
    filtered_count = 0
    
    for index, rendered_image in enumerate(rendered_images, start=1):
        logger.info(f"Processing {index}/{total_count}: {rendered_image.original_url}")
        
        try:
            # サイズフィルタリング
            if config.min_width is not None or config.min_height is not None or \
                config.max_width is not None or config.max_height is not None:
                
                # BytesIOに変換してフィルタチェック
                image_bytes = BytesIO(rendered_image.image_data)
                passes_filter = check_image_size(
                    image_bytes, 
                    config.min_width, 
                    config.min_height,
                    config.max_width,
                    config.max_height
                )
                
                if not passes_filter:
                    logger.info(
                        f"Filtered out: {rendered_image.original_url} "
                        f"(size: {rendered_image.dimensions.width}x{rendered_image.dimensions.height}, "
                        f"required: {config.min_width or '*'}x{config.min_height or '*'}, "
                        f"max: {config.max_width or '*'}x{config.max_height or '*'})"
                    )
                    filtered_count += 1
                    continue
            
            # ユニークなファイル名を生成
            unique_path = generate_unique_filename(config.output_dir, rendered_image.filename)
            
            # BytesIOに変換して保存
            image_bytes = BytesIO(rendered_image.image_data)
            save_image(image_bytes, unique_path)
            
            success_count += 1
            logger.info(
                f"Saved: {unique_path.name} "
                f"({rendered_image.dimensions.width}x{rendered_image.dimensions.height})"
            )
            
        except FileWriteError as e:
            logger.warning(f"Failed to save {rendered_image.original_url}: {e}")
            failed_count += 1
            continue
        except Exception as e:
            logger.warning(f"Unexpected error for {rendered_image.original_url}: {e}")
            failed_count += 1
            continue
    
    # Step 3: Return summary
    result = DownloadResult(
        success_count=success_count,
        failed_count=failed_count,
        filtered_count=filtered_count,
        total_count=total_count
    )
    
    logger.info(
        f"Download complete: {success_count} succeeded, "
        f"{failed_count} failed, {filtered_count} filtered"
    )
    
    return result
