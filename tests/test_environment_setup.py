"""Test to verify project environment setup is complete."""
import sys
import subprocess
from pathlib import Path


def test_python_version():
    """Verify Python version is 3.11 or higher."""
    assert sys.version_info >= (3, 11), f"Python 3.11+ required, got {sys.version}"


def test_required_packages_installed():
    """Verify all required packages are installed."""
    required_packages = [
        'requests',
        'beautifulsoup4',
        'lxml',
        'Pillow',
        'pytest',
        'pytest-cov',
        'pytest-mock'
    ]
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        pytest.skip("pip command failed - skipping package check")
        return
    
    installed_packages = result.stdout.lower()
    
    for package in required_packages:
        # Handle package name variations (Pillow vs pillow, beautifulsoup4 vs bs4)
        assert package.lower().replace('-', '_') in installed_packages or \
               package.lower().replace('_', '-') in installed_packages, \
               f"Package {package} not installed"


def test_project_structure():
    """Verify project directory structure exists."""
    base_dir = Path(__file__).parent.parent
    
    required_dirs = [
        base_dir / 'DownloadImagesOnPage',
        base_dir / 'tests',
        base_dir / '.venv',
    ]
    
    for directory in required_dirs:
        assert directory.exists(), f"Directory {directory} does not exist"
        assert directory.is_dir(), f"{directory} is not a directory"


def test_required_files():
    """Verify required configuration files exist."""
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        base_dir / 'requirements.txt',
        base_dir / '.gitignore',
        base_dir / 'README.md',
        base_dir / 'DownloadImagesOnPage' / '__init__.py',
        base_dir / 'tests' / '__init__.py',
    ]
    
    for file_path in required_files:
        assert file_path.exists(), f"File {file_path} does not exist"
        assert file_path.is_file(), f"{file_path} is not a file"


def test_requirements_txt_content():
    """Verify requirements.txt contains all necessary packages."""
    base_dir = Path(__file__).parent.parent
    requirements_file = base_dir / 'requirements.txt'
    
    content = requirements_file.read_text()
    
    required_packages = [
        'requests',
        'beautifulsoup4',
        'lxml',
        'Pillow',
        'pytest'
    ]
    
    for package in required_packages:
        assert package in content, f"Package {package} not found in requirements.txt"


def test_gitignore_content():
    """Verify .gitignore contains necessary patterns."""
    base_dir = Path(__file__).parent.parent
    gitignore_file = base_dir / '.gitignore'
    
    content = gitignore_file.read_text()
    
    required_patterns = [
        'venv/',
        '__pycache__',
        '.pytest_cache'
    ]
    
    for pattern in required_patterns:
        assert pattern in content, f"Pattern {pattern} not found in .gitignore"
