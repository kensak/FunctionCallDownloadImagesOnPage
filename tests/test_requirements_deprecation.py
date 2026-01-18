"""Test requirements.txt deprecation or removal."""
from pathlib import Path


def test_requirements_txt_deprecated_or_removed():
    """Test that requirements.txt is either removed or contains deprecation notice."""
    base_dir = Path(__file__).parent.parent
    requirements_path = base_dir / "requirements.txt"
    
    if requirements_path.exists():
        # If it exists, it should contain a deprecation notice
        content = requirements_path.read_text(encoding="utf-8")
        
        # Should mention deprecation or migration
        assert any(keyword in content.lower() for keyword in ["deprecated", "非推奨", "移行", "pyproject.toml"]), \
            "requirements.txt should contain deprecation notice mentioning pyproject.toml"
        
        # Should reference pyproject.toml
        assert "pyproject.toml" in content.lower(), "requirements.txt should reference pyproject.toml"
    else:
        # If removed, that's also acceptable
        assert True, "requirements.txt has been removed (acceptable)"


def test_pyproject_toml_has_all_dependencies():
    """Test that pyproject.toml contains all necessary dependencies."""
    base_dir = Path(__file__).parent.parent
    pyproject_path = base_dir / "pyproject.toml"
    
    assert pyproject_path.exists(), "pyproject.toml should exist"
    
    content = pyproject_path.read_text(encoding="utf-8")
    
    # Check production dependencies
    assert "requests" in content, "pyproject.toml should contain requests"
    assert "beautifulsoup4" in content, "pyproject.toml should contain beautifulsoup4"
    assert "lxml" in content, "pyproject.toml should contain lxml"
    assert "Pillow" in content or "pillow" in content, "pyproject.toml should contain Pillow"
    
    # Check dev dependencies
    assert "pytest" in content, "pyproject.toml should contain pytest"
    assert "pytest-cov" in content, "pyproject.toml should contain pytest-cov"
    assert "pytest-mock" in content, "pyproject.toml should contain pytest-mock"
