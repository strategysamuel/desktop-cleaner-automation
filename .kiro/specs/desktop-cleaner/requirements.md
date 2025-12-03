# Requirements Document

## Introduction

The Desktop Cleaner Automation Tool is a Windows desktop application that automatically organizes files on a user's Desktop by categorizing them into appropriate folders based on file type. The system scans the Desktop directory, identifies file types by extension, creates category folders if they don't exist, and moves files into their respective categories. This tool helps users maintain an organized Desktop without manual file management.

## Glossary

- **Desktop Cleaner**: The system that automatically organizes files on the Windows Desktop
- **Category Folder**: A folder created by the system to store files of a specific type (e.g., Documents, Images, Videos)
- **File Type**: The classification of a file based on its extension (e.g., .pdf, .jpg, .mp4)
- **Desktop Directory**: The Windows Desktop folder location for the current user
- **Scan Operation**: The process of reading all files present in the Desktop directory
- **Move Operation**: The process of relocating a file from the Desktop to a Category Folder

## Requirements

### Requirement 1

**User Story:** As a user, I want the system to scan my Desktop directory, so that all files can be identified for organization.

#### Acceptance Criteria

1. WHEN the Desktop Cleaner starts THEN the system SHALL locate the Windows Desktop directory for the current user
2. WHEN the Desktop directory is located THEN the system SHALL read all file entries in the Desktop directory
3. WHEN reading file entries THEN the system SHALL distinguish between files and folders
4. WHEN the scan completes THEN the system SHALL provide a count of files found for organization
5. IF the Desktop directory cannot be accessed THEN the system SHALL report an error with the specific access issue

### Requirement 2

**User Story:** As a user, I want files to be categorized by their type, so that similar files are grouped together.

#### Acceptance Criteria

1. WHEN a file is encountered THEN the system SHALL extract the file extension
2. WHEN the file extension is extracted THEN the system SHALL map the extension to a category using predefined rules
3. WHEN mapping to Documents category THEN the system SHALL include extensions: .doc, .docx, .txt, .rtf, .odt, .xls, .xlsx, .ppt, .pptx
4. WHEN mapping to Images category THEN the system SHALL include extensions: .jpg, .jpeg, .png, .gif, .bmp, .svg, .ico, .webp
5. WHEN mapping to Videos category THEN the system SHALL include extensions: .mp4, .avi, .mkv, .mov, .wmv, .flv, .webm
6. WHEN mapping to PDF category THEN the system SHALL include extensions: .pdf
7. WHEN mapping to ZIPs category THEN the system SHALL include extensions: .zip, .rar, .7z, .tar, .gz
8. WHEN mapping to Installers category THEN the system SHALL include extensions: .exe, .msi, .dmg, .pkg
9. WHEN a file extension does not match any category THEN the system SHALL assign the file to the Others category
10. WHEN categorizing files THEN the system SHALL treat file extensions as case-insensitive

### Requirement 3

**User Story:** As a user, I want category folders to be created automatically, so that I don't have to create them manually.

#### Acceptance Criteria

1. WHEN the Desktop Cleaner identifies files for a category THEN the system SHALL check if the Category Folder exists on the Desktop
2. IF a Category Folder does not exist THEN the system SHALL create the folder on the Desktop
3. WHEN creating a Category Folder THEN the system SHALL use the category name as the folder name
4. IF a Category Folder already exists THEN the system SHALL reuse the existing folder
5. IF folder creation fails THEN the system SHALL report an error with the specific failure reason

### Requirement 4

**User Story:** As a user, I want files to be moved into their category folders automatically, so that my Desktop becomes organized.

#### Acceptance Criteria

1. WHEN a file is categorized and the Category Folder exists THEN the system SHALL move the file into the Category Folder
2. WHEN moving a file THEN the system SHALL preserve the original filename
3. IF a file with the same name already exists in the Category Folder THEN the system SHALL append a numeric suffix to avoid overwriting
4. WHEN all files are processed THEN the system SHALL report the number of files moved per category
5. IF a file move operation fails THEN the system SHALL log the error and continue processing remaining files

### Requirement 5

**User Story:** As a user, I want to see what the system will do before it executes, so that I can verify the planned actions.

#### Acceptance Criteria

1. WHEN the Desktop Cleaner completes scanning THEN the system SHALL display a summary of planned actions
2. WHEN displaying the summary THEN the system SHALL show the number of files per category
3. WHEN displaying the summary THEN the system SHALL list which folders will be created
4. WHEN the user reviews the summary THEN the system SHALL wait for user confirmation before proceeding
5. IF the user cancels the operation THEN the system SHALL exit without making any changes

### Requirement 6

**User Story:** As a user, I want to exclude certain files or folders from organization, so that important items remain on my Desktop.

#### Acceptance Criteria

1. WHEN scanning the Desktop THEN the system SHALL skip existing Category Folders created by the Desktop Cleaner
2. WHEN scanning the Desktop THEN the system SHALL skip system folders and shortcuts
3. WHEN scanning the Desktop THEN the system SHALL skip hidden files
4. WHEN scanning the Desktop THEN the system SHALL skip files named "desktop.ini"
5. WHEN a file is skipped THEN the system SHALL not include it in the organization count

### Requirement 7

**User Story:** As a user, I want to see the results of the organization, so that I know what was accomplished.

#### Acceptance Criteria

1. WHEN the organization completes THEN the system SHALL display a completion summary
2. WHEN displaying the completion summary THEN the system SHALL show the total number of files moved
3. WHEN displaying the completion summary THEN the system SHALL show the breakdown of files moved per category
4. WHEN displaying the completion summary THEN the system SHALL list any errors encountered
5. WHEN displaying the completion summary THEN the system SHALL indicate the operation completion time

### Requirement 8

**User Story:** As a user, I want the tool to handle errors gracefully, so that partial failures don't prevent other files from being organized.

#### Acceptance Criteria

1. IF a file cannot be accessed THEN the system SHALL log the error and continue with remaining files
2. IF a file cannot be moved THEN the system SHALL log the error and continue with remaining files
3. WHEN errors occur THEN the system SHALL collect all error messages for final reporting
4. WHEN the operation completes with errors THEN the system SHALL display all collected errors to the user
5. IF critical errors prevent operation THEN the system SHALL display an error message and exit safely
