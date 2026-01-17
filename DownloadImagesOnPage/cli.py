"""Command-line interface for image downloader.

This module handles parsing and validation of command-line arguments.
It uses argparse to define the CLI interface and returns a type-safe
CLIConfig dataclass.

Key Features:
- URL validation (http/https only)
- Positive integer validation for size filters
- Type-safe configuration object
- Comprehensive help messages

Example:
    python -m DownloadImagesOnPage https://example.com ./output --min-width 800
"""
import argparse
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from .models import CLIConfig


def _validate_url(url: str) -> str:
    """Validate URL has http or https scheme.
    
    Args:
        url: URL to validate
        
    Returns:
        The validated URL
        
    Raises:
        argparse.ArgumentTypeError: If URL scheme is invalid
        
    Example:
        >>> _validate_url('https://example.com')
        'https://example.com'
        >>> _validate_url('ftp://example.com')
        ArgumentTypeError: Invalid URL scheme
    """
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise argparse.ArgumentTypeError(
            f"Invalid URL scheme: '{parsed.scheme}'. "
            f"Only 'http' and 'https' are supported."
        )
    return url


def _validate_positive_int(value: str) -> int:
    """Validate value is a positive integer.
    
    Args:
        value: String value to validate
        
    Returns:
        The validated positive integer
        
    Raises:
        argparse.ArgumentTypeError: If value is not a positive integer
        
    Example:
        >>> _validate_positive_int('800')
        800
        >>> _validate_positive_int('-100')
        ArgumentTypeError: Value must be positive
    """
    try:
        int_value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid integer value: '{value}'")
    
    if int_value <= 0:
        raise argparse.ArgumentTypeError(
            f"Value must be positive, got: {int_value}"
        )
    
    return int_value


def _validate_output_dir(path: str) -> str:
    """Validate output directory path.
    
    Args:
        path: Directory path to validate
        
    Returns:
        The validated directory path
        
    Raises:
        argparse.ArgumentTypeError: If path is invalid
        
    Example:
        >>> _validate_output_dir('/tmp/output')
        '/tmp/output'
        >>> _validate_output_dir('')
        ArgumentTypeError: Path cannot be empty
    """
    if not path or not path.strip():
        raise argparse.ArgumentTypeError("Output directory path cannot be empty")
    
    # Check if path exists and is a file (not a directory)
    path_obj = Path(path)
    if path_obj.exists() and path_obj.is_file():
        raise argparse.ArgumentTypeError(
            f"Path '{path}' exists but is a file, not a directory"
        )
    
    # Path is valid (either doesn't exist yet, or exists and is a directory)
    return path


def parse_arguments() -> CLIConfig:
    """Parse command-line arguments and return CLIConfig.
    
    This function creates an argument parser, defines all CLI arguments,
    validates them, and returns a type-safe CLIConfig object.
    
    Required Arguments:
        url: Webpage URL to download images from (http/https)
        output_dir: Directory to save downloaded images
        
    Optional Arguments:
        --min-width: Minimum image width in pixels
        --min-height: Minimum image height in pixels
        --verbose: Enable verbose output
        --help/-h: Show help message
    
    Returns:
        CLIConfig with parsed and validated arguments
        
    Raises:
        SystemExit: If arguments are invalid (exit code != 0)
                   or --help is requested (exit code 0)
        
    Example:
        With sys.argv = ['script', 'https://example.com', './output']:
        >>> config = parse_arguments()
        >>> config.url
        'https://example.com'
        >>> config.output_dir
        Path('./output')
    """
    parser = argparse.ArgumentParser(
        prog='DownloadImagesOnPage',
        description='Download all images from a webpage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python -m DownloadImagesOnPage https://example.com ./images

  # With size filtering
  python -m DownloadImagesOnPage https://example.com ./images --min-width 800 --min-height 600

  # Verbose mode
  python -m DownloadImagesOnPage https://example.com ./images --verbose
'''
    )
    
    # Required positional arguments
    parser.add_argument(
        'url',
        type=_validate_url,
        help='URL of the webpage to download images from (http or https)'
    )
    
    parser.add_argument(
        'output_dir',
        type=_validate_output_dir,
        help='Directory to save downloaded images'
    )
    
    # Optional arguments
    parser.add_argument(
        '--min-width',
        type=_validate_positive_int,
        metavar='PIXELS',
        help='Minimum image width in pixels (filter out smaller images)'
    )
    
    parser.add_argument(
        '--min-height',
        type=_validate_positive_int,
        metavar='PIXELS',
        help='Minimum image height in pixels (filter out smaller images)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert to CLIConfig dataclass for type safety
    config = CLIConfig(
        url=args.url,
        output_dir=Path(args.output_dir),
        min_width=args.min_width,
        min_height=args.min_height,
        verbose=args.verbose
    )
    
    return config
