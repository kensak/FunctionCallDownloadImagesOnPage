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
from .fetcher import fetch_html
from .parser import extract_image_urls
from .downloader import download_image
from .filter import check_image_size, get_image_dimensions
from .file_manager import generate_unique_filename, save_image
from .exceptions import DownloadError, FileWriteError

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
            if config.min_width is not None or config.min_height is not None:
                passes_filter = check_image_size(image_data, config.min_width, config.min_height)
                
                if not passes_filter:
                    # Get dimensions for logging
                    dimensions = get_image_dimensions(image_data)
                    if dimensions:
                        logger.info(
                            f"Filtered out: {url} "
                            f"(size: {dimensions.width}x{dimensions.height}, "
                            f"required: {config.min_width or 'any'}x{config.min_height or 'any'})"
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
