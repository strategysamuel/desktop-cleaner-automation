"""Tests for the main application entry point."""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest


def test_critical_error_desktop_not_found():
    """
    Test that critical errors cause safe exit when Desktop directory is not found.
    
    Validates: Requirements 8.5
    """
    # Import main module
    import main
    
    # Mock the scanner to raise FileNotFoundError (critical error)
    with patch('main.DesktopScanner') as mock_scanner_class:
        mock_scanner = MagicMock()
        mock_scanner.get_desktop_path.side_effect = FileNotFoundError("Desktop directory not found")
        mock_scanner_class.return_value = mock_scanner
        
        # Mock CLI to capture error display
        with patch('main.CLI') as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli_class.return_value = mock_cli
            
            # Mock sys.exit to prevent actual exit
            with patch('sys.exit') as mock_exit:
                # Run main
                main.main()
                
                # Verify error was displayed
                mock_cli.display_error.assert_called_once()
                error_message = mock_cli.display_error.call_args[0][0]
                assert "Desktop directory not found" in error_message or "Critical error" in error_message
                
                # Verify safe exit was called
                mock_exit.assert_called_once_with(1)


def test_critical_error_desktop_not_accessible():
    """
    Test that critical errors cause safe exit when Desktop directory cannot be accessed.
    
    Validates: Requirements 8.5
    """
    # Import main module
    import main
    
    # Mock the scanner to raise PermissionError (critical error)
    with patch('main.DesktopScanner') as mock_scanner_class:
        mock_scanner = MagicMock()
        mock_scanner.scan_desktop.side_effect = PermissionError("Cannot access Desktop directory")
        mock_scanner_class.return_value = mock_scanner
        
        # Mock CLI to capture error display
        with patch('main.CLI') as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli_class.return_value = mock_cli
            
            # Mock sys.exit to prevent actual exit
            with patch('sys.exit') as mock_exit:
                # Run main
                main.main()
                
                # Verify error was displayed
                mock_cli.display_error.assert_called_once()
                error_message = mock_cli.display_error.call_args[0][0]
                assert "Cannot access" in error_message or "Critical error" in error_message
                
                # Verify safe exit was called
                mock_exit.assert_called_once_with(1)


def test_critical_error_unexpected_exception():
    """
    Test that unexpected critical errors cause safe exit.
    
    Validates: Requirements 8.5
    """
    # Import main module
    import main
    
    # Mock the scanner to raise an unexpected exception
    with patch('main.DesktopScanner') as mock_scanner_class:
        mock_scanner = MagicMock()
        mock_scanner.scan_desktop.side_effect = RuntimeError("Unexpected error")
        mock_scanner_class.return_value = mock_scanner
        
        # Mock CLI to capture error display
        with patch('main.CLI') as mock_cli_class:
            mock_cli = MagicMock()
            mock_cli_class.return_value = mock_cli
            
            # Mock sys.exit to prevent actual exit
            with patch('sys.exit') as mock_exit:
                # Run main
                main.main()
                
                # Verify error was displayed
                mock_cli.display_error.assert_called_once()
                error_message = mock_cli.display_error.call_args[0][0]
                assert "error" in error_message.lower()
                
                # Verify safe exit was called
                mock_exit.assert_called_once_with(1)
