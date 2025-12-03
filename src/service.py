"""Desktop Cleaner Service orchestration module."""

import time
from pathlib import Path
from typing import List
from src.models import FileInfo, OrganizationPlan, ExecutionResult
from src.scanner import DesktopScanner
from src.categorizer import FileCategorizer
from src.mover import FileMover


class DesktopCleanerService:
    """Orchestrates the complete Desktop cleaning workflow."""
    
    def __init__(self):
        """Initialize the service with required components."""
        self.scanner = DesktopScanner()
        self.categorizer = FileCategorizer()
        self.mover = FileMover()
    
    def create_organization_plan(self, files: List[FileInfo]) -> OrganizationPlan:
        """
        Create an organization plan by grouping files by category.
        
        Args:
            files: List of FileInfo objects to organize
            
        Returns:
            OrganizationPlan with files grouped by category
        """
        # Group files by category
        files_by_category = {}
        
        for file_info in files:
            category = self.categorizer.get_category(file_info.path)
            
            if category not in files_by_category:
                files_by_category[category] = []
            
            files_by_category[category].append(file_info)
        
        # Determine which folders need to be created
        folders_to_create = list(files_by_category.keys())
        
        return OrganizationPlan(
            files_by_category=files_by_category,
            folders_to_create=folders_to_create,
            total_files=len(files)
        )
    
    def execute_plan(self, plan: OrganizationPlan, desktop_path: Path) -> ExecutionResult:
        """
        Execute the organization plan by creating folders and moving files.
        
        Args:
            plan: OrganizationPlan to execute
            desktop_path: Path to the Desktop directory
            
        Returns:
            ExecutionResult with statistics and any errors
        """
        start_time = time.time()
        
        errors = []
        moved_by_category = {}
        total_moved = 0
        
        # Create category folders
        for category in plan.folders_to_create:
            success = self.mover.create_category_folder(desktop_path, category)
            if not success:
                errors.append(f"Failed to create folder for category: {category}")
        
        # Move files
        for category, files in plan.files_by_category.items():
            category_folder = desktop_path / category
            moved_count = 0
            
            for file_info in files:
                result = self.mover.move_file(file_info.path, category_folder)
                
                if result.success:
                    moved_count += 1
                    total_moved += 1
                else:
                    errors.append(f"Failed to move {file_info.name}: {result.error}")
            
            moved_by_category[category] = moved_count
        
        duration = time.time() - start_time
        
        return ExecutionResult(
            total_moved=total_moved,
            moved_by_category=moved_by_category,
            errors=errors,
            duration=duration
        )
