# Design Document

## Overview

The Desktop Cleaner Automation Tool is a command-line application for Windows that automatically organizes Desktop files into categorized folders. The system follows a scan-plan-execute workflow: it scans the Desktop to identify files, creates an organization plan showing which files will be moved to which categories, requests user confirmation, and then executes the file moves. The tool is designed to be safe, transparent, and resilient to errors.

The application will be built using Python for cross-platform compatibility and ease of file system operations. It will use a modular architecture with clear separation between file scanning, categorization logic, folder management, and file operations.

## Architecture

The system follows a layered architecture with the following components:

```
┌─────────────────────────────────────┐
│         CLI Interface               │
│  (User interaction & display)       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│      Desktop Cleaner Service        │
│  (Orchestration & workflow)         │
└─────────────────────────────────────┘
              ↓
┌──────────────┬──────────────┬───────────────┐
│   Scanner    │ Categorizer  │ File Mover    │
│   Module     │   Module     │   Module      │
└──────────────┴──────────────┴───────────────┘
              ↓
┌─────────────────────────────────────┐
│      File System Operations         │
│         (OS Interface)              │
└─────────────────────────────────────┘
```

**Layer Responsibilities:**

1. **CLI Interface**: Handles user input/output, displays summaries, and manages confirmation prompts
2. **Desktop Cleaner Service**: Orchestrates the overall workflow and coordinates between modules
3. **Scanner Module**: Discovers files on the Desktop and filters out excluded items
4. **Categorizer Module**: Maps file extensions to categories using predefined rules
5. **File Mover Module**: Creates folders and moves files with conflict resolution
6. **File System Operations**: Low-level OS interactions for file and folder operations

## Components and Interfaces

### 1. Scanner Module

**Responsibility**: Scan the Desktop directory and identify files for organization.

**Interface**:
```python
class DesktopScanner:
    def get_desktop_path() -> Path
    def scan_desktop() -> List[FileInfo]
    def should_exclude(file_path: Path) -> bool
```

**Key Functions**:
- `get_desktop_path()`: Returns the Windows Desktop path for the current user
- `scan_desktop()`: Returns a list of FileInfo objects representing files to organize
- `should_exclude()`: Determines if a file should be skipped based on exclusion rules

**Exclusion Rules**:
- Existing category folders (Documents, Images, Videos, PDF, ZIPs, Installers, Others)
- Hidden files
- System files (desktop.ini)
- Directories (except category folders)
- Shortcuts

### 2. Categorizer Module

**Responsibility**: Map file extensions to categories.

**Interface**:
```python
class FileCategorizer:
    def get_category(file_path: Path) -> str
    def get_extension_mapping() -> Dict[str, str]
```

**Category Mappings**:
- **Documents**: .doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx
- **Images**: .jpg, .jpeg, .png, .gif, .bmp, .svg, .ico, .webp
- **Videos**: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm
- **PDF**: .pdf
- **ZIPs**: .zip, .rar, .7z, .tar, .gz
- **Installers**: .exe, .msi, .dmg, .pkg
- **Others**: All unmatched extensions

**Key Functions**:
- `get_category()`: Returns the category name for a given file
- `get_extension_mapping()`: Returns the complete extension-to-category mapping

### 3. File Mover Module

**Responsibility**: Create category folders and move files.

**Interface**:
```python
class FileMover:
    def create_category_folder(desktop_path: Path, category: str) -> bool
    def move_file(source: Path, destination_folder: Path) -> MoveResult
    def resolve_name_conflict(destination: Path) -> Path
```

**Key Functions**:
- `create_category_folder()`: Creates a category folder if it doesn't exist
- `move_file()`: Moves a file to the destination folder with error handling
- `resolve_name_conflict()`: Appends numeric suffix if filename already exists

**Conflict Resolution Strategy**:
- If `document.pdf` exists, try `document_1.pdf`, `document_2.pdf`, etc.
- Continue incrementing until an available name is found

### 4. Desktop Cleaner Service

**Responsibility**: Orchestrate the complete workflow.

**Interface**:
```python
class DesktopCleanerService:
    def run() -> None
    def create_organization_plan(files: List[FileInfo]) -> OrganizationPlan
    def execute_plan(plan: OrganizationPlan) -> ExecutionResult
```

**Workflow**:
1. Scan Desktop and get list of files
2. Categorize each file
3. Create organization plan
4. Display plan summary to user
5. Request confirmation
6. Execute plan if confirmed
7. Display results

### 5. CLI Interface

**Responsibility**: Handle user interaction and display.

**Interface**:
```python
class CLI:
    def display_plan_summary(plan: OrganizationPlan) -> None
    def request_confirmation() -> bool
    def display_results(result: ExecutionResult) -> None
    def display_error(error: str) -> None
```

**Display Elements**:
- Plan summary showing files per category
- Folders to be created
- Confirmation prompt
- Progress indicators during execution
- Final results with statistics
- Error messages if any

## Data Models

### FileInfo
```python
@dataclass
class FileInfo:
    path: Path
    name: str
    extension: str
    size: int
```

### OrganizationPlan
```python
@dataclass
class OrganizationPlan:
    files_by_category: Dict[str, List[FileInfo]]
    folders_to_create: List[str]
    total_files: int
```

### MoveResult
```python
@dataclass
class MoveResult:
    success: bool
    source: Path
    destination: Path
    error: Optional[str]
```

### ExecutionResult
```python
@dataclass
class ExecutionResult:
    total_moved: int
    moved_by_category: Dict[str, int]
    errors: List[str]
    duration: float
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Scan completeness
*For any* directory with a known set of files, scanning should return exactly those files (excluding folders and excluded items), and the count should match the number of files returned.
**Validates: Requirements 1.2, 1.3, 1.4**

### Property 2: Extension extraction consistency
*For any* file path with an extension, extracting the extension should return the characters after the last dot, and the result should be case-insensitive.
**Validates: Requirements 2.1**

### Property 3: Category mapping totality
*For any* file extension (including random/unknown extensions), the categorizer should return exactly one category name, never null or empty.
**Validates: Requirements 2.2**

### Property 4: Unknown extensions default to Others
*For any* file extension that is not in the predefined category lists, the categorizer should return "Others" as the category.
**Validates: Requirements 2.9**

### Property 5: Case-insensitive categorization
*For any* file extension, the uppercase, lowercase, and mixed-case versions should all map to the same category.
**Validates: Requirements 2.10**

### Property 6: Folder creation idempotence
*For any* category name, creating the folder multiple times should succeed without errors, and only one folder should exist after multiple creation attempts.
**Validates: Requirements 3.2, 3.4**

### Property 7: Folder name matches category
*For any* category, the created folder path should end with the exact category name.
**Validates: Requirements 3.3**

### Property 8: File move preserves filename
*For any* file moved to a category folder (without naming conflicts), the filename in the destination should match the original filename exactly.
**Validates: Requirements 4.2**

### Property 9: Name conflict resolution uniqueness
*For any* file moved to a category folder where a file with the same name exists, the system should generate a unique filename with a numeric suffix, and no files should be overwritten.
**Validates: Requirements 4.3**

### Property 10: Move count consistency
*For any* organization operation, the sum of files moved per category should equal the total number of files in the organization plan.
**Validates: Requirements 4.4**

### Property 11: Error resilience
*For any* set of files where some operations fail, the system should continue processing remaining files, collect all error messages, and successfully move all files that don't have errors.
**Validates: Requirements 4.5, 8.1, 8.2, 8.3**

### Property 12: Plan summary completeness
*For any* organization plan, the plan should contain the count of files per category and the list of folders to be created.
**Validates: Requirements 5.2, 5.3**

### Property 13: Exclusion consistency
*For any* scan operation, the results should not include category folders, hidden files, or system files, and the count should only reflect non-excluded files.
**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

### Property 14: Result summary completeness
*For any* execution result, the result should contain the total files moved, the breakdown per category, any errors encountered, and the operation duration.
**Validates: Requirements 7.2, 7.3, 7.4, 7.5**

## Error Handling

The system implements a fail-safe approach to error handling:

**Error Categories**:

1. **Critical Errors** (stop execution):
   - Desktop directory not found
   - Desktop directory not accessible
   - Invalid permissions on Desktop

2. **Recoverable Errors** (log and continue):
   - Individual file access failures
   - Individual file move failures
   - Folder creation failures for specific categories

**Error Handling Strategy**:

- All errors include descriptive messages with context (file path, operation, reason)
- Recoverable errors are collected in a list and reported at the end
- Critical errors cause immediate termination with error message
- Partial success is acceptable - some files can be organized even if others fail
- No silent failures - all errors are reported to the user

**Error Logging**:
- Errors are collected in the ExecutionResult object
- Each error includes: operation type, file path, and error message
- Errors are displayed in the final summary

## Testing Strategy

The Desktop Cleaner will be tested using a dual approach combining unit tests and property-based tests.

**Property-Based Testing**:

We will use **Hypothesis** (Python's property-based testing library) to verify the correctness properties defined above. Each property will be implemented as a separate property-based test that:
- Generates random test inputs (file paths, extensions, directory structures)
- Executes the relevant system function
- Verifies the property holds for all generated inputs
- Runs a minimum of 100 iterations per property

Each property-based test will be tagged with a comment in this format:
`# Feature: desktop-cleaner, Property {number}: {property_text}`

This ensures traceability between the design properties and test implementation.

**Unit Testing**:

Unit tests will cover:
- Specific extension mappings (Documents, Images, Videos, PDF, ZIPs, Installers categories)
- Desktop path detection on Windows
- Specific exclusion cases (desktop.ini file)
- Error handling for inaccessible directories
- User cancellation behavior
- Critical error scenarios

**Test Organization**:
- `test_scanner.py`: Tests for DesktopScanner module
- `test_categorizer.py`: Tests for FileCategorizer module
- `test_file_mover.py`: Tests for FileMover module
- `test_service.py`: Tests for DesktopCleanerService orchestration
- `test_integration.py`: End-to-end integration tests

**Test Environment**:
- Tests will use temporary directories to avoid affecting real Desktop
- Mock file systems will be created for testing various scenarios
- Tests will be platform-aware (Windows-specific paths)

## Implementation Notes

**Technology Stack**:
- **Language**: Python 3.8+
- **Standard Libraries**: pathlib, shutil, os
- **Testing**: pytest, hypothesis
- **CLI**: Built-in input/print (simple CLI, no external dependencies)

**Platform Considerations**:
- Primary target: Windows 10/11
- Desktop path detection uses `os.path.expanduser("~/Desktop")`
- File operations use pathlib for cross-platform compatibility
- Hidden file detection uses Windows file attributes

**Performance Considerations**:
- Scanning is done in a single pass
- No recursive directory traversal (Desktop only)
- File moves are atomic operations
- Expected to handle 100-1000 files efficiently

**Security Considerations**:
- No files are deleted, only moved
- User confirmation required before any changes
- Dry-run mode shows plan before execution
- No external network access
- No elevation of privileges required
