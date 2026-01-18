"""Test package build and distribution."""
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


def test_uv_build_command_succeeds():
    """Test that 'uv build' command succeeds."""
    result = subprocess.run(
        ["uv", "build"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    assert result.returncode == 0, f"uv build failed: {result.stderr}"


def test_dist_directory_exists():
    """Test that dist/ directory is created."""
    dist_path = Path(__file__).parent.parent / "dist"
    assert dist_path.exists(), "dist/ directory should exist after build"
    assert dist_path.is_dir(), "dist/ should be a directory"


def test_wheel_file_exists():
    """Test that .whl wheel file is generated."""
    dist_path = Path(__file__).parent.parent / "dist"
    wheel_files = list(dist_path.glob("*.whl"))
    
    assert len(wheel_files) > 0, "At least one .whl file should be generated"
    
    # Check wheel filename format
    wheel_file = wheel_files[0]
    assert "download_images_on_page" in wheel_file.name.lower(), "Wheel filename should contain package name"
    assert "0.1.0" in wheel_file.name, "Wheel filename should contain version"


def test_sdist_tar_gz_exists():
    """Test that .tar.gz source distribution is generated."""
    dist_path = Path(__file__).parent.parent / "dist"
    sdist_files = list(dist_path.glob("*.tar.gz"))
    
    assert len(sdist_files) > 0, "At least one .tar.gz file should be generated"
    
    # Check sdist filename format
    sdist_file = sdist_files[0]
    assert "download_images_on_page" in sdist_file.name.lower(), "Sdist filename should contain package name"
    assert "0.1.0" in sdist_file.name, "Sdist filename should contain version"


def test_wheel_contains_metadata():
    """Test that wheel contains proper METADATA."""
    dist_path = Path(__file__).parent.parent / "dist"
    wheel_files = list(dist_path.glob("*.whl"))
    
    assert len(wheel_files) > 0, "Wheel file should exist"
    
    wheel_file = wheel_files[0]
    with zipfile.ZipFile(wheel_file, 'r') as whl:
        # Find METADATA file
        metadata_files = [f for f in whl.namelist() if f.endswith('/METADATA')]
        assert len(metadata_files) > 0, "Wheel should contain METADATA file"
        
        # Read and verify METADATA content
        metadata_content = whl.read(metadata_files[0]).decode('utf-8')
        assert "Name: download-images-on-page" in metadata_content, "METADATA should contain package name"
        assert "Version: 0.1.0" in metadata_content, "METADATA should contain version"
        assert "Author: Ken Sakakibara" in metadata_content, "METADATA should contain author"


def test_wheel_contains_entry_points():
    """Test that wheel contains entry_points.txt with CLI command."""
    dist_path = Path(__file__).parent.parent / "dist"
    wheel_files = list(dist_path.glob("*.whl"))
    
    assert len(wheel_files) > 0, "Wheel file should exist"
    
    wheel_file = wheel_files[0]
    with zipfile.ZipFile(wheel_file, 'r') as whl:
        # Find entry_points.txt
        entry_points_files = [f for f in whl.namelist() if f.endswith('/entry_points.txt')]
        assert len(entry_points_files) > 0, "Wheel should contain entry_points.txt"
        
        # Read and verify entry_points.txt content
        entry_points_content = whl.read(entry_points_files[0]).decode('utf-8')
        assert "[console_scripts]" in entry_points_content, "entry_points.txt should have [console_scripts] section"
        assert "DownloadImagesOnPage" in entry_points_content, "entry_points.txt should contain CLI command name"
        assert "DownloadImagesOnPage.main:main" in entry_points_content, "entry_points.txt should reference main function"


def test_sdist_contains_source_files():
    """Test that source distribution contains source files."""
    dist_path = Path(__file__).parent.parent / "dist"
    sdist_files = list(dist_path.glob("*.tar.gz"))
    
    assert len(sdist_files) > 0, "Sdist file should exist"
    
    sdist_file = sdist_files[0]
    with tarfile.open(sdist_file, 'r:gz') as tar:
        filenames = tar.getnames()
        
        # Check for essential files
        assert any("pyproject.toml" in f for f in filenames), "Sdist should contain pyproject.toml"
        assert any("README.md" in f for f in filenames), "Sdist should contain README.md"
        assert any("DownloadImagesOnPage" in f for f in filenames), "Sdist should contain package directory"
