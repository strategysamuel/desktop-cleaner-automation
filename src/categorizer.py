"""File categorization module for the Desktop Cleaner."""

from pathlib import Path
from typing import Dict


class FileCategorizer:
    """Categorizes files based on their extensions."""
    
    # Category mappings
    CATEGORIES = {
        "Documents": [".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".ico", ".webp"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
        "PDF": [".pdf"],
        "ZIPs": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Installers": [".exe", ".msi", ".dmg", ".pkg"],
    }
    
    def __init__(self):
        """Initialize the FileCategorizer."""
        # Create reverse mapping for faster lookup
        self._extension_to_category = {}
        for category, extensions in self.CATEGORIES.items():
            for ext in extensions:
                self._extension_to_category[ext.lower()] = category
    
    def get_category(self, file_path: Path) -> str:
        """
        Get the category for a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name (Documents, Images, Videos, PDF, ZIPs, Installers, or Others)
        """
        # Extract extension and normalize to lowercase
        extension = file_path.suffix.lower()
        
        # Look up category, default to "Others" if not found
        return self._extension_to_category.get(extension, "Others")
    
    def get_extension_mapping(self) -> Dict[str, str]:
        """
        Get the complete extension-to-category mapping.
        
        Returns:
            Dictionary mapping extensions to category names
        """
        return self._extension_to_category.copy()
