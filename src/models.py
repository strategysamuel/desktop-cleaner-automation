"""Data models for the Desktop Cleaner application."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class FileInfo:
    """Information about a file to be organized."""
    path: Path
    name: str
    extension: str
    size: int


@dataclass
class OrganizationPlan:
    """Plan for organizing files into categories."""
    files_by_category: Dict[str, List[FileInfo]]
    folders_to_create: List[str]
    total_files: int


@dataclass
class MoveResult:
    """Result of a single file move operation."""
    success: bool
    source: Path
    destination: Path
    error: Optional[str]


@dataclass
class ExecutionResult:
    """Result of the complete organization execution."""
    total_moved: int
    moved_by_category: Dict[str, int]
    errors: List[str]
    duration: float
