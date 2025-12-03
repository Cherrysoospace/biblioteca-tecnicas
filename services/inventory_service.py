import os 
import json
from typing import List, Optional, Dict, Any, Tuple

from models.Books import Book
from models.inventory import Inventory
from repositories.inventory_repository import InventoryRepository
from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal
from utils.config import FilePaths


class InventoryService:
    """Service responsible for managing inventory groups.

    Responsibilities:
    - BUSINESS LOGIC ONLY: inventory synchronization, stock management, ordering
    - Persistence delegated to InventoryRepository (SRP compliance)
    
    Manages in-memory lists:
    - self.inventory_general: List[Inventory] (unsorted, grouped by ISBN)
    - self.inventory_sorted: List[Inventory] (sorted by ISBN using insercion_ordenada)
    
    Each Inventory object represents a group of books with the same ISBN:
    - stock: total number of copies
    - items: list of Book objects (physical copies)
    """

    def __init__(self, repository: InventoryRepository = None):
        """Initialize InventoryService with a repository.

        Parameters:
        - repository: Optional InventoryRepository instance. If None, creates a new one.

        Raises:
        - Exception: for IO errors or invalid JSON format.
        """
        self.repository = repository or InventoryRepository()

        self.inventory_general: List[Inventory] = []
        self.inventory_sorted: List[Inventory] = []

        self._load_inventories()
        
        # If inventory is empty, regenerate from books.json
        if len(self.inventory_general) == 0:
            self._regenerate_from_books()
        
        self.synchronize_inventories()  # Ensure synchronization at initialization

    # -------------------- Persistence (delegated to repository) --------------------
    def _load_inventories(self) -> None:
        """Load inventories from repository.
        
        Raises:
        - ValueError: if JSON is malformed
        - Exception: for IO errors.
        """
        try:
            self.inventory_general = self.repository.load_general()
        except Exception:
            # Start with empty if load fails
            self.inventory_general = []

    def _save_inventories(self) -> None:
        """Persist both inventory lists using repository.
        
        Raises:
        - Exception: for IO errors
        """
        self.repository.save_both(self.inventory_general, self.inventory_sorted)

    # -------------------- CRUD --------------------
    def add_item(self, book: Book, stock: int = 1) -> None:
        """
        Add a new book to the inventory.
        
        If an inventory group with the same ISBN already exists, adds the book to that group.
        Otherwise, creates a new inventory group for this ISBN.

        Parameters:
        - book: Book instance to add to inventory.
        - stock: ignored (kept for compatibility), each book counts as 1 item.

        Returns: None

        Raises:
        - ValueError: if a book with the same id already exists.
        - Exception: for IO errors while saving.
        """
        # Check if book id already exists in any inventory group
        for inventory in self.inventory_general:
            for existing_book in inventory.get_items():
                if existing_book.get_id() == book.get_id():
                    raise ValueError(f"A book with id '{book.get_id()}' already exists in inventory")

        # Find existing inventory group with same ISBN
        target_inventory = None
        for inventory in self.inventory_general:
            if inventory.get_isbn() == book.get_ISBNCode():
                target_inventory = inventory
                break

        if target_inventory:
            # Add to existing group
            target_inventory.add_item(book)
        else:
            # Create new group
            new_inventory = Inventory(stock=1, items=[book])
            self.inventory_general.append(new_inventory)

        # Synchronize and save
        self.synchronize_inventories()

    def update_book_in_inventory(self, book_id: str, updated_book: Book) -> None:
        """
        Update a book's information in the inventory.
        
        If the ISBN changes, moves the book to the appropriate group.

        Parameters:
        - book_id: ID of the book to update
        - updated_book: Book object with updated information

        Raises:
        - ValueError: if book not found in inventory
        """
        found = False
        old_inventory = None
        
        # Find the book in inventory
        for inventory in self.inventory_general:
            for idx, book in enumerate(inventory.get_items()):
                if book.get_id() == book_id:
                    # Update book in place
                    items = inventory.get_items()
                    items[idx] = updated_book
                    inventory.set_items(items)
                    old_inventory = inventory
                    found = True
                    break
            if found:
                break
        
        if not found:
            raise ValueError(f"Book with id '{book_id}' not found in inventory")
        
        # If ISBN changed, move to different group
        if old_inventory and old_inventory.get_isbn() != updated_book.get_ISBNCode():
            # Remove from old group
            old_inventory.remove_item(book_id)
            
            # Remove empty groups (groups with no items).
            # Do NOT remove groups that have stock == 0 because they represent
            # out-of-stock ISBN groups which we keep for reservation/waitlist logic.
            self.inventory_general = [inv for inv in self.inventory_general if len(inv.get_items()) > 0]
            
            # Add to new group (or create it)
            target_inventory = None
            for inventory in self.inventory_general:
                if inventory.get_isbn() == updated_book.get_ISBNCode():
                    target_inventory = inventory
                    break
            
            if target_inventory:
                target_inventory.add_item(updated_book)
            else:
                new_inventory = Inventory(stock=1, items=[updated_book])
                self.inventory_general.append(new_inventory)
        
        self.synchronize_inventories()

    def delete_book_from_inventory(self, book_id: str) -> None:
        """
        Delete a book from inventory.

        Parameters:
        - book_id: ID of the book to delete

        Raises:
        - ValueError: if book not found
        """
        found = False
        
        for inventory in self.inventory_general:
            if inventory.remove_item(book_id):
                found = True
                break
        
        if not found:
            raise ValueError(f"Book with id '{book_id}' not found in inventory")
        
        # Remove empty groups (groups with no items). Keep groups with stock == 0
        # so reservations / waiting lists can reference them.
        self.inventory_general = [inv for inv in self.inventory_general if len(inv.get_items()) > 0]

        self.synchronize_inventories()

    def synchronize_inventories(self) -> None:
        """
        Synchronize the unordered inventory with the ordered inventory.

        This method ensures that inventory_sorted is a sorted copy of inventory_general
        using the insertion sort algorithm (insercion_ordenada).

        Raises:
        - Exception: for IO errors while saving.
        """
        # Create deep copy of inventory_general to inventory_sorted
        self.inventory_sorted = []
        for inv in self.inventory_general:
            # Create new Inventory with same data
            books_copy = []
            for book in inv.get_items():
                book_copy = Book(
                    book.get_id(),
                    book.get_ISBNCode(),
                    book.get_title(),
                    book.get_author(),
                    book.get_weight(),
                    book.get_price(),
                    book.get_isBorrowed()
                )
                books_copy.append(book_copy)
            
            inv_copy = Inventory(stock=inv.get_stock(), items=books_copy)
            self.inventory_sorted.append(inv_copy)

        # Sort using the insertion sort algorithm
        insercion_ordenada(self.inventory_sorted)

        # Save both inventories
        self._save_inventories()

    def _regenerate_from_books(self) -> None:
        """
        Regenerate inventory from books.json if inventory is empty.
        
        This method loads all books from books.json and creates inventory groups
        organized by ISBN. Each book becomes an item in the appropriate group.
        """
        books_json = FilePaths.BOOKS

        # Check if books.json exists
        if not os.path.exists(books_json):
            return

        # Read books.json using JSONFileHandler
        try:
            from utils.file_handler import JSONFileHandler
            books_data = JSONFileHandler.load_json(books_json, expected_type=list)
        except Exception:
            return

        if not isinstance(books_data, list) or len(books_data) == 0:
            return

        # Group books by ISBN
        isbn_groups: Dict[str, List[Book]] = {}
        
        for item in books_data:
            if not isinstance(item, dict):
                continue
            
            try:
                book = Book(
                    item['id'],
                    item['ISBNCode'],
                    item['title'],
                    item['author'],
                    float(item['weight']),
                    int(item['price']),
                    bool(item.get('isBorrowed', False))
                )
                
                isbn = book.get_ISBNCode()
                if isbn not in isbn_groups:
                    isbn_groups[isbn] = []
                isbn_groups[isbn].append(book)
                
            except (KeyError, ValueError):
                continue

        # Create Inventory groups
        for isbn, books in isbn_groups.items():
            inventory = Inventory(stock=len(books), items=books)
            self.inventory_general.append(inventory)

    def regenerate_general_from_books(self, books_path: Optional[str] = None, preserve_borrowed: bool = True) -> None:
        """Rebuild `self.inventory_general` from `books.json`.

        Parameters:
        - books_path: optional path to a books.json file. If None, defaults to
          './data/books.json' in the project data directory.
        - preserve_borrowed: if True, attempts to preserve existing per-book
          `isBorrowed` flags by matching book ids from the current inventory.

        This method:
        - loads books.json (must be a list of book objects),
        - for each book entry (in file order) creates a Book + Inventory item
          with stock=1 and appropriate isBorrowed flag,
        - replaces `self.inventory_general` with the rebuilt list,
        - saves both general and sorted inventory files.

        Raises:
        - ValueError: if books.json is invalid.
        - Exception: for IO errors while reading/writing files.
        """
        # determine books.json path
        books_json = books_path or FilePaths.BOOKS

        # read books.json using JSONFileHandler
        try:
            from utils.file_handler import JSONFileHandler
            books_data = JSONFileHandler.load_json(books_json, expected_type=list)
        except ValueError as e:
            raise ValueError(f"{books_json} contains invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"Unable to read {books_json}: {e}")

        if not isinstance(books_data, list):
            raise ValueError(f"{books_json} must contain a JSON list of books")

        rebuilt: List[Inventory] = []
        for it in books_data:
            try:
                book = Book(
                    it['id'],
                    it['ISBNCode'],
                    it['title'],
                    it['author'],
                    it['weight'],
                    it['price'],
                    False
                )
                inv_item = Inventory(book, 1)
                rebuilt.append(inv_item)
            except KeyError:
                continue

        # replace and persist
        self.inventory_general = rebuilt
        self.synchronize_inventories()

    def update_borrow_status(self, book_id: str, is_borrowed: bool) -> None:
        """Set the isBorrowed flag for a specific inventory entry and persist.

        This modifies the inventory item having the given book_id and saves
        both general and sorted files.
        """
        found = False
        for inv in self.inventory_general:
            if inv.get_book().get_id() == book_id:
                inv.set_isBorrowed(bool(is_borrowed))
                # Keep per-item stock consistent with borrow status: borrowed => 0, available => 1
                try:
                    inv.set_stock(0 if bool(is_borrowed) else 1)
                except Exception:
                    pass
                found = True
                break

        if not found:
            raise ValueError(f"No inventory item found with book id '{book_id}'")

        # persist changes
        self._save_inventories()

    # -------------------- Searches & Reports --------------------
    def find_by_book_id(self, id: str) -> Optional[Inventory]:
        """Find an inventory item by the book's unique id.

        Parameters:
        - id: book id

        Returns:
        - Inventory if found, else None
        """
        for inv in self.inventory_general:
            if inv.get_book().get_id() == id:
                return inv
        return None

    def find_by_isbn(self, isbn: str) -> List[Inventory]:
        """Find inventory items by ISBN using binary search on `inventory_sorted`.

        Parameters:
        - isbn: ISBN string to search

        Returns:
        - List[Inventory] matching the ISBN (may be multiple)

        Raises:
        - ImportError: if `buscar_binario` not available.
        """
        # Simple linear search fallback: scan the general inventory list and
        # collect items whose book ISBN matches the requested value.
        # This avoids depending on external binary-search implementation.
        if isbn is None:
            return []

        matches: List[Inventory] = [inv for inv in self.inventory_general if inv.get_book().get_ISBNCode() == isbn]
        return matches

    def get_isbns_with_zero_stock(self) -> List[Tuple[str, Optional[str]]]:
        """Return a list of (ISBN, title) tuples for ISBN groups whose total stock sums to 0.

        This consolidates the logic used by UI forms to list waiting-list candidates and
        centralizes it for reuse.
        """
        results: List[Tuple[str, Optional[str]]] = []
        totals: Dict[str, int] = {}
        samples: Dict[str, Tuple[Optional[str], Optional[str]]] = {}

        for inv in self.inventory_general:
            try:
                book = inv.get_book()
                if book is None:
                    continue
                isbn = book.get_ISBNCode()
                totals[isbn] = totals.get(isbn, 0) + int(inv.get_stock())
                if isbn not in samples:
                    samples[isbn] = (book.get_title(), book.get_id())
            except Exception:
                continue

        for isbn, total in totals.items():
            if total == 0:
                title = samples.get(isbn, (None, None))[0]
                results.append((isbn, title))

        return results

    def get_isbns_with_available_copies(self) -> List[Tuple[str, Optional[str], Optional[str]]]:
        """Return a list of (ISBN, title, sample_book_id) for ISBN groups with available copies (>0).

        This is useful for loan flows where we need an ISBN that currently has at least
        one available (not borrowed) physical copy.
        """
        results: List[Tuple[str, Optional[str], Optional[str]]] = []
        for inv in self.inventory_general:
            try:
                available = inv.get_available_count()
                if available and available > 0:
                    book = inv.get_book()
                    if book is None:
                        continue
                    isbn = book.get_ISBNCode()
                    title = book.get_title()
                    bid = book.get_id()
                    results.append((isbn, title, bid))
            except Exception:
                continue
        return results

    def find_by_title(self, title: str) -> List[Inventory]:
        """Find inventory items where the book title matches using linear search.

        Uses the recursive busqueda_lineal algorithm to search through the
        Inventario General (unsorted list) for books matching the title.
        The search is case-insensitive and supports partial matches.

        Parameters:
        - title: title string to search (can be partial)

        Returns:
        - List[Inventory]: All inventory items with matching titles

        Example:
        >>> service.find_by_title("quijote")
        [<Inventory for "Don Quijote de la Mancha">]
        """
        results = []
        start_index = 0
        
        # Buscar todas las coincidencias iterativamente usando búsqueda lineal
        while start_index < len(self.inventory_general):
            # Usar busqueda_lineal desde start_index
            index = busqueda_lineal(self.inventory_general, title, start_index)
            
            if index == -1:
                # No más coincidencias
                break
            
            # Agregar resultado encontrado
            results.append(self.inventory_general[index])
            
            # Continuar buscando desde la siguiente posición
            start_index = index + 1
        
        return results

    def find_by_author(self, author: str) -> List[Inventory]:
        """Find inventory items where the book author matches using linear search.

        Uses the recursive busqueda_lineal algorithm to search through the
        Inventario General (unsorted list) for books matching the author.
        The search is case-insensitive and supports partial matches.

        Parameters:
        - author: author string to search (can be partial)

        Returns:
        - List[Inventory]: All inventory items with matching authors

        Example:
        >>> service.find_by_author("garcía márquez")
        [<Inventory for books by Gabriel García Márquez>]
        """
        results = []
        start_index = 0
        
        # Buscar todas las coincidencias iterativamente usando búsqueda lineal
        while start_index < len(self.inventory_general):
            # Usar busqueda_lineal desde start_index
            index = busqueda_lineal(self.inventory_general, author, start_index)
            
            if index == -1:
                # No más coincidencias
                break
            
            # Agregar resultado encontrado
            results.append(self.inventory_general[index])
            
            # Continuar buscando desde la siguiente posición
            start_index = index + 1
        
        return results


# Example usage:
# service = InventoryService()
# service.add_item(Book('1','978-1','Title','Author',0.5,100,False), 3)
# invs = service.find_by_title('Title')
# for inv in invs:
#     print(inv.get_book().get_title(), inv.get_stock())
