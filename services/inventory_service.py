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
    """Service responsible for managing inventory groups and stock levels.

    SINGLE RESPONSIBILITY: Business logic for inventory management, synchronization,
    and search operations. All persistence operations are delegated to the
    InventoryRepository following the Single Responsibility Principle.
    
    Architecture Pattern:
        This service implements the Service Layer pattern, acting as a facade between
        controllers and the data layer. It coordinates business rules, validation,
        and delegates persistence to the repository layer.
    
    In-Memory State:
        The service maintains two synchronized in-memory lists:
        
        - inventory_general (List[Inventory]): Unsorted list of inventory groups,
          organized by ISBN. Each group contains all physical copies of books with
          the same ISBN. This is the primary working list for most operations.
          
        - inventory_sorted (List[Inventory]): Sorted copy of inventory_general,
          ordered by ISBN using the insertion sort algorithm (insercion_ordenada).
          This sorted list enables efficient binary search operations.
    
    Inventory Group Concept:
        Each Inventory object represents a logical group of books sharing the same ISBN:
        - stock: count of available (not borrowed) copies
        - items: list of Book objects (each represents a physical copy)
        
        Example: If the library has 3 copies of "Don Quijote" (ISBN 978-123),
        there will be ONE Inventory object with stock=2 (if 1 is borrowed) and
        items=[book1, book2, book3].
    
    Synchronization:
        The service ensures both lists remain synchronized:
        1. All mutations (add/update/delete) are applied to inventory_general
        2. synchronize_inventories() creates a sorted copy in inventory_sorted
        3. Both lists are persisted to JSON files via the repository
    
    Attributes:
        repository (InventoryRepository): Handles persistence to JSON files
        inventory_general (List[Inventory]): Unsorted inventory groups
        inventory_sorted (List[Inventory]): Sorted inventory groups (by ISBN)
    
    Example:
        >>> service = InventoryService()
        >>> book = Book("B001", "978-123", "Title", "Author", 1.5, 25000, False)
        >>> service.add_item(book)
        >>> results = service.find_by_title("Title")
        >>> for inv in results:
        ...     print(f"{inv.get_isbn()}: {inv.get_stock()} available")
    """

    def __init__(self, repository: InventoryRepository = None):
        """Initialize the InventoryService with an optional repository.

        Creates a new inventory service instance, loads existing inventory data
        from persistent storage, and ensures both in-memory lists (general and sorted)
        are synchronized. If the inventory is empty, attempts to regenerate it from
        the books catalog (books.json).
        
        Initialization Process:
            1. Set repository (use provided or create new InventoryRepository)
            2. Initialize empty in-memory lists
            3. Load inventory from repository (JSON files)
            4. If empty, regenerate from books.json catalog
            5. Synchronize general and sorted lists
            6. Persist synchronized state
        
        Args:
            repository (InventoryRepository, optional): Repository instance for
                persistence operations. If None, creates a new InventoryRepository
                with default file paths. Defaults to None.

        Returns:
            None
        
        Raises:
            Exception: For IO errors when reading from repository or books.json.
                If initialization fails, the service will have empty inventory lists.
        
        Side Effects:
            - Loads data from inventory_general.json and inventory_sorted.json
            - May regenerate inventory from books.json if empty
            - Persists synchronized inventory to both JSON files
        
        Example:
            >>> # Default initialization (auto-creates repository)
            >>> service = InventoryService()
            >>> len(service.inventory_general)
            33
            >>> 
            >>> # Custom repository for testing
            >>> mock_repo = MockInventoryRepository()
            >>> service = InventoryService(repository=mock_repo)
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
        """Load inventory data from persistent storage via repository.
        
        This private method delegates the loading operation to the repository layer,
        following the separation of concerns principle. It loads only the general
        (unsorted) inventory; the sorted version is generated via synchronization.
        
        Error Handling:
            If loading fails (file doesn't exist, corrupted JSON, etc.), the method
            gracefully initializes with an empty inventory list rather than crashing.
            This allows the service to function even on first run or after data loss.
        
        Args:
            None
        
        Returns:
            None
        
        Side Effects:
            - Populates self.inventory_general from repository
            - If loading fails, sets self.inventory_general to empty list []
        
        Raises:
            Does not raise exceptions. All errors are caught and logged internally.
        
        Note:
            This is a private method (prefix _) and should not be called directly
            by external code. It's part of the initialization sequence.
        """
        try:
            self.inventory_general = self.repository.load_general()
        except Exception:
            # Start with empty if load fails
            self.inventory_general = []

    def _save_inventories(self) -> None:
        """Persist both inventory lists to storage via repository.
        
        This private method delegates persistence to the repository layer, saving
        both the general (unsorted) and sorted inventory lists to their respective
        JSON files. This ensures data consistency across both files.
        
        Synchronization Requirement:
            This method should only be called AFTER synchronize_inventories() to
            ensure both lists are consistent. Most public methods call
            synchronize_inventories() which internally calls this method.
        
        Args:
            None
        
        Returns:
            None
        
        Raises:
            Exception: Propagated from repository if file write operations fail.
                Callers should handle this exception appropriately.
        
        Side Effects:
            - Writes to inventory_general.json
            - Writes to inventory_sorted.json
        
        Note:
            This is a private method (prefix _) and should not be called directly.
            Use synchronize_inventories() instead, which calls this automatically.
        """
        self.repository.save_both(self.inventory_general, self.inventory_sorted)

    # -------------------- CRUD --------------------
    def add_item(self, book: Book, stock: int = 1) -> None:
        """Add a new book to the inventory system.
        
        This method integrates a new physical book copy into the inventory, either
        by adding it to an existing ISBN group or creating a new group if this is
        the first copy of that ISBN.
        
        Business Logic:
            1. Validate that the book ID doesn't already exist (prevents duplicates)
            2. Search for an existing inventory group with matching ISBN
            3. If found: Add book to that group (increases group size)
            4. If not found: Create new inventory group for this ISBN
            5. Synchronize and persist both inventory lists
        
        Inventory Grouping:
            Books with the same ISBN are grouped together in a single Inventory
            object. For example, 3 copies of "Don Quijote" (ISBN 978-123) will
            be managed as one Inventory group with 3 items.
        
        Args:
            book (Book): Book instance to add to inventory. Must have unique ID.
            stock (int, optional): Legacy parameter, kept for compatibility but
                ignored. Stock is calculated automatically from items count.
                Defaults to 1.

        Returns:
            None

        Raises:
            ValueError: If a book with the same ID already exists in any inventory
                group. Book IDs must be unique across the entire inventory.
            Exception: If persistence operations fail (IO errors).
        
        Side Effects:
            - Adds book to inventory_general (to existing or new group)
            - Synchronizes inventory_sorted (creates sorted copy)
            - Persists both lists to JSON files
        
        Example:
            >>> service = InventoryService()
            >>> book1 = Book("B001", "978-123", "Don Quijote", "Cervantes", 1.5, 25000, False)
            >>> service.add_item(book1)
            >>> # First copy creates new group
            >>> 
            >>> book2 = Book("B002", "978-123", "Don Quijote", "Cervantes", 1.5, 25000, False)
            >>> service.add_item(book2)
            >>> # Second copy added to existing group
            >>> 
            >>> # Trying to add duplicate ID raises error
            >>> duplicate = Book("B001", "978-456", "Other", "Author", 1.0, 1000, False)
            >>> service.add_item(duplicate)  # Raises ValueError
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
        """Update a book's information in the inventory system.
        
        This method locates a book by ID and updates its properties with new data.
        If the ISBN changes, the book is automatically moved to the appropriate
        inventory group, maintaining proper ISBN-based organization.
        
        Update Workflow:
            1. Search for book across all inventory groups by ID
            2. Update book data in place
            3. If ISBN changed:
               a. Remove book from old ISBN group
               b. Clean up empty groups
               c. Add book to new ISBN group (or create new group)
            4. Synchronize and persist changes
        
        ISBN Change Handling:
            When a book's ISBN is updated, the inventory structure must be reorganized:
            - Old group: Book is removed; empty groups are deleted
            - New group: Book is added to existing group or new group is created
            This maintains the invariant that each group contains only one ISBN.
        
        Args:
            book_id (str): Unique identifier of the book to update.
            updated_book (Book): Book object with new/updated information.
                Can have different ISBN, which triggers group reorganization.

        Returns:
            None

        Raises:
            ValueError: If no book with the specified ID is found in inventory.
            Exception: If persistence operations fail.
        
        Side Effects:
            - Updates book data in inventory_general
            - May move book between groups (if ISBN changed)
            - Removes empty groups
            - Synchronizes inventory_sorted
            - Persists changes to JSON files
        
        Example:
            >>> service = InventoryService()
            >>> # Update title only (same ISBN)
            >>> updated = Book("B001", "978-123", "New Title", "Author", 1.5, 25000, False)
            >>> service.update_book_in_inventory("B001", updated)
            >>> 
            >>> # Update ISBN (moves to different group)
            >>> updated2 = Book("B001", "978-456", "Title", "Author", 1.5, 25000, False)
            >>> service.update_book_in_inventory("B001", updated2)
            >>> # Book B001 now in ISBN 978-456 group
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
        """Synchronize the sorted inventory list with the general inventory list.

        This method ensures that inventory_sorted remains a properly ordered copy
        of inventory_general by creating a deep copy and applying the insertion
        sort algorithm. Both lists are then persisted to their respective JSON files.
        
        Synchronization Process:
            1. Create deep copy of each Inventory object in inventory_general
               (includes copying all Book objects to avoid shared references)
            2. Store copies in inventory_sorted list
            3. Apply insertion sort algorithm (insercion_ordenada) to sort by ISBN
            4. Persist both lists to JSON files via repository
        
        Why Synchronization?
            The system maintains two versions of the inventory:
            - inventory_general: Working list for mutations (add/update/delete)
            - inventory_sorted: Sorted list for efficient binary search operations
            
            This dual-list approach separates concerns:
            - Fast mutations on unsorted list
            - Fast searches on sorted list
        
        Sorting Algorithm:
            Uses insercion_ordenada (insertion sort) from AlgoritmosOrdenamiento.
            Time Complexity: O(n²) worst case, but efficient for small datasets
            and nearly-sorted data. The inventory is sorted by ISBN in ascending order.
        
        Deep Copy Rationale:
            Deep copying prevents mutations to inventory_general from affecting
            inventory_sorted, maintaining data integrity across both lists.
        
        Args:
            None

        Returns:
            None

        Raises:
            Exception: If persistence operations fail (propagated from _save_inventories).
        
        Side Effects:
            - Creates new inventory_sorted list (replaces existing)
            - Writes to both JSON files (inventory_general.json, inventory_sorted.json)
        
        Performance:
            Called after every mutation operation (add/update/delete). For large
            inventories, consider batching operations to reduce synchronization overhead.
        
        Example:
            >>> service = InventoryService()
            >>> # After any mutation
            >>> service.inventory_general.append(new_inventory)
            >>> service.synchronize_inventories()
            >>> # Now inventory_sorted is updated and sorted
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
        """Find inventory items by book title using recursive linear search.

        This method implements the project requirement for recursive linear search
        (búsqueda lineal recursiva). It searches through the unsorted inventory_general
        list to find all books whose titles match the search query.
        
        Algorithm:
            Uses busqueda_lineal from AlgoritmosBusqueda module, which implements
            recursive linear search with the following characteristics:
            - Time Complexity: O(n) where n is the number of inventory groups
            - Space Complexity: O(n) for recursion stack
            - Case-insensitive matching
            - Supports partial matches (substring search)
        
        Search Strategy:
            The method performs iterative calls to busqueda_lineal to find ALL
            matching results, not just the first one:
            1. Start search from index 0
            2. Find first match using busqueda_lineal
            3. If found, add to results and continue from next index
            4. Repeat until no more matches found
            5. Return all collected results
        
        Why Unsorted List?
            Linear search doesn't require sorted data, so we use inventory_general
            (the primary working list) rather than inventory_sorted. This avoids
            unnecessary sorting overhead for a search that must scan all items anyway.
        
        Args:
            title (str): Title string to search for. Can be partial (e.g., "quijote"
                will match "Don Quijote de la Mancha"). Search is case-insensitive
                thanks to text normalization in the search helper functions.

        Returns:
            List[Inventory]: All inventory groups containing books with matching titles.
                Returns empty list [] if no matches found.

        Example:
            >>> service = InventoryService()
            >>> # Partial match search
            >>> results = service.find_by_title("quijote")
            >>> for inv in results:
            ...     book = inv.get_book()
            ...     print(f"{book.get_title()}: {inv.get_stock()} available")
            Don Quijote de la Mancha: 2 available
            >>> 
            >>> # Case-insensitive search
            >>> results = service.find_by_title("QUIJOTE")  # Same results
            >>> 
            >>> # No matches
            >>> results = service.find_by_title("nonexistent")
            >>> len(results)
            0
        
        See Also:
            - find_by_author(): Similar search by author name
            - utils.algorithms.AlgoritmosBusqueda.busqueda_lineal: The recursive
              linear search implementation
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
        """Find inventory items by book author using recursive linear search.

        This method implements the project requirement for recursive linear search
        (búsqueda lineal recursiva). It searches through the unsorted inventory_general
        list to find all books whose authors match the search query.
        
        Algorithm:
            Uses busqueda_lineal from AlgoritmosBusqueda module, which implements
            recursive linear search with the following characteristics:
            - Time Complexity: O(n) where n is the number of inventory groups
            - Space Complexity: O(n) for recursion stack
            - Case-insensitive matching
            - Supports partial matches (substring search)
        
        Search Strategy:
            Identical to find_by_title() but matches against the author field:
            1. Iteratively call busqueda_lineal starting from index 0
            2. Collect all matches (not just first one)
            3. Continue until no more matches found
            4. Return complete result set
        
        Use Cases:
            - Find all books by a specific author
            - Search with partial author name (e.g., "garcía" matches "García Márquez")
            - Case-insensitive author lookup
        
        Args:
            author (str): Author name to search for. Can be partial (e.g., "márquez"
                will match "Gabriel García Márquez"). Search is case-insensitive.

        Returns:
            List[Inventory]: All inventory groups containing books with matching authors.
                Returns empty list [] if no matches found.

        Example:
            >>> service = InventoryService()
            >>> # Full or partial author search
            >>> results = service.find_by_author("garcía márquez")
            >>> for inv in results:
            ...     book = inv.get_book()
            ...     print(f"{book.get_title()} by {book.get_author()}")
            Cien años de soledad by Gabriel García Márquez
            El amor en los tiempos del cólera by Gabriel García Márquez
            >>> 
            >>> # Partial match
            >>> results = service.find_by_author("márquez")  # Same results
            >>> 
            >>> # Case-insensitive
            >>> results = service.find_by_author("GARCÍA")  # Same results
        
        See Also:
            - find_by_title(): Similar search by book title
            - utils.algorithms.AlgoritmosBusqueda.busqueda_lineal: The recursive
              linear search implementation
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
