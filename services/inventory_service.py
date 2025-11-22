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
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Invalid inventory entry at index {idx}: expected object/dict")
            required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price', 'isBorrowed', 'stock']
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
                    bool(item['isBorrowed']),
                )
                stock = int(item['stock'])
                if stock < 0:
                    raise ValueError(f"Stock must be >= 0 at index {idx}")
            except Exception as e:
                raise ValueError(f"Invalid data types in inventory entry at index {idx}: {e}")

            loaded.append(Inventory(book, stock))

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
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                self.regenerate_sorted_inventory()
                return
            required = ['id', 'ISBNCode', 'title', 'author', 'weight', 'price', 'isBorrowed', 'stock']
            for key in required:
                if key not in item:
                    self.regenerate_sorted_inventory()
                    return
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
                stock = int(item['stock'])
            except Exception:
                self.regenerate_sorted_inventory()
                return

            loaded.append(Inventory(book, stock))

        self.inventory_sorted = loaded

    def _save_general(self) -> None:
        """Serialize `self.inventory_general` to `inventory_general.json` in flattened format.

        Raises:
        - Exception: for IO errors.
        """
        data = []
        for inv in self.inventory_general:
            b = inv.get_book()
            data.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'isBorrowed': b.get_isBorrowed(),
                'stock': inv.get_stock(),
            })

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
        for inv in self.inventory_sorted:
            b = inv.get_book()
            data.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'isBorrowed': b.get_isBorrowed(),
                'stock': inv.get_stock(),
            })

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
        if inv.get_book().get_isBorrowed():
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
        if buscar_binario is None:
            raise ImportError("Required algorithm `buscar_binario` not found in utils.algoritmos/busqueda_binaria")

        try:
            result = buscar_binario(self.inventory_sorted, isbn, lambda inv: inv.get_book().get_ISBNCode())
        except TypeError:
            result = buscar_binario(self.inventory_sorted, isbn)

        if result is None:
            return []
        if isinstance(result, list):
            return result
        return [result]

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
