"""Main application entry point for Desktop Cleaner."""

import sys
from src.scanner import DesktopScanner
from src.categorizer import FileCategorizer
from src.mover import FileMover
from src.service import DesktopCleanerService
from src.cli import CLI


def main():
    """
    Main application entry point.
    
    Implements the complete workflow:
    1. Scan Desktop directory
    2. Create organization plan
    3. Display plan summary
    4. Request user confirmation
    5. Execute plan if confirmed
    6. Display results
    
    Handles critical errors gracefully and exits safely.
    """
    # Initialize CLI for user interaction
    cli = CLI()
    
    try:
        # Initialize the service (which creates scanner, categorizer, and mover)
        service = DesktopCleanerService()
        
        # Step 1: Scan Desktop directory
        print("\nScanning Desktop directory...")
        scanner = DesktopScanner()
        desktop_path = scanner.get_desktop_path()
        files = scanner.scan_desktop()
        
        print(f"Found {len(files)} file(s) to organize.")
        
        # If no files found, exit gracefully
        if len(files) == 0:
            print("\nNo files to organize. Desktop is already clean!")
            return
        
        # Step 2: Create organization plan
        print("\nCreating organization plan...")
        plan = service.create_organization_plan(files)
        
        # Step 3: Display plan summary
        cli.display_plan_summary(plan)
        
        # Step 4: Request user confirmation
        confirmed = cli.request_confirmation()
        
        if not confirmed:
            print("\nOperation cancelled by user. No changes made.")
            return
        
        # Step 5: Execute plan
        print("\nOrganizing files...")
        result = service.execute_plan(plan, desktop_path)
        
        # Step 6: Display results
        cli.display_results(result)
        
    except FileNotFoundError as e:
        # Critical error: Desktop directory not found
        cli.display_error(f"Critical error: {e}")
        sys.exit(1)
        
    except PermissionError as e:
        # Critical error: Cannot access Desktop directory
        cli.display_error(f"Critical error: {e}")
        sys.exit(1)
        
    except Exception as e:
        # Unexpected critical error
        cli.display_error(f"Critical error: An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
