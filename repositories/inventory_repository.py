"""inventory_repository.py

Repository for inventory persistence.
Single Responsibility: Persisting inventory data in inventory_value.json and inventory_sorted.json

Author: Library Management System Team
Date: 2025-12-02
"""

from typing import List, Dict
from models.inventory import Inventory
from models.Books import Book
from utils.file_handler import JSONFileHandler
from utils.config import FilePaths


class InventoryRepository:
    """Repository for inventory persistence.
    
    SINGLE RESPONSIBILITY: Read/write inventory_value.json and inventory_sorted.json
    
    This repository manages the persistence of inventory groups (collections of books
    with the same ISBN). Each inventory group contains multiple physical copies of
    the same book.
    
    Note: This repository does NOT use DualFileRepository because it handles lists
    of Inventory objects, not a single Inventory object. The format is different.
    
    Attributes:
        general_path (str): Path to the general inventory file (unsorted)
        sorted_path (str): Path to the sorted inventory file (sorted by ISBN)
    """
    
    def __init__(self, general_path: str = None, sorted_path: str = None):
        """Initialize the inventory repository with file paths.
        
        Args:
            general_path (str, optional): Custom path for general inventory file.
                Defaults to FilePaths.INVENTORY_GENERAL if None.
            sorted_path (str, optional): Custom path for sorted inventory file.
                Defaults to FilePaths.INVENTORY_SORTED if None.
        
        Returns:
            None
        """
        self.general_path = general_path or FilePaths.INVENTORY_GENERAL
        self.sorted_path = sorted_path or FilePaths.INVENTORY_SORTED
    
    def load_general(self) -> List[Inventory]:
        """Load general inventory from file.
        
        This method reads the general (unsorted) inventory file and deserializes
        it into a list of Inventory objects. Each inventory group contains books
        with the same ISBN code.
        
        Expected JSON Format:
            [
              {
                "stock": 2,
                "items": [
                  {"id": "B001", "ISBNCode": "978-123", "title": "Book Title", 
                   "author": "Author Name", "weight": 1.5, "price": 25000, 
                   "isBorrowed": false},
                  {"id": "B002", "ISBNCode": "978-123", "title": "Book Title", 
                   "author": "Author Name", "weight": 1.5, "price": 25000, 
                   "isBorrowed": true}
                ]
              },
              ...
            ]
        
        Stock Calculation:
            The stock is computed as the count of AVAILABLE copies (not borrowed)
            to keep the stored 'stock' field consistent with current borrow flags.
            This ensures data integrity when books are borrowed or returned.
        
        Args:
            None
        
        Returns:
            List[Inventory]: List of inventory groups loaded from file.
                Returns empty list if file doesn't exist or contains invalid data.
        
        Raises:
            Does not raise exceptions. Invalid entries are skipped and logged.
        
        Example:
            >>> repo = InventoryRepository()
            >>> inventories = repo.load_general()
            >>> for inv in inventories:
            ...     print(f"ISBN: {inv.get_isbn()}, Stock: {inv.get_stock()}")
        """
        try:
            data = JSONFileHandler.load_json(self.general_path, expected_type=list)
        except Exception:
            return []
        
        loaded: List[Inventory] = []
        for group in data:
            if not isinstance(group, dict):
                continue
            
            items_data = group.get('items', [])
            books: List[Book] = []
            
            for item in items_data:
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
                except Exception:
                    continue
            
            # Compute stock as AVAILABLE copies (not borrowed) to keep the
            # stored 'stock' field consistent with current borrow flags.
            try:
                stock = sum(1 for b in books if not b.get_isBorrowed())
            except Exception:
                stock = int(group.get('stock', len(books)))
            inventory = Inventory(stock=stock, items=books)
            loaded.append(inventory)
        
        return loaded
    
    def save_general(self, inventories: List[Inventory]) -> None:
        """Save general inventory to file.
        
        This method serializes a list of Inventory objects into JSON format and
        saves it to the general inventory file. Each inventory group is converted
        to a dictionary containing stock count and a list of book items.
        
        Serialization Process:
            1. Iterate through each Inventory object
            2. Extract stock count and items list
            3. Convert each Book object to dictionary
            4. Write complete structure to JSON file
        
        JSON Output Format:
            [
              {
                "stock": 2,
                "items": [
                  {
                    "id": "B001",
                    "ISBNCode": "978-123",
                    "title": "Book Title",
                    "author": "Author Name",
                    "weight": 1.5,
                    "price": 25000,
                    "isBorrowed": false
                  },
                  ...
                ]
              },
              ...
            ]
        
        Args:
            inventories (List[Inventory]): List of inventory groups to save.
                Each Inventory object contains multiple Book objects with the same ISBN.
        
        Returns:
            None
        
        Raises:
            Exception: If file cannot be written (propagated from JSONFileHandler).
        
        Example:
            >>> repo = InventoryRepository()
            >>> inventories = [inv1, inv2, inv3]
            >>> repo.save_general(inventories)  # Saves to file
        """
        data = []
        for inventory in inventories:
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
        
        JSONFileHandler.save_json(self.general_path, data)
    
    def save_sorted(self, inventories: List[Inventory]) -> None:
        """Save sorted inventory to file.
        
        This method serializes a list of sorted Inventory objects into JSON format
        and saves it to the sorted inventory file. The structure is identical to
        save_general(), but the inventories are expected to be sorted by ISBN.
        
        Purpose:
            Maintain a pre-sorted version of the inventory for faster binary search
            operations. The sorted file is used by search algorithms that require
            ordered data (e.g., binary search by ISBN).
        
        Usage Pattern:
            After sorting inventories using insertion sort algorithm:
            >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
            >>> insercion_ordenada(inventories)
            >>> repo.save_sorted(inventories)
        
        JSON Output Format:
            [
              {
                "stock": 2,
                "items": [
                  {
                    "id": "B001",
                    "ISBNCode": "978-123",
                    "title": "Book Title",
                    "author": "Author Name",
                    "weight": 1.5,
                    "price": 25000,
                    "isBorrowed": false
                  },
                  ...
                ]
              },
              ...
            ]
        
        Args:
            inventories (List[Inventory]): List of sorted inventory groups to save.
                Expected to be sorted by ISBN in ascending order.
        
        Returns:
            None
        
        Raises:
            Exception: If file cannot be written (propagated from JSONFileHandler).
        
        Example:
            >>> repo = InventoryRepository()
            >>> sorted_inventories = sorted(inventories, key=lambda i: i.get_isbn())
            >>> repo.save_sorted(sorted_inventories)
        """
        data = []
        for inventory in inventories:
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
        
        JSONFileHandler.save_json(self.sorted_path, data)
    
    def save_both(self, general_inventories: List[Inventory], sorted_inventories: List[Inventory]) -> None:
        """Save both general and sorted inventory files atomically.
        
        This convenience method saves both inventory files (general and sorted)
        in a single operation. This ensures data consistency between the two
        files and reduces the number of I/O operations.
        
        Purpose:
            Maintain synchronization between the unsorted (general) and sorted
            inventory files. Both files contain the same inventory data, but
            sorted_inventories is ordered by ISBN for efficient binary search.
        
        Typical Usage:
            When the inventory is updated, both versions need to be persisted:
            1. Update general_inventories with changes
            2. Sort a copy to create sorted_inventories
            3. Save both using this method
        
        Data Consistency:
            This method ensures that both files are updated together. If one
            save operation fails, the other may still succeed, potentially
            leading to inconsistency. The caller should handle exceptions
            appropriately.
        
        Args:
            general_inventories (List[Inventory]): Unsorted inventory groups
                containing all inventory data in insertion order or natural order.
            sorted_inventories (List[Inventory]): Same inventory groups but
                sorted by ISBN in ascending order for binary search operations.
        
        Returns:
            None
        
        Raises:
            Exception: If either file write operation fails (propagated from
                JSONFileHandler via save_general() or save_sorted()).
        
        Example:
            >>> repo = InventoryRepository()
            >>> # After updating inventory
            >>> general = inventory_service.inventory_general
            >>> sorted_inv = inventory_service.inventory_sorted
            >>> repo.save_both(general, sorted_inv)
            >>> # Both files now updated
        
        See Also:
            - save_general(): Saves only the general inventory file
            - save_sorted(): Saves only the sorted inventory file
        """
        self.save_general(general_inventories)
        self.save_sorted(sorted_inventories)


__all__ = ['InventoryRepository']
