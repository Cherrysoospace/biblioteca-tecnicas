import os 
import json
from typing import List, Optional, Dict, Any

from models.Books import Book
from models.inventory import Inventory

# Try to import required algorithm functions from expected modules.
try:
    from utils.algoritmos.insertion_sort import insertion_sort_inventory
    from utils.algoritmos.busqueda_lineal import buscar_lineal
    from utils.algoritmos.busqueda_binaria import buscar_binario
    from utils.algoritmos.merge_sort import merge_sort_inventory_by_price
except Exception:
    try:
        from utils.algorithms.insertion_sort import insertion_sort_inventory  # type: ignore
        from utils.algorithms.busqueda_lineal import buscar_lineal  # type: ignore
        from utils.algorithms.busqueda_binaria import buscar_binario  # type: ignore
        from utils.algorithms.merge_sort import merge_sort_inventory_by_price  # type: ignore
    except Exception:
        insertion_sort_inventory = None  # type: ignore
        buscar_lineal = None  # type: ignore
        buscar_binario = None  # type: ignore
        merge_sort_inventory_by_price = None  # type: ignore


class InventoryService:
    """Service responsible for managing inventory items persisted as JSON.

    Manages two JSON files (general and sorted), keeps in-memory lists:
    - self.inventory_general: List[Inventory] (unsorted)
    - self.inventory_sorted: List[Inventory]  (sorted by ISBN)

    Algorithms (insertion sort, linear search, binary search, merge sort) are
    expected to live in `utils/algoritmos` and are called by this service.
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
        self._load_sorted()

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

        Expects a JSON list of flattened inventory items. Converts each entry into
        an `Inventory(Book(...), stock)` instance.

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
            raise ValueError(f"{self.general_path} must contain a JSON list of inventory objects")

        loaded: List[Inventory] = []

        # Support two file formats for backwards compatibility:
        # 1) Legacy: list of flattened inventory entries (one per physical copy).
        #    Example element: { 'id': 'B001', 'ISBNCode': '...', 'title': '...', ..., 'stock': 1 }
        # 2) Aggregated-by-ISBN: list of groups, one per ISBN. Each group contains
        #    'ISBNCode', 'stock' (total) and 'items' (list of per-copy book objects).
        #    Example: { 'ISBNCode': '...', 'stock': 3, 'items': [ { 'id': 'B001', 'title': ... }, ... ] }

        if len(data) == 0:
            self.inventory_general = []
            return

        first = data[0]
        if isinstance(first, dict) and 'items' in first:
            # Aggregated format
            for grp in data:
                if not isinstance(grp, dict) or 'ISBNCode' not in grp or 'items' not in grp:
                    raise ValueError("Invalid aggregated inventory group format")
                total_stock = int(grp.get('stock', 0))
                items = grp.get('items', [])
                if not isinstance(items, list):
                    raise ValueError("'items' must be a list in aggregated inventory group")

                # For aggregated format we derive per-item stock from the
                # 'isBorrowed' flag unless an explicit per-item 'stock' exists.
                # This preserves availability even though per-item 'stock' is
                # not saved in the new format.
                for idx_it, it in enumerate(items):
                    if not isinstance(it, dict):
                        raise ValueError("Invalid item in aggregated 'items' list: expected dict")
                    try:
                        book = Book(
                            it['id'],
                            grp['ISBNCode'],
                            it['title'],
                            it['author'],
                            float(it['weight']),
                            int(it['price']),
                            bool(it.get('isBorrowed', False)),
                        )
                    except Exception as e:
                        raise ValueError(f"Invalid book data in aggregated items: {e}")

                    # if explicit per-item stock provided, use it; otherwise
                    # derive: available => 1, borrowed => 0
                    if 'stock' in it:
                        stock = int(it.get('stock', 1))
                    else:
                        stock = 0 if bool(it.get('isBorrowed', False)) else 1

                    loaded.append(Inventory(book, stock, bool(it.get('isBorrowed', False))))
        else:
            # Legacy format (per-copy entries)
            for idx, item in enumerate(data):
                if not isinstance(item, dict):
                    raise ValueError(f"Invalid inventory entry at index {idx}: expected object/dict")
                required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price', 'isBorrowed']
                for key in required:
                    if key not in item:
                        raise ValueError(f"Missing '{key}' in inventory entry at index {idx}")

                try:
                    book = Book(
                        item['id'],
                        item['ISBNCode'],
                        item['title'],
                        item['author'],
                        float(item['weight']),
                        int(item['price']),
                        bool(item.get('isBorrowed', False)),
                    )
                    stock = int(item.get('stock', 0))
                    if stock < 0:
                        raise ValueError(f"Stock must be >= 0 at index {idx}")
                except Exception as e:
                    raise ValueError(f"Invalid data types in inventory entry at index {idx}: {e}")

                loaded.append(Inventory(book, stock, bool(item.get('isBorrowed', False))))

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
        except json.JSONDecodeError:
            # If malformed, regenerate from general
            self.regenerate_sorted_inventory()
            return
        except Exception as e:
            raise Exception(f"Unable to read {self.sorted_path}: {e}")

        if not isinstance(data, list) or len(data) == 0:
            # regenerate if empty
            self.regenerate_sorted_inventory()
            return

        loaded: List[Inventory] = []
        if len(data) == 0:
            self.inventory_sorted = []
            return

        first = data[0]
        if isinstance(first, dict) and 'items' in first:
            # Aggregated format
            for grp in data:
                if not isinstance(grp, dict) or 'ISBNCode' not in grp or 'items' not in grp:
                    self.regenerate_sorted_inventory()
                    return
                total_stock = int(grp.get('stock', 0))
                items = grp.get('items', [])
                if not isinstance(items, list):
                    self.regenerate_sorted_inventory()
                    return

                item_stocks = [int(it.get('stock', 1)) if isinstance(it, dict) else 1 for it in items]
                sum_items = sum(item_stocks)
                if total_stock == 0:
                    total_stock = sum_items
                extra = total_stock - sum_items

                for idx_it, it in enumerate(items):
                    if not isinstance(it, dict):
                        self.regenerate_sorted_inventory()
                        return
                    try:
                        book = Book(
                            it['id'],
                            grp['ISBNCode'],
                            it['title'],
                            it['author'],
                            float(it['weight']),
                            int(it['price']),
                            bool(it.get('isBorrowed', False)),
                        )
                    except Exception:
                        self.regenerate_sorted_inventory()
                        return

                    stock = int(it.get('stock', 1))
                    if idx_it == 0 and extra > 0:
                        stock += extra
                    loaded.append(Inventory(book, stock, bool(it.get('isBorrowed', False))))
        else:
            # Legacy per-copy format
            try:
                for idx, item in enumerate(data):
                    if not isinstance(item, dict):
                        self.regenerate_sorted_inventory()
                        return
                    required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price', 'isBorrowed']
                    for key in required:
                        if key not in item:
                            self.regenerate_sorted_inventory()
                            return
                    book = Book(
                        item['id'],
                        item['ISBNCode'],
                        item['title'],
                        item['author'],
                        float(item['weight']),
                        int(item['price']),
                        bool(item.get('isBorrowed', False)),
                    )
                    stock = int(item.get('stock', 0))
                    loaded.append(Inventory(book, stock, bool(item.get('isBorrowed', False))))
            except Exception:
                self.regenerate_sorted_inventory()
                return

        self.inventory_sorted = loaded

    def _save_general(self) -> None:
        """Serialize `self.inventory_general` to `inventory_general.json` in flattened format.

        Raises:
        - Exception: for IO errors.
        """
        data = []
        # New aggregated-by-ISBN format: one object per ISBN with total 'stock'
        # and an 'items' list containing per-copy book attributes.
        groups: Dict[str, List[Inventory]] = {}
        for inv in self.inventory_general:
            isbn = inv.get_book().get_ISBNCode()
            groups.setdefault(isbn, []).append(inv)

        data = []
        for isbn, items in groups.items():
            total = sum(i.get_stock() for i in items)
            grp: Dict[str, Any] = {
                'ISBNCode': isbn,
                'stock': total,
                'items': []
            }
            for inv in items:
                b = inv.get_book()
                # Do NOT write per-item 'stock' into saved JSON; stock is
                # represented only at the group (ISBN) level.
                grp['items'].append({
                    'id': b.get_id(),
                    'title': b.get_title(),
                    'author': b.get_author(),
                    'weight': b.get_weight(),
                    'price': b.get_price(),
                    'isBorrowed': inv.get_isBorrowed(),
                })
            data.append(grp)

        try:
            with open(self.general_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write {self.general_path}: {e}")

    def _save_sorted(self) -> None:
        """Serialize `self.inventory_sorted` to `inventory_sorted.json` in flattened format.

        Raises:
        - Exception: for IO errors.
        """
        data = []
        # Aggregated-by-ISBN format for sorted file as well
        groups: Dict[str, List[Inventory]] = {}
        for inv in self.inventory_sorted:
            isbn = inv.get_book().get_ISBNCode()
            groups.setdefault(isbn, []).append(inv)

        data = []
        for isbn, items in groups.items():
            total = sum(i.get_stock() for i in items)
            grp: Dict[str, Any] = {
                'ISBNCode': isbn,
                'stock': total,
                'items': []
            }
            for inv in items:
                b = inv.get_book()
                # Save item attributes without per-copy 'stock'. The group's
                # 'stock' contains the total count for that ISBN.
                grp['items'].append({
                    'id': b.get_id(),
                    'title': b.get_title(),
                    'author': b.get_author(),
                    'weight': b.get_weight(),
                    'price': b.get_price(),
                    'isBorrowed': inv.get_isBorrowed(),
                })
            data.append(grp)

        try:
            with open(self.sorted_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise Exception(f"Unable to write {self.sorted_path}: {e}")

    # -------------------- CRUD --------------------
    def add_item(self, book: Book, stock: int) -> None:
        """Add a new inventory item.

        Parameters:
        - book: Book instance to add to inventory.
        - stock: non-negative integer stock value.

        Returns: None

        Raises:
        - ValueError: if a book with same id already exists or stock < 0.
        - ImportError: if required insertion sort algorithm is missing when regenerating sorted list.
        - Exception: for IO errors while saving.
        """
        if stock < 0:
            raise ValueError("stock must be >= 0")

        if any(inv.get_book().get_id() == book.get_id() for inv in self.inventory_general):
            raise ValueError(f"An inventory item with book id '{book.get_id()}' already exists")

        new_inv = Inventory(book, int(stock))
        self.inventory_general.append(new_inv)

        # Try to insert into sorted list using external insertion sort
        if insertion_sort_inventory is None:
            # fallback: regenerate sorted using builtin sort by ISBN
            self.inventory_sorted = sorted(self.inventory_general, key=lambda inv: inv.get_book().get_ISBNCode())
        else:
            self.inventory_sorted = insertion_sort_inventory(list(self.inventory_general))

        self._save_general()
        self._save_sorted()

    def update_stock(self, book_id: str, new_stock: int) -> None:
        """Update the stock for an existing inventory item.

        Parameters:
        - book_id: id of the Book to update.
        - new_stock: non-negative integer stock value.

        Returns: None

        Raises:
        - ValueError: if item not found or new_stock < 0.
        - Exception: for IO errors while saving.
        """
        if new_stock < 0:
            raise ValueError("new_stock must be >= 0")

        found = False
        for inv in self.inventory_general:
            if inv.get_book().get_id() == book_id:
                inv.set_stock(int(new_stock))
                found = True
                break

        if not found:
            raise ValueError(f"No inventory item found with book id '{book_id}'")

        # Keep sorted consistent
        if insertion_sort_inventory is None:
            self.inventory_sorted = sorted(self.inventory_general, key=lambda inv: inv.get_book().get_ISBNCode())
        else:
            self.inventory_sorted = insertion_sort_inventory(list(self.inventory_general))

        self._save_general()
        self._save_sorted()

    def delete_item(self, book_id: str) -> None:
        """Delete an inventory item by book id.

        Parameters:
        - book_id: id of the Book to delete.

        Returns: None

        Raises:
        - ValueError: if item not found or book is currently borrowed.
        - Exception: for IO errors while saving.
        """
        inv = next((i for i in self.inventory_general if i.get_book().get_id() == book_id), None)
        if inv is None:
            raise ValueError(f"No inventory item found with book id '{book_id}'")
        if inv.get_isBorrowed():
            raise ValueError("Cannot delete inventory item: the book is currently borrowed")

        self.inventory_general = [i for i in self.inventory_general if i.get_book().get_id() != book_id]
        self.inventory_sorted = [i for i in self.inventory_sorted if i.get_book().get_id() != book_id]

        self._save_general()
        self._save_sorted()

    # -------------------- Sorted regeneration --------------------
    def regenerate_sorted_inventory(self) -> None:
        """Rebuild `self.inventory_sorted` by applying insertion sort on `inventory_general`.

        Uses external algorithm `insertion_sort_inventory`. If missing, falls back to built-in sort.

        Returns: None

        Raises:
        - ImportError: if algorithm is required but missing (this service falls back instead of raising).
        """
        if insertion_sort_inventory is None:
            self.inventory_sorted = sorted(self.inventory_general, key=lambda inv: inv.get_book().get_ISBNCode())
        else:
            self.inventory_sorted = insertion_sort_inventory(list(self.inventory_general))

        self._save_sorted()

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

        # load existing borrow map if requested
        borrow_map = {}
        if preserve_borrowed:
            for inv in self.inventory_general:
                try:
                    borrow_map[inv.get_book().get_id()] = inv.get_isBorrowed()
                except Exception:
                    continue

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
        for idx, it in enumerate(books_data):
            if not isinstance(it, dict):
                raise ValueError(f"Invalid book entry at index {idx}: expected object/dict")
            required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price']
            for key in required:
                if key not in it:
                    raise ValueError(f"Missing '{key}' in book entry at index {idx}")

            try:
                book = Book(
                    it['id'],
                    it['ISBNCode'],
                    it['title'],
                    it['author'],
                    float(it['weight']),
                    int(it['price']),
                    bool(borrow_map.get(it['id'], False)),
                )
            except Exception as e:
                raise ValueError(f"Invalid data types in book entry at index {idx}: {e}")

            inv_item = Inventory(book, 1, bool(borrow_map.get(it['id'], False)))
            rebuilt.append(inv_item)

        # replace and persist
        self.inventory_general = rebuilt
        # regenerate sorted
        if insertion_sort_inventory is None:
            self.inventory_sorted = sorted(self.inventory_general, key=lambda inv: inv.get_book().get_ISBNCode())
        else:
            self.inventory_sorted = insertion_sort_inventory(list(self.inventory_general))

        self._save_general()
        self._save_sorted()

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
