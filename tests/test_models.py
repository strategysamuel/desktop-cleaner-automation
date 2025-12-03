"""Tests for data models."""

from pathlib import Path
from src.models import FileInfo, OrganizationPlan, MoveResult, ExecutionResult


def test_file_info_creation():
    """Test that FileInfo can be created with required fields."""
    file_info = FileInfo(
        path=Path("test.txt"),
        name="test.txt",
        extension=".txt",
        size=1024
    )
    assert file_info.name == "test.txt"
    assert file_info.extension == ".txt"
    assert file_info.size == 1024


def test_organization_plan_creation():
    """Test that OrganizationPlan can be created."""
    plan = OrganizationPlan(
        files_by_category={"Documents": []},
        folders_to_create=["Documents"],
        total_files=0
    )
    assert plan.total_files == 0
    assert "Documents" in plan.folders_to_create


def test_move_result_creation():
    """Test that MoveResult can be created."""
    result = MoveResult(
        success=True,
        source=Path("test.txt"),
        destination=Path("Documents/test.txt"),
        error=None
    )
    assert result.success is True
    assert result.error is None


def test_execution_result_creation():
    """Test that ExecutionResult can be created."""
    result = ExecutionResult(
        total_moved=5,
        moved_by_category={"Documents": 3, "Images": 2},
        errors=[],
        duration=1.5
    )
    assert result.total_moved == 5
    assert len(result.errors) == 0
    assert result.duration == 1.5
