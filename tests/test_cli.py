"""Tests for CLI argument parsing."""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch
from DownloadImagesOnPage.cli import parse_arguments
from DownloadImagesOnPage.models import CLIConfig


class TestParseArgumentsBasic:
    """Tests for basic argument parsing."""
    
    def test_parse_arguments_with_required_args(self):
        """Should parse URL and output directory."""
        test_args = ['script', 'https://example.com', '/tmp/images']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.url == 'https://example.com'
        assert config.output_dir == Path('/tmp/images')
        assert config.min_width is None
        assert config.min_height is None
        assert config.verbose is False
    
    def test_parse_arguments_with_http_url(self):
        """Should accept HTTP URL."""
        test_args = ['script', 'http://example.com', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.url == 'http://example.com'
    
    def test_parse_arguments_with_https_url(self):
        """Should accept HTTPS URL."""
        test_args = ['script', 'https://example.com/page', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.url == 'https://example.com/page'


class TestParseArgumentsOptional:
    """Tests for optional argument parsing."""
    
    def test_parse_arguments_with_min_width(self):
        """Should parse --min-width option."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-width', '800']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.min_width == 800
    
    def test_parse_arguments_with_min_height(self):
        """Should parse --min-height option."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-height', '600']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.min_height == 600
    
    def test_parse_arguments_with_both_dimensions(self):
        """Should parse both --min-width and --min-height."""
        test_args = [
            'script', 'https://example.com', '/tmp/output',
            '--min-width', '1024', '--min-height', '768'
        ]
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.min_width == 1024
        assert config.min_height == 768
    
    def test_parse_arguments_with_verbose(self):
        """Should parse --verbose flag."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--verbose']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.verbose is True
    
    def test_parse_arguments_with_playwright(self):
        """Should parse --playwright flag."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--playwright']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.use_playwright is True
    
    def test_parse_arguments_with_all_options(self):
        """Should parse all optional arguments together."""
        test_args = [
            'script', 'https://example.com', '/tmp/output',
            '--min-width', '800',
            '--min-height', '600',
            '--playwright',
            '--verbose'
        ]
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert config.url == 'https://example.com'
        assert config.output_dir == Path('/tmp/output')
        assert config.min_width == 800
        assert config.min_height == 600
        assert config.verbose is True


class TestParseArgumentsValidation:
    """Tests for argument validation."""
    
    def test_parse_arguments_rejects_invalid_url_scheme(self):
        """Should reject URL with invalid scheme."""
        test_args = ['script', 'ftp://example.com', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_url_without_scheme(self):
        """Should reject URL without scheme."""
        test_args = ['script', 'example.com', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_negative_min_width(self):
        """Should reject negative min-width."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-width', '-100']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_zero_min_width(self):
        """Should reject zero min-width."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-width', '0']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_negative_min_height(self):
        """Should reject negative min-height."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-height', '-50']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_zero_min_height(self):
        """Should reject zero min-height."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-height', '0']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_rejects_non_integer_min_width(self):
        """Should reject non-integer min-width."""
        test_args = ['script', 'https://example.com', '/tmp/output', '--min-width', 'abc']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0


class TestParseArgumentsRequired:
    """Tests for required arguments."""
    
    def test_parse_arguments_requires_url(self):
        """Should require URL argument."""
        test_args = ['script']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0
    
    def test_parse_arguments_requires_output_dir(self):
        """Should require output directory argument."""
        test_args = ['script', 'https://example.com']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code != 0


class TestParseArgumentsHelp:
    """Tests for help functionality."""
    
    def test_parse_arguments_help_exits(self):
        """Should exit with code 0 when --help is provided."""
        test_args = ['script', '--help']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0
    
    def test_parse_arguments_h_short_help_exits(self):
        """Should exit with code 0 when -h is provided."""
        test_args = ['script', '-h']
        
        with patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                parse_arguments()
            assert exc_info.value.code == 0


class TestParseArgumentsReturnType:
    """Tests for return type."""
    
    def test_parse_arguments_returns_cli_config(self):
        """Should return CLIConfig instance."""
        test_args = ['script', 'https://example.com', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert isinstance(config, CLIConfig)
    
    def test_parse_arguments_output_dir_is_path(self):
        """Should convert output_dir to Path object."""
        test_args = ['script', 'https://example.com', '/tmp/output']
        
        with patch.object(sys, 'argv', test_args):
            config = parse_arguments()
        
        assert isinstance(config.output_dir, Path)
