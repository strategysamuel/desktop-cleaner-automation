"""File moving module for the Desktop Cleaner."""

import shutil
from pathlib import Path
from src.models import MoveResult


class FileMover:
    """Handles folder creation and file moving operations."""
    
    def create_category_folder(self, desktop_path: Path, category: str) -> bool:
        """
        Create a category folder on the Desktop if it doesn't exist.
        
        Args:
            desktop_path: Path to the Desktop directory
            category: Name of the category folder to create
            
        Returns:
            True if folder was created or already exists, False on error
        """
        folder_path = desktop_path / category
        
        try:
            # Create folder if it doesn't exist (exist_ok=True makes it idempotent)
            folder_path.mkdir(exist_ok=True)
            return True
        except (OSError, PermissionError) as e:
            # Return False if folder creation fails
            return False
    
    def resolve_name_conflict(self, destination: Path) -> Path:
        """
        Resolve filename conflicts by appending numeric suffixes.
        
        If a file already exists at the destination, this method generates
        a new filename with a numeric suffix (e.g., file_1.txt, file_2.txt).
        
        Args:
            destination: Original destination path
            
        Returns:
            Path with a unique filename that doesn't conflict
        """
        if not destination.exists():
            return destination
        
        # Extract stem (filename without extension) and suffix (extension)
        stem = destination.stem
        suffix = destination.suffix
        parent = destination.parent
        
        # Try incrementing numbers until we find an available name
        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            
            if not new_path.exists():
                return new_path
            
            counter += 1
    
    def move_file(self, source: Path, destination_folder: Path) -> MoveResult:
        """
        Move a file to the destination folder with error handling.
        
        Preserves the original filename unless there's a naming conflict,
        in which case a numeric suffix is appended.
        
        Args:
            source: Path to the source file
            destination_folder: Path to the destination folder
            
        Returns:
            MoveResult object containing success status and details
        """
        try:
            # Construct destination path preserving original filename
            destination = destination_folder / source.name
            
            # Resolve any naming conflicts
            destination = self.resolve_name_conflict(destination)
            
            # Move the file
            shutil.move(str(source), str(destination))
            
            return MoveResult(
                success=True,
                source=source,
                destination=destination,
                error=None
            )
        except (OSError, PermissionError, shutil.Error) as e:
            # Return error result if move fails
            return MoveResult(
                success=False,
                source=source,
                destination=destination_folder / source.name,
                error=str(e)
            )
