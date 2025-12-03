"""Tests for the Desktop Cleaner Service."""

import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings
from src.service import DesktopCleanerService
from src.models import FileInfo, OrganizationPlan


# Feature: desktop-cleaner, Property 10: Move count consistency
@settings(max_examples=100, deadline=None)
@given(
    file_count=st.integers(min_value=0, max_value=50),
    seed=st.integers(min_value=0, max_value=1000000)
)
def test_move_count_consistency(file_count, seed):
    """
    Property 10: Move count consistency
    For any organization operation, the sum of files moved per category 
    should equal the total number of files in the organization plan.
    
    Validates: Requirements 4.4
    """
    service = DesktopCleanerService()
    
    # Create a temporary desktop directory
    with tempfile.TemporaryDirectory() as temp_dir:
        desktop_path = Path(temp_dir)
        
        # Generate random files with various extensions
        extensions = ['.txt', '.jpg', '.mp4', '.pdf', '.zip', '.exe', '.unknown']
        files = []
        
        for i in range(file_count):
            ext = extensions[(seed + i) % len(extensions)]
            file_path = desktop_path / f"file_{i}{ext}"
            file_path.write_text(f"content {i}")
            
            files.append(FileInfo(
                path=file_path,
                name=file_path.name,
                extension=ext,
                size=len(f"content {i}")
            ))
        
        # Create organization plan
        plan = service.create_organization_plan(files)
        
        # Execute the plan
        result = service.execute_plan(plan, desktop_path)
        
        # Property: sum of moved_by_category should equal total_moved
        sum_by_category = sum(result.moved_by_category.values())
        assert sum_by_category == result.total_moved, \
            f"Sum of files by category ({sum_by_category}) != total moved ({result.total_moved})"
        
        # Also verify it matches the plan's total_files (if no errors)
        if not result.errors:
            assert result.total_moved == plan.total_files, \
                f"Total moved ({result.total_moved}) != planned files ({plan.total_files})"



# Feature: desktop-cleaner, Property 11: Error resilience
@settings(max_examples=100, deadline=None)
@given(
    file_count=st.integers(min_value=2, max_value=20),
    fail_count=st.integers(min_value=1, max_value=5)
)
def test_error_resilience(file_count, fail_count):
    """
    Property 11: Error resilience
    For any set of files where some operations fail, the system should 
    continue processing remaining files, collect all error messages, 
    and successfully move all files that don't have errors.
    
    Validates: Requirements 4.5, 8.1, 8.2, 8.3
    """
    service = DesktopCleanerService()
    
    # Create a temporary desktop directory
    with tempfile.TemporaryDirectory() as temp_dir:
        desktop_path = Path(temp_dir)
        
        # Limit fail_count to file_count
        actual_fail_count = min(fail_count, file_count)
        
        # Generate files
        extensions = ['.txt', '.jpg', '.pdf']
        files = []
        
        for i in range(file_count):
            ext = extensions[i % len(extensions)]
            file_path = desktop_path / f"file_{i}{ext}"
            
            # Create files - some will be non-existent to simulate access errors
            if i < actual_fail_count:
                # Don't create the file - this will cause a move failure
                # But still add it to the list as if it was scanned
                pass
            else:
                # Create normal file
                file_path.write_text(f"content {i}")
            
            files.append(FileInfo(
                path=file_path,
                name=file_path.name,
                extension=ext,
                size=len(f"content {i}")
            ))
        
        # Create organization plan
        plan = service.create_organization_plan(files)
        
        # Execute the plan
        result = service.execute_plan(plan, desktop_path)
        
        # Property 1: Errors should be collected for files that don't exist
        assert len(result.errors) >= actual_fail_count, \
            f"Expected at least {actual_fail_count} errors, got {len(result.errors)}"
        
        # Property 2: Files that exist should still be moved
        expected_success = file_count - actual_fail_count
        assert result.total_moved == expected_success, \
            f"Expected {expected_success} files moved, got {result.total_moved}"
        
        # Property 3: The system should not crash (we got here, so it didn't crash)
        assert result is not None
        
        # Property 4: Total moved + errors should account for all files
        assert result.total_moved + len(result.errors) >= file_count, \
            f"Total moved ({result.total_moved}) + errors ({len(result.errors)}) should be >= {file_count}"



# Feature: desktop-cleaner, Property 12: Plan summary completeness
@settings(max_examples=100, deadline=None)
@given(
    file_count=st.integers(min_value=0, max_value=50),
    seed=st.integers(min_value=0, max_value=1000000)
)
def test_plan_summary_completeness(file_count, seed):
    """
    Property 12: Plan summary completeness
    For any organization plan, the plan should contain the count of files 
    per category and the list of folders to be created.
    
    Validates: Requirements 5.2, 5.3
    """
    service = DesktopCleanerService()
    
    # Create a temporary desktop directory
    with tempfile.TemporaryDirectory() as temp_dir:
        desktop_path = Path(temp_dir)
        
        # Generate random files with various extensions
        extensions = ['.txt', '.jpg', '.mp4', '.pdf', '.zip', '.exe', '.unknown', '.docx']
        files = []
        
        for i in range(file_count):
            ext = extensions[(seed + i) % len(extensions)]
            file_path = desktop_path / f"file_{i}{ext}"
            file_path.write_text(f"content {i}")
            
            files.append(FileInfo(
                path=file_path,
                name=file_path.name,
                extension=ext,
                size=len(f"content {i}")
            ))
        
        # Create organization plan
        plan = service.create_organization_plan(files)
        
        # Property 1: Plan should have files_by_category
        assert plan.files_by_category is not None
        assert isinstance(plan.files_by_category, dict)
        
        # Property 2: Plan should have folders_to_create
        assert plan.folders_to_create is not None
        assert isinstance(plan.folders_to_create, list)
        
        # Property 3: folders_to_create should match categories in files_by_category
        assert set(plan.folders_to_create) == set(plan.files_by_category.keys()), \
            f"Folders to create {set(plan.folders_to_create)} != categories {set(plan.files_by_category.keys())}"
        
        # Property 4: Sum of files per category should equal total_files
        total_in_categories = sum(len(files) for files in plan.files_by_category.values())
        assert total_in_categories == plan.total_files, \
            f"Sum of files in categories ({total_in_categories}) != total_files ({plan.total_files})"
        
        # Property 5: total_files should match input file count
        assert plan.total_files == file_count, \
            f"Plan total_files ({plan.total_files}) != input file count ({file_count})"



# Feature: desktop-cleaner, Property 14: Result summary completeness
@settings(max_examples=100, deadline=None)
@given(
    file_count=st.integers(min_value=0, max_value=50),
    seed=st.integers(min_value=0, max_value=1000000)
)
def test_result_summary_completeness(file_count, seed):
    """
    Property 14: Result summary completeness
    For any execution result, the result should contain the total files moved, 
    the breakdown per category, any errors encountered, and the operation duration.
    
    Validates: Requirements 7.2, 7.3, 7.4, 7.5
    """
    service = DesktopCleanerService()
    
    # Create a temporary desktop directory
    with tempfile.TemporaryDirectory() as temp_dir:
        desktop_path = Path(temp_dir)
        
        # Generate random files with various extensions
        extensions = ['.txt', '.jpg', '.mp4', '.pdf', '.zip', '.exe', '.unknown']
        files = []
        
        for i in range(file_count):
            ext = extensions[(seed + i) % len(extensions)]
            file_path = desktop_path / f"file_{i}{ext}"
            file_path.write_text(f"content {i}")
            
            files.append(FileInfo(
                path=file_path,
                name=file_path.name,
                extension=ext,
                size=len(f"content {i}")
            ))
        
        # Create organization plan
        plan = service.create_organization_plan(files)
        
        # Execute the plan
        result = service.execute_plan(plan, desktop_path)
        
        # Property 1: Result should have total_moved (Requirement 7.2)
        assert result.total_moved is not None
        assert isinstance(result.total_moved, int)
        assert result.total_moved >= 0
        
        # Property 2: Result should have moved_by_category breakdown (Requirement 7.3)
        assert result.moved_by_category is not None
        assert isinstance(result.moved_by_category, dict)
        
        # Property 3: Result should have errors list (Requirement 7.4)
        assert result.errors is not None
        assert isinstance(result.errors, list)
        
        # Property 4: Result should have duration (Requirement 7.5)
        assert result.duration is not None
        assert isinstance(result.duration, (int, float))
        assert result.duration >= 0, f"Duration should be non-negative, got {result.duration}"
        
        # Property 5: moved_by_category should contain all categories from the plan
        for category in plan.folders_to_create:
            assert category in result.moved_by_category, \
                f"Category {category} missing from result breakdown"
