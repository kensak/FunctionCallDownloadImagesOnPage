"""Test pyproject.toml configuration for uv package migration."""
import tomllib
from pathlib import Path


def test_pyproject_toml_exists():
    """Test that pyproject.toml file exists."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml should exist"


def test_project_metadata():
    """Test project metadata is correctly defined."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    # Test basic metadata
    assert "project" in config
    project = config["project"]
    
    assert project["name"] == "download-images-on-page"
    assert project["version"] == "0.1.0"
    assert "description" in project
    assert project["readme"] == "README.md"
    assert project["requires-python"] == ">=3.11"


def test_project_license_and_authors():
    """Test license and authors are correctly set."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    project = config["project"]
    
    # Test license
    assert "license" in project
    assert project["license"]["text"] == "MIT"
    
    # Test authors
    assert "authors" in project
    assert len(project["authors"]) > 0
    assert project["authors"][0]["name"] == "Ken Sakakibara"


def test_project_classifiers():
    """Test PyPI classifiers are defined."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    project = config["project"]
    
    assert "classifiers" in project
    classifiers = project["classifiers"]
    
    # Check for required classifier categories
    assert any("Development Status" in c for c in classifiers)
    assert any("Intended Audience" in c for c in classifiers)
    assert any("License :: OSI Approved :: MIT License" in c for c in classifiers)
    assert any("Programming Language :: Python :: 3" in c for c in classifiers)
    assert any("Topic ::" in c for c in classifiers)


def test_build_system():
    """Test build system is configured with hatchling."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    assert "build-system" in config
    build_system = config["build-system"]
    
    assert build_system["requires"] == ["hatchling"]
    assert build_system["build-backend"] == "hatchling.build"


def test_hatch_build_config():
    """Test hatch build configuration specifies packages."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    assert "tool" in config
    assert "hatch" in config["tool"]
    assert "build" in config["tool"]["hatch"]
    assert "targets" in config["tool"]["hatch"]["build"]
    assert "wheel" in config["tool"]["hatch"]["build"]["targets"]
    
    wheel_config = config["tool"]["hatch"]["build"]["targets"]["wheel"]
    assert "packages" in wheel_config
    assert "DownloadImagesOnPage" in wheel_config["packages"]



def test_cli_entry_point():
    """Test CLI entry point is defined."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    project = config["project"]
    
    assert "scripts" in project
    scripts = project["scripts"]
    
    assert "DownloadImagesOnPage" in scripts
    assert scripts["DownloadImagesOnPage"] == "DownloadImagesOnPage.main:main"


def test_production_dependencies():
    """Test production dependencies are correctly defined in [project.dependencies]."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    project = config["project"]
    
    assert "dependencies" in project
    deps = project["dependencies"]
    
    # Check required production dependencies
    assert any("requests" in dep for dep in deps)
    assert any("beautifulsoup4" in dep for dep in deps)
    assert any("lxml" in dep for dep in deps)
    assert any("Pillow" in dep for dep in deps)
    
    # Check version constraints
    assert any("requests>=2.31.0" in dep for dep in deps)
    assert any("beautifulsoup4>=4.12.0" in dep for dep in deps)
    assert any("lxml>=5.0.0" in dep for dep in deps)
    assert any("Pillow>=10.0.0" in dep for dep in deps)


def test_development_dependencies_separated():
    """Test development dependencies are separated in [dependency-groups.dev]."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    # Check that dependency-groups section exists
    assert "dependency-groups" in config, "[dependency-groups] section should exist"
    dep_groups = config["dependency-groups"]
    
    # Check that dev group exists
    assert "dev" in dep_groups, "dev group should exist in dependency-groups"
    dev_deps = dep_groups["dev"]
    
    # Check development dependencies
    assert any("pytest" in dep for dep in dev_deps)
    assert any("pytest-cov" in dep for dep in dev_deps)
    assert any("pytest-mock" in dep for dep in dev_deps)
    
    # Check version constraints
    assert any("pytest>=7.4.0" in dep for dep in dev_deps)
    assert any("pytest-cov>=4.1.0" in dep for dep in dev_deps)
    assert any("pytest-mock>=3.12.0" in dep for dep in dev_deps)


def test_dev_dependencies_not_in_production():
    """Test that development dependencies are NOT in production dependencies."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    
    with open(pyproject_path, "rb") as f:
        config = tomllib.load(f)
    
    project = config["project"]
    prod_deps = project.get("dependencies", [])
    
    # Ensure test/dev tools are not in production dependencies
    assert not any("pytest" in dep for dep in prod_deps), "pytest should not be in production dependencies"
    assert not any("pytest-cov" in dep for dep in prod_deps), "pytest-cov should not be in production dependencies"
    assert not any("pytest-mock" in dep for dep in prod_deps), "pytest-mock should not be in production dependencies"
