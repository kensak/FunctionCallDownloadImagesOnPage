"""Test uv tool installation and CLI execution."""
import subprocess
import sys
import shutil
from pathlib import Path


def test_uv_tool_install_succeeds():
    """Test that 'uv tool install' succeeds."""
    # First uninstall if exists to ensure clean state
    subprocess.run(["uv", "tool", "uninstall", "download-images-on-page"], 
                   capture_output=True, timeout=30)
    
    # Install from local directory
    result = subprocess.run(
        ["uv", "tool", "install", "--force", "."],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"uv tool install failed: {result.stderr}"


def test_command_available_in_path():
    """Test that DownloadImagesOnPage command is available in PATH."""
    # Check if command exists using 'where' on Windows
    result = subprocess.run(
        ["where", "DownloadImagesOnPage"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0, "DownloadImagesOnPage command should be in PATH"
    assert "DownloadImagesOnPage" in result.stdout, "Command path should be returned"


def test_installed_cli_help_works():
    """Test that installed CLI --help works."""
    result = subprocess.run(
        ["DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0, f"CLI help failed: {result.stderr}"
    assert "usage:" in result.stdout.lower(), "Help should show usage"
    assert "DownloadImagesOnPage" in result.stdout, "Help should mention command name"


def test_installed_cli_shows_options():
    """Test that installed CLI shows all expected options."""
    result = subprocess.run(
        ["DownloadImagesOnPage", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    assert result.returncode == 0
    assert "--min-width" in result.stdout, "Should show --min-width option"
    assert "--min-height" in result.stdout, "Should show --min-height option"
    assert "--verbose" in result.stdout or "-v" in result.stdout, "Should show --verbose option"


def test_installed_cli_requires_arguments():
    """Test that installed CLI requires URL and output directory."""
    result = subprocess.run(
        ["DownloadImagesOnPage"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    # Should fail without required arguments
    assert result.returncode != 0, "Should fail when required arguments are missing"


def test_installed_cli_accepts_valid_arguments():
    """Test that installed CLI accepts valid arguments (dry run check)."""
    # Just test that it accepts the arguments structure (will fail on network, but that's OK)
    result = subprocess.run(
        ["DownloadImagesOnPage", "https://example.com", "test_output", "--min-width", "100"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # We expect it might fail on network/parsing, but not on argument parsing
    # If it fails on argument parsing, returncode would be 2 typically
    # Network/fetch errors are typically returncode 1
    assert result.returncode != 2, f"Should accept valid arguments: {result.stderr}"
