"""Test script to verify Backtracking UI integration.

This script tests that the BacktrackingReport window can be opened
and displays data correctly.
"""

import customtkinter as ctk
from ui.book.backtracking_report import BacktrackingReport

def test_backtracking_ui():
    """Test the BacktrackingReport window."""
    print("=" * 70)
    print("TESTING BACKTRACKING UI COMPONENT")
    print("=" * 70)
    print()
    
    # Create main window (required for Toplevel)
    root = ctk.CTk()
    root.withdraw()  # Hide main window
    
    # Open BacktrackingReport
    print("Opening BacktrackingReport window...")
    try:
        report_window = BacktrackingReport(root)
        print("✅ Window created successfully!")
        print()
        print("Please check the window and close it to complete the test.")
        print()
        
        # Run the event loop
        root.mainloop()
        
        print()
        print("=" * 70)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        print()
        print("=" * 70)
        print("❌ TEST FAILED")
        print("=" * 70)
        raise

if __name__ == "__main__":
    test_backtracking_ui()
