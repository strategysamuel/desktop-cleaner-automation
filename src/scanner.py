"""Desktop scanning module for the Desktop Cleaner."""

import os
from pathlib import Path
from typing import List
from src.models import FileInfo


class DesktopScanner:
    """Scans the Desktop directory and identifies files for organization."""
    
    # Category folders that should be excluded from scanning
    CATEGORY_FOLDERS = {"Documents", "Images", "Videos", "PDF", "ZIPs", "Installers", "Others"}
    
    def get_desktop_path(self) -> Path:
        """
        Get the path to the Windows Desktop directory for the current user.
        
        Returns:
            Path to the Desktop directory
            
        Raises:
            FileNotFoundError: If Desktop directory cannot be located
        """
        desktop_path = Path.home() / "Desktop"
        
        if not desktop_path.exists():
            raise FileNotFoundError(f"Desktop directory not found at {desktop_path}")
        
        return desktop_path
    
    def should_exclude(self, file_path: Path) -> bool:
        """
        Determine if a file should be excluded from organization.
        
        Exclusion rules:
        - Category folders created by Desktop Cleaner
        - Hidden files
        - System files (desktop.ini)
        - Directories
        
        Args:
            file_path: Path to check
            
        Returns:
            True if the file should be excluded, False otherwise
        """
        # Exclude directories
        if file_path.is_dir():
            # Check if it's a category folder
            if file_path.name in self.CATEGORY_FOLDERS:
                return True
            # Exclude all other directories too
            return True
        
        # Exclude desktop.ini
        if file_path.name.lower() == "desktop.ini":
            return True
        
        # Exclude hidden files (Windows: check file attributes)
        try:
            # On Windows, check if file has hidden attribute
            if os.name == 'nt':
                import stat
                attrs = os.stat(file_path).st_file_attributes
                if attrs & stat.FILE_ATTRIBUTE_HIDDEN:
                    return True
            else:
                # On Unix-like systems, hidden files start with a dot
                if file_path.name.startswith('.'):
                    return True
        except (AttributeError, OSError):
            # If we can't check attributes, don't exclude based on hidden status
            pass
        
        return False
    
    def scan_desktop(self) -> List[FileInfo]:
        """
        Scan the Desktop directory and return a list of files to organize.
        
        Returns:
            List of FileInfo objects for files that should be organized
            
        Raises:
            PermissionError: If Desktop directory cannot be accessed
            FileNotFoundError: If Desktop directory doesn't exist
        """
        desktop_path = self.get_desktop_path()
        
        # Check if we can access the directory
        if not os.access(desktop_path, os.R_OK):
            raise PermissionError(f"Cannot access Desktop directory at {desktop_path}")
        
        files = []
        
        try:
            # Iterate through all items in the Desktop directory
            for item in desktop_path.iterdir():
                # Skip excluded items
                if self.should_exclude(item):
                    continue
                
                # Only process files (not directories)
                if item.is_file():
                    try:
                        file_info = FileInfo(
                            path=item,
                            name=item.name,
                            extension=item.suffix.lower(),
                            size=item.stat().st_size
                        )
                        files.append(file_info)
                    except OSError:
                        # Skip files we can't access
                        continue
        except PermissionError as e:
            raise PermissionError(f"Cannot access Desktop directory: {e}")
        
        return files
