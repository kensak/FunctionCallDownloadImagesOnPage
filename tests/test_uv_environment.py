"""Test uv environment setup and configuration for uv package migration."""
import subprocess
import sys
from pathlib import Path


def test_uv_lock_exists():
    """Test that uv.lock file is generated after uv sync."""
    lock_path = Path(__file__).parent.parent / "uv.lock"
    assert lock_path.exists(), "uv.lock should exist after uv sync"


def test_production_dependencies_installed():
    """Test that production dependencies are installed in the environment."""
    # Check if production dependencies can be imported
    try:
        import requests
        import bs4
        import lxml
        from PIL import Image
        assert True, "All production dependencies are available"
    except ImportError as e:
        assert False, f"Production dependency missing: {e}"


def test_development_dependencies_installed():
    """Test that development dependencies are installed with --group dev."""
    # Check if development dependencies can be imported
    try:
        import pytest
        import pytest_cov
        import pytest_mock
        assert True, "All development dependencies are available"
    except ImportError as e:
        assert False, f"Development dependency missing: {e}"


def test_venv_directory_exists():
    """Test that .venv directory exists."""
    venv_path = Path(__file__).parent.parent / ".venv"
    assert venv_path.exists(), ".venv directory should exist"
    assert venv_path.is_dir(), ".venv should be a directory"


def test_python_version_requirement():
    """Test that Python version meets the minimum requirement (>=3.11)."""
    version_info = sys.version_info
    assert version_info >= (3, 11), f"Python version should be >= 3.11, got {version_info.major}.{version_info.minor}"
