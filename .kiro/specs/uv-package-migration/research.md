# Research & Design Decisions

---
**Purpose**: Capture discovery findings, architectural investigations, and rationale that inform the technical design.

**Usage**:
- Log research activities and outcomes during the discovery phase.
- Document design decision trade-offs that are too detailed for `design.md`.
- Provide references and evidence for future audits or reuse.
---

## Summary
- **Feature**: `uv-package-migration`
- **Discovery Scope**: Extension (existing codebase migrating to uv package structure)
- **Key Findings**:
  - uv supports modern Python packaging with `pyproject.toml` standard (PEP 517/518)
  - CLI entry points defined via `[project.scripts]` enable `uv tool install` and `uvx` execution
  - Development dependencies separated via `[dependency-groups.dev]` or `[project.optional-dependencies.dev]`
  - Existing `DownloadImagesOnPage` module structure can be preserved for backward compatibility
  - Build system choice: hatchling (modern, minimal config) vs setuptools (traditional, well-established)

## Research Log

### Topic: uv Package Manager Ecosystem
- **Context**: Need to understand uv's package structure requirements and best practices for tool installation
- **Sources Consulted**: 
  - [uv Official Documentation - Configuring Projects](https://docs.astral.sh/uv/concepts/projects/config/)
  - [Real Python - Managing Python Projects With uv](https://realpython.com/python-uv/)
  - uv version 0.6.12+ features and conventions
- **Findings**:
  - `[project.scripts]` table in pyproject.toml defines CLI commands: `command-name = "module:function"`
  - `uv tool install` isolates packages in dedicated environments (no dependency conflicts)
  - `uvx package-name` enables one-off execution without installation
  - `uv.lock` file ensures reproducible environments (cross-platform)
  - Development dependencies should use `[dependency-groups.dev]` (modern approach) or `[project.optional-dependencies.dev]` (legacy compatible)
- **Implications**: 
  - pyproject.toml must define `[project.scripts]` with `DownloadImagesOnPage = "DownloadImagesOnPage.cli:main"` entry point
  - Package name should follow PyPI conventions (lowercase, hyphens): `download-images-on-page`
  - Existing `__main__.py` preserved for `python -m DownloadImagesOnPage` backward compatibility

### Topic: Build System Selection
- **Context**: Choose between hatchling and setuptools as build backend
- **Sources Consulted**:
  - setuptools documentation
  - hatchling documentation
  - Community best practices (Real Python, uv docs)
- **Findings**:
  - **Hatchling**: Modern, zero-config for simple projects, faster builds, PEP 517/660 compliant
  - **Setuptools**: Traditional, widely used, extensive plugin ecosystem, more configuration options
  - Both support editable installs and CLI entry points
  - uv works seamlessly with both backends
- **Implications**: 
  - Recommend **hatchling** for this project due to simplicity and modern standards
  - Fallback to setuptools acceptable if team prefers familiarity
  - Build system config minimal: `requires = ["hatchling"]`, `build-backend = "hatchling.build"`

### Topic: Dependency Version Constraints
- **Context**: Determine appropriate version constraints for dependencies
- **Sources Consulted**: 
  - Current requirements.txt
  - Package documentation for requests, beautifulsoup4, lxml, Pillow
  - Python packaging best practices
- **Findings**:
  - Current dependencies: requests>=2.31.0, beautifulsoup4>=4.12.0, lxml>=5.0.0, Pillow>=10.0.0
  - Development dependencies: pytest>=7.4.0, pytest-cov>=4.1.0, pytest-mock>=3.12.0
  - Using `>=` allows for compatible updates while preventing breaking changes
  - Could consider `~=` for tighter control (e.g., `~=2.31` allows 2.31.x but not 2.32.0)
- **Implications**: 
  - Maintain current `>=` constraints for runtime dependencies
  - Use same approach for dev dependencies in separate group
  - uv.lock file will pin exact versions for reproducibility

### Topic: Package Naming and Metadata
- **Context**: Determine appropriate package name and PyPI metadata
- **Sources Consulted**: 
  - PyPI naming guidelines
  - Existing README.md and LICENSE
  - PEP 8 naming conventions
- **Findings**:
  - Current module: `DownloadImagesOnPage` (PascalCase)
  - Recommended PyPI name: `download-images-on-page` (lowercase-hyphen)
  - Command name should match or be shorter: `DownloadImagesOnPage` (keep consistent with module)
  - License: MIT (from existing LICENSE file, author: Ken Sakakibara)
  - Python requirement: >=3.11 (from current README)
- **Implications**: 
  - Package name: `download-images-on-page`
  - CLI command: `DownloadImagesOnPage`
  - Version: Start at 0.1.0 (pre-release)
  - Include classifiers for PyPI: Development Status, Intended Audience, Programming Language, Topic

### Topic: Backward Compatibility Strategy
- **Context**: Ensure existing workflows continue to work after migration
- **Sources Consulted**: 
  - Existing codebase structure
  - Test suite patterns
  - Python packaging standards
- **Findings**:
  - Current execution: `python -m DownloadImagesOnPage <args>`
  - Module structure uses `__main__.py` as entry point
  - Tests may rely on module execution pattern
  - CLI functionality in `cli.py` and `main.py`
- **Implications**: 
  - Preserve `DownloadImagesOnPage/__main__.py` unchanged
  - Preserve `DownloadImagesOnPage/__init__.py` for module imports
  - CLI entry point can use existing `main:main` function
  - All existing tests should continue to pass without modification

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| Standard pyproject.toml | Single pyproject.toml with all metadata and dependencies | Simple, industry standard, tool support | None significant | **Selected** - Best fit for this project size |
| Workspace setup | Multiple pyproject.toml files if splitting into sub-packages | Modularity for larger projects | Overkill for current scope | Not needed |
| Hybrid (pyproject + setup.py) | Keep setup.py for complex build logic | Maximum compatibility | More maintenance, deprecated pattern | Not recommended |

## Design Decisions

### Decision: Use Hatchling as Build Backend
- **Context**: Need to select a build system for packaging
- **Alternatives Considered**:
  1. Hatchling - Modern, minimal configuration, fast
  2. Setuptools - Traditional, feature-rich, widely adopted
  3. PDM-backend - Modern but less widely adopted
- **Selected Approach**: Hatchling with minimal configuration
- **Rationale**: 
  - Project has simple build requirements (no compiled extensions)
  - Hatchling aligns with modern Python packaging practices
  - Zero-config philosophy reduces maintenance burden
  - Excellent uv integration
- **Trade-offs**: 
  - Benefits: Simpler configuration, faster builds, modern standards
  - Compromises: Slightly less plugin ecosystem than setuptools
- **Follow-up**: Document in README if users need setuptools compatibility

### Decision: Separate Development Dependencies via dependency-groups
- **Context**: Need clear separation between runtime and development dependencies
- **Alternatives Considered**:
  1. `[dependency-groups.dev]` - Modern uv/PEP 735 approach
  2. `[project.optional-dependencies.dev]` - Traditional extras approach
  3. Keep requirements.txt - Legacy approach (not recommended)
- **Selected Approach**: Use `[dependency-groups.dev]`
- **Rationale**: 
  - Modern standard aligned with uv best practices
  - Clear semantic separation (not an "optional" feature)
  - Better tooling support in uv ecosystem
  - Cleaner `uv sync --group dev` command
- **Trade-offs**: 
  - Benefits: Modern, explicit, better tool support
  - Compromises: Newer standard, less familiar to some developers
- **Follow-up**: Update documentation with `uv sync --group dev` instructions

### Decision: CLI Entry Point Name
- **Context**: Determine command name for `uv tool install` and `uvx` usage
- **Alternatives Considered**:
  1. `DownloadImagesOnPage` - Match module name
  2. `download-images` - Shorter, lowercase
  3. `dl-images` - Very short abbreviation
- **Selected Approach**: `DownloadImagesOnPage`
- **Rationale**: 
  - Consistency with existing module name
  - User requirement explicitly specified this name
  - Clear, descriptive, no ambiguity
  - Follows Python convention for module names
- **Trade-offs**: 
  - Benefits: Clear, consistent, meets user requirements
  - Compromises: Longer to type (but tab-completion helps)
- **Follow-up**: Document both `uvx DownloadImagesOnPage` and `uv tool install` usage

### Decision: Package Name Format
- **Context**: Choose PyPI-compatible package name
- **Alternatives Considered**:
  1. `download-images-on-page` - Lowercase with hyphens (PyPI convention)
  2. `DownloadImagesOnPage` - Match module name exactly
  3. `download_images_on_page` - Underscores (not recommended)
- **Selected Approach**: `download-images-on-page`
- **Rationale**: 
  - Follows PyPI naming conventions (lowercase, hyphens)
  - Prevents naming conflicts with module
  - Standard practice in Python ecosystem
  - Better discoverability on PyPI
- **Trade-offs**: 
  - Benefits: Standards-compliant, familiar pattern
  - Compromises: Differs from module name (but this is normal)
- **Follow-up**: Clarify package vs module naming in documentation

## Risks & Mitigations
- **Risk**: Existing tests may fail if they depend on specific import patterns
  - **Mitigation**: Run full test suite immediately after pyproject.toml creation; preserve all existing module structure
- **Risk**: Users unfamiliar with uv may struggle with new workflow
  - **Mitigation**: Provide comprehensive README with examples for both uv and traditional workflows; include troubleshooting section
- **Risk**: Development dependency separation may be unclear
  - **Mitigation**: Document `uv sync --group dev` clearly; provide examples of production install vs development install
- **Risk**: Entry point configuration errors could prevent CLI functionality
  - **Mitigation**: Test `uv tool install` and `uvx` execution immediately after implementation; validate with both methods

## References
- [uv Official Documentation - Configuring Projects](https://docs.astral.sh/uv/concepts/projects/config/) - Comprehensive guide to pyproject.toml structure for uv
- [Real Python - Managing Python Projects With uv](https://realpython.com/python-uv/) - Practical tutorial with examples
- [PEP 517 - Build System Interface](https://peps.python.org/pep-0517/) - Build backend specification
- [PEP 518 - pyproject.toml Specification](https://peps.python.org/pep-0518/) - Configuration file format
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/) - Project metadata in pyproject.toml
- [PEP 735 - Dependency Groups](https://peps.python.org/pep-0735/) - Modern dependency group specification
- [Python Packaging User Guide - Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official packaging guide
