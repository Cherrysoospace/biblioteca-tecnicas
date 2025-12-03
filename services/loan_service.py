import os
import json
from datetime import datetime
from typing import List, Optional

from models.loan import Loan
from repositories.loan_repository import LoanRepository
from utils.structures.stack import Stack
from utils.validators import LoanValidator, ValidationError
from utils.logger import LibraryLogger
from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


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
        # Keep property for backward compatibility but avoid using it in loan flows
        if self._inventory_service is None:
            try:
                from services.inventory_service import InventoryService
                self._inventory_service = InventoryService()
            except Exception:
                self._inventory_service = None
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
        - Validates user_id and isbn BEFORE creating loan
        - Finds an inventory item matching the ISBN with stock > 0.
        - Decrements stock by 1 via InventoryService.update_stock.
        - Persists the new loan to disk and returns the Loan instance.

        Raises:
        - ValidationError: if user_id or isbn are invalid
        - ValueError if no matching inventory item or no stock available.
        """
        # VALIDAR datos ANTES de crear préstamo
        # Nota: book_id se validará después de encontrar el libro por ISBN
        try:
            validated = LoanValidator.validate_loan_data(
                user_id=user_id,
                book_id="temp",  # Se validará después
                isbn=isbn
            )
            user_id = validated['user_id']
            isbn = validated['isbn']
        except ValidationError as e:
            logger.error(f"Validación fallida al crear préstamo: {e}")
            raise
        
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
        # Use BookService to find a physical book copy with this ISBN that is not borrowed
        books = self.book_service.find_by_isbn(isbn)
        if not books:
            raise ValueError(f"No books found for ISBN '{isbn}'")

        chosen_book = None
        for b in books:
            try:
                if not b.get_isBorrowed():
                    chosen_book = b
                    break
            except Exception:
                continue

        if chosen_book is None:
            raise ValueError(f"No available copies for ISBN '{isbn}'")

        book_id = chosen_book.get_id()

        # VALIDAR book_id ahora que lo conocemos
        try:
            from utils.validators import BookValidator
            book_id = BookValidator.validate_id(book_id)
        except ValidationError as e:
            logger.error(f"book_id inválido al crear préstamo: {e}")
            raise

        # Mark the chosen book as borrowed via BookService (this also persists books.json)
        try:
            # Use update_book to change isBorrowed -> True
            self.book_service.update_book(book_id, {'isBorrowed': True})
        except Exception as e:
            logger.error(f"Failed to mark book {book_id} as borrowed: {e}")
            raise

        # Create loan record and persist
        loan = Loan(loan_id, user_id, isbn)
        self.loans.append(loan)
        logger.info(f"Préstamo creado: id={loan_id}, user={user_id}, isbn={isbn}, book={book_id}")
        
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
        
        CRITICAL FEATURE: Uses búsqueda binaria to check if returned book
        has pending reservations in the queue. If found, auto-assigns to
        the next pending reservation by priority.
        """
        loan = next((l for l in self.loans if l.get_loan_id() == loan_id), None)
        if loan is None:
            raise ValueError(f"No loan found with id '{loan_id}'")
        if loan.is_returned():
            return

        # find a book by isbn that is currently marked borrowed and clear it
        try:
            books = self.book_service.find_by_isbn(loan.get_isbn())
            if books:
                book_borrowed = next((b for b in books if b.get_isBorrowed()), None)
                if book_borrowed:
                    try:
                        self.book_service.update_book(book_borrowed.get_id(), {'isBorrowed': False})
                    except Exception:
                        # ignore failures to update book but continue marking returned
                        pass
        except Exception:
            pass

        loan.mark_returned()
        
        # CRITICAL: Check reservation queue using búsqueda binaria (required by project spec)
        try:
            # Get sorted inventory to use binary search
            if self.inventory_service:
                inventories = self.inventory_service.inventory_general
                # Sort by ISBN for binary search
                inventario_ordenado = sorted(inventories, key=lambda inv: inv.get_isbn())
                
                # Use búsqueda binaria to verify book exists in inventory
                isbn_returned = loan.get_isbn()
                index = busqueda_binaria(inventario_ordenado, isbn_returned)
                
                # If book found in inventory, check for pending reservations
                if index != -1:
                    # Lazy import to avoid circular dependency
                    from services.reservation_service import ReservationService
                    reservation_service = ReservationService()
                    
                    # Check if there are pending reservations for this ISBN
                    pending_reservations = reservation_service.find_by_isbn(isbn_returned, only_pending=True)
                    
                    if pending_reservations:
                        # Auto-assign to the next in queue (earliest pending)
                        assigned_reservation = reservation_service.assign_next_for_isbn(isbn_returned)
                        if assigned_reservation:
                            logger.info(f"Book '{isbn_returned}' auto-assigned to reservation "
                                      f"'{assigned_reservation.get_reservation_id()}' for user "
                                      f"'{assigned_reservation.get_user_id()}'")
                            
                            # CRITICAL: Create automatic loan for the user with assigned reservation
                            # This ensures the book goes directly from returned user to reserved user
                            # without the reserved user having to manually create a loan
                            try:
                                new_loan = self.create_loan(
                                    loan_id=None,
                                    user_id=assigned_reservation.get_user_id(),
                                    isbn=isbn_returned
                                )
                                logger.info(f"Auto-created loan '{new_loan.get_loan_id()}' for user "
                                          f"'{assigned_reservation.get_user_id()}' from reservation "
                                          f"'{assigned_reservation.get_reservation_id()}'")
                            except Exception as loan_err:
                                logger.error(f"Failed to create automatic loan for reservation: {loan_err}")
                                # Note: Reservation is still assigned even if loan creation fails
        except Exception as e:
            # Log error but don't fail the return operation
            logger.error(f"Error checking reservations for returned book: {e}")
        
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
                # re-loan: find a book copy not borrowed and mark it borrowed
                books = self.book_service.find_by_isbn(loan.get_isbn())
                if not books:
                    raise ValueError(f"No books found for ISBN '{loan.get_isbn()}' to re-loan")
                chosen = next((b for b in books if not b.get_isBorrowed()), None)
                if chosen is None:
                    raise ValueError(f"No available copies to re-loan ISBN '{loan.get_isbn()}'")
                book_id = chosen.get_id()
                try:
                    self.book_service.update_book(book_id, {'isBorrowed': True})
                except Exception:
                    pass
                loan.set_returned(False)

        # Update ISBN: if changed and loan not returned, adjust inventories
        if isbn is not None and isbn != old_isbn:
            # find inventory for new isbn
            # find available book copy for new isbn
            new_books = self.book_service.find_by_isbn(isbn)
            if not new_books:
                raise ValueError(f"No books found for new ISBN '{isbn}'")
            chosen_new = next((b for b in new_books if not b.get_isBorrowed()), None)
            if chosen_new is None:
                raise ValueError(f"No available copies for new ISBN '{isbn}'")

            # If loan currently not returned, restore old book (mark its copy returned)
            if not loan.is_returned():
                try:
                    old_books = self.book_service.find_by_isbn(old_isbn)
                    if old_books:
                        # try to mark the first borrowed copy of old_isbn as returned
                        old_borrowed = next((b for b in old_books if b.get_isBorrowed()), None)
                        if old_borrowed:
                            try:
                                self.book_service.update_book(old_borrowed.get_id(), {'isBorrowed': False})
                            except Exception:
                                pass
                except Exception:
                    pass

                # mark new chosen book as borrowed
                try:
                    self.book_service.update_book(chosen_new.get_id(), {'isBorrowed': True})
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
