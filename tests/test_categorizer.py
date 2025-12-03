"""Tests for the FileCategorizer module."""

from pathlib import Path
import pytest
from hypothesis import given, strategies as st

from src.categorizer import FileCategorizer


class TestCategoryMappings:
    """Unit tests for specific category mappings."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.categorizer = FileCategorizer()
    
    def test_documents_extensions(self):
        """Test Documents extensions (.doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx)."""
        documents_extensions = [".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"]
        
        for ext in documents_extensions:
            file_path = Path(f"test{ext}")
            assert self.categorizer.get_category(file_path) == "Documents", \
                f"Extension {ext} should map to Documents"
    
    def test_images_extensions(self):
        """Test Images extensions (.jpg, .jpeg, .png, .gif, .bmp, .svg, .ico, .webp)."""
        images_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp"]
        
        for ext in images_extensions:
            file_path = Path(f"test{ext}")
            assert self.categorizer.get_category(file_path) == "Images", \
                f"Extension {ext} should map to Images"
    
    def test_videos_extensions(self):
        """Test Videos extensions (.mp4, .avi, .mkv, .mov, .wmv, .flv, .webm)."""
        videos_extensions = [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"]
        
        for ext in videos_extensions:
            file_path = Path(f"test{ext}")
            assert self.categorizer.get_category(file_path) == "Videos", \
                f"Extension {ext} should map to Videos"
    
    def test_pdf_extension(self):
        """Test PDF extension (.pdf)."""
        file_path = Path("test.pdf")
        assert self.categorizer.get_category(file_path) == "PDF"
    
    def test_zips_extensions(self):
        """Test ZIPs extensions (.zip, .rar, .7z, .tar, .gz)."""
        zips_extensions = [".zip", ".rar", ".7z", ".tar", ".gz"]
        
        for ext in zips_extensions:
            file_path = Path(f"test{ext}")
            assert self.categorizer.get_category(file_path) == "ZIPs", \
                f"Extension {ext} should map to ZIPs"
    
    def test_installers_extensions(self):
        """Test Installers extensions (.exe, .msi, .dmg, .pkg)."""
        installers_extensions = [".exe", ".msi", ".dmg", ".pkg"]
        
        for ext in installers_extensions:
            file_path = Path(f"test{ext}")
            assert self.categorizer.get_category(file_path) == "Installers", \
                f"Extension {ext} should map to Installers"



class TestCategoryProperties:
    """Property-based tests for FileCategorizer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.categorizer = FileCategorizer()
    
    @given(
        filename=st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))),
        extension=st.text(min_size=1, max_size=10, alphabet=st.characters(min_codepoint=97, max_codepoint=122))
    )
    def test_extension_extraction_consistency(self, filename, extension):
        """
        Feature: desktop-cleaner, Property 2: Extension extraction consistency
        Validates: Requirements 2.1
        
        For any file path with an extension, extracting the extension should return 
        the characters after the last dot, and the result should be case-insensitive.
        """
        # Create a file path with explicit extension
        full_filename = f"{filename}.{extension}"
        file_path = Path(full_filename)
        
        # Get category (which internally extracts extension)
        category = self.categorizer.get_category(file_path)
        
        # Verify that a category is returned (extension was extracted)
        assert category is not None
        assert isinstance(category, str)
        assert len(category) > 0
        
        # Verify case-insensitivity: same file with different case should give same result
        upper_path = Path(full_filename.upper())
        lower_path = Path(full_filename.lower())
        
        assert self.categorizer.get_category(upper_path) == self.categorizer.get_category(lower_path)
    
    @given(st.text(min_size=1, max_size=50))
    def test_category_mapping_totality(self, extension):
        """
        Feature: desktop-cleaner, Property 3: Category mapping totality
        Validates: Requirements 2.2
        
        For any file extension (including random/unknown extensions), the categorizer 
        should return exactly one category name, never null or empty.
        """
        # Create a file path with the given extension
        file_path = Path(f"test.{extension}")
        
        # Get category
        category = self.categorizer.get_category(file_path)
        
        # Verify category is not null or empty
        assert category is not None
        assert isinstance(category, str)
        assert len(category) > 0
    
    @given(st.text(min_size=1, max_size=20).filter(
        lambda x: x.lower() not in [
            "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx",
            "jpg", "jpeg", "png", "gif", "bmp", "svg", "ico", "webp",
            "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm",
            "pdf",
            "zip", "rar", "7z", "tar", "gz",
            "exe", "msi", "dmg", "pkg"
        ]
    ))
    def test_unknown_extensions_default_to_others(self, unknown_ext):
        """
        Feature: desktop-cleaner, Property 4: Unknown extensions default to Others
        Validates: Requirements 2.9
        
        For any file extension that is not in the predefined category lists, 
        the categorizer should return "Others" as the category.
        """
        file_path = Path(f"test.{unknown_ext}")
        category = self.categorizer.get_category(file_path)
        
        assert category == "Others"
    
    @given(st.sampled_from([
        "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx", "ppt", "pptx",
        "jpg", "jpeg", "png", "gif", "bmp", "svg", "ico", "webp",
        "mp4", "avi", "mkv", "mov", "wmv", "flv", "webm",
        "pdf",
        "zip", "rar", "7z", "tar", "gz",
        "exe", "msi", "dmg", "pkg"
    ]))
    def test_case_insensitive_categorization(self, extension):
        """
        Feature: desktop-cleaner, Property 5: Case-insensitive categorization
        Validates: Requirements 2.10
        
        For any file extension, the uppercase, lowercase, and mixed-case versions 
        should all map to the same category.
        """
        # Create paths with different case variations
        lower_path = Path(f"test.{extension.lower()}")
        upper_path = Path(f"test.{extension.upper()}")
        mixed_path = Path(f"test.{extension.capitalize()}")
        
        # Get categories
        lower_category = self.categorizer.get_category(lower_path)
        upper_category = self.categorizer.get_category(upper_path)
        mixed_category = self.categorizer.get_category(mixed_path)
        
        # All should be the same
        assert lower_category == upper_category
        assert lower_category == mixed_category
        assert upper_category == mixed_category
