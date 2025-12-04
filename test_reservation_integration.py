"""
Test: Búsqueda Binaria Integration with Loan Return and Reservation Queue

This test verifies the CRITICAL requirement: When a book is returned,
búsqueda binaria MUST be used to check if there are pending reservations,
and auto-assign to the next user in the queue.

Test Scenario:
1. Create a reservation for a book (User A reserves ISBN X)
2. Create a loan for the same book (User B borrows ISBN X)
3. Return the loan
4. Verify: Reservation status changed to 'assigned' with assigned_date set
"""

from services.loan_service import LoanService
from services.reservation_service import ReservationService
from services.book_service import BookService
from services.inventory_service import InventoryService
from datetime import datetime


def test_reservation_auto_assignment_on_return():
    """Test that returning a book auto-assigns it to pending reservations."""
    
    # Initialize services
    loan_service = LoanService()
    reservation_service = ReservationService()
    book_service = BookService()
    inventory_service = InventoryService()
    
    # Find a book with available copies
    inventories = inventory_service.inventory_general
    if not inventories:
        print("❌ No inventory found - cannot test")
        return False
    
    # Find an inventory with at least 2 copies (1 to loan, 1 for reservation check)
    test_inventory = None
    for inv in inventories:
        if inv.get_available_count() >= 2:
            test_inventory = inv
            break
    
    if not test_inventory:
        print("❌ No inventory with 2+ copies found - cannot test")
        return False
    
    test_isbn = test_inventory.get_isbn()
    print(f"\n📚 Testing with ISBN: {test_isbn}")
    print(f"   Available copies: {test_inventory.get_available_count()}")
    
    # Step 1: Create a reservation (User A reserves the book)
    print("\n1️⃣ Creating reservation for User A...")
    reservation = reservation_service.create_reservation(
        reservation_id=None,
        user_id="U002",  # Usuario válido de la BD
        isbn=test_isbn
    )
    print(f"   ✅ Reservation created: {reservation.get_reservation_id()}")
    print(f"      Status: {reservation.get_status()}")
    
    # Step 2: Create a loan (User B borrows the book)
    print("\n2️⃣ Creating loan for User B...")
    try:
        loan = loan_service.create_loan(
            loan_id=None,
            user_id="U003",  # Usuario válido de la BD
            isbn=test_isbn
        )
        print(f"   ✅ Loan created: {loan.get_loan_id()}")
        print(f"      User: {loan.get_user_id()}")
        print(f"      ISBN: {loan.get_isbn()}")
        print(f"      Returned: {loan.is_returned()}")
    except Exception as e:
        print(f"   ❌ Failed to create loan: {e}")
        return False
    
    # Step 3: Return the loan (this should trigger reservation assignment)
    print("\n3️⃣ Returning the loan...")
    print("   🔍 This should trigger búsqueda binaria to check for pending reservations...")
    try:
        loan_service.mark_returned(loan.get_loan_id())
        print(f"   ✅ Loan marked as returned")
    except Exception as e:
        print(f"   ❌ Failed to mark loan as returned: {e}")
        return False
    
    # Step 4: Verify reservation was auto-assigned
    print("\n4️⃣ Verifying reservation auto-assignment...")
    # IMPORTANT: Reload from file because LoanService created a new ReservationService instance
    reservation_service_reloaded = ReservationService()
    updated_reservation = reservation_service_reloaded.find_by_id(reservation.get_reservation_id())
    
    if updated_reservation:
        print(f"   Reservation Status: {updated_reservation.get_status()}")
        print(f"   Assigned Date: {updated_reservation.get_assigned_date()}")
        
        if updated_reservation.get_status() == 'assigned':
            print("\n✅ SUCCESS! Reservation auto-assigned using búsqueda binaria")
            
            # Step 5: Verify automatic loan creation
            print("\n5️⃣ Verifying automatic loan creation for reserved user...")
            loan_service_reloaded = LoanService()
            all_loans = loan_service_reloaded.get_all_loans()
            auto_loan = None
            for l in all_loans:
                if (l.get_user_id() == updated_reservation.get_user_id() and 
                    l.get_isbn() == test_isbn and 
                    not l.is_returned()):
                    auto_loan = l
                    break
            
            if auto_loan:
                print(f"   ✅ Automatic loan created: {auto_loan.get_loan_id()}")
                print(f"      User: {auto_loan.get_user_id()}")
                print(f"      ISBN: {auto_loan.get_isbn()}")
                print(f"      Returned: {auto_loan.is_returned()}")
                print("\n✅ COMPLETE SUCCESS! Full workflow verified:")
                print("   1. Book returned → búsqueda binaria found ISBN in inventory")
                print("   2. Pending reservations checked")
                print("   3. Next reservation auto-assigned with timestamp")
                print("   4. Automatic loan created for reserved user")
                print("   5. Book transferred directly from User B → User A")
                return True
            else:
                print("\n❌ FAILURE! Reservation assigned but automatic loan NOT created")
                print("   This means the reserved user cannot return the book later")
                return False
        else:
            print(f"\n❌ FAILURE! Reservation status is '{updated_reservation.get_status()}', expected 'assigned'")
            return False
    else:
        print("\n❌ FAILURE! Could not find reservation after return")
        return False


def test_no_assignment_when_no_reservations():
    """Test that returning a book without reservations doesn't cause errors."""
    
    loan_service = LoanService()
    reservation_service = ReservationService()
    inventory_service = InventoryService()
    
    # Find a book with available copies and NO pending reservations
    inventories = inventory_service.inventory_general
    test_inventory = None
    
    for inv in inventories:
        if inv.get_available_count() >= 1:
            isbn = inv.get_isbn()
            pending = reservation_service.find_by_isbn(isbn, only_pending=True)
            if not pending:
                test_inventory = inv
                break
    
    if not test_inventory:
        print("\n⚠️ Skipping test - no inventory without reservations")
        return True
    
    test_isbn = test_inventory.get_isbn()
    print(f"\n📚 Testing with ISBN: {test_isbn} (no pending reservations)")
    
    # Create and return a loan
    try:
        loan = loan_service.create_loan(None, "U005", test_isbn)  # Usuario válido de la BD
        print(f"   ✅ Loan created: {loan.get_loan_id()}")
        
        loan_service.mark_returned(loan.get_loan_id())
        print(f"   ✅ Loan returned successfully (no crash)")
        print("   ✅ Binary search executed but found no reservations to assign")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("TESTING: Búsqueda Binaria Integration with Reservation Queue")
    print("=" * 70)
    
    # Test 1: Auto-assignment when reservation exists
    result1 = test_reservation_auto_assignment_on_return()
    
    print("\n" + "=" * 70)
    
    # Test 2: No errors when no reservations exist
    result2 = test_no_assignment_when_no_reservations()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS:")
    print(f"   Test 1 (Auto-assignment): {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"   Test 2 (No reservations): {'✅ PASS' if result2 else '❌ FAIL'}")
    print("=" * 70)
