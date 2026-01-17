"""Tests for validation logic in CLI module."""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from DownloadImagesOnPage.cli import (
    _validate_url,
    _validate_positive_int,
    _validate_output_dir,
)


class TestValidateUrl:
    """Tests for URL validation function."""
    
    def test_validate_url_accepts_https(self):
        """Should accept HTTPS URL."""
        url = "https://example.com"
        result = _validate_url(url)
        assert result == url
    
    def test_validate_url_accepts_http(self):
        """Should accept HTTP URL."""
        url = "http://example.com"
        result = _validate_url(url)
        assert result == url
    
    def test_validate_url_accepts_with_path(self):
        """Should accept URL with path."""
        url = "https://example.com/path/to/page"
        result = _validate_url(url)
        assert result == url
    
    def test_validate_url_accepts_with_query(self):
        """Should accept URL with query parameters."""
        url = "https://example.com?param=value"
        result = _validate_url(url)
        assert result == url
    
    def test_validate_url_rejects_ftp(self):
        """Should reject FTP URL."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            _validate_url("ftp://example.com")
        assert "ftp" in str(exc_info.value).lower()
    
    def test_validate_url_rejects_file(self):
        """Should reject file:// URL."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            _validate_url("file:///path/to/file")
        assert "file" in str(exc_info.value).lower()
    
    def test_validate_url_rejects_no_scheme(self):
        """Should reject URL without scheme."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_url("example.com")
    
    def test_validate_url_rejects_mailto(self):
        """Should reject mailto: URL."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_url("mailto:user@example.com")


class TestValidatePositiveInt:
    """Tests for positive integer validation function."""
    
    def test_validate_positive_int_accepts_positive(self):
        """Should accept positive integer."""
        result = _validate_positive_int("100")
        assert result == 100
    
    def test_validate_positive_int_accepts_large_number(self):
        """Should accept large positive integer."""
        result = _validate_positive_int("10000")
        assert result == 10000
    
    def test_validate_positive_int_rejects_zero(self):
        """Should reject zero."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            _validate_positive_int("0")
        assert "positive" in str(exc_info.value).lower()
    
    def test_validate_positive_int_rejects_negative(self):
        """Should reject negative integer."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError) as exc_info:
            _validate_positive_int("-50")
        assert "positive" in str(exc_info.value).lower()
    
    def test_validate_positive_int_rejects_float(self):
        """Should reject float value."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_positive_int("10.5")
    
    def test_validate_positive_int_rejects_string(self):
        """Should reject non-numeric string."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_positive_int("abc")
    
    def test_validate_positive_int_rejects_empty(self):
        """Should reject empty string."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_positive_int("")


class TestValidateOutputDir:
    """Tests for output directory validation function."""
    
    def test_validate_output_dir_accepts_valid_path(self):
        """Should accept valid directory path."""
        path = "/tmp/output"
        result = _validate_output_dir(path)
        assert result == path
    
    def test_validate_output_dir_accepts_relative_path(self):
        """Should accept relative directory path."""
        path = "./output"
        result = _validate_output_dir(path)
        assert result == path
    
    def test_validate_output_dir_accepts_nested_path(self):
        """Should accept nested directory path."""
        path = "/tmp/images/downloads"
        result = _validate_output_dir(path)
        assert result == path
    
    def test_validate_output_dir_accepts_existing_dir(self):
        """Should accept existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _validate_output_dir(tmpdir)
            assert result == tmpdir
    
    def test_validate_output_dir_accepts_nonexistent_dir(self):
        """Should accept non-existent directory (will be created later)."""
        path = "/tmp/nonexistent_dir_12345"
        result = _validate_output_dir(path)
        assert result == path
    
    def test_validate_output_dir_rejects_existing_file(self):
        """Should reject path that points to an existing file."""
        import argparse
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmpfile:
            tmpfile.write("test")
            tmpfile_name = tmpfile.name
        
        try:
            with pytest.raises(argparse.ArgumentTypeError) as exc_info:
                _validate_output_dir(tmpfile_name)
            assert "file" in str(exc_info.value).lower() or "directory" in str(exc_info.value).lower()
        finally:
            try:
                os.unlink(tmpfile_name)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors on Windows
    
    def test_validate_output_dir_rejects_empty_string(self):
        """Should reject empty string."""
        import argparse
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_output_dir("")
    
    def test_validate_output_dir_windows_path(self):
        """Should accept Windows-style path."""
        path = "C:\\Users\\test\\output"
        result = _validate_output_dir(path)
        assert result == path
    
    def test_validate_output_dir_current_dir(self):
        """Should accept current directory."""
        result = _validate_output_dir(".")
        assert result == "."


class TestValidationIntegration:
    """Integration tests for validation functions."""
    
    def test_all_validators_raise_argument_type_error(self):
        """All validators should raise ArgumentTypeError for invalid input."""
        import argparse
        
        # Test URL validator
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_url("invalid")
        
        # Test positive int validator
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_positive_int("-1")
        
        # Test output dir validator
        with pytest.raises(argparse.ArgumentTypeError):
            _validate_output_dir("")
    
    def test_validators_return_correct_types(self):
        """Validators should return correct types."""
        # URL returns string
        url_result = _validate_url("https://example.com")
        assert isinstance(url_result, str)
        
        # Positive int returns int
        int_result = _validate_positive_int("100")
        assert isinstance(int_result, int)
        
        # Output dir returns string
        dir_result = _validate_output_dir("/tmp/output")
        assert isinstance(dir_result, str)
