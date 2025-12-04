"""Shelf Repository - Persistence Layer for Library Shelves.

This module implements the Repository Pattern for shelf entities, providing
a clean abstraction layer between the business logic (services) and data
storage (JSON files). It handles bidirectional conversion between Shelf
objects and dictionary representations for JSON serialization.

Architecture:
    The repository follows the same pattern as book_repository, delegating
    low-level file operations to BaseRepository and JSONFileHandler while
    providing shelf-specific conversion logic.

Key Components:
    - _shelf_from_dict: Deserializes JSON data into Shelf objects with Books
    - _shelf_to_dict: Serializes Shelf objects into JSON-compatible dicts
    - ShelfRepository: Main repository class for CRUD operations

Data Flow:
    Load:  JSON File → JSONFileHandler → dict → _shelf_from_dict → Shelf
    Save:  Shelf → _shelf_to_dict → dict → JSONFileHandler → JSON File

Design Decisions:
    - Book reconstruction is handled HERE (unlike Shelf.from_dict which leaves
      it to the service layer), ensuring complete shelf restoration from storage
    - Fault tolerance: Malformed book entries are skipped rather than failing
      the entire shelf load operation
    - Uses BaseRepository for consistent error handling and file operations

Default Storage:
    File: shelves.json (configured in utils.config.FilePaths.SHELVES)
    Format: JSON array of shelf objects with embedded book arrays

Example JSON Structure:
    [
        {
            "id": "S001",
            "name": "Fiction Section",
            "capacity": 8.0,
            "books": [
                {
                    "id": "B001",
                    "ISBNCode": "978-0-123456-78-9",
                    "title": "Example Book",
                    "author": "John Doe",
                    "weight": 1.5,
                    "price": 29.99,
                    "isBorrowed": false
                }
            ]
        }
    ]

See Also:
    - repositories.base_repository: Base CRUD operations
    - models.shelf: Shelf domain model
    - models.Books: Book domain model
    - utils.file_handler: Low-level JSON file operations
"""

from typing import List
from models.shelf import Shelf
from models.Books import Book
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _shelf_from_dict(data: dict) -> Shelf:
    """Deserialize a dictionary into a Shelf object with full Book reconstruction.
    
    Converts JSON dictionary data (typically from shelves.json) into a complete
    Shelf instance with all contained books reconstructed as Book objects.
    
    Design Philosophy:
        Unlike Shelf.from_dict() which leaves book reconstruction to the service
        layer, THIS function handles complete deserialization including books.
        This is appropriate for the repository layer, which is responsible for
        translating between storage format and domain objects.
    
    Fault Tolerance Strategy:
        Individual malformed book entries are SKIPPED rather than causing the
        entire shelf load to fail. This ensures data resilience:
        - Missing required fields (id, ISBNCode, title) → skip book
        - Type errors during Book construction → skip book
        - Non-dict entries in books array → skip entry
        
        The shelf itself is still created successfully with whatever books
        could be reconstructed.
    
    Algorithm:
        1. Initialize empty books list
        2. For each entry in data['books']:
            a. Validate it's a dictionary
            b. Check for required fields (id, ISBNCode, title)
            c. Try to construct Book object with all fields
            d. Skip entry if any exception occurs
        3. Create Shelf with reconstructed books and capacity
        4. Set optional name if present
        5. Return complete Shelf instance
    
    Required Book Fields:
        - id: Unique book identifier
        - ISBNCode: ISBN standard code
        - title: Book title
    
    Optional Book Fields (with defaults):
        - author: Book author (None if missing)
        - weight: Physical weight in kg (None if missing)
        - price: Book price (None if missing)
        - isBorrowed: Loan status (False if missing)
    
    Args:
        data (dict): Dictionary with shelf data. Expected structure:
            {
                "id" (str): Shelf unique identifier
                "capacity" (float, optional): Max capacity, defaults to 8.0
                "name" (str, optional): Display name
                "books" (List[dict], optional): Array of book dictionaries
            }

    Returns:
        Shelf: Fully reconstructed Shelf instance with Book objects.
            Books list may be shorter than data['books'] if some entries
            were malformed and skipped.
    
    Side Effects:
        None (pure deserialization function)
    
    Example:
        >>> data = {
        ...     "id": "S001",
        ...     "capacity": 8.0,
        ...     "name": "Main Shelf",
        ...     "books": [
        ...         {
        ...             "id": "B001",
        ...             "ISBNCode": "978-0-123456-78-9",
        ...             "title": "Example Book",
        ...             "author": "John Doe",
        ...             "weight": 1.5,
        ...             "price": 29.99,
        ...             "isBorrowed": False
        ...         }
        ...     ]
        ... }
        >>> shelf = _shelf_from_dict(data)
        >>> shelf.get_id()
        'S001'
        >>> len(shelf._Shelf__books)
        1
        >>> 
        >>> # With malformed book (missing title) - book is skipped
        >>> data_bad = {
        ...     "id": "S002",
        ...     "books": [
        ...         {"id": "B001", "ISBNCode": "123"},  # Missing title
        ...         {"id": "B002", "ISBNCode": "456", "title": "Valid Book"}
        ...     ]
        ... }
        >>> shelf2 = _shelf_from_dict(data_bad)
        >>> len(shelf2._Shelf__books)  # Only 1 book (the valid one)
        1
    
    Note:
        This function is private (underscore prefix) and intended only for use
        by ShelfRepository. External code should use the repository methods.
    
    See Also:
        - _shelf_to_dict: Inverse operation (serialization)
        - Shelf.from_dict: Simpler deserialization without book reconstruction
        - Book.__init__: Book constructor with parameter details
    """
    books: List[Book] = []
    for bd in data.get('books', []) or []:
        # ignore non-dict entries quickly
        if not isinstance(bd, dict):
            continue
        # require minimal fields to consider a book valid
        if bd.get('id') is None or bd.get('ISBNCode') is None or bd.get('title') is None:
            # skip entries that lack essential information
            continue
        try:
            book = Book(
                bd.get('id'),
                bd.get('ISBNCode'),
                bd.get('title'),
                bd.get('author'),
                bd.get('weight'),
                bd.get('price'),
                bd.get('isBorrowed', False),
            )
            books.append(book)
        except Exception:
            # ignorar libro inválido pero continuar
            continue

    shelf = Shelf(data.get('id'), books=books, capacity=data.get('capacity', 8.0))
    if data.get('name') is not None:
        try:
            shelf.set_name(data.get('name', ''))
        except Exception:
            pass
    return shelf


def _shelf_to_dict(shelf: Shelf) -> dict:
    """Serialize a Shelf object into a JSON-compatible dictionary.
    
    Converts a Shelf instance with all its contained books into a plain
    dictionary structure suitable for JSON serialization and file storage.
    
    Serialization Strategy (Priority Order):
        For each book in the shelf, try these approaches in order:
        
        1. **Getter Methods (Preferred)**: Use Book's getter methods to extract
           all fields individually. This is the most reliable approach.
           
        2. **to_dict Method (Fallback 1)**: If getters fail, try calling
           book.to_dict() if available.
           
        3. **__dict__ Attribute (Fallback 2)**: Use the object's __dict__
           to capture all attributes.
           
        4. **String Representation (Last Resort)**: Convert to string using
           str(book) to preserve some information.
    
    This multi-level fallback ensures robustness even with partially
    initialized or non-standard Book objects.
    
    Output Structure:
        {
            "id": <shelf_id>,
            "name": <display_name>,
            "capacity": <max_capacity_kg>,
            "books": [
                {
                    "id": <book_id>,
                    "ISBNCode": <isbn>,
                    "title": <title>,
                    "author": <author>,
                    "weight": <weight_kg>,
                    "price": <price>,
                    "isBorrowed": <loan_status>
                },
                ...
            ]
        }
    
    Args:
        shelf (Shelf): The Shelf instance to serialize.

    Returns:
        dict: JSON-serializable dictionary with complete shelf data including
            all metadata and serialized books array.
    
    Side Effects:
        None (read-only serialization)
    
    Example:
        >>> book1 = Book("B001", "978-0-123456-78-9", "Example", "Author", 1.5, 29.99, False)
        >>> shelf = Shelf(id="S001", books=[book1], capacity=8.0)
        >>> shelf.set_name("Main Shelf")
        >>> data = _shelf_to_dict(shelf)
        >>> data['id']
        'S001'
        >>> data['name']
        'Main Shelf'
        >>> data['capacity']
        8.0
        >>> len(data['books'])
        1
        >>> data['books'][0]['title']
        'Example'
    
    Implementation Details:
        - Accesses private __books attribute via getattr for compatibility
        - Handles None/empty books list gracefully
        - Each book serialization is wrapped in try-except to prevent one
          malformed book from breaking the entire shelf serialization
    
    Note:
        This function is private (underscore prefix) and intended only for use
        by ShelfRepository. External code should use repository.save() or
        repository.save_all().
    
    See Also:
        - _shelf_from_dict: Inverse operation (deserialization)
        - Shelf.to_dict: Alternative serialization method in the model
        - Book getter methods: get_id, get_ISBNCode, get_title, etc.
    """
    books_serialized = []
    books_list = getattr(shelf, '_Shelf__books', []) or []
    for b in books_list:
        try:
            books_serialized.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'isBorrowed': b.get_isBorrowed(),
            })
        except Exception:
            # Fallbacks: to_dict, __dict__, or str
            if hasattr(b, 'to_dict'):
                try:
                    books_serialized.append(b.to_dict())
                    continue
                except Exception:
                    pass
            if hasattr(b, '__dict__'):
                books_serialized.append(b.__dict__)
            else:
                books_serialized.append(str(b))

    return {
        'id': shelf.get_id(),
        'name': shelf.get_name(),
        'capacity': shelf.capacity,
        'books': books_serialized,
    }


class ShelfRepository(BaseRepository[Shelf]):
    """Repository for shelf entity persistence and retrieval operations.
    
    Provides a clean abstraction layer for all shelf-related data operations,
    implementing the Repository Pattern to separate business logic from data
    storage concerns.
    
    Inherits all CRUD operations from BaseRepository:
        - load(): Load all shelves from storage
        - save_all(shelves): Save complete list of shelves
        - find_by_id(shelf_id): Find specific shelf by ID
        - add(shelf): Add new shelf to storage
        - update(shelf): Update existing shelf
        - delete(shelf_id): Remove shelf from storage
    
    Default Storage Configuration:
        - File: shelves.json (utils.config.FilePaths.SHELVES)
        - Format: JSON array of shelf objects
        - Location: Typically in data/ directory
    
    Conversion Functions:
        - Uses _shelf_from_dict for deserialization (dict → Shelf)
        - Uses _shelf_to_dict for serialization (Shelf → dict)
    
    Data Integrity:
        - Maintains complete book objects within shelves
        - Handles malformed data gracefully (skips invalid books)
        - Preserves all shelf metadata (ID, name, capacity)
    
    Thread Safety:
        Not thread-safe. External synchronization required for concurrent access.
    
    Args:
        file_path (str, optional): Custom path to shelves JSON file.
            Defaults to None, which uses FilePaths.SHELVES.

    Attributes:
        Inherited from BaseRepository:
            - _file_path (str): Path to JSON storage file
            - _from_dict (Callable): Deserialization function
            - _to_dict (Callable): Serialization function
    
    Example:
        >>> # Using default file path
        >>> repo = ShelfRepository()
        >>> 
        >>> # Load all shelves
        >>> shelves = repo.load()
        >>> len(shelves)
        3
        >>> 
        >>> # Find specific shelf
        >>> shelf = repo.find_by_id("S001")
        >>> shelf.get_name()
        'Fiction Section'
        >>> 
        >>> # Add new shelf
        >>> new_shelf = Shelf(id="S004", capacity=8.0)
        >>> new_shelf.set_name("New Arrivals")
        >>> repo.add(new_shelf)
        >>> 
        >>> # Update existing shelf
        >>> shelf.set_name("Updated Fiction")
        >>> repo.update(shelf)
        >>> 
        >>> # Delete shelf
        >>> repo.delete("S004")
        >>> 
        >>> # Custom file path
        >>> test_repo = ShelfRepository(file_path="test_shelves.json")
    
    Typical Usage Pattern:
        ```python
        # In a service layer
        class ShelfService:
            def __init__(self):
                self.repo = ShelfRepository()
            
            def get_all_shelves(self):
                return self.repo.load()
            
            def add_shelf(self, shelf):
                # Business logic validation here
                if self.validate_shelf(shelf):
                    self.repo.add(shelf)
        ```
    
    Error Handling:
        - FileNotFoundError: If shelves.json doesn't exist (creates empty file)
        - JSONDecodeError: If file contains invalid JSON (logged, returns empty list)
        - ValueError: If shelf violates capacity constraints (raised by Shelf model)
    
    See Also:
        - repositories.base_repository.BaseRepository: Parent class with CRUD methods
        - models.shelf.Shelf: Domain model being persisted
        - utils.file_handler.JSONFileHandler: Low-level file operations
        - utils.config.FilePaths: Configuration for file paths
    """

    def __init__(self, file_path: str = None):
        path = file_path or FilePaths.SHELVES
        super().__init__(path, _shelf_from_dict, _shelf_to_dict)


__all__ = ['ShelfRepository']
