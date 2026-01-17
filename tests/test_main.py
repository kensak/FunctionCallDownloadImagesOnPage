"""Tests for main entry point module."""
import pytest
import sys
from unittest.mock import Mock, patch, call
from pathlib import Path
from io import StringIO

from DownloadImagesOnPage.main import main
from DownloadImagesOnPage.models import CLIConfig, DownloadResult
from DownloadImagesOnPage.exceptions import FetchError, FileWriteError


class TestMainSuccess:
    """Tests for successful main execution."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    def test_main_returns_zero_on_success(
        self, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should return 0 on successful execution."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_run_download.return_value = DownloadResult(
            success_count=5,
            failed_count=0,
            filtered_count=0,
            total_count=5
        )
        
        exit_code = main()
        
        assert exit_code == 0
        mock_ensure_dir.assert_called_once_with(Path("/output"))
        mock_run_download.assert_called_once()
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    def test_main_calls_ensure_directory(
        self, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should call ensure_directory with output_dir."""
        output_dir = Path("/test/output")
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=output_dir
        )
        mock_run_download.return_value = DownloadResult(1, 0, 0, 1)
        
        main()
        
        mock_ensure_dir.assert_called_once_with(output_dir)
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.setup_logging')
    def test_main_calls_setup_logging(
        self, mock_setup_logging, mock_run_download, 
        mock_ensure_dir, mock_parse_args
    ):
        """Should call setup_logging with verbose flag."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            verbose=True
        )
        mock_run_download.return_value = DownloadResult(1, 0, 0, 1)
        
        main()
        
        mock_setup_logging.assert_called_once_with(verbose=True)
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    def test_main_passes_config_to_run_download(
        self, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should pass CLIConfig to run_download."""
        config = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output"),
            min_width=800,
            min_height=600,
            verbose=True
        )
        mock_parse_args.return_value = config
        mock_run_download.return_value = DownloadResult(1, 0, 0, 1)
        
        main()
        
        mock_run_download.assert_called_once_with(config)


class TestMainFetchError:
    """Tests for FetchError handling."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_returns_2_on_fetch_error(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should return exit code 2 when HTML fetch fails."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_run_download.side_effect = FetchError(
            url="https://example.com",
            status_code=404,
            message="Not found"
        )
        
        exit_code = main()
        
        assert exit_code == 2
        mock_logger.error.assert_called()
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_logs_fetch_error_message(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should log error message when fetch fails."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        error = FetchError(
            url="https://example.com",
            status_code=500,
            message="Server error"
        )
        mock_run_download.side_effect = error
        
        main()
        
        # Should log the error
        assert mock_logger.error.called
        call_args = str(mock_logger.error.call_args)
        assert "fetch" in call_args.lower() or "500" in call_args or "server" in call_args.lower()


class TestMainFileWriteError:
    """Tests for FileWriteError handling."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_returns_2_on_directory_creation_error(
        self, mock_logger, mock_ensure_dir, mock_parse_args
    ):
        """Should return exit code 2 when directory creation fails."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_ensure_dir.side_effect = FileWriteError(
            path=Path("/output"),
            message="Permission denied"
        )
        
        exit_code = main()
        
        assert exit_code == 2
        mock_logger.error.assert_called()


class TestMainArgumentError:
    """Tests for argument parsing errors."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_returns_1_on_argument_error(
        self, mock_logger, mock_parse_args
    ):
        """Should return exit code 1 when argument parsing fails."""
        mock_parse_args.side_effect = SystemExit(2)
        
        exit_code = main()
        
        assert exit_code == 1
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    def test_main_returns_0_on_help_request(self, mock_parse_args):
        """Should return exit code 0 when --help is requested."""
        mock_parse_args.side_effect = SystemExit(0)
        
        exit_code = main()
        
        assert exit_code == 0


class TestMainKeyboardInterrupt:
    """Tests for KeyboardInterrupt handling (Ctrl+C)."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_returns_0_on_keyboard_interrupt(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should return exit code 0 when interrupted by user."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_run_download.side_effect = KeyboardInterrupt()
        
        exit_code = main()
        
        assert exit_code == 0
        mock_logger.info.assert_called()
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_logs_interrupt_message(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should log info message when interrupted."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_run_download.side_effect = KeyboardInterrupt()
        
        main()
        
        # Should log that operation was interrupted
        assert mock_logger.info.called
        call_args = str(mock_logger.info.call_args)
        assert "interrupt" in call_args.lower() or "cancel" in call_args.lower()


class TestMainUnexpectedError:
    """Tests for unexpected exception handling."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_returns_2_on_unexpected_error(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should return exit code 2 on unexpected exceptions."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        mock_run_download.side_effect = RuntimeError("Unexpected error")
        
        exit_code = main()
        
        assert exit_code == 2
        mock_logger.error.assert_called()


class TestMainEntryPoint:
    """Tests for entry point integration."""
    
    def test_entry_point_has_main_function(self):
        """Should have main() function defined."""
        from DownloadImagesOnPage.main import main
        
        # Verify main function exists and is callable
        assert callable(main)


class TestMainSummaryDisplay:
    """Tests for summary display."""
    
    @patch('DownloadImagesOnPage.main.parse_arguments')
    @patch('DownloadImagesOnPage.main.ensure_directory')
    @patch('DownloadImagesOnPage.main.run_download')
    @patch('DownloadImagesOnPage.main.logger')
    def test_main_displays_summary(
        self, mock_logger, mock_run_download, mock_ensure_dir, mock_parse_args
    ):
        """Should display summary after download completes."""
        mock_parse_args.return_value = CLIConfig(
            url="https://example.com",
            output_dir=Path("/output")
        )
        result = DownloadResult(
            success_count=10,
            failed_count=2,
            filtered_count=3,
            total_count=15
        )
        mock_run_download.return_value = result
        
        main()
        
        # Should log summary information
        assert mock_logger.info.called
        # Check that summary contains counts
        calls = [str(call) for call in mock_logger.info.call_args_list]
        summary_text = " ".join(calls).lower()
        # Verify some form of summary was logged
        assert any(c in summary_text for c in ["success", "complete", "download"])
