import os
import json
from typing import List, Optional, Dict, Any

from models.Books import Book
from repositories.book_repository import BookRepository
from utils.validators import BookValidator, ValidationError
from utils.logger import LibraryLogger
from utils.config import FilePaths

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


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
        - ValidationError: if book data is invalid (ISBN, title, weight, price)
        - ValueError: if a book with the same `id` already exists.
        - Exception: for IO errors when saving.
        """
        # Validar datos del libro ANTES de agregar
        try:
            BookValidator.validate_book_data(
                isbn=book.get_ISBNCode(),
                title=book.get_title(),
                author=book.get_author(),
                weight=book.get_weight(),
                price=book.get_price(),
                book_id=book.get_id()
            )
        except ValidationError as e:
            logger.error(f"Validación fallida al agregar libro: {e}")
            raise  # Re-lanzar la excepción para que el controlador la maneje
        
        if any(b.get_id() == book.get_id() for b in self.books):
            raise ValueError(f"A book with id '{book.get_id()}' already exists")

        self.books.append(book)
        self._save_books()
        logger.info(f"Libro agregado: id={book.get_id()}, ISBN={book.get_ISBNCode()}, título={book.get_title()}")

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

        # VALIDAR campos ANTES de actualizar
        try:
            if 'ISBNCode' in new_data:
                new_data['ISBNCode'] = BookValidator.validate_isbn(new_data['ISBNCode'])
            if 'title' in new_data:
                new_data['title'] = BookValidator.validate_title(new_data['title'])
            if 'author' in new_data:
                new_data['author'] = BookValidator.validate_author(new_data['author'])
            if 'weight' in new_data:
                new_data['weight'] = BookValidator.validate_weight(new_data['weight'])
            if 'price' in new_data:
                new_data['price'] = BookValidator.validate_price(new_data['price'])
            if 'id' in new_data:
                new_data['id'] = BookValidator.validate_id(new_data['id'])
        except ValidationError as e:
            logger.error(f"Validación fallida al actualizar libro {id}: {e}")
            raise

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
            # Los valores ya fueron validados y convertidos arriba
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
        
        # Remove the book from all shelves
        try:
            from services.shelf_service import ShelfService
            shelf_svc = ShelfService()
            try:
                shelf_svc.remove_book_from_all_shelves(id)
                logger.info(f"Libro {id} eliminado de todas las estanterías")
            except Exception as e:
                logger.warning(f"Error al eliminar libro {id} de estanterías: {e}")
        except Exception:
            # Don't block book deletion if shelf sync fails
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

    def calculate_total_value_by_author(self, author: str) -> float:
        """Calculate total monetary value of all books by a given author using stack recursion.
        
        This method uses stack-style recursion to compute the sum of prices for all books
        by the specified author. The recursion mimics the classical factorial example where
        each call processes one element and pushes the rest onto the call stack.
        
        Parameters:
        - author: string with the author name to match (case-sensitive)
        
        Returns:
        - total value (float or int) of all books by that author
        
        Example:
        >>> service = BookService()
        >>> total = service.calculate_total_value_by_author("Homer")
        >>> print(total)
        30000
        
        Complexity: O(n) time and O(n) call-stack depth where n is number of books.
        """
        from utils.recursion.stack_recursion import total_value_by_author
        
        # Convert Book objects to dict format expected by the recursion function
        books_data = []
        for book in self.books:
            books_data.append({
                'author': book.get_author(),
                'price': book.get_price()
            })
        
        return total_value_by_author(books_data, author)

    def get_all_authors(self) -> List[str]:
        """Get a sorted list of unique authors in the catalog.
        
        Returns:
        - List[str] of unique author names, sorted alphabetically
        """
        authors = set()
        for book in self.books:
            author = book.get_author()
            if author:  # Skip empty authors
                authors.add(author)
        return sorted(authors)

    def calculate_average_weight_by_author(self, author: str, debug: bool = False) -> float:
        """Calculate average weight of all books by a given author using tail recursion.
        
        This method uses tail-style (queue) recursion with accumulators to compute
        the average weight. The recursion demonstrates the accumulator pattern where
        state is passed through parameters rather than accumulated on the call stack.
        
        Parameters:
        - author: string with the author name to match (case-sensitive)
        - debug: if True, prints recursion flow to console
        
        Returns:
        - average weight (float) in kg of all books by that author
        - returns 0.0 if no books found for the author
        
        Example:
        >>> service = BookService()
        >>> avg = service.calculate_average_weight_by_author("Homer")
        >>> print(avg)
        1.1
        
        Complexity: O(n) time and O(n) call-stack depth where n is number of books.
        """
        from utils.recursion.queue_recursion import avg_weight_by_author
        
        # Convert Book objects to dict format expected by the recursion function
        books_data = []
        for book in self.books:
            books_data.append({
                'id': book.get_id(),
                'ISBNCode': book.get_ISBNCode(),
                'title': book.get_title(),
                'author': book.get_author(),
                'weight': book.get_weight(),
                'price': book.get_price()
            })
        
        return avg_weight_by_author(books_data, author, debug=debug)


# Example:
# service = BookService()
# service.add_book(Book('id1','978-1','Title','Author',0.5,100,False))
# b = service.find_by_id('id1')
# print(b)
