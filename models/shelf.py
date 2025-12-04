from typing import List, Optional, Dict, Any
from .Books import Book


class Shelf:
    """Model representing a physical shelf that stores books in the library.

    This model implements a lightweight data holder pattern where the shelf serves
    as a container for book objects with enforced capacity constraints. Business
    logic for operations (adding/removing books, validation) is delegated to the
    service layer, while the model focuses on data integrity and basic validation.
    
    Design Philosophy:
        - Model as Data Holder: The shelf stores metadata and a collection of Books
        - Validation at Model Level: Capacity constraints are enforced here because
          they represent physical properties of a real shelf
        - Business Rules in Service: Complex operations like "can this book fit?"
          or "which books to remove?" belong in ShelfService
    
    Physical Constraints:
        According to project requirements, a physical library shelf has:
        - Maximum capacity: 8.0 kg (MAX_CAPACITY constant)
        - Current capacity: Sum of weights of all books currently on the shelf
        - Available capacity: MAX_CAPACITY - current_capacity
    
    Attributes:
        MAX_CAPACITY (float): Class constant defining maximum weight capacity (8.0 kg)
        __id (str): Unique identifier for the shelf (immutable after creation)
        __name (str): Optional human-readable name (e.g., "Fiction Section A1")
        __capacity (float): Maximum allowed weight for this shelf instance
        __books (List[Book]): Collection of Book objects currently on the shelf
    
    Example:
        >>> from models.Books import Book
        >>> shelf = Shelf(id="S001", capacity=8.0)
        >>> shelf.set_name("Science Fiction")
        >>> book = Book("B001", "978-123", "Title", "Author", 1.5, 25000, False)
        >>> # Adding books handled by ShelfService
        >>> shelf.current_capacity()
        0.0
        >>> shelf.capacity
        8.0
    
    Note:
        Book objects are stored as a simple list. The service layer (ShelfService)
        is responsible for manipulating this list with proper validation and
        business rule enforcement.
    """

    # maximum allowed capacity per project requirement
    MAX_CAPACITY: float = 8.0

    def __init__(self, id: str, books: Optional[List[Book]] = None, capacity: float = 8.0):
        """Initialize a new Shelf instance with validation.
        
        Creates a shelf object with a unique identifier, optional initial books,
        and a specified maximum capacity. The capacity is validated against the
        MAX_CAPACITY constant (8.0 kg) and must be positive.
        
        Validation Rules:
            - capacity must be > 0 (shelves can't have zero or negative capacity)
            - capacity must be <= MAX_CAPACITY (8.0 kg per project requirements)
            - id is required and becomes immutable after creation
            - books list defaults to empty if not provided
        
        Design Decisions:
            - ID is stored but has no setter (immutable) to maintain referential integrity
            - Books are stored as-is; the service layer handles book manipulation
            - Capacity validation happens immediately to fail fast on invalid data
        
        Args:
            id (str): Unique identifier for the shelf. Required. Should be unique
                across all shelves in the library system.
            books (Optional[List[Book]], optional): Initial list of Book objects
                to place on the shelf. Defaults to None (creates empty list).
            capacity (float, optional): Maximum weight capacity in kilograms.
                Must be > 0 and <= MAX_CAPACITY (8.0). Defaults to 8.0.

        Returns:
            None

        Raises:
            ValueError: If capacity exceeds MAX_CAPACITY (8.0 kg).
            ValueError: If capacity is <= 0.
            ValueError: If capacity cannot be converted to float.
        
        Side Effects:
            - Sets __name to empty string (can be set later via set_name)
        
        Example:
            >>> # Default capacity (8.0 kg)
            >>> shelf1 = Shelf(id="S001")
            >>> shelf1.capacity
            8.0
            >>> 
            >>> # Custom capacity
            >>> shelf2 = Shelf(id="S002", capacity=5.0)
            >>> shelf2.capacity
            5.0
            >>> 
            >>> # With initial books
            >>> books = [book1, book2]
            >>> shelf3 = Shelf(id="S003", books=books, capacity=8.0)
            >>> len(shelf3._Shelf__books)
            2
            >>> 
            >>> # Invalid capacity (too high)
            >>> shelf4 = Shelf(id="S004", capacity=10.0)  # Raises ValueError
            >>> 
            >>> # Invalid capacity (negative)
            >>> shelf5 = Shelf(id="S005", capacity=-1.0)  # Raises ValueError
        """
        # private attributes
        self.__id: str = id
        # store books as a simple list; service layer will manipulate it
        self.__books: List[Book] = books if books is not None else []
        # enforce numeric storage and basic validation on construction
        self.__capacity: float = float(capacity)
        if self.__capacity > self.MAX_CAPACITY:
            raise ValueError(f"capacity cannot exceed {self.MAX_CAPACITY} kg")
        if self.__capacity <= 0:
            raise ValueError("capacity must be a positive number")

        # optional human-readable name for the shelf (e.g., "Shelf A1")
        self.__name: str = ""

    # ID accessor (read-only, id should not be modified after creation)
    def get_id(self) -> str:
        """Return the immutable unique identifier of the shelf.
        
        The ID is set during construction and cannot be changed afterward,
        ensuring referential integrity throughout the system. This design
        prevents accidental ID modifications that could break relationships
        with other entities (e.g., inventory assignments).
        
        Design Decision:
            - No corresponding set_id() method exists intentionally
            - ID is private (__id) to enforce immutability
            - Services and repositories rely on stable IDs
        
        Args:
            None

        Returns:
            str: The unique identifier assigned during shelf creation.
        
        Example:
            >>> shelf = Shelf(id="S001")
            >>> shelf.get_id()
            'S001'
            >>> 
            >>> # ID cannot be changed
            >>> # shelf.set_id("S002")  # No such method exists
        
        See Also:
            - __init__: Where the ID is initially set
        """
        return self.__id

    # Name accessors (kept for backward compatibility with code that used them)
    def get_name(self) -> str:
        """Return the shelf's optional human-readable name.
        
        Provides an optional display name for the shelf (e.g., "Shelf A1",
        "Fiction Section - Top Row"). This is independent of the unique ID
        and defaults to an empty string if not set.
        
        Use Case:
            - UI display labels
            - User-friendly shelf identification
            - Reporting and administrative interfaces
        
        Args:
            None

        Returns:
            str: The human-readable name. Returns empty string "" if never set.
        
        Example:
            >>> shelf = Shelf(id="S001")
            >>> shelf.get_name()
            ''
            >>> shelf.set_name("Main Floor - A1")
            >>> shelf.get_name()
            'Main Floor - A1'
        
        See Also:
            - set_name: To assign a display name
            - get_id: For the immutable unique identifier
        """
        return self.__name

    def set_name(self, name: str) -> None:
        """Set a human-readable display name for the shelf.
        
        Assigns an optional descriptive name to the shelf for UI display
        and administrative purposes. Unlike the ID, the name can be changed
        at any time and has no uniqueness constraint.
        
        Common Naming Patterns:
            - Location-based: "Main Floor - A1", "Basement - C3"
            - Category-based: "Fiction Section", "Reference Materials"
            - Descriptive: "New Arrivals", "Staff Picks"
        
        Args:
            name (str): The display name to assign. Can be any string,
                including empty string to clear the name.

        Returns:
            None
        
        Side Effects:
            - Updates the private __name attribute
        
        Example:
            >>> shelf = Shelf(id="S001")
            >>> shelf.set_name("Fiction - Top Shelf")
            >>> shelf.get_name()
            'Fiction - Top Shelf'
            >>> 
            >>> # Name can be changed freely
            >>> shelf.set_name("Science Fiction")
            >>> shelf.get_name()
            'Science Fiction'
            >>> 
            >>> # Clear the name
            >>> shelf.set_name("")
            >>> shelf.get_name()
            ''
        
        See Also:
            - get_name: To retrieve the current name
        """
        self.__name = name

    # Capacity property with validation - centralises the business rule in the model
    @property
    def capacity(self) -> float:
        """Get the maximum weight capacity of the shelf in kilograms.
        
        Returns the shelf's maximum weight limit as defined during construction
        or modified via the setter. This represents the physical constraint
        of how much weight the shelf can safely hold.
        
        Physical Constraint:
            - All shelves are bound by MAX_CAPACITY (8.0 kg)
            - Actual capacity may be less but never more
            - Capacity is used to calculate remaining space via current_capacity()
        
        Args:
            None

        Returns:
            float: Maximum capacity in kilograms. Always > 0 and <= MAX_CAPACITY (8.0).
        
        Example:
            >>> shelf = Shelf(id="S001", capacity=5.0)
            >>> shelf.capacity
            5.0
            >>> 
            >>> # Default capacity
            >>> shelf2 = Shelf(id="S002")
            >>> shelf2.capacity
            8.0
        
        See Also:
            - capacity.setter: To modify the capacity
            - current_capacity: To calculate remaining available space
            - MAX_CAPACITY: Class-level constant defining the absolute maximum
        """
        return self.__capacity

    @capacity.setter
    def capacity(self, value: float) -> None:
        """Set the maximum weight capacity of the shelf with validation.
        
        Allows modifying the capacity after creation while enforcing business
        rules. This is primarily used by repositories when loading shelves from
        persistent storage with variable capacities.
        
        Validation Rules:
            - Must be convertible to float
            - Must be > 0 (shelves can't have zero capacity)
            - Must be <= MAX_CAPACITY (8.0 kg per project requirement)
        
        Use Cases:
            - Loading shelves from JSON files with stored capacities
            - Administrative capacity adjustments
            - Testing scenarios with different capacity constraints
        
        Args:
            value (float): The new maximum capacity in kilograms.
                Will be converted to float if numeric.

        Returns:
            None
        
        Raises:
            ValueError: If value exceeds MAX_CAPACITY (8.0 kg).
            ValueError: If value is <= 0.
            ValueError: If value cannot be converted to float.
        
        Side Effects:
            - Updates the private __capacity attribute
            - Does not check if current books exceed new capacity
              (service layer responsibility)
        
        Example:
            >>> shelf = Shelf(id="S001", capacity=8.0)
            >>> shelf.capacity
            8.0
            >>> 
            >>> # Reduce capacity
            >>> shelf.capacity = 5.0
            >>> shelf.capacity
            5.0
            >>> 
            >>> # Invalid: exceeds MAX_CAPACITY
            >>> shelf.capacity = 10.0  # Raises ValueError
            >>> 
            >>> # Invalid: negative capacity
            >>> shelf.capacity = -1.0  # Raises ValueError
            >>> 
            >>> # Invalid: zero capacity
            >>> shelf.capacity = 0.0  # Raises ValueError
        
        Note:
            This setter does NOT validate if existing books exceed the new
            capacity. That check is the responsibility of the service layer
            (ShelfService) to maintain separation of concerns.
        
        See Also:
            - capacity: Getter property
            - current_capacity: To check how much weight is currently on the shelf
        """
        val = float(value)
        if val > self.MAX_CAPACITY:
            raise ValueError(f"capacity cannot exceed {self.MAX_CAPACITY} kg")
        if val <= 0:
            raise ValueError("capacity must be a positive number")
        self.__capacity = val

    # Simple helpers for persistence/inspection. Services may still implement
    # richer (book-level) serialization if Book objects require special handling.
    def to_dict(self) -> Dict[str, Any]:
        """Serialize shelf data to a dictionary for JSON persistence.
        
        Converts the shelf object to a plain dictionary suitable for JSON
        serialization. This includes all shelf metadata and attempts to
        serialize contained books using their to_dict() method if available.
        
        Serialization Strategy:
            1. Try book.to_dict() if method exists (preferred)
            2. Fall back to book.__dict__ if available
            3. Fall back to str(book) as last resort
        
        The service layer can override or augment this strategy if needed.
        
        Fields Included:
            - id: Unique shelf identifier
            - name: Human-readable display name (may be empty)
            - capacity: Maximum weight capacity in kg
            - current_capacity: Current total weight of books on shelf
            - books: List of serialized book objects
        
        Args:
            None

        Returns:
            Dict[str, Any]: Dictionary with keys:
                - "id" (str): Shelf unique identifier
                - "name" (str): Display name or empty string
                - "capacity" (float): Maximum capacity in kg
                - "current_capacity" (float): Current weight in kg
                - "books" (List[Dict]): Serialized book objects
        
        Side Effects:
            None (read-only operation)
        
        Example:
            >>> book1 = Book(isbn="123", title="Test", weight=1.5)
            >>> shelf = Shelf(id="S001", books=[book1], capacity=8.0)
            >>> shelf.set_name("Main Shelf")
            >>> data = shelf.to_dict()
            >>> data['id']
            'S001'
            >>> data['name']
            'Main Shelf'
            >>> data['capacity']
            8.0
            >>> data['current_capacity']
            1.5
            >>> len(data['books'])
            1
        
        Note:
            The current_capacity field represents the current load in kg
            (sum of all book weights), calculated via current_capacity() method.
        
        See Also:
            - from_dict: Deserialize a shelf from dictionary
            - current_capacity: Calculate current weight on shelf
            - Book.to_dict: Book serialization method
        """
        books_serialized = []
        for b in self.__books:
            if hasattr(b, "to_dict"):
                books_serialized.append(b.to_dict())
            elif hasattr(b, "__dict__"):
                books_serialized.append(b.__dict__)
            else:
                books_serialized.append(str(b))

        return {
            "id": self.__id,
            "name": self.__name,
            "capacity": self.__capacity,
            # current_capacity representa la carga actual en kg (suma de pesos de los libros)
            "current_capacity": self.current_capacity(),
            "books": books_serialized,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shelf":
        """Construct a Shelf instance from a dictionary (deserialization).
        
        Creates a new Shelf object from dictionary data produced by to_dict().
        This is the inverse operation of to_dict() and is used when loading
        shelves from JSON files.
        
        Important Design Decision:
            Reconstruction of Book objects from dictionaries is INTENTIONALLY
            left to the service layer (ShelfService), which has knowledge of
            the Book class and proper deserialization strategies. This method
            only restores shelf metadata and leaves the books list empty.
        
        The service layer should call this method and then populate books
        using its own Book reconstruction logic.
        
        Workflow:
            1. Extract capacity from dict (default to MAX_CAPACITY if missing)
            2. Create Shelf with empty books list
            3. Restore display name if present
            4. Service layer adds reconstructed Book objects separately
        
        Args:
            data (Dict[str, Any]): Dictionary with shelf data. Expected keys:
                - "id" (str, required): Unique shelf identifier
                - "capacity" (float, optional): Max capacity, defaults to MAX_CAPACITY (8.0)
                - "name" (str, optional): Display name, defaults to empty string
                - "books" (List, ignored): Book data handled by service layer

        Returns:
            Shelf: New Shelf instance with metadata restored but empty books list.
        
        Raises:
            ValueError: If capacity in data exceeds MAX_CAPACITY or is invalid.
            KeyError: If required "id" field is missing from data.
        
        Side Effects:
            None (creates new object without modifying existing state)
        
        Example:
            >>> # Basic deserialization
            >>> data = {"id": "S001", "capacity": 5.0, "name": "Main Shelf"}
            >>> shelf = Shelf.from_dict(data)
            >>> shelf.get_id()
            'S001'
            >>> shelf.capacity
            5.0
            >>> shelf.get_name()
            'Main Shelf'
            >>> len(shelf._Shelf__books)
            0
            >>> 
            >>> # Service layer would then add books
            >>> # shelf_service.add_books_to_shelf(shelf, reconstructed_books)
        
        Note:
            This separation of concerns ensures that the Shelf model doesn't
            have tight coupling to the Book class, maintaining clean architecture.
        
        See Also:
            - to_dict: Serialize shelf to dictionary
            - ShelfService: Handles full shelf reconstruction with books
        """
        cap = data.get("capacity", cls.MAX_CAPACITY)
        # keep books empty; service should rebuild Book instances if needed
        shelf = cls(id=data.get("id"), books=None, capacity=cap)
        shelf.set_name(data.get("name", ""))
        return shelf

    def __str__(self) -> str:
        """Return a human-readable string representation of the shelf.
        
        Provides a concise summary of the shelf's key attributes for debugging,
        logging, and display purposes. Includes ID, optional name, book count,
        and capacity.
        
        Format:
            "Shelf[ID: <id>, name: <name>, books: <count> items, capacity: <kg>kg]"
            
            If name is not set, the "name:" portion is omitted:
            "Shelf[ID: <id>, books: <count> items, capacity: <kg>kg]"
        
        Args:
            None

        Returns:
            str: Formatted string representation with shelf metadata.
        
        Example:
            >>> shelf = Shelf(id="S001", capacity=8.0)
            >>> str(shelf)
            'Shelf[ID: S001, books: 0 items, capacity: 8.0kg]'
            >>> 
            >>> shelf.set_name("Fiction")
            >>> str(shelf)
            'Shelf[ID: S001, name: Fiction, books: 0 items, capacity: 8.0kg]'
            >>> 
            >>> # With books
            >>> shelf = Shelf(id="S002", books=[book1, book2], capacity=5.0)
            >>> str(shelf)
            'Shelf[ID: S002, books: 2 items, capacity: 5.0kg]'
        
        See Also:
            - to_dict: For structured serialization
        """
        name_part = f", name: {self.__name}" if getattr(self, '_Shelf__name', None) else ""
        return f"Shelf[ID: {self.__id}{name_part}, books: {len(self.__books)} items, capacity: {self.__capacity}kg]"

    def current_capacity(self) -> float:
        """Calculate the current total weight of all books on the shelf.
        
        Iterates through all stored book objects and sums their weights to
        determine the current load on the shelf. This value is used to check
        if additional books can be added without exceeding the maximum capacity.
        
        Algorithm:
            For each book in self.__books:
                1. If book has get_weight() method, call it (Book instance)
                2. If book is a dict with 'weight' key, use that value
                3. Try numeric cast as last resort
                4. Skip book if none of the above work (silently ignore)
            Return sum of all parsable weights
        
        Weight Extraction Strategy:
            - Book instances: Calls book.get_weight() method
            - Dictionaries: Extracts data['weight'] field (default 0.0)
            - Numeric values: Direct float conversion
            - Other types: Ignored (no error raised)
        
        This flexible approach handles both Book objects and dictionary
        representations during deserialization workflows.
        
        Args:
            None

        Returns:
            float: Total weight in kilograms of all books currently on shelf.
                Returns 0.0 if shelf is empty or no books have parsable weights.
        
        Side Effects:
            None (read-only calculation)
        
        Example:
            >>> book1 = Book(isbn="111", title="Book1", weight=2.5)
            >>> book2 = Book(isbn="222", title="Book2", weight=1.5)
            >>> shelf = Shelf(id="S001", books=[book1, book2])
            >>> shelf.current_capacity()
            4.0
            >>> 
            >>> # Empty shelf
            >>> shelf2 = Shelf(id="S002")
            >>> shelf2.current_capacity()
            0.0
            >>> 
            >>> # With dictionary data (during deserialization)
            >>> dict_book = {"title": "Test", "weight": 3.0}
            >>> shelf3 = Shelf(id="S003")
            >>> shelf3._Shelf__books = [dict_book]
            >>> shelf3.current_capacity()
            3.0
        
        Note:
            This method silently ignores books that don't have parsable weight
            data rather than raising errors, ensuring robustness during data
            migration or when handling incomplete records.
        
        See Also:
            - capacity: Maximum allowed weight
            - to_dict: Includes current_capacity in serialization
            - ShelfService: Uses this to validate book additions
        """
        total = 0.0
        for b in self.__books:
            try:
                # Book instances expose get_weight(); dictionaries may include 'weight'
                if hasattr(b, 'get_weight'):
                    total += float(b.get_weight())
                elif isinstance(b, dict) and 'weight' in b:
                    total += float(b.get('weight', 0.0))
                else:
                    # try a numeric cast as a last resort
                    total += float(b)
            except Exception:
                # ignore unparseable entries
                continue
        return total
