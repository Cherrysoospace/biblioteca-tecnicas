import os
import json
from typing import List, Optional, Dict, Any

from models.Books import Book

# Try to import required algorithm functions from expected modules.
try:
    # Preferred (Spanish) path if user uses `utils/algoritmos`
    from utils.algoritmos.insertion_sort import insertion_sort_books
    from utils.algoritmos.busqueda_lineal import buscar_lineal
    from utils.algoritmos.busqueda_binaria import buscar_binario
    from utils.algoritmos.merge_sort import merge_sort_books_by_price
except Exception:
    try:
        # Fallback to English-named package `utils.algorithms` if present.
        from utils.algorithms.insertion_sort import insertion_sort_books  # type: ignore
        from utils.algorithms.busqueda_lineal import buscar_lineal  # type: ignore
        from utils.algorithms.busqueda_binaria import buscar_binario  # type: ignore
        from utils.algorithms.merge_sort import merge_sort_books_by_price  # type: ignore
    except Exception:
        # If imports fail we will raise a clear ImportError when the service attempts to call them.
        insertion_sort_books = None  # type: ignore
        buscar_lineal = None  # type: ignore
        buscar_binario = None  # type: ignore
        merge_sort_books_by_price = None  # type: ignore


class BookService:
    """Service layer for managing books.

    Responsibilities:
    - Manage persistence to `./data/books.json` (create if missing, validate, serialize/deserialize).
    - Maintain `inventory_general` (unsorted insertion order) and `inventory_sorted` (sorted by ISBN string).
    - Implement CRUD operations calling external algorithm implementations (service does NOT implement algorithms).

    Note: This service expects external algorithm implementations to be available. If they are not,
    methods that rely on them will raise ImportError with guidance.
    """

    def __init__(self, json_path: Optional[str] = None):
        """Initialize BookService and load data from JSON.

        Parameters:
        - json_path: optional path to `books.json`. If None, defaults to `./data/books.json` relative to repo root.

        Raises:
        - ValueError: if JSON exists but is malformed / not a list of book dicts.
        - Exception: for unexpected IO errors.
        """
        # Determine JSON path
        if json_path:
            self.json_path = os.path.abspath(json_path)
        else:
            # data directory is sibling of `services` directory
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.json_path = os.path.join(base, 'data', 'books.json')

        self.inventory_general: List[Book] = []
        self.inventory_sorted: List[Book] = []

        # Ensure file exists and load
        self._ensure_file()
        self._load_from_file()

    # -------------------- File IO --------------------
    def _ensure_file(self) -> None:
        """Ensure the JSON file exists; create if missing with empty list.

        Raises:
        - Exception: if the directory cannot be created or file cannot be written.
        """
        directory = os.path.dirname(self.json_path)
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        if not os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise Exception(f"Unable to create books JSON file: {e}")

    def _load_from_file(self) -> None:
        """Load books from JSON into the two inventories.

        Validates that the top-level JSON is a list and that each item contains required fields.

        Raises:
        - ValueError: if JSON format is invalid.
        - Exception: for IO errors.
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"books.json contains invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"Unable to read books JSON file: {e}")

        if not isinstance(data, list):
            raise ValueError("books.json must contain a JSON list of book objects")

        loaded: List[Book] = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Invalid book entry at index {idx}: expected object/dict")
            # Required fields
            required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price', 'isBorrowed']
            for key in required:
                if key not in item:
                    raise ValueError(f"Missing '{key}' in book entry at index {idx}")

            # Create Book instance (trust types but coerce where reasonable)
            try:
                book = Book(
                    item['id'],
                    item['ISBNCode'],
                    item['title'],
                    item['author'],
                    float(item['weight']),
                    int(item['price']),
                    bool(item['isBorrowed']),
                )
            except Exception as e:
                raise ValueError(f"Invalid data types in book entry at index {idx}: {e}")
            loaded.append(book)

        # Populate inventories. inventory_general keeps insertion order from file.
        self.inventory_general = loaded

        # inventory_sorted must be sorted by ISBN (string). Use external insertion sort if available.
        if insertion_sort_books is not None:
            self.inventory_sorted = insertion_sort_books(list(self.inventory_general))
        else:
            # Fallback: use built-in sorted but signal that external algorithm is missing when used.
            self.inventory_sorted = sorted(self.inventory_general, key=lambda b: b.get_ISBNCode())

    def _save_to_file(self) -> None:
        """Serialize inventories to JSON (writes only one canonical list: `inventory_general`).

        Raises:
        - Exception: for IO errors.
        """
        data = []
        for b in self.inventory_general:
            data.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'isBorrowed': b.get_isBorrowed(),
            })

        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write books JSON file: {e}")

    # -------------------- CRUD --------------------
    def add_book(self, book: Book) -> None:
        """Add a book to the inventories and persist.

        Rules:
        - `id` must be unique (no other book in `inventory_general` with same id).
        - ISBN and title may be duplicated.
        - Insert into `inventory_general` (append) and update `inventory_sorted` using external insertion sort.

        Parameters:
        - book: `Book` instance to add.

        Returns: None

        Raises:
        - ValueError: if book with same id already exists.
        - ImportError: if `insertion_sort_books` algorithm is missing.
        - Exception: for IO errors when saving.
        """
        # Check unique id
        if any(b.get_id() == book.get_id() for b in self.inventory_general):
            raise ValueError(f"A book with id '{book.get_id()}' already exists")

        # Append to general inventory
        self.inventory_general.append(book)

        # Update sorted inventory using insertion sort algorithm
        if insertion_sort_books is None:
            raise ImportError("Required algorithm `insertion_sort_books` not found in utils.algoritmos/insertion_sort")
        self.inventory_sorted = insertion_sort_books(list(self.inventory_sorted) + [book])

        # Persist
        self._save_to_file()

    def get_all_books(self) -> List[Book]:
        """Return all books in inventory_general (preserve insertion order).

        Returns:
        - List[Book]
        """
        return list(self.inventory_general)

    def find_by_id(self, id: str) -> Optional[Book]:
        """Find and return a book by its unique id using linear scan.

        Parameters:
        - id: str

        Returns:
        - Book if found, else None
        """
        for b in self.inventory_general:
            if b.get_id() == id:
                return b
        return None

    def find_by_isbn(self, isbn: str) -> List[Book]:
        """Find all books matching an ISBN using binary search on `inventory_sorted`.

        Parameters:
        - isbn: str

        Returns:
        - List[Book] matching the ISBN (may be multiple)

        Raises:
        - ImportError: if `buscar_binario` not available.
        """
        if buscar_binario is None:
            raise ImportError("Required algorithm `buscar_binario` not found in utils.algoritmos/busqueda_binaria")

        # The external binary search implementation may have different signatures.
        # Attempt common calling conventions.
        try:
            # Signature: buscar_binario(list, key, key_func)
            result = buscar_binario(self.inventory_sorted, isbn, lambda b: b.get_ISBNCode())
        except TypeError:
            try:
                # Signature: buscar_binario(list, key)
                result = buscar_binario(self.inventory_sorted, isbn)
            except Exception as e:
                raise

        # Normalize result to list of Book objects
        if result is None:
            return []
        if isinstance(result, list):
            return result
        # If single Book returned
        return [result]

    def find_by_title(self, title: str) -> List[Book]:
        """Find books by title using linear search algorithm `buscar_lineal`.

        Parameters:
        - title: str

        Returns:
        - List[Book]

        Raises:
        - ImportError: if `buscar_lineal` not available.
        """
        if buscar_lineal is None:
            raise ImportError("Required algorithm `buscar_lineal` not found in utils.algoritmos/busqueda_lineal")

        try:
            result = buscar_lineal(self.inventory_general, title, lambda b: b.get_title())
        except TypeError:
            result = buscar_lineal(self.inventory_general, title)

        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result]

    def find_by_author(self, author: str) -> List[Book]:
        """Find books by author using linear search algorithm `buscar_lineal`.

        Parameters:
        - author: str

        Returns:
        - List[Book]

        Raises:
        - ImportError: if `buscar_lineal` not available.
        """
        if buscar_lineal is None:
            raise ImportError("Required algorithm `buscar_lineal` not found in utils.algoritmos/busqueda_lineal")

        try:
            result = buscar_lineal(self.inventory_general, author, lambda b: b.get_author())
        except TypeError:
            result = buscar_lineal(self.inventory_general, author)

        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result]

    def update_book(self, id: str, new_data: Dict[str, Any]) -> None:
        """Update fields of a book with given `id` using keys from `new_data`.

        Only fields present in `new_data` will be updated. After updating, inventories are kept consistent
        and `inventory_sorted` is re-ordered using the external insertion sort.

        Parameters:
        - id: str
        - new_data: dict with any of ['ISBNCode','title','author','weight','price','isBorrowed']

        Returns: None

        Raises:
        - ValueError: if book not found.
        - ImportError: if `insertion_sort_books` not available for reordering.
        - Exception: for IO errors when saving.
        """
        book = self.find_by_id(id)
        if book is None:
            raise ValueError(f"No book found with id '{id}'")

        # Allowed fields and corresponding setter methods
        field_setters = {
            'id': book.set_id,
            'ISBNCode': book.set_ISBNCode,
            'title': book.set_title,
            'author': book.set_author,
            'weight': book.set_weight,
            'price': book.set_price,
            'isBorrowed': book.set_isBorrowed,
        }

        for key, value in new_data.items():
            if key not in field_setters:
                continue
            # Coerce types reasonably
            if key == 'weight':
                value = float(value)
            if key == 'price':
                value = int(value)
            if key == 'isBorrowed':
                value = bool(value)
            field_setters[key](value)

        # Reorder sorted inventory
        if insertion_sort_books is None:
            raise ImportError("Required algorithm `insertion_sort_books` not found in utils.algoritmos/insertion_sort")
        self.inventory_sorted = insertion_sort_books(list(self.inventory_general))

        # Persist
        self._save_to_file()

    def delete_book(self, id: str) -> None:
        """Delete a book by id from both inventories and persist.

        Rules:
        - Cannot delete a book if `isBorrowed` is True.

        Parameters:
        - id: str

        Returns: None

        Raises:
        - ValueError: if book not found or is currently borrowed.
        - Exception: for IO errors when saving.
        """
        book = self.find_by_id(id)
        if book is None:
            raise ValueError(f"No book found with id '{id}'")
        if book.get_isBorrowed():
            raise ValueError("Cannot delete a book that is currently borrowed")

        # Remove by identity (or by id) from both lists
        self.inventory_general = [b for b in self.inventory_general if b.get_id() != id]
        self.inventory_sorted = [b for b in self.inventory_sorted if b.get_id() != id]

        # Persist
        self._save_to_file()

    # -------------------- Reports / Algorithms --------------------
    def generate_price_report(self) -> List[Book]:
        """Generate a report (list of books) ordered by price using external merge sort.

        Returns:
        - List[Book] sorted by `price` ascending (implementation depends on external algorithm).

        Raises:
        - ImportError: if `merge_sort_books_by_price` not available.
        """
        if merge_sort_books_by_price is None:
            raise ImportError("Required algorithm `merge_sort_books_by_price` not found in utils.algoritmos/merge_sort")

        return merge_sort_books_by_price(self.inventory_general)

    # -------------------- Integration placeholders --------------------
    def check_waiting_list(self, book: Book) -> None:
        """Placeholder for checking waiting list integration.

        Parameters:
        - book: Book

        Returns: None

        Note: intentionally unimplemented; for future integration.
        """
        pass

    def update_history_on_borrow(self, book: Book, user) -> None:
        """Placeholder for updating borrow history when a book is borrowed.

        Parameters:
        - book: Book
        - user: user object (integration-specific)

        Returns: None

        Note: intentionally unimplemented; for future integration.
        """
        pass

    def update_history_on_return(self, book: Book, user) -> None:
        """Placeholder for updating history when a book is returned.

        Parameters:
        - book: Book
        - user: user object (integration-specific)

        Returns: None

        Note: intentionally unimplemented; for future integration.
        """
        pass


# Example usage:
# service = BookService()
# books = service.get_all_books()
# for b in books:
#     print(b.get_title())
