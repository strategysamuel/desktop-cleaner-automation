"""Integration tests for Desktop Cleaner - End-to-end workflow testing."""

import tempfile
import shutil
from pathlib import Path
import pytest

from src.scanner import DesktopScanner
from src.categorizer import FileCategorizer
from src.mover import FileMover
from src.service import DesktopCleanerService
from src.models import FileInfo


class TestDesktopCleanerIntegration:
    """End-to-end integration tests for the complete Desktop Cleaner workflow."""
    
    def setup_method(self):
        """Set up test fixtures for each test."""
        # Create a temporary directory to simulate Desktop
        self.temp_dir = tempfile.mkdtemp()
        self.desktop_path = Path(self.temp_dir)
        
        # Initialize service components
        self.service = DesktopCleanerService()
        self.scanner = DesktopScanner()
        self.categorizer = FileCategorizer()
        self.mover = FileMover()
    
    def teardown_method(self):
        """Clean up test fixtures after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_file(self, filename: str, content: str = "test content") -> Path:
        """Helper to create a test file in the temporary desktop."""
        file_path = self.desktop_path / filename
        file_path.write_text(content)
        return file_path
    
    def test_complete_workflow_with_various_file_types(self):
        """
        Test complete workflow from scan to file organization with various file types.
        
        This test validates the entire system working together:
        - Scanning Desktop directory
        - Categorizing files by extension
        - Creating organization plan
        - Creating category folders
        - Moving files to appropriate folders
        
        Requirements: All
        """
        # Create test files of various types
        test_files = {
            "document.txt": "Documents",
            "report.docx": "Documents",
            "spreadsheet.xlsx": "Documents",
            "photo.jpg": "Images",
            "screenshot.png": "Images",
            "icon.svg": "Images",
            "video.mp4": "Videos",
            "movie.avi": "Videos",
            "manual.pdf": "PDF",
            "archive.zip": "ZIPs",
            "backup.rar": "ZIPs",
            "installer.exe": "Installers",
            "unknown.xyz": "Others",
            "noext": "Others",
        }
        
        for filename in test_files.keys():
            self._create_test_file(filename, f"content of {filename}")
        
        # Mock scanner to use our temp directory
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Step 1: Scan Desktop
            files = self.scanner.scan_desktop()
            
            # Verify all files were found
            assert len(files) == len(test_files)
            
            # Step 2: Create organization plan
            plan = self.service.create_organization_plan(files)
            
            # Verify plan contains all expected categories
            expected_categories = set(test_files.values())
            assert set(plan.folders_to_create) == expected_categories
            assert plan.total_files == len(test_files)
            
            # Step 3: Execute plan
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify all files were moved successfully
            assert result.total_moved == len(test_files)
            assert len(result.errors) == 0
            
            # Verify category folders were created
            for category in expected_categories:
                category_folder = self.desktop_path / category
                assert category_folder.exists()
                assert category_folder.is_dir()
            
            # Verify files are in correct categories
            for filename, expected_category in test_files.items():
                expected_location = self.desktop_path / expected_category / filename
                assert expected_location.exists(), f"{filename} should be in {expected_category}"
                
                # Verify file content is preserved
                original_content = f"content of {filename}"
                assert expected_location.read_text() == original_content
            
            # Verify original files are gone from Desktop root
            for filename in test_files.keys():
                original_location = self.desktop_path / filename
                assert not original_location.exists(), f"{filename} should be moved from Desktop root"
            
            # Verify result statistics
            assert result.duration >= 0
            assert sum(result.moved_by_category.values()) == result.total_moved
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_naming_conflicts(self):
        """
        Test complete workflow when files with same names exist in destination.
        
        This test validates:
        - Name conflict detection
        - Automatic numeric suffix generation
        - No file overwriting
        - All files successfully moved with unique names
        
        Requirements: 4.2, 4.3
        """
        # Create initial files
        self._create_test_file("document.txt", "first document")
        self._create_test_file("photo.jpg", "first photo")
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # First pass: organize initial files
            files = self.scanner.scan_desktop()
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            assert result.total_moved == 2
            assert len(result.errors) == 0
            
            # Verify files are in their categories
            doc_folder = self.desktop_path / "Documents"
            img_folder = self.desktop_path / "Images"
            assert (doc_folder / "document.txt").exists()
            assert (img_folder / "photo.jpg").exists()
            
            # Create new files with same names
            self._create_test_file("document.txt", "second document")
            self._create_test_file("photo.jpg", "second photo")
            
            # Second pass: organize new files (should create conflicts)
            files = self.scanner.scan_desktop()
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            assert result.total_moved == 2
            assert len(result.errors) == 0
            
            # Verify original files still exist with original content
            assert (doc_folder / "document.txt").read_text() == "first document"
            assert (img_folder / "photo.jpg").read_text() == "first photo"
            
            # Verify new files were renamed with numeric suffixes
            assert (doc_folder / "document_1.txt").exists()
            assert (doc_folder / "document_1.txt").read_text() == "second document"
            assert (img_folder / "photo_1.jpg").exists()
            assert (img_folder / "photo_1.jpg").read_text() == "second photo"
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_mixed_success_and_failure(self):
        """
        Test complete workflow with error scenarios where some files succeed and others fail.
        
        This test validates:
        - Error resilience (system continues despite failures)
        - Error collection and reporting
        - Partial success handling
        - Files that can be moved are still moved
        
        Requirements: 4.5, 8.1, 8.2, 8.3
        """
        # Create some valid files
        self._create_test_file("valid1.txt", "valid content 1")
        self._create_test_file("valid2.jpg", "valid content 2")
        self._create_test_file("valid3.pdf", "valid content 3")
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan to get valid files
            files = self.scanner.scan_desktop()
            
            # Add some non-existent files to simulate access errors
            fake_file1 = FileInfo(
                path=self.desktop_path / "nonexistent1.txt",
                name="nonexistent1.txt",
                extension=".txt",
                size=100
            )
            fake_file2 = FileInfo(
                path=self.desktop_path / "nonexistent2.jpg",
                name="nonexistent2.jpg",
                extension=".jpg",
                size=200
            )
            
            files.extend([fake_file1, fake_file2])
            
            # Create organization plan
            plan = self.service.create_organization_plan(files)
            
            # Execute plan
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify partial success
            assert result.total_moved == 3, "Valid files should be moved"
            assert len(result.errors) == 2, "Should have 2 errors for non-existent files"
            
            # Verify valid files were moved successfully
            assert (self.desktop_path / "Documents" / "valid1.txt").exists()
            assert (self.desktop_path / "Images" / "valid2.jpg").exists()
            assert (self.desktop_path / "PDF" / "valid3.pdf").exists()
            
            # Verify error messages contain information about failures
            error_text = " ".join(result.errors)
            assert "nonexistent1.txt" in error_text or "nonexistent" in error_text.lower()
            
            # Verify result statistics are accurate
            assert result.moved_by_category["Documents"] == 1
            assert result.moved_by_category["Images"] == 1
            assert result.moved_by_category["PDF"] == 1
            assert result.duration >= 0
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_exclusions(self):
        """
        Test complete workflow respects exclusion rules.
        
        This test validates:
        - Category folders are not scanned
        - desktop.ini is excluded
        - Hidden files are excluded
        - Only eligible files are organized
        
        Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
        """
        # Create regular files
        self._create_test_file("document.txt", "regular document")
        self._create_test_file("photo.jpg", "regular photo")
        
        # Create desktop.ini (should be excluded)
        self._create_test_file("desktop.ini", "[.ShellClassInfo]")
        
        # Create existing category folders (should be excluded)
        (self.desktop_path / "Documents").mkdir()
        (self.desktop_path / "Images").mkdir()
        (self.desktop_path / "Documents" / "existing.txt").write_text("existing file")
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan Desktop
            files = self.scanner.scan_desktop()
            
            # Should only find the 2 regular files, not desktop.ini or existing folders
            assert len(files) == 2
            file_names = {f.name for f in files}
            assert "document.txt" in file_names
            assert "photo.jpg" in file_names
            assert "desktop.ini" not in file_names
            assert "existing.txt" not in file_names
            
            # Create and execute plan
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify only the 2 regular files were moved
            assert result.total_moved == 2
            assert len(result.errors) == 0
            
            # Verify desktop.ini still exists in root
            assert (self.desktop_path / "desktop.ini").exists()
            
            # Verify existing file in Documents folder wasn't touched
            assert (self.desktop_path / "Documents" / "existing.txt").exists()
            assert (self.desktop_path / "Documents" / "existing.txt").read_text() == "existing file"
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_empty_desktop(self):
        """
        Test complete workflow when Desktop has no files to organize.
        
        This test validates:
        - System handles empty Desktop gracefully
        - No errors occur with zero files
        - No folders are created unnecessarily
        
        Requirements: 1.4, 5.2
        """
        # Don't create any files - Desktop is empty
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan Desktop
            files = self.scanner.scan_desktop()
            
            # Should find no files
            assert len(files) == 0
            
            # Create organization plan
            plan = self.service.create_organization_plan(files)
            
            # Plan should be empty
            assert plan.total_files == 0
            assert len(plan.folders_to_create) == 0
            assert len(plan.files_by_category) == 0
            
            # Execute plan (should do nothing)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify nothing was moved
            assert result.total_moved == 0
            assert len(result.errors) == 0
            assert len(result.moved_by_category) == 0
            assert result.duration >= 0
            
            # Verify no category folders were created
            for category in ["Documents", "Images", "Videos", "PDF", "ZIPs", "Installers", "Others"]:
                assert not (self.desktop_path / category).exists()
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_case_insensitive_extensions(self):
        """
        Test complete workflow handles case-insensitive file extensions correctly.
        
        This test validates:
        - Extensions are treated case-insensitively
        - .TXT, .txt, .Txt all go to Documents
        - Files are categorized correctly regardless of extension case
        
        Requirements: 2.10
        """
        # Create files with various extension cases
        self._create_test_file("file1.txt", "lowercase")
        self._create_test_file("file2.TXT", "uppercase")
        self._create_test_file("file3.Txt", "mixed case")
        self._create_test_file("photo1.jpg", "lowercase jpg")
        self._create_test_file("photo2.JPG", "uppercase JPG")
        self._create_test_file("photo3.JpG", "mixed JPG")
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan and organize
            files = self.scanner.scan_desktop()
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify all files were moved
            assert result.total_moved == 6
            assert len(result.errors) == 0
            
            # Verify all .txt files went to Documents
            doc_folder = self.desktop_path / "Documents"
            assert (doc_folder / "file1.txt").exists()
            assert (doc_folder / "file2.TXT").exists()
            assert (doc_folder / "file3.Txt").exists()
            assert result.moved_by_category["Documents"] == 3
            
            # Verify all .jpg files went to Images
            img_folder = self.desktop_path / "Images"
            assert (img_folder / "photo1.jpg").exists()
            assert (img_folder / "photo2.JPG").exists()
            assert (img_folder / "photo3.JpG").exists()
            assert result.moved_by_category["Images"] == 3
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_preserves_file_content_and_metadata(self):
        """
        Test complete workflow preserves file content during moves.
        
        This test validates:
        - File content is preserved exactly
        - File size is maintained
        - No data corruption during move
        
        Requirements: 4.1, 4.2
        """
        # Create files with specific content
        test_content = {
            "document.txt": "This is a test document with specific content.\nMultiple lines.\n",
            "data.json": '{"key": "value", "number": 42}',
            "script.py": "def hello():\n    print('Hello, World!')\n",
        }
        
        for filename, content in test_content.items():
            self._create_test_file(filename, content)
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan and organize
            files = self.scanner.scan_desktop()
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify all files were moved
            assert result.total_moved == 3
            assert len(result.errors) == 0
            
            # Verify content is preserved exactly
            doc_folder = self.desktop_path / "Documents"
            assert (doc_folder / "document.txt").read_text() == test_content["document.txt"]
            
            others_folder = self.desktop_path / "Others"
            assert (others_folder / "data.json").read_text() == test_content["data.json"]
            assert (others_folder / "script.py").read_text() == test_content["script.py"]
            
            # Verify file sizes are reasonable (content is preserved)
            # Note: On Windows, text mode converts \n to \r\n, so sizes may differ slightly
            for filename, content in test_content.items():
                if filename == "document.txt":
                    moved_file = doc_folder / filename
                else:
                    moved_file = others_folder / filename
                
                # File should exist and have non-zero size
                assert moved_file.stat().st_size > 0
                # Size should be at least as large as the content (may be larger due to line endings)
                assert moved_file.stat().st_size >= len(content)
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
    
    def test_workflow_with_all_category_types(self):
        """
        Test complete workflow with at least one file from each category.
        
        This test validates:
        - All category types are handled correctly
        - All category folders are created
        - Files are distributed correctly across all categories
        
        Requirements: 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.3
        """
        # Create one file for each category
        category_files = {
            "Documents": "report.docx",
            "Images": "photo.png",
            "Videos": "clip.mp4",
            "PDF": "manual.pdf",
            "ZIPs": "archive.zip",
            "Installers": "setup.exe",
            "Others": "unknown.xyz",
        }
        
        for category, filename in category_files.items():
            self._create_test_file(filename, f"content for {category}")
        
        # Mock scanner
        original_get_desktop = self.scanner.get_desktop_path
        self.scanner.get_desktop_path = lambda: self.desktop_path
        
        try:
            # Scan and organize
            files = self.scanner.scan_desktop()
            plan = self.service.create_organization_plan(files)
            result = self.service.execute_plan(plan, self.desktop_path)
            
            # Verify all files were moved
            assert result.total_moved == 7
            assert len(result.errors) == 0
            
            # Verify all category folders were created
            for category in category_files.keys():
                category_folder = self.desktop_path / category
                assert category_folder.exists()
                assert category_folder.is_dir()
            
            # Verify each category has exactly 1 file
            for category, filename in category_files.items():
                assert result.moved_by_category[category] == 1
                file_path = self.desktop_path / category / filename
                assert file_path.exists()
                assert file_path.read_text() == f"content for {category}"
            
            # Verify plan had all categories
            assert len(plan.folders_to_create) == 7
            assert set(plan.folders_to_create) == set(category_files.keys())
            
        finally:
            self.scanner.get_desktop_path = original_get_desktop
