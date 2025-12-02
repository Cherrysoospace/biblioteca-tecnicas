import os 
import json
from typing import List, Optional, Dict, Any

from models.Books import Book
from models.inventory import Inventory
from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada


class InventoryService:
    """Service responsible for managing inventory groups persisted as JSON.

    Manages two JSON files (general and sorted), keeps in-memory lists:
    - self.inventory_general: List[Inventory] (unsorted, grouped by ISBN)
    - self.inventory_sorted: List[Inventory] (sorted by ISBN using insercion_ordenada)
    
    Each Inventory object represents a group of books with the same ISBN:
    - stock: total number of copies
    - items: list of Book objects (physical copies)
    """

    def __init__(self, general_path: Optional[str] = None, sorted_path: Optional[str] = None):
        """Initialize InventoryService and load inventories from JSON files.

        Parameters:
        - general_path: Optional path for `inventory_general.json`. Defaults to `./data/inventory_general.json`.
        - sorted_path: Optional path for `inventory_sorted.json`. Defaults to `./data/inventory_sorted.json`.

        Raises:
        - Exception: for IO errors or invalid JSON format.
        """
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        data_dir = os.path.join(base, 'data')

        if general_path:
            self.general_path = os.path.abspath(general_path)
        else:
            self.general_path = os.path.join(data_dir, 'inventory_general.json')

        if sorted_path:
            self.sorted_path = os.path.abspath(sorted_path)
        else:
            self.sorted_path = os.path.join(data_dir, 'inventory_sorted.json')

        self.inventory_general: List[Inventory] = []
        self.inventory_sorted: List[Inventory] = []

        self._ensure_files_exist()
        self._load_general()
        
        # If inventory is empty, regenerate from books.json
        if len(self.inventory_general) == 0:
            self._regenerate_from_books()
        
        self.synchronize_inventories()  # Ensure synchronization at initialization

    # -------------------- File IO --------------------
    def _ensure_files_exist(self) -> None:
        """Ensure both JSON files and their parent directory exist.

        Creates files with empty list content if they don't exist.

        Raises:
        - Exception: if directories or files cannot be created.
        """
        for path in (self.general_path, self.sorted_path):
            directory = os.path.dirname(path)
            if not os.path.isdir(directory):
                os.makedirs(directory, exist_ok=True)
            if not os.path.exists(path):
                try:
                    with open(path, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
                except Exception as e:
                    raise Exception(f"Unable to create inventory JSON file '{path}': {e}")

    def _load_general(self) -> None:
        """Load `inventory_general.json` into `self.inventory_general`.

        Expects a JSON list with structure:
        [
          {
            "stock": 2,
            "items": [
              { "id": "B001", "ISBNCode": "...", "title": "...", ... },
              { "id": "B002", "ISBNCode": "...", "title": "...", ... }
            ]
          },
          ...
        ]

        Raises:
        - ValueError: if JSON is malformed or entries missing required fields.
        - Exception: for IO errors.
        """
        try:
            with open(self.general_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"{self.general_path} contains invalid JSON: {e}")
        except Exception as e:
            raise Exception(f"Unable to read {self.general_path}: {e}")

        if not isinstance(data, list):
            raise ValueError(f"{self.general_path} must contain a JSON list of inventory groups")

        loaded: List[Inventory] = []

        for idx, group in enumerate(data):
            if not isinstance(group, dict):
                raise ValueError(f"Invalid inventory group at index {idx}: expected object/dict")
            
            if 'items' not in group:
                raise ValueError(f"Missing 'items' in inventory group at index {idx}")
            
            items_data = group['items']
            if not isinstance(items_data, list):
                raise ValueError(f"'items' must be a list in inventory group at index {idx}")

            # Parse each book in items
            books: List[Book] = []
            for item_idx, item in enumerate(items_data):
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
                    books.append(book)
                except KeyError as e:
                    raise ValueError(f"Missing field {e} in item {item_idx} of group {idx}")
                except Exception as e:
                    raise ValueError(f"Invalid data in item {item_idx} of group {idx}: {e}")

            # Create Inventory group
            stock = int(group.get('stock', len(books)))
            inventory = Inventory(stock=stock, items=books)
            loaded.append(inventory)

        self.inventory_general = loaded

    def _load_sorted(self) -> None:
        """Load `inventory_sorted.json` into `self.inventory_sorted`.

        If the file is empty or invalid, attempts to regenerate sorted inventory from general.

        Raises:
        - Exception: for IO errors or malformed JSON.
        """
        try:
            with open(self.sorted_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, Exception):
            # If malformed or unreadable, regenerate from general
            self.synchronize_inventories()
            return

        if not isinstance(data, list) or len(data) == 0:
            # Regenerate if empty
            self.synchronize_inventories()
            return

        loaded: List[Inventory] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            try:
                book = Book(
                    item['id'],
                    item['ISBNCode'],
                    item['title'],
                    item['author'],
                    item['weight'],
                    item['price'],
                    item['isBorrowed']
                )
                inventory_item = Inventory(book, item['stock'])
                loaded.append(inventory_item)
            except KeyError:
                continue

        self.inventory_sorted = loaded
        insercion_ordenada(self.inventory_sorted)

    def _save_general(self) -> None:
        """Serialize `self.inventory_general` to `inventory_general.json`.

        Format:
        [
          {
            "stock": 2,
            "items": [
              { "id": "B001", "ISBNCode": "...", ... },
              { "id": "B002", "ISBNCode": "...", ... }
            ]
          },
          ...
        ]

        Raises:
        - Exception: for IO errors.
        """
        data = []
        for inventory in self.inventory_general:
            group = {
                'stock': inventory.get_stock(),
                'items': []
            }
            
            for book in inventory.get_items():
                group['items'].append({
                    'id': book.get_id(),
                    'ISBNCode': book.get_ISBNCode(),
                    'title': book.get_title(),
                    'author': book.get_author(),
                    'weight': book.get_weight(),
                    'price': book.get_price(),
                    'isBorrowed': book.get_isBorrowed(),
                })
            
            data.append(group)

        try:
            with open(self.general_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write {self.general_path}: {e}")

    def _save_sorted(self) -> None:
        """Serialize `self.inventory_sorted` to `inventory_sorted.json`.

        Same format as _save_general but with sorted groups.

        Raises:
        - Exception: for IO errors.
        """
        data = []
        for inventory in self.inventory_sorted:
            group = {
                'stock': inventory.get_stock(),
                'items': []
            }
            
            for book in inventory.get_items():
                group['items'].append({
                    'id': book.get_id(),
                    'ISBNCode': book.get_ISBNCode(),
                    'title': book.get_title(),
                    'author': book.get_author(),
                    'weight': book.get_weight(),
                    'price': book.get_price(),
                    'isBorrowed': book.get_isBorrowed(),
                })
            
            data.append(group)

        try:
            with open(self.sorted_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write {self.sorted_path}: {e}")

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
            
            # Remove empty groups
            self.inventory_general = [inv for inv in self.inventory_general if inv.get_stock() > 0]
            
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
        
        # Remove empty groups
        self.inventory_general = [inv for inv in self.inventory_general if inv.get_stock() > 0]
        
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
        self._save_general()
        self._save_sorted()

    def _regenerate_from_books(self) -> None:
        """
        Regenerate inventory from books.json if inventory is empty.
        
        This method loads all books from books.json and creates inventory groups
        organized by ISBN. Each book becomes an item in the appropriate group.
        """
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        books_json = os.path.join(base, 'data', 'books.json')

        # Check if books.json exists
        if not os.path.exists(books_json):
            return

        # Read books.json
        try:
            with open(books_json, 'r', encoding='utf-8') as f:
                books_data = json.load(f)
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
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if books_path:
            books_json = os.path.abspath(books_path)
        else:
            books_json = os.path.join(base, 'data', 'books.json')

        # read books.json
        try:
            with open(books_json, 'r', encoding='utf-8') as f:
                books_data = json.load(f)
        except json.JSONDecodeError as e:
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
        self._save_general()
        self._save_sorted()

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

    def find_by_title(self, title: str) -> List[Inventory]:
        """Find inventory items where the book title matches using linear search.

        Parameters:
        - title: title string to search

        Returns:
        - List[Inventory]

        Raises:
        - ImportError: if `buscar_lineal` not available.
        """
        if buscar_lineal is None:
            raise ImportError("Required algorithm `buscar_lineal` not found in utils.algoritmos/busqueda_lineal")

        try:
            result = buscar_lineal(self.inventory_general, title, lambda inv: inv.get_book().get_title())
        except TypeError:
            result = buscar_lineal(self.inventory_general, title)

        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result]

    def find_by_author(self, author: str) -> List[Inventory]:
        """Find inventory items where the book author matches using linear search.

        Parameters:
        - author: author string to search

        Returns:
        - List[Inventory]

        Raises:
        - ImportError: if `buscar_lineal` not available.
        """
        if buscar_lineal is None:
            raise ImportError("Required algorithm `buscar_lineal` not found in utils.algoritmos/busqueda_lineal")

        try:
            result = buscar_lineal(self.inventory_general, author, lambda inv: inv.get_book().get_author())
        except TypeError:
            result = buscar_lineal(self.inventory_general, author)

        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result]

    def generate_price_report(self) -> List[Inventory]:
        """Generate a report (list of Inventory) ordered by book price using merge sort.

        Returns:
        - List[Inventory] sorted by book.price ascending.

        Raises:
        - ImportError: if `merge_sort_inventory_by_price` not available.
        """
        if merge_sort_inventory_by_price is None:
            raise ImportError("Required algorithm `merge_sort_inventory_by_price` not found in utils.algoritmos/merge_sort")

        return merge_sort_inventory_by_price(self.inventory_general)


# Example usage:
# service = InventoryService()
# service.add_item(Book('1','978-1','Title','Author',0.5,100,False), 3)
# invs = service.find_by_title('Title')
# for inv in invs:
#     print(inv.get_book().get_title(), inv.get_stock())
