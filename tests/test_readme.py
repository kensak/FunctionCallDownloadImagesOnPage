from pathlib import Path


def test_readme_contains_required_sections():
    """README should document setup, usage, options, and troubleshooting (Task 14.1)."""
    base_dir = Path(__file__).parent.parent
    readme_path = base_dir / "README.md"

    content = readme_path.read_text(encoding="utf-8")

    # High-level project description
    assert "Image Downloader" in content or "画像" in content

    # venv/.venv setup instructions
    assert "python -m venv" in content
    assert ".venv" in content  # this repo uses .venv

    # dependency installation
    assert "pip install -r requirements.txt" in content

    # basic usage and examples
    assert "python -m DownloadImagesOnPage" in content
    assert "使用例" in content or "Example" in content

    # options
    assert "--min-width" in content
    assert "--min-height" in content
    assert "--verbose" in content

    # troubleshooting
    assert "トラブルシューティング" in content
