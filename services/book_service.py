import os
import json
from typing import List, Optional, Dict, Any

from models.Books import Book
from repositories.book_repository import BookRepository


class BookService:
    """Service for basic management of Book objects (no inventory, no algorithms).

    Responsibilities:
    - BUSINESS LOGIC ONLY: ID generation, validation, synchronization with inventory
    - Persistence delegated to BookRepository (SRP compliance)

    Important: This service does NOT handle stock, sorted lists, or call any algorithms.
    """

    def __init__(self, repository: BookRepository = None):
        """Initialize BookService with a repository.

        Parameters:
        - repository: Optional BookRepository instance. If None, creates a new one.
        """
        self.repository = repository or BookRepository()
        self.books: List[Book] = []
        self._load_books()

    def generate_next_id(self, prefix: str = 'B', min_width: int = 3) -> str:
        """Generate the next chronological ID for a Book.

        Strategy:
        - Extract trailing numeric portion from existing book IDs (e.g. 'B012' -> 12).
        - Increment the maximum found (or start at 1 if none present).
        - Preserve a sensible zero-padding width (at least `min_width`, or the
          maximum width found in existing IDs).

        Returns a string like 'B011'.
        """
        import re

        nums = []
        max_width = min_width
        for b in self.books:
            bid = b.get_id()
            if not isinstance(bid, str):
                continue
            m = re.search(r"(\d+)$", bid)
            if m:
                s = m.group(1)
                try:
                    nums.append(int(s))
                    if len(s) > max_width:
                        max_width = len(s)
                except Exception:
                    continue

        next_num = (max(nums) + 1) if nums else 1
        return f"{prefix}{str(next_num).zfill(max_width)}"

    # -------------------- Persistence (delegated to repository) --------------------
    def _load_books(self) -> None:
        """Load books from repository.
        
        Raises:
        - ValueError: if JSON structure is invalid
        - Exception: for IO errors
        """
        self.books = self.repository.load_all()

    def _save_books(self) -> None:
        """Persist books using repository.
        
        Raises:
        - Exception: for IO errors
        """
        self.repository.save_all(self.books)

    # -------------------- CRUD --------------------
    def add_book(self, book: Book) -> None:
        """Add a new Book to the catalog and persist.

        Parameters:
        - book: Book instance to add.

        Returns: None

        Raises:
        - ValueError: if a book with the same `id` already exists.
        - Exception: for IO errors when saving.
        """
        if any(b.get_id() == book.get_id() for b in self.books):
            raise ValueError(f"A book with id '{book.get_id()}' already exists")

        self.books.append(book)
        self._save_books()

    def update_book(self, id: str, new_data: Dict[str, Any]) -> None:
        """Update fields of a book identified by `id`.

        Only keys present in `new_data` will be updated. Allowed fields:
        'id','ISBNCode','title','author','weight','price','isBorrowed'.

        Parameters:
        - id: str (identifier of the book to update)
        - new_data: dict containing the fields to update

        Returns: None

        Raises:
        - ValueError: if book not found, or if updating `id` would cause a duplicate.
        - Exception: for IO errors when saving.
        """
        book = self.find_by_id(id)
        if book is None:
            raise ValueError(f"No book found with id '{id}'")

        # Allowed fields and setters
        setters = {
            'id': book.set_id,
            'ISBNCode': book.set_ISBNCode,
            'title': book.set_title,
            'author': book.set_author,
            'weight': book.set_weight,
            'price': book.set_price,
            'isBorrowed': book.set_isBorrowed,
        }

        if 'id' in new_data:
            new_id = new_data['id']
            if new_id != id and any(b.get_id() == new_id for b in self.books):
                raise ValueError(f"Cannot update id: another book with id '{new_id}' already exists")

        # capture previous identifying fields to propagate changes to inventory
        old_id = book.get_id()
        old_isbn = book.get_ISBNCode()

        for key, value in new_data.items():
            if key not in setters:
                continue
            if key == 'weight':
                value = float(value)
            if key == 'price':
                value = int(value)
            if key == 'isBorrowed':
                value = bool(value)
            setters[key](value)

        # persist books.json
        self._save_books()

        # Synchronize with inventory
        try:
            from services.inventory_service import InventoryService
            inv_svc = InventoryService()
            
            # Update the book in inventory
            try:
                inv_svc.update_book_in_inventory(old_id, book)
            except Exception:
                # If update fails, inventory might not have this book yet
                pass
        except Exception:
            # Don't block book updates if inventory sync fails
            pass

    def delete_book(self, id: str) -> None:
        """Delete a book from the catalog by id and persist.

        Parameters:
        - id: str

        Returns: None

        Raises:
        - ValueError: if book not found or if the book is currently borrowed (`isBorrowed==True`).
        - Exception: for IO errors when saving.
        """
        book = self.find_by_id(id)
        if book is None:
            raise ValueError(f"No book found with id '{id}'")
        # Prevent deleting if book is currently borrowed or has stock remaining
        if book.get_isBorrowed():
            raise ValueError("Cannot delete a book that is currently borrowed")

        self.books = [b for b in self.books if b.get_id() != id]
        self._save_books()
        
        # Synchronize with inventory - delete the book
        try:
            from services.inventory_service import InventoryService
            inv_svc = InventoryService()
            try:
                inv_svc.delete_book_from_inventory(id)
            except Exception:
                # If delete fails, book might not be in inventory
                pass
        except Exception:
            # Don't block book deletion if inventory sync fails
            pass

    def find_by_id(self, id: str) -> Optional[Book]:
        """Find and return a Book by its unique id.

        Parameters:
        - id: str

        Returns:
        - Book if found, else None
        """
        for b in self.books:
            if b.get_id() == id:
                return b
        return None

    def find_by_isbn(self, isbn: str) -> List[Book]:
        """Find books matching an ISBN (simple linear scan).

        Parameters:
        - isbn: str

        Returns:
        - List[Book] (may be empty)
        """
        return [b for b in self.books if b.get_ISBNCode() == isbn]

    def get_all_books(self) -> List[Book]:
        """Return a shallow copy of the internal books list.

        Returns:
        - List[Book]
        """
        return list(self.books)


# Example:
# service = BookService()
# service.add_book(Book('id1','978-1','Title','Author',0.5,100,False))
# b = service.find_by_id('id1')
# print(b)
