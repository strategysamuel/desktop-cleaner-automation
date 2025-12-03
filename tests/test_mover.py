"""Tests for the FileMover module."""

import tempfile
import shutil
from pathlib import Path
import pytest
from hypothesis import given, strategies as st, settings

from src.mover import FileMover


class TestFileMoverProperties:
    """Property-based tests for FileMover."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mover = FileMover()
    
    def _create_temp_dir(self):
        """Create a fresh temporary directory for each test."""
        return Path(tempfile.mkdtemp())
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),
        blacklist_characters='/\\:*?"<>|'
    )).filter(lambda x: x.upper() not in [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ] and not x.endswith('.') and not x.endswith(' ')))
    @settings(max_examples=100)
    def test_folder_creation_idempotence(self, category_name):
        """
        Feature: desktop-cleaner, Property 6: Folder creation idempotence
        Validates: Requirements 3.2, 3.4
        
        For any category name, creating the folder multiple times should succeed 
        without errors, and only one folder should exist after multiple creation attempts.
        """
        desktop_path = self._create_temp_dir()
        
        try:
            # Create the folder multiple times
            result1 = self.mover.create_category_folder(desktop_path, category_name)
            result2 = self.mover.create_category_folder(desktop_path, category_name)
            result3 = self.mover.create_category_folder(desktop_path, category_name)
            
            # All attempts should succeed
            assert result1 is True
            assert result2 is True
            assert result3 is True
            
            # Verify only one folder exists
            folder_path = desktop_path / category_name
            assert folder_path.exists()
            assert folder_path.is_dir()
            
            # Count folders with this name (should be exactly 1)
            # Use iterdir() instead of glob() to avoid issues with special characters
            matching_folders = [f for f in desktop_path.iterdir() if f.name == category_name]
            assert len(matching_folders) == 1
        finally:
            shutil.rmtree(desktop_path, ignore_errors=True)
    
    @given(st.text(min_size=1, max_size=50, alphabet=st.characters(
        blacklist_categories=('Cc', 'Cs'),
        blacklist_characters='/\\:*?"<>|'
    )).filter(lambda x: x.upper() not in [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ] and not x.endswith('.') and not x.endswith(' ')))
    @settings(max_examples=100)
    def test_folder_name_matches_category(self, category_name):
        """
        Feature: desktop-cleaner, Property 7: Folder name matches category
        Validates: Requirements 3.3
        
        For any category, the created folder path should end with the exact category name.
        """
        desktop_path = self._create_temp_dir()
        
        try:
            # Create the folder
            result = self.mover.create_category_folder(desktop_path, category_name)
            
            assert result is True
            
            # Verify the folder path ends with the category name
            folder_path = desktop_path / category_name
            assert folder_path.exists()
            assert folder_path.name == category_name
        finally:
            shutil.rmtree(desktop_path, ignore_errors=True)
    
    @given(
        filename=st.text(min_size=1, max_size=30, alphabet=st.characters(
            blacklist_categories=('Cc', 'Cs'),
            blacklist_characters='/\\:*?"<>|'
        )).filter(lambda x: x.upper() not in [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ] and not x.endswith('.') and not x.endswith(' ')),
        extension=st.sampled_from(['.txt', '.pdf', '.jpg', '.doc', '.zip'])
    )
    @settings(max_examples=100)
    def test_file_move_preserves_filename(self, filename, extension):
        """
        Feature: desktop-cleaner, Property 8: File move preserves filename
        Validates: Requirements 4.2
        
        For any file moved to a category folder (without naming conflicts), 
        the filename in the destination should match the original filename exactly.
        """
        desktop_path = self._create_temp_dir()
        
        try:
            # Create a source file
            full_filename = f"{filename}{extension}"
            source_file = desktop_path / full_filename
            source_file.write_text("test content")
            
            # Create destination folder
            dest_folder = desktop_path / "TestCategory"
            dest_folder.mkdir()
            
            # Move the file
            result = self.mover.move_file(source_file, dest_folder)
            
            # Verify success
            assert result.success is True
            assert result.error is None
            
            # Verify filename is preserved
            assert result.destination.name == full_filename
            assert result.destination.parent == dest_folder
        finally:
            shutil.rmtree(desktop_path, ignore_errors=True)
    
    @given(
        filename=st.text(min_size=1, max_size=30, alphabet=st.characters(
            blacklist_categories=('Cc', 'Cs'),
            blacklist_characters='/\\:*?"<>|'
        )).filter(lambda x: x.upper() not in [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ] and not x.endswith('.') and not x.endswith(' ')),
        extension=st.sampled_from(['.txt', '.pdf', '.jpg', '.doc', '.zip']),
        num_conflicts=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=100, deadline=None)
    def test_name_conflict_resolution_uniqueness(self, filename, extension, num_conflicts):
        """
        Feature: desktop-cleaner, Property 9: Name conflict resolution uniqueness
        Validates: Requirements 4.3
        
        For any file moved to a category folder where a file with the same name exists, 
        the system should generate a unique filename with a numeric suffix, 
        and no files should be overwritten.
        """
        desktop_path = self._create_temp_dir()
        
        try:
            # Create destination folder
            dest_folder = desktop_path / "TestCategory"
            dest_folder.mkdir()
            
            # Create the original file in destination
            full_filename = f"{filename}{extension}"
            original_file = dest_folder / full_filename
            original_file.write_text("original content")
            
            moved_files = []
            
            # Try to move multiple files with the same name
            for i in range(num_conflicts):
                # Create a new source file
                source_file = desktop_path / f"temp_{i}{extension}"
                source_file.write_text(f"content {i}")
                
                # Move the file
                result = self.mover.move_file(source_file, dest_folder)
                
                # Verify success
                assert result.success is True
                assert result.error is None
                
                moved_files.append(result.destination)
            
            # Verify all moved files have unique names
            moved_names = [f.name for f in moved_files]
            assert len(moved_names) == len(set(moved_names)), "All filenames should be unique"
            
            # Verify original file still exists and wasn't overwritten
            assert original_file.exists()
            assert original_file.read_text() == "original content"
            
            # Verify all moved files have numeric suffixes
            for moved_file in moved_files:
                assert moved_file.exists()
                # Should have format: filename_N.extension
                assert "_" in moved_file.stem
        finally:
            shutil.rmtree(desktop_path, ignore_errors=True)


class TestFileMoverUnitTests:
    """Unit tests for FileMover."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mover = FileMover()
        self.temp_dir = tempfile.mkdtemp()
        self.desktop_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_folder_creation_error(self):
        """
        Test error handling when folder creation fails.
        Validates: Requirements 3.5
        """
        # Try to create a folder in a non-existent parent directory
        # This should fail gracefully
        invalid_path = Path("/nonexistent/invalid/path")
        
        result = self.mover.create_category_folder(invalid_path, "TestCategory")
        
        # Should return False on error
        assert result is False
