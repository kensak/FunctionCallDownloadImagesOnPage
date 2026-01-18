"""Test uvx temporary execution."""
import subprocess
import sys


def test_uvx_help_works_with_local_package():
    """Test that 'uvx --from . DownloadImagesOnPage --help' works."""
    result = subprocess.run(
        ["uvx", "--from", ".", "DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"uvx help failed: {result.stderr}"
    assert "usage:" in result.stdout.lower(), "Help should show usage"
    assert "DownloadImagesOnPage" in result.stdout, "Help should mention command name"


def test_uvx_shows_all_options():
    """Test that uvx execution shows all CLI options."""
    result = subprocess.run(
        ["uvx", "--from", ".", "DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0
    assert "--min-width" in result.stdout, "Should show --min-width option"
    assert "--min-height" in result.stdout, "Should show --min-height option"
    assert "--verbose" in result.stdout or "-v" in result.stdout, "Should show --verbose option"


def test_uvx_requires_arguments():
    """Test that uvx execution requires proper arguments."""
    result = subprocess.run(
        ["uvx", "--from", ".", "DownloadImagesOnPage"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Should fail without required arguments (URL and output directory)
    assert result.returncode != 0, "Should fail when required arguments are missing"


def test_uvx_accepts_valid_arguments():
    """Test that uvx accepts valid arguments structure."""
    # Just test argument acceptance (will fail on network, but that's expected)
    result = subprocess.run(
        ["uvx", "--from", ".", "DownloadImagesOnPage", "https://example.com", "test_output"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # We expect network/parsing failure, not argument parsing failure
    # Argument parsing errors typically return exit code 2
    assert result.returncode != 2, f"Should accept valid arguments: {result.stderr}"
