from pathlib import Path


def test_readme_contains_required_sections():
    """README should document setup, usage, options, and troubleshooting (Task 14.1)."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"

    content = readme_path.read_text(encoding="utf-8")

    # High-level project description
    assert "Image Downloader" in content or "画像" in content

    # basic usage and examples
    assert "python -m DownloadImagesOnPage" in content
    assert "使用例" in content or "Example" in content

    # options
    assert "--min-width" in content
    assert "--min-height" in content
    assert "--verbose" in content

    # troubleshooting
    assert "トラブルシューティング" in content


def test_readme_contains_uv_requirements():
    """README should mention Python 3.11+ and uv installation."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"
    
    content = readme_path.read_text(encoding="utf-8")
    
    # Python version requirement
    assert "Python 3.11" in content, "Should mention Python 3.11+"
    
    # uv installation link
    assert "uv" in content.lower(), "Should mention uv package manager"
    assert "https://docs.astral.sh/uv" in content or "astral.sh/uv" in content, "Should link to uv installation docs"


def test_readme_contains_uv_tool_install():
    """README should document uv tool install method."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"
    
    content = readme_path.read_text(encoding="utf-8")
    
    # uv tool install
    assert "uv tool install" in content, "Should document uv tool install"
    assert "download-images-on-page" in content, "Should mention package name"


def test_readme_contains_uvx_usage():
    """README should document uvx temporary execution."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"
    
    content = readme_path.read_text(encoding="utf-8")
    
    # uvx execution
    assert "uvx" in content, "Should document uvx usage"
    assert "DownloadImagesOnPage" in content, "Should show command name"


def test_readme_contains_dev_setup_with_uv():
    """README should document development setup with uv sync."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"
    
    content = readme_path.read_text(encoding="utf-8")
    
    # uv sync for development
    assert "uv sync" in content, "Should document uv sync"
    assert "--group dev" in content or "dev" in content, "Should mention dev dependencies"


def test_readme_contains_backward_compatibility():
    """README should maintain python -m execution method for backward compatibility."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"
    
    content = readme_path.read_text(encoding="utf-8")
    
    # Backward compatible method
    assert "python -m DownloadImagesOnPage" in content, "Should maintain python -m method for backward compatibility"

