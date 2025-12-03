"""CLI interface for the Desktop Cleaner application."""

from src.models import OrganizationPlan, ExecutionResult


class CLI:
    """Command-line interface for user interaction and display."""
    
    def display_plan_summary(self, plan: OrganizationPlan) -> None:
        """
        Display a summary of the organization plan.
        
        Args:
            plan: OrganizationPlan to display
        """
        print("\n" + "=" * 60)
        print("DESKTOP ORGANIZATION PLAN")
        print("=" * 60)
        
        print(f"\nTotal files to organize: {plan.total_files}")
        
        print("\nFiles per category:")
        for category, files in sorted(plan.files_by_category.items()):
            print(f"  {category}: {len(files)} file(s)")
        
        print("\nFolders to be created:")
        for folder in sorted(plan.folders_to_create):
            print(f"  - {folder}")
        
        print("\n" + "=" * 60)
    
    def request_confirmation(self) -> bool:
        """
        Request user confirmation to proceed with the plan.
        
        Returns:
            True if user confirms, False if user cancels
        """
        while True:
            response = input("\nProceed with organization? (yes/no): ").strip().lower()
            
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def display_results(self, result: ExecutionResult) -> None:
        """
        Display the results of the organization execution.
        
        Args:
            result: ExecutionResult to display
        """
        print("\n" + "=" * 60)
        print("ORGANIZATION COMPLETE")
        print("=" * 60)
        
        print(f"\nTotal files moved: {result.total_moved}")
        print(f"Operation duration: {result.duration:.2f} seconds")
        
        print("\nFiles moved per category:")
        for category, count in sorted(result.moved_by_category.items()):
            print(f"  {category}: {count} file(s)")
        
        if result.errors:
            print(f"\nErrors encountered ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")
        else:
            print("\nNo errors encountered.")
        
        print("\n" + "=" * 60)
    
    def display_error(self, error: str) -> None:
        """
        Display an error message.
        
        Args:
            error: Error message to display
        """
        print("\n" + "=" * 60)
        print("ERROR")
        print("=" * 60)
        print(f"\n{error}")
        print("\n" + "=" * 60)
