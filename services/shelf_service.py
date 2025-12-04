"""Shelf Service - Business Logic Layer for Shelf Management.

This module implements the service layer for shelf-related operations in the
library management system, providing business logic for book placement,
capacity validation, and shelf lifecycle management.

Architecture - Service Layer Pattern:
    The service acts as an intermediary between controllers/UI and the data
    layer (repository), implementing business rules while delegating persistence
    operations to ShelfRepository.

Responsibilities (Single Responsibility Principle):
    BUSINESS LOGIC:
        - Book placement validation (weight capacity checks)
        - Capacity management and remaining space calculations
        - Book assignment tracking across shelves
        - Duplicate book prevention within shelves
        - Cross-shelf operations (moving books, clearing shelves)
    
    PERSISTENCE (Delegated to Repository):
        - All file I/O operations handled by ShelfRepository
        - Service only calls repository.load_all() and repository.save_all()

Key Operations:
    - Shelf Lifecycle: create_shelf, list_shelves, find_shelf, set_capacity
    - Book Management: add_book, remove_book_by_isbn, move_book, clear_shelf
    - Capacity Checks: total_weight, remaining_capacity, can_add
    - Book Tracking: get_books, is_book_assigned, remove_book_from_all_shelves

Business Rules Enforced:
    1. Capacity Constraint: Books can't be added if total weight exceeds shelf capacity
    2. Uniqueness: No duplicate book IDs allowed within a single shelf
    3. Atomic Moves: Book moves between shelves are transactional (rollback on failure)
    4. Weight Validation: All weight calculations handle missing/invalid data gracefully

Data Flow:
    UI/Controller → ShelfService (business logic) → ShelfRepository (persistence)
    
    Example:
        add_book() → validates capacity → modifies shelf → calls _save_shelves()
                  → repository.save_all() → JSONFileHandler → shelves.json

Design Patterns:
    - Service Layer: Encapsulates business logic
    - Repository Pattern: Abstracts data access
    - Dependency Injection: Repository injected via constructor

Typical Usage:
    ```python
    # In a controller or UI component
    shelf_service = ShelfService()
    
    # Create new shelf
    shelf = shelf_service.create_shelf("S001", capacity=8.0, name="Fiction")
    
    # Add book with validation
    book = Book("B001", "978-0-123456-78-9", "Example", "Author", 1.5, 29.99)
    if shelf_service.can_add("S001", book):
        shelf_service.add_book("S001", book)
    
    # Check remaining space
    remaining = shelf_service.remaining_capacity("S001")
    ```

Thread Safety:
    Not thread-safe. External synchronization required for concurrent operations.

See Also:
    - repositories.shelf_repository.ShelfRepository: Persistence layer
    - models.shelf.Shelf: Domain model
    - models.Books.Book: Book domain model
"""

from typing import List, Optional

from models.shelf import Shelf
from models.Books import Book
from repositories.shelf_repository import ShelfRepository


class ShelfService:
	"""Service layer for shelf management and book placement operations.
	
	Provides high-level business logic for managing library shelves, including
	book placement with capacity validation, shelf operations, and book tracking
	across multiple shelves.
	
	Architecture:
		This service implements the Service Layer pattern, separating business
		rules from data persistence. All shelf data is managed in-memory with
		synchronization to persistent storage via ShelfRepository.
	
	Core Responsibilities:
		1. Book Placement Validation:
		   - Weight capacity checks before adding books
		   - Duplicate book ID prevention
		   - Remaining capacity calculations
		
		2. Shelf Operations:
		   - Create/find shelves
		   - Add/remove books
		   - Move books between shelves (transactional)
		   - Clear all books from shelf
		
		3. Book Assignment Tracking:
		   - Check if book exists on any shelf
		   - Remove book from all shelves (cascade deletion)
		   - List all books on specific shelf
		
		4. Capacity Management:
		   - Calculate total weight on shelf
		   - Calculate remaining capacity
		   - Validate if book can be added
		   - Update shelf capacity limits
	
	Business Rules:
		- MAX_CAPACITY: 8.0 kg per shelf (enforced by Shelf model)
		- No duplicate book IDs within a shelf
		- Books can't be added if weight exceeds capacity
		- Move operations are atomic (rollback on failure)
	
	Data Management:
		- In-Memory: _shelves list maintains current state
		- Persistence: Automatic save after each modification via _save_shelves()
		- Loading: Shelves loaded from repository on initialization
	
	Attributes:
		repository (ShelfRepository): Persistence layer for shelf data
		_shelves (List[Shelf]): In-memory collection of all shelves
	
	Example:
		>>> # Initialize service
		>>> service = ShelfService()
		>>> 
		>>> # Create shelf
		>>> shelf = service.create_shelf("S001", capacity=8.0, name="Fiction")
		>>> 
		>>> # Add book with validation
		>>> book = Book("B001", "978-0-123", "Title", "Author", 2.5, 19.99)
		>>> success = service.add_book("S001", book)
		>>> success
		True
		>>> 
		>>> # Check capacity
		>>> service.total_weight("S001")
		2.5
		>>> service.remaining_capacity("S001")
		5.5
		>>> 
		>>> # Move book to another shelf
		>>> service.create_shelf("S002", capacity=8.0)
		>>> service.move_book("S001", "S002", "978-0-123")
		True
	
	See Also:
		- repositories.shelf_repository.ShelfRepository: Data persistence
		- models.shelf.Shelf: Domain model for shelves
		- models.Books.Book: Domain model for books
	"""

	def __init__(self, repository: ShelfRepository = None, shelves: Optional[List[Shelf]] = None):
		"""Initialize ShelfService with repository and optional initial shelves.
		
		Sets up the service with a repository for persistence and optionally
		loads shelves from storage or accepts a pre-configured list.
		
		Dependency Injection:
			- Repository can be injected for testing or custom configurations
			- Shelves can be injected to bypass repository loading (testing)
		
		Initialization Workflow:
			1. Set repository (use provided or create default ShelfRepository)
			2. If shelves provided: use them directly (testing mode)
			3. If shelves None: load from repository (normal mode)
		
		Use Cases:
			- Production: ShelfService() - uses default repository and loads data
			- Testing: ShelfService(repository=mock_repo, shelves=[]) - full control
			- Custom Storage: ShelfService(repository=ShelfRepository("custom.json"))
		
		Args:
			repository (ShelfRepository, optional): Repository instance for persistence.
				Defaults to None, which creates a new ShelfRepository() with default
				file path (shelves.json).
			shelves (Optional[List[Shelf]], optional): Initial list of Shelf objects.
				Defaults to None, which triggers loading from repository.
				Provide empty list [] for testing without persistence.

		Returns:
			None
		
		Side Effects:
			- If shelves is None: Reads from persistent storage via repository.load_all()
			- Creates repository instance if not provided
		
		Example:
			>>> # Default initialization (production)
			>>> service = ShelfService()
			>>> # Shelves loaded from shelves.json
			>>> 
			>>> # Testing with empty shelves
			>>> test_service = ShelfService(shelves=[])
			>>> len(test_service.list_shelves())
			0
			>>> 
			>>> # Custom repository
			>>> custom_repo = ShelfRepository(file_path="test_shelves.json")
			>>> service = ShelfService(repository=custom_repo)
			>>> 
			>>> # Pre-configured shelves (testing)
			>>> shelf1 = Shelf("S001", capacity=8.0)
			>>> service = ShelfService(shelves=[shelf1])
			>>> len(service.list_shelves())
			1
		
		See Also:
			- _load_shelves: Method that loads from repository
			- ShelfRepository: Persistence layer
		"""
		self.repository = repository or ShelfRepository()
		self._shelves: List[Shelf] = shelves if shelves is not None else []
		if shelves is None:
			self._load_shelves()

	def create_shelf(self, id, capacity: float = 8.0, books: Optional[List[Book]] = None, name: Optional[str] = None) -> Shelf:
		"""Create and register a new shelf in the system.
		
		Creates a new Shelf instance, adds it to the in-memory collection,
		and persists it to storage. The shelf is immediately available for
		book placement operations.
		
		Workflow:
			1. Create Shelf instance with provided parameters
			2. Set optional name if provided
			3. Add to in-memory _shelves list
			4. Persist to storage via _save_shelves()
			5. Return created shelf
		
		Validation:
			- Capacity validated by Shelf model (must be > 0 and <= 8.0 kg)
			- No duplicate ID check performed (caller's responsibility)
			- Books validated during Shelf construction
		
		Args:
			id: Unique identifier for the shelf. Should be unique across all shelves,
				but this method doesn't enforce uniqueness.
			capacity (float, optional): Maximum weight capacity in kilograms.
				Must be > 0 and <= Shelf.MAX_CAPACITY (8.0). Defaults to 8.0.
			books (Optional[List[Book]], optional): Initial list of Book objects
				to place on the shelf. Defaults to None (empty shelf).
			name (Optional[str], optional): Human-readable display name for the shelf.
				Defaults to None (empty name).

		Returns:
			Shelf: The newly created and persisted Shelf instance.
		
		Raises:
			ValueError: If capacity exceeds Shelf.MAX_CAPACITY (8.0 kg).
			ValueError: If capacity is <= 0.
		
		Side Effects:
			- Adds shelf to in-memory _shelves list
			- Persists all shelves to storage (shelves.json)
		
		Example:
			>>> service = ShelfService()
			>>> 
			>>> # Simple shelf
			>>> shelf1 = service.create_shelf("S001")
			>>> shelf1.get_id()
			'S001'
			>>> shelf1.capacity
			8.0
			>>> 
			>>> # Named shelf with custom capacity
			>>> shelf2 = service.create_shelf("S002", capacity=5.0, name="Fiction Section")
			>>> shelf2.get_name()
			'Fiction Section'
			>>> 
			>>> # Shelf with initial books
			>>> books = [book1, book2]
			>>> shelf3 = service.create_shelf("S003", books=books)
			>>> len(service.get_books("S003"))
			2
		
		Note:
			This method does not check for duplicate shelf IDs. Callers should
			ensure uniqueness by checking find_shelf() before creating.
		
		See Also:
			- find_shelf: Check if shelf ID already exists
			- list_shelves: View all existing shelves
		"""
		shelf = Shelf(id, books=books, capacity=capacity)
		if name is not None:
			shelf.set_name(name)
		self._shelves.append(shelf)
		self._save_shelves()
		return shelf

	def list_shelves(self) -> List[Shelf]:
		"""Return all registered shelves in the system.
		
		Provides access to the complete collection of shelves currently
		managed by the service. Returns a shallow copy to prevent external
		modification of the internal list.
		
		Args:
			None

		Returns:
			List[Shelf]: Copy of all Shelf instances. Returns empty list if
				no shelves exist.
		
		Side Effects:
			None (read-only operation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", name="Fiction")
			>>> service.create_shelf("S002", name="Non-Fiction")
			>>> shelves = service.list_shelves()
			>>> len(shelves)
			2
			>>> [s.get_id() for s in shelves]
			['S001', 'S002']
		
		See Also:
			- find_shelf: Locate specific shelf by ID
			- create_shelf: Add new shelf to collection
		"""
		return list(self._shelves)

	def find_shelf(self, id) -> Optional[Shelf]:
		"""Find and return a shelf by its unique identifier.
		
		Performs a linear search through the shelves collection to locate
		a shelf with the matching ID.
		
		Algorithm:
			Linear Search - O(n) where n is the number of shelves
			Iterates through _shelves until match found or end reached
		
		Args:
			id: Shelf identifier to search for. Type should match the ID type
				used during shelf creation (typically str).

		Returns:
			Optional[Shelf]: The Shelf instance if found, None otherwise.
		
		Side Effects:
			None (read-only operation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", name="Fiction")
			>>> 
			>>> # Found
			>>> shelf = service.find_shelf("S001")
			>>> shelf.get_name()
			'Fiction'
			>>> 
			>>> # Not found
			>>> result = service.find_shelf("S999")
			>>> result is None
			True
		
		Note:
			For large shelf collections, consider implementing indexed lookup
			(dictionary) for O(1) access time.
		
		See Also:
			- list_shelves: Get all shelves
			- create_shelf: Add new shelf
		"""
		for s in self._shelves:
			if s.get_id() == id:
				return s
		return None

	def add_book(self, shelf_id, book: Book) -> bool:
		"""Add a book to a shelf with capacity and duplicate validation.
		
		Attempts to add a book to the specified shelf after performing business
		rule validation: capacity check and duplicate ID prevention.
		
		Validation Steps:
			1. Shelf Existence: Verify shelf_id exists
			2. Weight Extraction: Get book weight (handle exceptions)
			3. Capacity Check: Ensure total_weight + book_weight <= capacity
			4. Duplicate Check: Prevent books with duplicate IDs on same shelf
			5. Addition: Append book to shelf's book list
			6. Persistence: Save changes to storage
		
		Business Rules Enforced:
			- Cannot add book if it exceeds shelf capacity
			- Cannot add book with duplicate ID on same shelf
			- Book must have valid weight attribute
		
		Args:
			shelf_id: Identifier of the target shelf.
			book (Book): Book instance to add. Must have valid get_id() and
				get_weight() methods.

		Returns:
			bool: True if book was successfully added, False otherwise.
			
			Returns False if:
				- Shelf not found
				- Book weight cannot be extracted
				- Adding book would exceed capacity
				- Book ID already exists on shelf
		
		Side Effects:
			- Modifies shelf's internal books list on success
			- Persists all shelves to storage on success
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", capacity=8.0)
			>>> 
			>>> # Successful addition
			>>> book1 = Book("B001", "978-0-123", "Title", "Author", 2.0, 19.99)
			>>> service.add_book("S001", book1)
			True
			>>> 
			>>> # Duplicate ID - rejected
			>>> book2 = Book("B001", "978-0-456", "Other", "Author", 1.0, 15.99)
			>>> service.add_book("S001", book2)
			False
			>>> 
			>>> # Exceeds capacity - rejected
			>>> book3 = Book("B003", "978-0-789", "Heavy", "Author", 7.0, 49.99)
			>>> service.add_book("S001", book3)  # 2.0 + 7.0 > 8.0
			False
			>>> 
			>>> # Non-existent shelf
			>>> service.add_book("S999", book1)
			False
		
		Note:
			Use can_add() to check if a book fits before attempting to add,
			to provide user feedback without state changes.
		
		See Also:
			- can_add: Pre-check if book fits without modification
			- remove_book_by_isbn: Remove book from shelf
			- total_weight: Calculate current shelf weight
			- remaining_capacity: Check available space
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False

		# Validate capacity
		total = self.total_weight(shelf_id)
		capacity = shelf.capacity
		
		try:
			weight = book.get_weight()
		except Exception:
			return False

		if total + weight > capacity:
			return False

		# Prevent duplicate book IDs
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		book_id = book.get_id()
		
		for existing in books_list:
			if existing.get_id() == book_id:
				return False

		books_list.append(book)
		self._save_shelves()
		return True

	def remove_book_by_isbn(self, shelf_id, isbn: str) -> Optional[Book]:
		"""Remove and return the first book matching ISBN from the shelf.

		Args:
			shelf_id: Identifier of the shelf.
			isbn: ISBN code to match.

		Returns:
			The removed Book if found, otherwise None.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return None
			
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		for i, b in enumerate(books_list):
			if getattr(b, '_Book__ISBNCode', None) == isbn:
				removed = books_list.pop(i)
				self._save_shelves()
				return removed
		return None

	def total_weight(self, shelf_id) -> float:
		"""Calculate the total weight of all books currently on a shelf.
		
		Iterates through all books on the specified shelf and sums their
		weights, handling missing or invalid weight data gracefully.
		
		Algorithm:
			1. Find shelf by ID
			2. Access private __books list
			3. For each book, try to extract weight via get_weight()
			4. Skip books with invalid/missing weight (don't raise error)
			5. Return sum of all valid weights
		
		Fault Tolerance:
			- Books without get_weight() method: skipped
			- Books with non-numeric weight: skipped
			- Invalid shelf ID: returns 0.0
		
		Args:
			shelf_id: Identifier of the shelf to calculate weight for.

		Returns:
			float: Total weight in kilograms. Returns 0.0 if:
				- Shelf not found
				- Shelf has no books
				- All books have invalid weight data
		
		Side Effects:
			None (read-only calculation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001")
			>>> 
			>>> book1 = Book("B001", "978-0-123", "Book1", "Author", 2.5, 19.99)
			>>> book2 = Book("B002", "978-0-456", "Book2", "Author", 1.5, 15.99)
			>>> service.add_book("S001", book1)
			>>> service.add_book("S001", book2)
			>>> 
			>>> service.total_weight("S001")
			4.0
			>>> 
			>>> # Empty shelf
			>>> service.create_shelf("S002")
			>>> service.total_weight("S002")
			0.0
			>>> 
			>>> # Invalid shelf
			>>> service.total_weight("S999")
			0.0
		
		See Also:
			- remaining_capacity: Calculate available space
			- can_add: Check if book fits
			- Shelf.current_capacity: Alternative method in model
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return 0.0
			
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		total = 0.0
		for b in books_list:
			try:
				total += float(b.get_weight())
			except Exception:
				pass
		return total

	def remaining_capacity(self, shelf_id) -> float:
		"""Calculate the remaining weight capacity available on a shelf.
		
		Computes how much additional weight (in kg) can be added to the
		shelf before reaching its maximum capacity limit.
		
		Calculation:
			remaining_capacity = shelf.capacity - total_weight(shelf_id)
		
		Use Case:
			- UI display: Show users available space
			- Validation: Check before attempting to add books
			- Reporting: Shelf utilization statistics
		
		Args:
			shelf_id: Identifier of the shelf to check.

		Returns:
			float: Remaining capacity in kilograms. Returns 0.0 if shelf not found.
			
			Possible values:
				- Positive: Available space remaining
				- Zero: Shelf at full capacity
				- Negative: Shelf over capacity (should not occur with proper validation)
		
		Side Effects:
			None (read-only calculation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", capacity=8.0)
			>>> 
			>>> # Empty shelf
			>>> service.remaining_capacity("S001")
			8.0
			>>> 
			>>> # Add book (2.5 kg)
			>>> book = Book("B001", "978-0-123", "Title", "Author", 2.5, 19.99)
			>>> service.add_book("S001", book)
			>>> service.remaining_capacity("S001")
			5.5
			>>> 
			>>> # Invalid shelf
			>>> service.remaining_capacity("S999")
			0.0
		
		Note:
			Prefer using can_add() for validation checks, as it includes
			additional error handling for book weight extraction.
		
		See Also:
			- total_weight: Calculate current weight
			- can_add: Check if specific book fits
			- add_book: Add book with capacity validation
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return 0.0
		return shelf.capacity - self.total_weight(shelf_id)

	def can_add(self, shelf_id, book: Book) -> bool:
		"""Check if a book can be added to shelf without exceeding capacity.
		
		Validates whether adding a specific book would violate the shelf's
		weight capacity constraint. This is a read-only check that doesn't
		modify any state.
		
		Validation:
			1. Shelf exists
			2. Book has valid weight attribute
			3. remaining_capacity >= book_weight
		
		Use Case:
			- Pre-validation before attempting add_book()
			- UI feedback to show if book fits
			- Batch operations to filter compatible books
		
		Note:
			This method does NOT check for duplicate book IDs. Use add_book()
			for complete validation including duplicates.
		
		Args:
			shelf_id: Identifier of the shelf to check.
			book (Book): Book instance to validate. Must have get_weight() method.

		Returns:
			bool: True if book fits within remaining capacity, False if:
				- Shelf not found
				- Book weight cannot be extracted
				- Remaining capacity insufficient
		
		Side Effects:
			None (read-only validation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", capacity=8.0)
			>>> 
			>>> book1 = Book("B001", "978-0-123", "Book", "Author", 5.0, 29.99)
			>>> # Check before adding
			>>> if service.can_add("S001", book1):
			...     service.add_book("S001", book1)
			>>> 
			>>> # Too heavy
			>>> book2 = Book("B002", "978-0-456", "Heavy", "Author", 4.0, 39.99)
			>>> service.can_add("S001", book2)  # 5.0 + 4.0 > 8.0
			False
			>>> 
			>>> # Fits
			>>> book3 = Book("B003", "978-0-789", "Light", "Author", 2.0, 19.99)
			>>> service.can_add("S001", book3)  # 5.0 + 2.0 <= 8.0
			True
		
		See Also:
			- add_book: Actually add book with full validation
			- remaining_capacity: Get available space
			- total_weight: Get current weight
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False
		try:
			weight = float(book.get_weight())
		except Exception:
			return False
		return self.remaining_capacity(shelf_id) >= weight

	def get_books(self, shelf_id) -> List[Book]:
		"""Retrieve all books currently on a specific shelf.
		
		Returns a copy of the books list to prevent external modification
		of the shelf's internal state.
		
		Args:
			shelf_id: Identifier of the shelf to query.

		Returns:
			List[Book]: Copy of all Book instances on the shelf.
				Returns empty list if shelf not found.
		
		Side Effects:
			None (read-only operation)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001")
			>>> book1 = Book("B001", "978-0-123", "Title1", "Author", 1.5, 19.99)
			>>> book2 = Book("B002", "978-0-456", "Title2", "Author", 2.0, 24.99)
			>>> service.add_book("S001", book1)
			>>> service.add_book("S001", book2)
			>>> 
			>>> books = service.get_books("S001")
			>>> len(books)
			2
			>>> [b.get_title() for b in books]
			['Title1', 'Title2']
			>>> 
			>>> # Invalid shelf
			>>> service.get_books("S999")
			[]
		
		See Also:
			- add_book: Add book to shelf
			- remove_book_by_isbn: Remove book from shelf
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return []
		return list(getattr(shelf, '_Shelf__books'))

	def is_book_assigned(self, book_id: str) -> bool:
		"""Check if a book is currently assigned to any shelf in the system.
		
		Searches across all shelves to determine if a book with the given
		ID exists on any shelf. Useful for preventing deletion of books
		that are currently placed on shelves.
		
		Algorithm:
			Linear Search - O(n*m) where:
				n = number of shelves
				m = average books per shelf
			
			1. Iterate through all shelves
			2. For each shelf, iterate through books
			3. Match against book_id
			4. Return True on first match (early exit)
			5. Return False if no match found
		
		Use Case:
			- Validation before deleting books from library
			- Referential integrity checks
			- Reporting book locations
		
		Args:
			book_id (str): Book identifier to search for.

		Returns:
			bool: True if book is found on any shelf, False if book is not
				assigned to any shelf.
		
		Side Effects:
			None (read-only search)
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001")
			>>> service.create_shelf("S002")
			>>> 
			>>> book = Book("B001", "978-0-123", "Title", "Author", 1.5, 19.99)
			>>> service.add_book("S001", book)
			>>> 
			>>> # Book is assigned
			>>> service.is_book_assigned("B001")
			True
			>>> 
			>>> # Book not assigned
			>>> service.is_book_assigned("B999")
			False
			>>> 
			>>> # After removal
			>>> service.remove_book_by_isbn("S001", "978-0-123")
			>>> service.is_book_assigned("B001")
			False
		
		Note:
			This method checks by book ID, not ISBN. Multiple books with
			same ISBN but different IDs are treated as separate books.
		
		See Also:
			- remove_book_from_all_shelves: Remove book from all locations
			- get_books: Get all books on specific shelf
		"""
		for s in self._shelves:
			books = getattr(s, '_Shelf__books', [])
			for b in books:
				if b.get_id() == book_id:
					return True
		return False

	def clear_shelf(self, shelf_id) -> List[Book]:
		"""Remove all books from a shelf and return them.
		
		Clears the shelf by removing all books while preserving the shelf
		itself in the system. The removed books are returned for potential
		reassignment or other operations.
		
		Workflow:
			1. Find shelf by ID
			2. Create copy of books list
			3. Clear the original list
			4. Persist changes
			5. Return copied books
		
		Use Cases:
			- Shelf reorganization
			- Moving all books to different shelf
			- Preparing shelf for maintenance
			- Batch book operations
		
		Args:
			shelf_id: Identifier of the shelf to clear.

		Returns:
			List[Book]: List of all removed Book objects. Returns empty list
				if shelf not found or shelf was already empty.
		
		Side Effects:
			- Clears shelf's books list (sets to empty)
			- Persists changes to storage on success
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001")
			>>> book1 = Book("B001", "978-0-123", "Title1", "Author", 1.5, 19.99)
			>>> book2 = Book("B002", "978-0-456", "Title2", "Author", 2.0, 24.99)
			>>> service.add_book("S001", book1)
			>>> service.add_book("S001", book2)
			>>> 
			>>> # Clear shelf
			>>> removed = service.clear_shelf("S001")
			>>> len(removed)
			2
			>>> len(service.get_books("S001"))
			0
			>>> 
			>>> # Reassign books to another shelf
			>>> service.create_shelf("S002")
			>>> for book in removed:
			...     service.add_book("S002", book)
			>>> 
			>>> # Invalid shelf
			>>> service.clear_shelf("S999")
			[]
		
		Note:
			The shelf itself remains in the system with its capacity and
			other properties unchanged. Only the books are removed.
		
		See Also:
			- remove_book_by_isbn: Remove specific book
			- move_book: Move single book between shelves
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return []
			
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		removed = list(books_list)
		books_list.clear()
		self._save_shelves()
		return removed

	def move_book(self, from_shelf_id, to_shelf_id, isbn: str) -> bool:
		"""Move a book from one shelf to another with transactional rollback.
		
		Performs an atomic book transfer operation between two shelves. If
		the destination shelf cannot accept the book (capacity exceeded or
		other validation failure), the operation is rolled back and the book
		remains on the source shelf.
		
		Transactional Workflow:
			1. Remove book from source shelf by ISBN
			2. Attempt to add book to destination shelf
			3. If addition succeeds: commit and return True
			4. If addition fails: rollback (restore to source) and return False
		
		Validation (via add_book):
			- Destination shelf exists
			- Book weight doesn't exceed destination capacity
			- No duplicate book ID on destination shelf
		
		Rollback Guarantee:
			If destination addition fails, the book is restored to the source
			shelf's books list and changes are persisted. The operation is
			fully reversed.
		
		Args:
			from_shelf_id: Source shelf identifier where book currently resides.
			to_shelf_id: Destination shelf identifier where book should be moved.
			isbn (str): ISBN code of the book to move.

		Returns:
			bool: True if book was successfully moved to destination, False if:
				- Book not found on source shelf
				- Destination shelf not found
				- Destination shelf at capacity
				- Duplicate book ID on destination
				- Book weight invalid
		
		Side Effects:
			- On success: Book removed from source, added to destination, persisted
			- On failure: Book restored to source (if it was removed), persisted
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", capacity=8.0)
			>>> service.create_shelf("S002", capacity=8.0)
			>>> 
			>>> book = Book("B001", "978-0-123-45678-9", "Title", "Author", 2.5, 19.99)
			>>> service.add_book("S001", book)
			>>> 
			>>> # Successful move
			>>> service.move_book("S001", "S002", "978-0-123-45678-9")
			True
			>>> len(service.get_books("S001"))
			0
			>>> len(service.get_books("S002"))
			1
			>>> 
			>>> # Failed move (destination at capacity) - book stays on S002
			>>> service.create_shelf("S003", capacity=1.0)  # Too small
			>>> service.move_book("S002", "S003", "978-0-123-45678-9")
			False
			>>> len(service.get_books("S002"))  # Still on S002
			1
			>>> 
			>>> # Book not found on source
			>>> service.move_book("S001", "S002", "978-9-999-99999-9")
			False
		
		Note:
			The operation triggers two save operations in worst case:
			1. After removal from source (via remove_book_by_isbn)
			2. After rollback if destination add fails
			
			For better performance with batch moves, consider using clear_shelf
			and bulk add operations.
		
		See Also:
			- add_book: Validation logic for destination
			- remove_book_by_isbn: Removal from source
			- clear_shelf: Move all books at once
		"""
		book = self.remove_book_by_isbn(from_shelf_id, isbn)
		if book is None:
			return False
			
		if self.add_book(to_shelf_id, book):
			return True
			
		# Restore to source if destination fails
		src = self.find_shelf(from_shelf_id)
		if src is not None:
			getattr(src, '_Shelf__books').append(book)
			self._save_shelves()
		return False

	def set_capacity(self, shelf_id, capacity: float) -> bool:
		"""Update the maximum weight capacity of a shelf.
		
		Modifies the capacity limit of an existing shelf. The new capacity
		must adhere to the same validation rules as shelf creation.
		
		Validation (via Shelf.capacity setter):
			- Must be > 0 (positive number)
			- Must be <= Shelf.MAX_CAPACITY (8.0 kg)
			- Must be convertible to float
		
		Important:
			This method does NOT validate if existing books exceed the new
			capacity. It's possible to reduce capacity below current weight,
			resulting in an over-capacity shelf. Callers should check
			total_weight() before reducing capacity.
		
		Args:
			shelf_id: Identifier of the shelf to modify.
			capacity (float): New maximum capacity in kilograms.

		Returns:
			bool: True if capacity was updated successfully, False if:
				- Shelf not found
				- Capacity validation fails (> 8.0, <= 0, or invalid type)
		
		Side Effects:
			- Modifies shelf.capacity on success
			- Persists all shelves to storage on success
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001", capacity=8.0)
			>>> 
			>>> # Reduce capacity
			>>> service.set_capacity("S001", 5.0)
			True
			>>> shelf = service.find_shelf("S001")
			>>> shelf.capacity
			5.0
			>>> 
			>>> # Invalid: exceeds MAX_CAPACITY
			>>> service.set_capacity("S001", 10.0)
			False
			>>> 
			>>> # Invalid: zero capacity
			>>> service.set_capacity("S001", 0.0)
			False
			>>> 
			>>> # Invalid shelf
			>>> service.set_capacity("S999", 5.0)
			False
		
		Warning:
			Reducing capacity below current weight creates an over-capacity
			condition. Check total_weight() first:
			
			>>> if service.total_weight(shelf_id) <= new_capacity:
			...     service.set_capacity(shelf_id, new_capacity)
		
		See Also:
			- total_weight: Check current weight before reducing capacity
			- remaining_capacity: Calculate available space
			- Shelf.capacity: Model-level validation
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False
			
		try:
			shelf.capacity = float(capacity)
			self._save_shelves()
			return True
		except Exception:
			return False

	def remove_book_from_all_shelves(self, book_id: str) -> int:
		"""Remove a book from all shelves where it appears (cascade deletion).
		
		Searches through all shelves and removes every instance of a book
		matching the given book_id. This is typically used when deleting
		a book from the library system entirely.
		
		Use Cases:
			- Book deletion from library catalog
			- Referential integrity maintenance
			- Cleanup operations
			- Removing damaged/lost books from all locations
		
		Algorithm:
			1. For each shelf in system:
			   a. Get books list
			   b. Filter out books matching book_id (list comprehension)
			   c. If list length changed, increment counter
			2. If any books removed, persist changes
			3. Return count of affected shelves
		
		Complexity:
			O(n*m) where n = number of shelves, m = average books per shelf
		
		Args:
			book_id (str): Identifier of the book to remove from all shelves.

		Returns:
			int: Number of shelves from which the book was removed.
				Returns 0 if book not found on any shelf.
		
		Side Effects:
			- Modifies books lists on all affected shelves
			- Persists all shelves to storage if any changes made
		
		Example:
			>>> service = ShelfService()
			>>> service.create_shelf("S001")
			>>> service.create_shelf("S002")
			>>> service.create_shelf("S003")
			>>> 
			>>> book = Book("B001", "978-0-123", "Title", "Author", 1.5, 19.99)
			>>> service.add_book("S001", book)
			>>> service.add_book("S002", book)  # Same book on multiple shelves
			>>> 
			>>> # Remove from all shelves
			>>> count = service.remove_book_from_all_shelves("B001")
			>>> count
			2
			>>> 
			>>> # Verify removal
			>>> service.is_book_assigned("B001")
			False
			>>> 
			>>> # Book not found
			>>> service.remove_book_from_all_shelves("B999")
			0
		
		Note:
			This operation is more efficient than calling remove_book_by_isbn
			for each shelf individually, as it only triggers one save operation
			for all changes.
		
		See Also:
			- remove_book_by_isbn: Remove from specific shelf
			- is_book_assigned: Check if book exists on any shelf
		"""
		removed_count = 0
		for shelf in self._shelves:
			books_list: List[Book] = getattr(shelf, '_Shelf__books')
			# Find and remove all instances of the book
			original_length = len(books_list)
			books_list[:] = [b for b in books_list if b.get_id() != book_id]
			if len(books_list) < original_length:
				removed_count += 1
		
		if removed_count > 0:
			self._save_shelves()
		
		return removed_count

	# -------------------- Persistence (delegated to repository) --------------------

	def _load_shelves(self) -> None:
		"""Load all shelves from persistent storage into memory.
		
		Initializes the in-memory _shelves collection by loading data from
		the repository (typically shelves.json file). This method is called
		automatically during service initialization.
		
		Delegation:
			All file I/O and deserialization is handled by ShelfRepository,
			maintaining separation of concerns (SRP compliance).
		
		Workflow:
			1. Call repository.load_all()
			2. Repository reads JSON file
			3. Repository deserializes to Shelf objects (with Books)
			4. Assign result to _shelves
		
		Args:
			None

		Returns:
			None
		
		Side Effects:
			- Replaces _shelves list with data from storage
			- May read from disk via repository
		
		Error Handling:
			- File not found: Repository creates empty file, returns []
			- Invalid JSON: Repository logs error, returns []
			- Malformed shelf data: Repository skips invalid entries
		
		Example:
			>>> service = ShelfService()
			>>> # _load_shelves() called automatically in __init__
			>>> len(service._shelves)  # Contains loaded shelves
			3
		
		Note:
			This is a private method (underscore prefix) called only during
			initialization. Use list_shelves() to access shelves externally.
		
		See Also:
			- _save_shelves: Persist changes to storage
			- ShelfRepository.load_all: Underlying load operation
			- __init__: Automatic invocation during initialization
		"""
		self._shelves = self.repository.load_all()

	def _save_shelves(self) -> None:
		"""Persist all shelves from memory to storage.
		
		Saves the current state of all shelves to persistent storage
		(typically shelves.json file). This method is called automatically
		after any modification operation to ensure data consistency.
		
		Delegation:
			All file I/O and serialization is handled by ShelfRepository,
			maintaining separation of concerns (SRP compliance).
		
		Workflow:
			1. Call repository.save_all(_shelves)
			2. Repository serializes Shelf objects (with Books)
			3. Repository writes JSON to file
			4. File atomically updated
		
		Called After:
			- create_shelf: New shelf added
			- add_book: Book added to shelf
			- remove_book_by_isbn: Book removed from shelf
			- clear_shelf: All books removed
			- move_book: Book moved between shelves
			- set_capacity: Capacity modified
			- remove_book_from_all_shelves: Book removed from all locations
		
		Args:
			None

		Returns:
			None
		
		Side Effects:
			- Writes to disk via repository
			- Overwrites existing shelves.json file
		
		Error Handling:
			- Write permission errors: Logged by repository
			- Serialization errors: Logged by repository
		
		Example:
			>>> service = ShelfService()
			>>> shelf = service.create_shelf("S001")
			>>> # _save_shelves() called automatically
			>>> # Changes now persisted to shelves.json
		
		Note:
			This is a private method (underscore prefix) called automatically
			after modifications. Manual calls should not be necessary.
		
		See Also:
			- _load_shelves: Load from storage
			- ShelfRepository.save_all: Underlying save operation
		"""
		self.repository.save_all(self._shelves)


__all__ = ['ShelfService']

