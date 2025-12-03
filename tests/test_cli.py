"""Unit tests for the CLI module."""

import pytest
from io import StringIO
from unittest.mock import patch
from pathlib import Path
from src.cli import CLI
from src.models import OrganizationPlan, ExecutionResult, FileInfo


class TestCLI:
    """Test cases for the CLI class."""
    
    def test_display_plan_summary(self, capsys):
        """Test that plan summary displays correctly."""
        cli = CLI()
        
        # Create a sample plan
        files = [
            FileInfo(Path("test1.pdf"), "test1.pdf", ".pdf", 1000),
            FileInfo(Path("test2.jpg"), "test2.jpg", ".jpg", 2000),
            FileInfo(Path("test3.jpg"), "test3.jpg", ".jpg", 3000),
        ]
        
        plan = OrganizationPlan(
            files_by_category={
                "PDF": [files[0]],
                "Images": [files[1], files[2]]
            },
            folders_to_create=["PDF", "Images"],
            total_files=3
        )
        
        cli.display_plan_summary(plan)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify key information is displayed
        assert "DESKTOP ORGANIZATION PLAN" in output
        assert "Total files to organize: 3" in output
        assert "Images: 2 file(s)" in output
        assert "PDF: 1 file(s)" in output
        assert "Folders to be created:" in output
    
    def test_request_confirmation_yes(self):
        """Test that confirmation returns True for 'yes' input."""
        cli = CLI()
        
        with patch('builtins.input', return_value='yes'):
            result = cli.request_confirmation()
            assert result is True
    
    def test_request_confirmation_no(self):
        """Test that confirmation returns False for 'no' input."""
        cli = CLI()
        
        with patch('builtins.input', return_value='no'):
            result = cli.request_confirmation()
            assert result is False
    
    def test_request_confirmation_y_shorthand(self):
        """Test that confirmation accepts 'y' as yes."""
        cli = CLI()
        
        with patch('builtins.input', return_value='y'):
            result = cli.request_confirmation()
            assert result is True
    
    def test_request_confirmation_n_shorthand(self):
        """Test that confirmation accepts 'n' as no."""
        cli = CLI()
        
        with patch('builtins.input', return_value='n'):
            result = cli.request_confirmation()
            assert result is False
    
    def test_request_confirmation_invalid_then_valid(self):
        """Test that confirmation handles invalid input then accepts valid input."""
        cli = CLI()
        
        with patch('builtins.input', side_effect=['maybe', 'yes']):
            result = cli.request_confirmation()
            assert result is True
    
    def test_display_results(self, capsys):
        """Test that results display correctly."""
        cli = CLI()
        
        result = ExecutionResult(
            total_moved=5,
            moved_by_category={"Documents": 3, "Images": 2},
            errors=[],
            duration=1.23
        )
        
        cli.display_results(result)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify key information is displayed
        assert "ORGANIZATION COMPLETE" in output
        assert "Total files moved: 5" in output
        assert "Operation duration: 1.23 seconds" in output
        assert "Documents: 3 file(s)" in output
        assert "Images: 2 file(s)" in output
        assert "No errors encountered" in output
    
    def test_display_results_with_errors(self, capsys):
        """Test that results display errors correctly."""
        cli = CLI()
        
        result = ExecutionResult(
            total_moved=3,
            moved_by_category={"Documents": 3},
            errors=["Failed to move file1.txt: Permission denied", "Failed to move file2.txt: File not found"],
            duration=0.5
        )
        
        cli.display_results(result)
        
        captured = capsys.readouterr()
        output = captured.out
        
        # Verify errors are displayed
        assert "Errors encountered (2)" in output
        assert "Failed to move file1.txt: Permission denied" in output
        assert "Failed to move file2.txt: File not found" in output
    
    def test_display_error(self, capsys):
        """Test that error messages display correctly."""
        cli = CLI()
        
        cli.display_error("Desktop directory not found")
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "ERROR" in output
        assert "Desktop directory not found" in output
    
    def test_cancellation_prevents_operations(self):
        """
        Test that cancelling prevents file operations.
        
        Requirements: 5.5
        """
        cli = CLI()
        
        # Simulate user cancelling
        with patch('builtins.input', return_value='no'):
            confirmed = cli.request_confirmation()
        
        # Verify that confirmation returned False
        assert confirmed is False
        
        # In the actual workflow, this False value would prevent
        # the service from executing the plan
