"""Test backward compatibility with python -m execution."""
import subprocess
import sys
from pathlib import Path


def test_python_m_help_works():
    """Test that 'python -m DownloadImagesOnPage --help' works."""
    result = subprocess.run(
        [sys.executable, "-m", "DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0, f"Command failed with: {result.stderr}"
    assert "usage:" in result.stdout.lower(), "Help message should contain usage information"
    assert "DownloadImagesOnPage" in result.stdout, "Help should mention the command name"


def test_python_m_shows_required_arguments():
    """Test that help shows required arguments (URL and output directory)."""
    result = subprocess.run(
        [sys.executable, "-m", "DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    # Check for positional arguments
    assert "url" in result.stdout.lower(), "Help should mention URL argument"
    assert "output" in result.stdout.lower() or "dir" in result.stdout.lower(), "Help should mention output directory"


def test_python_m_shows_optional_arguments():
    """Test that help shows all optional CLI arguments."""
    result = subprocess.run(
        [sys.executable, "-m", "DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    # Check for optional arguments
    assert "--min-width" in result.stdout, "Help should show --min-width option"
    assert "--min-height" in result.stdout, "Help should show --min-height option"
    assert "--verbose" in result.stdout or "-v" in result.stdout, "Help should show --verbose option"


def test_python_m_without_args_shows_error():
    """Test that running without arguments shows appropriate error."""
    result = subprocess.run(
        [sys.executable, "-m", "DownloadImagesOnPage"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Should fail without required arguments
    assert result.returncode != 0, "Should fail when required arguments are missing"
    # Should show error or usage message
    assert len(result.stderr) > 0 or "usage:" in result.stdout.lower(), "Should show error or usage message"


def test_main_py_has_main_function():
    """Test that main.py has a main() function that can be called."""
    from DownloadImagesOnPage.main import main
    
    # Verify the function exists and is callable
    assert callable(main), "main() function should exist and be callable"
