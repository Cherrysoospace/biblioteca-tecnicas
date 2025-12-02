import os
import json
from datetime import datetime
from typing import List, Optional

from models.loan import Loan
from repositories.loan_repository import LoanRepository
from utils.structures.stack import Stack


class LoanService:
    """Service to manage loans (borrow records).

    Responsibilities:
    - BUSINESS LOGIC ONLY: loan creation/update logic, inventory coordination
    - Persistence delegated to LoanRepository (SRP compliance)
    - Create loans and, when a loan is created, decrement the corresponding
      inventory stock by 1. If no stock is available, raises ValueError.
    - Mark loans returned (optionally increment stock back by 1).
    """

    def __init__(self, repository: LoanRepository = None, book_service=None, inventory_service=None):
        self.repository = repository or LoanRepository()
        # Lazy imports to avoid circular dependencies
        self._book_service = book_service
        self._inventory_service = inventory_service

        self.loans: List[Loan] = []
        # Stack to store quick-access loan entries (user, isbn, loan_date)
        self.stack = Stack()

        self._load_loans()
    
    @property
    def book_service(self):
        if self._book_service is None:
            from services.book_service import BookService
            self._book_service = BookService()
        return self._book_service
    
    @property
    def inventory_service(self):
        if self._inventory_service is None:
            from services.inventory_service import InventoryService
            self._inventory_service = InventoryService()
        return self._inventory_service

    def _load_loans(self) -> None:
        """Load loans from repository and build stack."""
        try:
            self.loans = self.repository.load_all()
            # Rebuild stack from loaded loans
            for loan in self.loans:
                try:
                    loan_date = loan.get_loan_date()
                    try:
                        loan_date_serial = loan_date.isoformat()
                    except Exception:
                        loan_date_serial = loan_date
                    self.stack.push({
                        'user_id': loan.get_user_id(),
                        'isbn': loan.get_isbn(),
                        'loan_date': loan_date_serial,
                    })
                except Exception:
                    # if any issue pushing to stack, continue without failing
                    pass
        except Exception:
            # Start with empty list if load fails
            self.loans = []

    def _save_loans(self) -> None:
        """Persist loans using repository."""
        self.repository.save_all(self.loans)

    # -------------------- CRUD / Actions --------------------
    def create_loan(self, loan_id: Optional[str], user_id: str, isbn: str) -> Loan:
        """Create a loan for a book identified by ISBN.

        Behavior:
        - Finds an inventory item matching the ISBN with stock > 0.
        - Decrements stock by 1 via InventoryService.update_stock.
        - Persists the new loan to disk and returns the Loan instance.

        Raises:
        - ValueError if no matching inventory item or no stock available.
        """
        # If caller didn't supply a loan_id, create one automatically following
        # the project's ID style (prefix + zero-padded numeric), consistent
        # with other services (e.g. Users: U001, Books: B001). Use prefix 'L'.
        if not loan_id:
            existing_ids = {l.get_loan_id() for l in self.loans if l.get_loan_id()}
            # find numeric suffixes for IDs like L123
            max_n = 0
            for lid in existing_ids:
                if isinstance(lid, str) and lid.startswith('L'):
                    num_part = lid[1:]
                    # strip any suffix like '-1'
                    if '-' in num_part:
                        num_part = num_part.split('-', 1)[0]
                    if num_part.isdigit():
                        try:
                            v = int(num_part)
                            if v > max_n:
                                max_n = v
                        except Exception:
                            pass

            base_num = max_n + 1
            new_id = f"L{base_num:03d}"
            counter = 1
            while new_id in existing_ids:
                new_id = f"L{base_num:03d}-{counter}"
                counter += 1
            loan_id = new_id
        # Use InventoryService to find an inventory entry with available stock
        invs = self.inventory_service.find_by_isbn(isbn)
        if not invs:
            raise ValueError(f"No inventory entries found for ISBN '{isbn}'")

        chosen_inv = None
        for inv in invs:
            try:
                if inv.get_stock() > 0:
                    chosen_inv = inv
                    break
            except Exception:
                continue

        if chosen_inv is None:
            raise ValueError(f"No stock available for ISBN '{isbn}'")

        # decrement stock in inventory and persist
        book_id = chosen_inv.get_book().get_id()
        new_stock = chosen_inv.get_stock() - 1
        if new_stock < 0:
            raise ValueError("Computed negative stock; aborting")

        self.inventory_service.update_stock(book_id, int(new_stock))
        # mark inventory entry as borrowed
        try:
            self.inventory_service.update_borrow_status(book_id, True)
        except Exception:
            pass

        # Create loan record and persist
        loan = Loan(loan_id, user_id, isbn)
        self.loans.append(loan)
        # Push minimal loan info onto the stack (user, isbn, loan_date)
        try:
            ld = loan.get_loan_date()
            try:
                ld_serial = ld.isoformat()
            except Exception:
                ld_serial = ld
            self.stack.push({'user_id': user_id, 'isbn': isbn, 'loan_date': ld_serial})
        except Exception:
            # non-fatal: proceed even if stack push fails
            pass
        self._save_loans()
        return loan

    def mark_returned(self, loan_id: str) -> None:
        """Mark a loan returned and increment inventory stock by 1.

        If the loan is already marked returned, this is a no-op.
        Raises ValueError if loan_id not found.
        """
        loan = next((l for l in self.loans if l.get_loan_id() == loan_id), None)
        if loan is None:
            raise ValueError(f"No loan found with id '{loan_id}'")
        if loan.is_returned():
            return

        # find an inventory entry by isbn and increment stock
        try:
            invs = self.inventory_service.find_by_isbn(loan.get_isbn())
            if invs:
                # Prefer to find the inventory entry that is currently marked
                # as borrowed for this ISBN and mark it returned. If none are
                # marked borrowed, fall back to the first entry.
                inv_borrowed = next((i for i in invs if i.get_isBorrowed()), None)
                target = inv_borrowed or invs[0]
                try:
                    # Use update_borrow_status to clear the borrowed flag and
                    # set the per-item stock back to 1.
                    self.inventory_service.update_borrow_status(target.get_book().get_id(), False)
                except Exception:
                    # ignore failures to update inventory, but continue marking returned
                    pass
        except Exception:
            pass

        loan.mark_returned()
        self._save_loans()

    def get_all_loans(self) -> List[Loan]:
        return list(self.loans)

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        return next((l for l in self.loans if l.get_loan_id() == loan_id), None)

    def delete_loan(self, loan_id: str) -> None:
        """Delete a loan. If the loan is active (not returned) attempt to
        mark it returned first (to restore inventory) and then remove it.

        Raises ValueError if not found.
        """
        loan = next((l for l in self.loans if l.get_loan_id() == loan_id), None)
        if loan is None:
            raise ValueError(f"No loan found with id '{loan_id}'")

        # If loan not returned, try to mark returned to restore inventory
        if not loan.is_returned():
            try:
                self.mark_returned(loan_id)
            except Exception:
                # ignore failures restoring inventory but proceed to delete
                pass

        # remove from list and persist
        self.loans = [l for l in self.loans if l.get_loan_id() != loan_id]
        self._save_loans()

    def update_loan(self, loan_id: str, user_id: Optional[str] = None, isbn: Optional[str] = None, returned: Optional[bool] = None, loan_date=None) -> Loan:
        """Update loan fields. Supported updates: user_id, isbn (best-effort), returned flag.

        Inventory adjustments are attempted when changing returned status or ISBN.
        Returns the updated Loan instance.
        """
        loan = next((l for l in self.loans if l.get_loan_id() == loan_id), None)
        if loan is None:
            raise ValueError(f"No loan found with id '{loan_id}'")

        old_isbn = loan.get_isbn()
        # Update user id
        if user_id is not None:
            loan.set_user_id(user_id)

    # Update returned status
        if returned is not None:
            # if marking returned now
            if returned and not loan.is_returned():
                # reuse existing service logic
                self.mark_returned(loan_id)
                # reload reference to loan (mark_returned mutates it)
                loan = next((l for l in self.loans if l.get_loan_id() == loan_id), loan)
            # if un-marking returned -> try to decrement inventory for this isbn
            elif not returned and loan.is_returned():
                invs = self.inventory_service.find_by_isbn(loan.get_isbn())
                if not invs:
                    raise ValueError(f"No inventory entries found for ISBN '{loan.get_isbn()}' to re-loan")
                chosen = next((i for i in invs if i.get_stock() > 0), None)
                if chosen is None:
                    raise ValueError(f"No stock available to re-loan ISBN '{loan.get_isbn()}'")
                # decrement stock
                book_id = chosen.get_book().get_id()
                new_stock = chosen.get_stock() - 1
                if new_stock < 0:
                    raise ValueError("Computed negative stock; aborting")
                self.inventory_service.update_stock(book_id, int(new_stock))
                try:
                    self.inventory_service.update_borrow_status(book_id, True)
                except Exception:
                    pass
                loan.set_returned(False)

        # Update ISBN: if changed and loan not returned, adjust inventories
        if isbn is not None and isbn != old_isbn:
            # find inventory for new isbn
            new_invs = self.inventory_service.find_by_isbn(isbn)
            if not new_invs:
                raise ValueError(f"No inventory entries found for new ISBN '{isbn}'")
            chosen_new = next((i for i in new_invs if i.get_stock() > 0), None)
            if chosen_new is None:
                raise ValueError(f"No stock available for new ISBN '{isbn}'")

            # If loan currently not returned, restore old inventory and decrement new
            if not loan.is_returned():
                old_invs = self.inventory_service.find_by_isbn(old_isbn)
                if old_invs:
                    # try to increment stock for an old inventory item
                    try:
                        old_book_id = old_invs[0].get_book().get_id()
                        self.inventory_service.update_borrow_status(old_book_id, False)
                    except Exception:
                        pass

                # decrement new
                new_book_id = chosen_new.get_book().get_id()
                new_stock = chosen_new.get_stock() - 1
                if new_stock < 0:
                    raise ValueError("Computed negative stock for new ISBN; aborting")
                self.inventory_service.update_stock(new_book_id, int(new_stock))
                try:
                    self.inventory_service.update_borrow_status(new_book_id, True)
                except Exception:
                    pass

            # finally set new isbn on loan
            loan.set_isbn(isbn)

        # Update loan_date if provided (accept ISO string or date/datetime)
        if loan_date is not None:
            # allow string in ISO format 'YYYY-MM-DD' or a datetime/date-like
            if isinstance(loan_date, str):
                try:
                    # try parsing ISO date or datetime
                    parsed = datetime.fromisoformat(loan_date)
                    try:
                        loan.set_loan_date(parsed.date())
                    except Exception:
                        loan.set_loan_date(parsed)
                except Exception:
                    # try YYYY-MM-DD fallback
                    try:
                        parsed = datetime.strptime(loan_date, "%Y-%m-%d")
                        loan.set_loan_date(parsed.date())
                    except Exception:
                        raise ValueError("Invalid loan_date format. Use 'YYYY-MM-DD' or ISO datetime string")
            else:
                # assume date/datetime-like
                try:
                    loan.set_loan_date(loan_date)
                except Exception as e:
                    raise ValueError(f"Invalid loan_date value: {e}")

        # persist changes
        self._save_loans()
        return loan


__all__ = ["LoanService"]
