import os
import json
from typing import List, Optional

from models.loan import Loan
from services.book_service import BookService
from utils.structures.stack import Stack


class LoanService:
    """Service to manage loans (borrow records).

    Responsibilities:
    - Persist loans to `data/loan.json` as a list of dicts (using Loan.to_dict())
    - Create loans and, when a loan is created, decrement the corresponding
      inventory stock by 1. If no stock is available, raises ValueError.
    - Mark loans returned (optionally increment stock back by 1).
    """

    def __init__(self, json_path: Optional[str] = None, book_service: Optional[BookService] = None):
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if json_path:
            self.json_path = os.path.abspath(json_path)
        else:
            self.json_path = os.path.join(base, 'data', 'loan.json')
        # BookService: if not provided, create a default one so we can
        # update stock in books.json when loans are created.
        self.book_service = book_service or BookService()

        self.loans: List[Loan] = []
        # Stack to store quick-access loan entries (user, isbn, loan_date)
        self.stack = Stack()

        self._ensure_file()
        self._load_from_file()

    def _ensure_file(self) -> None:
        directory = os.path.dirname(self.json_path)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise Exception(f"Unable to create loan JSON file: {e}")

    def _load_from_file(self) -> None:
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # if file is empty or malformed, start with empty list
            data = []
        except Exception as e:
            raise Exception(f"Unable to read loan JSON file: {e}")

        loaded: List[Loan] = []
        if isinstance(data, list):
            for item in data:
                try:
                    loan = Loan(
                        item.get('loan_id'),
                        item.get('user_id'),
                        item.get('isbn'),
                        item.get('loan_date'),
                        item.get('returned', False),
                    )
                    loaded.append(loan)
                    # Also push the minimal loan record onto the stack in the
                    # requested order: user, ISBN, loan_date (ISO string)
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
                    # skip invalid entries
                    continue

        self.loans = loaded

    def _save_to_file(self) -> None:
        data = [l.to_dict() for l in self.loans]
        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write loan JSON file: {e}")

    # -------------------- CRUD / Actions --------------------
    def create_loan(self, loan_id: str, user_id: str, isbn: str) -> Loan:
        """Create a loan for a book identified by ISBN.

        Behavior:
        - Finds an inventory item matching the ISBN with stock > 0.
        - Decrements stock by 1 via InventoryService.update_stock.
        - Persists the new loan to disk and returns the Loan instance.

        Raises:
        - ValueError if no matching inventory item or no stock available.
        """
        # Find matching Book objects by ISBN
        books = self.book_service.find_by_isbn(isbn)
        if not books:
            raise ValueError(f"No book found for ISBN '{isbn}'")

        # pick first book that has stock > 0
        chosen_book = None
        for b in books:
            try:
                if b.get_stock() > 0:
                    chosen_book = b
                    break
            except Exception:
                continue

        if chosen_book is None:
            raise ValueError(f"No stock available for ISBN '{isbn}'")

        # decrement stock in the BookService (persisted to books.json)
        book_id = chosen_book.get_id()
        new_stock = chosen_book.get_stock() - 1
        if new_stock < 0:
            raise ValueError("Computed negative stock; aborting")

        # Update book stock via BookService
        self.book_service.update_book(book_id, {'stock': int(new_stock)})

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
        self._save_to_file()
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

        # find book by isbn and increment stock
        books = self.book_service.find_by_isbn(loan.get_isbn())
        if books:
            b = books[0]
            try:
                self.book_service.update_book(b.get_id(), {'stock': int(b.get_stock() + 1)})
            except Exception:
                # ignore failures to increment stock, but continue marking returned
                pass

        loan.mark_returned()
        self._save_to_file()

    def get_all_loans(self) -> List[Loan]:
        return list(self.loans)

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        return next((l for l in self.loans if l.get_loan_id() == loan_id), None)


__all__ = ["LoanService"]
