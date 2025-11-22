import os
import json
from typing import List, Optional, Dict, Any

from models.Books import Book


class BookService:
    """Service for basic management of Book objects (no inventory, no algorithms).

    Responsibilities:
    - Maintain an internal list `self.books: List[Book]` representing the book catalog.
    - Persist the catalog to `./data/books.json` (create if missing, validate, serialize/deserialize).

    Important: This service does NOT handle stock, sorted lists, or call any algorithms.
    """

    def __init__(self, json_path: Optional[str] = None):
        """Initialize BookService and load books from JSON.

        Parameters:
        - json_path: Optional path to the books JSON file. If None, defaults to `./data/books.json`.

        Raises:
        - ValueError: if the JSON file exists but contains invalid format.
        - Exception: for unexpected IO errors.
        """
        if json_path:
            self.json_path = os.path.abspath(json_path)
        else:
            base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            self.json_path = os.path.join(base, 'data', 'books.json')

        self.books: List[Book] = []

        self._ensure_file()
        self._load_from_file()

    # -------------------- File handling --------------------
    def _ensure_file(self) -> None:
        """Ensure the JSON file and its directory exist; create with an empty list if missing.

        Raises:
        - Exception: if the directory or file cannot be created.
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
        """Load books from JSON into `self.books`.

        Expected JSON format: list of objects with keys
        ['id','ISBNCode','title','author','weight','price','isBorrowed'].

        Raises:
        - ValueError: if JSON structure is invalid or required fields are missing.
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

            required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price']
            for key in required:
                if key not in item:
                    raise ValueError(f"Missing '{key}' in book entry at index {idx}")

            try:
                # Support new 'stock' field. For backwards compatibility, accept files
                # that may have 'isBorrowed' instead: if 'stock' is missing we default to 1.
                stock_value = int(item.get('stock', 1))

                book = Book(
                    item['id'],
                    item['ISBNCode'],
                    item['title'],
                    item['author'],
                    float(item['weight']),
                    int(item['price']),
                    stock_value,
                )
            except Exception as e:
                raise ValueError(f"Invalid data types in book entry at index {idx}: {e}")
            loaded.append(book)

        self.books = loaded

    def _save_to_file(self) -> None:
        """Persist `self.books` to the JSON file in flattened format.

        Each book is saved as a plain object; stock or inventory fields are NOT saved.

        Raises:
        - Exception: for IO errors while writing the file.
        """
        data = []
        for b in self.books:
            data.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'stock': b.get_stock(),
            })

        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write books JSON file: {e}")

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
        self._save_to_file()

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
            'stock': book.set_stock,
        }

        if 'id' in new_data:
            new_id = new_data['id']
            if new_id != id and any(b.get_id() == new_id for b in self.books):
                raise ValueError(f"Cannot update id: another book with id '{new_id}' already exists")

        for key, value in new_data.items():
            if key not in setters:
                continue
            if key == 'weight':
                value = float(value)
            if key == 'price':
                value = int(value)
            if key == 'stock':
                value = int(value)
            if key == 'isBorrowed':
                value = bool(value)
            setters[key](value)

        self._save_to_file()

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
        if book.get_stock() > 0:
            raise ValueError("Cannot delete a book that has stock > 0")

        self.books = [b for b in self.books if b.get_id() != id]
        self._save_to_file()

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
