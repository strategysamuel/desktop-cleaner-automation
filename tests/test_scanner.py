"""Tests for the DesktopScanner module."""

import os
import tempfile
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings

from src.scanner import DesktopScanner
from src.models import FileInfo


class TestDesktopScanner:
    """Unit tests for DesktopScanner."""
    
    def test_get_desktop_path_returns_valid_path(self):
        """Test that get_desktop_path() returns valid Windows Desktop path.
        
        Requirements: 1.1
        """
        scanner = DesktopScanner()
        desktop_path = scanner.get_desktop_path()
        
        # Should return a Path object
        assert isinstance(desktop_path, Path)
        
        # Should end with "Desktop"
        assert desktop_path.name == "Desktop"
        
        # Should exist (assuming test runs on a system with Desktop)
        assert desktop_path.exists()
        
        # Should be a directory
        assert desktop_path.is_dir()

    def test_desktop_ini_is_excluded(self):
        """Test that desktop.ini is excluded from scan results.
        
        Requirements: 6.4
        """
        scanner = DesktopScanner()
        
        # Create a temporary directory to simulate Desktop
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create desktop.ini file
            desktop_ini = temp_path / "desktop.ini"
            desktop_ini.write_text("[.ShellClassInfo]")
            
            # Create a regular file
            regular_file = temp_path / "document.txt"
            regular_file.write_text("content")
            
            # Test should_exclude on desktop.ini
            assert scanner.should_exclude(desktop_ini) is True
            
            # Test should_exclude on regular file
            assert scanner.should_exclude(regular_file) is False

    def test_inaccessible_directory_raises_error(self, monkeypatch):
        """Test error handling when Desktop directory cannot be accessed.
        
        Requirements: 1.5
        """
        scanner = DesktopScanner()
        
        # Mock os.access to return False (simulating no read permission)
        def mock_access(path, mode):
            return False
        
        monkeypatch.setattr(os, "access", mock_access)
        
        # Should raise PermissionError when trying to scan
        with pytest.raises(PermissionError, match="Cannot access Desktop directory"):
            scanner.scan_desktop()



class TestDesktopScannerProperties:
    """Property-based tests for DesktopScanner."""
    
    @given(
        num_files=st.integers(min_value=0, max_value=50),
        num_folders=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_scan_completeness(self, num_files, num_folders):
        """
        Feature: desktop-cleaner, Property 1: Scan completeness
        
        For any directory with a known set of files, scanning should return 
        exactly those files (excluding folders and excluded items), and the 
        count should match the number of files returned.
        
        Validates: Requirements 1.2, 1.3, 1.4
        """
        scanner = DesktopScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create random files
            created_files = []
            for i in range(num_files):
                file_path = temp_path / f"file_{i}.txt"
                file_path.write_text(f"content {i}")
                created_files.append(file_path)
            
            # Create random folders (should be excluded)
            for i in range(num_folders):
                folder_path = temp_path / f"folder_{i}"
                folder_path.mkdir()
            
            # Mock get_desktop_path to return our temp directory
            original_method = scanner.get_desktop_path
            scanner.get_desktop_path = lambda: temp_path
            
            try:
                # Scan the directory
                result = scanner.scan_desktop()
                
                # The number of files returned should match the number we created
                assert len(result) == num_files
                
                # All returned items should be FileInfo objects
                for file_info in result:
                    assert isinstance(file_info, FileInfo)
                
                # All created files should be in the results
                result_paths = {fi.path for fi in result}
                for created_file in created_files:
                    assert created_file in result_paths
                
                # No folders should be in the results
                for file_info in result:
                    assert file_info.path.is_file()
                    assert not file_info.path.is_dir()
            finally:
                scanner.get_desktop_path = original_method

    
    @given(
        num_regular_files=st.integers(min_value=0, max_value=20),
        num_category_folders=st.integers(min_value=0, max_value=7),
        include_desktop_ini=st.booleans()
    )
    @settings(max_examples=100, deadline=None)
    def test_exclusion_consistency(self, num_regular_files, num_category_folders, include_desktop_ini):
        """
        Feature: desktop-cleaner, Property 13: Exclusion consistency
        
        For any scan operation, the results should not include category folders, 
        hidden files, or system files, and the count should only reflect 
        non-excluded files.
        
        Validates: Requirements 6.1, 6.2, 6.3, 6.5
        """
        scanner = DesktopScanner()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create regular files
            regular_files = []
            for i in range(num_regular_files):
                file_path = temp_path / f"document_{i}.txt"
                file_path.write_text(f"content {i}")
                regular_files.append(file_path)
            
            # Create category folders (should be excluded)
            category_names = list(scanner.CATEGORY_FOLDERS)[:num_category_folders]
            for category in category_names:
                folder_path = temp_path / category
                folder_path.mkdir()
            
            # Optionally create desktop.ini (should be excluded)
            if include_desktop_ini:
                desktop_ini = temp_path / "desktop.ini"
                desktop_ini.write_text("[.ShellClassInfo]")
            
            # Mock get_desktop_path to return our temp directory
            original_method = scanner.get_desktop_path
            scanner.get_desktop_path = lambda: temp_path
            
            try:
                # Scan the directory
                result = scanner.scan_desktop()
                
                # Should only return regular files, not excluded items
                assert len(result) == num_regular_files
                
                # No category folders should be in results
                result_names = {fi.name for fi in result}
                for category in category_names:
                    assert category not in result_names
                
                # desktop.ini should not be in results
                assert "desktop.ini" not in result_names
                
                # All results should be regular files we created
                result_paths = {fi.path for fi in result}
                for regular_file in regular_files:
                    assert regular_file in result_paths
            finally:
                scanner.get_desktop_path = original_method
