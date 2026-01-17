"""Main entry point for image downloader.

This module provides the main() function and command-line entry point.
It orchestrates the complete workflow: argument parsing, logging setup,
directory creation, and download execution.

Exit Codes:
    0: Success
    1: Argument error (invalid command-line arguments)
    2: Execution error (fetch error, file write error, etc.)
"""
import logging
import sys
from pathlib import Path

from .cli import parse_arguments
from .file_manager import ensure_directory
from .orchestrator import run_download
from .exceptions import FetchError, FileWriteError

# Module logger
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: If True, enable DEBUG level logging
                If False, enable INFO level logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )


def main() -> int:
    """Main entry point for the image downloader.
    
    This function:
    1. Parses command-line arguments
    2. Sets up logging
    3. Creates output directory
    4. Runs the download orchestrator
    5. Handles errors and returns appropriate exit codes
    
    Returns:
        Exit code:
            0: Success
            1: Argument error
            2: Execution error
    """
    try:
        # Parse arguments
        config = parse_arguments()
        
    except SystemExit as e:
        # argparse calls sys.exit() on error or --help
        # Exit code 0 means --help was requested (success)
        # Exit code != 0 means argument error
        if e.code == 0:
            return 0
        else:
            return 1
    
    # Setup logging
    setup_logging(verbose=config.verbose)
    
    try:
        # Ensure output directory exists
        logger.info(f"Output directory: {config.output_dir}")
        ensure_directory(config.output_dir)
        
        # Run download
        logger.info(f"Starting download from: {config.url}")
        result = run_download(config)
        
        # Display summary
        logger.info(
            f"Download complete: {result.success_count} succeeded, "
            f"{result.failed_count} failed, {result.filtered_count} filtered"
        )
        
        return 0
        
    except FetchError as e:
        logger.error(f"Failed to fetch URL: {e}")
        return 2
    
    except FileWriteError as e:
        logger.error(f"File operation error: {e}")
        return 2
    
    except KeyboardInterrupt:
        logger.info("\nOperation interrupted by user")
        return 0
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
