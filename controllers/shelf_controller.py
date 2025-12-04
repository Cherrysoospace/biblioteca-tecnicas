"""Shelf Controller - Presentation Layer for Shelf Management.

This module implements the Controller layer in the MVC architecture, acting as
a thin coordination layer between the UI/presentation layer and the business
logic (ShelfService). It follows the Thin Controller pattern used consistently
throughout the project.

Architecture - Thin Controller Pattern:
    The controller is deliberately minimal, delegating all business logic to
    ShelfService while providing:
    - ID generation convenience (auto-increment S001, S002, etc.)
    - Basic error translation and safe defaults
    - Method forwarding with simplified signatures

Responsibilities:
    COORDINATION (Thin Layer):
        - Mediate between UI and ShelfService
        - Generate shelf IDs when not provided
        - Provide search functionality for UI convenience
        - Forward operations to service layer
        - Handle exceptions gracefully (return safe defaults)
    
    NOT RESPONSIBLE FOR:
        - Business logic (delegated to ShelfService)
        - Data persistence (delegated to ShelfRepository via service)
        - Data validation (delegated to models and service)

Design Philosophy:
    Following the project's architectural standard, this controller maintains
    a thin profile by avoiding business logic duplication. It acts purely as
    a coordination layer, making it easy to:
    - Replace the UI layer without touching business logic
    - Test business logic independently of presentation
    - Maintain clear separation of concerns

Key Features:
    - Automatic shelf ID generation (S001, S002, S003, ...)
    - Search functionality by shelf ID or name
    - Safe exception handling with conservative defaults
    - One-to-one method forwarding to service layer

Typical Usage:
    ```python
    # In a UI component (e.g., CustomTkinter view)
    controller = ShelfController()
    
    # Create shelf (ID auto-generated)
    shelf = controller.create_shelf(name="Fiction Section", capacity=8.0)
    
    # Search shelves for UI display
    results = controller.search_shelves("Fiction")
    
    # Add book with validation
    if controller.add_book(shelf.get_id(), book):
        print("Book added successfully")
    ```

Thread Safety:
    Not thread-safe. Delegates to ShelfService which is also not thread-safe.

See Also:
    - services.shelf_service.ShelfService: Business logic layer
    - models.shelf.Shelf: Domain model
    - repositories.shelf_repository.ShelfRepository: Persistence layer
"""

from typing import Optional, List

from services.shelf_service import ShelfService
from models.Books import Book


class ShelfController:
	"""Thin controller layer mediating between UI and ShelfService.
	
	Provides a simplified interface for UI components to interact with shelf
	management functionality, following the Thin Controller pattern used
	consistently throughout the project.
	
	Architectural Role:
		This controller sits between the presentation layer (UI) and the business
		logic layer (ShelfService), providing:
		- Convenience methods (ID generation, search)
		- Error handling with safe defaults
		- Simple method forwarding
		
		It does NOT contain business logic - all validation and operations are
		delegated to ShelfService.
	
	Design Principles:
		1. Thin Layer: Minimal logic, mostly delegation
		2. Safe Defaults: Exceptions caught and converted to safe return values
		3. Convenience: Auto-generate IDs, provide search functionality
		4. Stateless: Only holds reference to service (which manages state)
	
	Key Features:
		- Automatic Sequential ID Generation: S001, S002, S003, ...
		- Search: Filter shelves by ID or name (case-insensitive)
		- Error Safety: Graceful handling of edge cases
		- Direct Service Delegation: All operations forwarded to ShelfService
	
	Attributes:
		service (ShelfService): Service layer instance handling business logic
			and persistence operations.
	
	Example:
		>>> # Initialize controller
		>>> controller = ShelfController()
		>>> 
		>>> # Create shelf with auto-generated ID
		>>> shelf1 = controller.create_shelf(name="Fiction", capacity=8.0)
		>>> shelf1.get_id()
		'S001'
		>>> 
		>>> # Create another (ID increments)
		>>> shelf2 = controller.create_shelf(name="Science", capacity=8.0)
		>>> shelf2.get_id()
		'S002'
		>>> 
		>>> # Search shelves
		>>> results = controller.search_shelves("sci")
		>>> len(results)
		1
		>>> 
		>>> # Add book
		>>> book = Book("B001", "978-0-123", "Title", "Author", 2.5, 19.99)
		>>> controller.add_book("S001", book)
		True
	
	See Also:
		- services.shelf_service.ShelfService: Business logic implementation
		- models.shelf.Shelf: Domain model
	"""

	def __init__(self):
		"""Initialize the ShelfController with a new service instance.
		
		Creates a new ShelfService which automatically loads all existing
		shelves from persistent storage (shelves.json via FilePaths.SHELVES).
		No additional loading is required as the service handles this in its
		own initialization.
		
		Workflow:
			1. Create ShelfService instance
			2. Service.__init__ creates ShelfRepository
			3. Service.__init__ calls _load_shelves()
			4. Repository loads from shelves.json
			5. Service ready with loaded data
		
		Args:
			None

		Returns:
			None
		
		Side Effects:
			- Creates ShelfService instance
			- Triggers loading from persistent storage
		
		Example:
			>>> controller = ShelfController()
			>>> # Service automatically loaded
			>>> len(controller.list_shelves())
			3
		
		See Also:
			- ShelfService.__init__: Service initialization and loading
		"""
		self.service = ShelfService()

	def _generate_next_id(self) -> str:
		"""Generate the next sequential shelf ID in format SNNN.
		
		Scans all existing shelves to find the highest numeric ID (e.g., S005),
		then returns the next value (S006) with zero-padding to 3 digits.
		
		ID Format:
			- Prefix: 'S' (for Shelf)
			- Number: 3-digit zero-padded (001, 002, ..., 999)
			- Examples: S001, S002, S010, S100
		
		Algorithm:
			1. Initialize max_n = 0
			2. For each existing shelf:
			   a. Extract ID string
			   b. Check if starts with 'S' and has numeric suffix
			   c. Parse numeric part
			   d. Update max_n if higher
			3. Return f"S{max_n + 1:03d}"
		
		Edge Cases:
			- No existing shelves: Returns 'S001'
			- Non-standard IDs exist: Ignores them, only counts S### format
			- Gaps in sequence (S001, S003): Returns next from highest (S004)
			- Invalid ID formats: Skipped silently
		
		Args:
			None

		Returns:
			str: Next sequential shelf ID in format SNNN (e.g., 'S001', 'S042').
		
		Side Effects:
			None (read-only operation)
		
		Example:
			>>> controller = ShelfController()
			>>> # No shelves exist
			>>> controller._generate_next_id()
			'S001'
			>>> 
			>>> # Create some shelves
			>>> controller.create_shelf(id="S001")
			>>> controller.create_shelf(id="S002")
			>>> controller._generate_next_id()
			'S003'
			>>> 
			>>> # Gap in sequence
			>>> controller.create_shelf(id="S005")
			>>> controller._generate_next_id()
			'S006'
			>>> 
			>>> # Mixed formats (non-standard ignored)
			>>> controller.service._shelves.append(Shelf(id="CUSTOM-001"))
			>>> controller._generate_next_id()
			'S006'  # Ignores CUSTOM-001
		
		Note:
			This is a private method (underscore prefix) primarily used by
			create_shelf() when no ID is provided. The format is consistent
			with other entity ID patterns in the project (B### for books, etc.).
		
		See Also:
			- create_shelf: Uses this method for auto-ID generation
		"""
		max_n = 0
		for s in self.service.list_shelves():
			sid = s.get_id()
			if not isinstance(sid, str):
				continue
			if sid.startswith('S') and len(sid) > 1:
				numpart = sid[1:]
				if numpart.isdigit():
					try:
						n = int(numpart)
						if n > max_n:
							max_n = n
					except Exception:
						pass
		# next number, zero-padded to 3 digits
		next_n = max_n + 1
		return f"S{next_n:03d}"

	def create_shelf(self, id: Optional[str] = None, capacity: float = 8.0, books: Optional[List[Book]] = None, name: Optional[str] = None):
		"""Create and register a new shelf with optional auto-generated ID.
		
		Creates a new shelf in the system, automatically generating a sequential
		ID if not provided. This is the primary method for shelf creation from
		the UI layer.
		
		Convenience Feature - Auto ID:
			If `id` parameter is omitted or falsy, the controller automatically
			generates a sequential ID (S001, S002, etc.) by calling
			_generate_next_id(). This prevents UI components from needing to
			manage ID generation logic.
		
		Workflow:
			1. If id is None or empty: generate sequential ID
			2. Forward to service.create_shelf() with all parameters
			3. Service validates capacity and creates Shelf
			4. Service sets name if provided
			5. Service adds to collection and persists
			6. Return created Shelf object
		
		Args:
			id (Optional[str], optional): Shelf identifier. If None or empty,
				auto-generates sequential ID (S001, S002, ...). Defaults to None.
			capacity (float, optional): Maximum weight capacity in kilograms.
				Must be > 0 and <= 8.0. Defaults to 8.0.
			books (Optional[List[Book]], optional): Initial books to place on shelf.
				Defaults to None (empty shelf).
			name (Optional[str], optional): Human-readable display name.
				Defaults to None (empty name).

		Returns:
			Shelf: The newly created and persisted Shelf instance.
		
		Raises:
			ValueError: If capacity exceeds 8.0 kg or is <= 0 (raised by Shelf model).
		
		Side Effects:
			- Adds shelf to system
			- Persists to shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> 
			>>> # Auto-generated ID
			>>> shelf1 = controller.create_shelf(name="Fiction", capacity=8.0)
			>>> shelf1.get_id()
			'S001'
			>>> shelf1.get_name()
			'Fiction'
			>>> 
			>>> # Another auto-generated ID
			>>> shelf2 = controller.create_shelf(name="Science")
			>>> shelf2.get_id()
			'S002'
			>>> 
			>>> # Custom ID
			>>> shelf3 = controller.create_shelf(id="SPECIAL-001", name="Reference")
			>>> shelf3.get_id()
			'SPECIAL-001'
			>>> 
			>>> # With initial books
			>>> books = [book1, book2]
			>>> shelf4 = controller.create_shelf(books=books, name="New Arrivals")
			>>> len(controller.get_books(shelf4.get_id()))
			2
		
		Note:
			Auto-generated IDs are sequential based on existing shelves,
			not necessarily consecutive if shelves have been deleted.
		
		See Also:
			- _generate_next_id: ID generation logic
			- service.create_shelf: Business logic implementation
		"""
		if not id:
			# generate sequential id like S001, S002, ...
			id = self._generate_next_id()
		# pass the name into the service so it is set before persisting
		shelf = self.service.create_shelf(id, capacity=capacity, books=books, name=name)
		return shelf

	def list_shelves(self):
		"""Return all registered shelves in the system.
		
		Delegates directly to service layer to retrieve complete shelf collection.
		Useful for UI display, reporting, and shelf selection interfaces.
		
		Args:
			None

		Returns:
			List[Shelf]: List of all Shelf objects. Returns empty list if no shelves exist.
		
		Side Effects:
			None (read-only)
		
		Example:
			>>> controller = ShelfController()
			>>> shelves = controller.list_shelves()
			>>> for shelf in shelves:
			...     print(f"{shelf.get_id()}: {shelf.get_name()}")
			S001: Fiction
			S002: Science
			S003: Reference
		
		See Also:
			- find_shelf: Get specific shelf by ID
			- search_shelves: Filter shelves by search term
		"""
		return self.service.list_shelves()

	def find_shelf(self, id: str):
		"""Find and return a shelf by its unique identifier.
		
		Delegates to service layer for shelf lookup. Returns None if not found.
		
		Args:
			id (str): Shelf identifier to search for.

		Returns:
			Shelf | None: The Shelf instance if found, None otherwise.
		
		Side Effects:
			None (read-only)
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.find_shelf("S001")
			>>> if shelf:
			...     print(shelf.get_name())
			Fiction
			>>> 
			>>> # Not found
			>>> result = controller.find_shelf("S999")
			>>> result is None
			True
		
		See Also:
			- list_shelves: Get all shelves
			- search_shelves: Search by term
		"""
		return self.service.find_shelf(id)

	def search_shelves(self, search_term: str) -> List:
		"""Search and filter shelves by ID or name (case-insensitive).
		
		Provides UI-friendly search functionality to filter shelves based on
		a search term. Searches both shelf ID and name fields.
		
		Search Behavior:
			- Case-insensitive matching
			- Partial matches allowed (substring search)
			- Searches in both ID and name fields
			- Empty/whitespace term returns empty list
		
		Algorithm:
			1. Normalize search term (lowercase, strip whitespace)
			2. If empty, return []
			3. Get all shelves from service
			4. Filter: keep if term found in ID or name (case-insensitive)
			5. Return filtered list
		
		Use Cases:
			- UI search bar for shelf selection
			- Filtering shelf lists in admin interfaces
			- Auto-complete suggestions
		
		Args:
			search_term (str): Term to search for in shelf ID or name.
				Case-insensitive, partial matches allowed.

		Returns:
			List[Shelf]: List of matching Shelf objects. Returns empty list if:
				- search_term is empty or whitespace
				- No matches found
		
		Side Effects:
			None (read-only filter operation)
		
		Example:
			>>> controller = ShelfController()
			>>> controller.create_shelf(id="S001", name="Fiction Section")
			>>> controller.create_shelf(id="S002", name="Science Books")
			>>> controller.create_shelf(id="S003", name="Reference Materials")
			>>> 
			>>> # Search by name
			>>> results = controller.search_shelves("science")
			>>> len(results)
			1
			>>> results[0].get_name()
			'Science Books'
			>>> 
			>>> # Search by ID
			>>> results = controller.search_shelves("s00")
			>>> len(results)
			3
			>>> 
			>>> # Partial match in name
			>>> results = controller.search_shelves("tion")
			>>> [s.get_name() for s in results]
			['Fiction Section']
			>>> 
			>>> # No matches
			>>> results = controller.search_shelves("history")
			>>> len(results)
			0
			>>> 
			>>> # Empty term
			>>> results = controller.search_shelves("")
			>>> len(results)
			0
		
		Note:
			This is a controller-level convenience method not found in the
			service layer. It implements UI-specific functionality.
		
		See Also:
			- list_shelves: Get all shelves without filtering
			- find_shelf: Exact ID lookup
		"""
		if not search_term:
			return []
		
		search_term = search_term.lower().strip()
		all_shelves = self.service.list_shelves()
		
		filtered_shelves = [
			shelf for shelf in all_shelves
			if search_term in shelf.get_id().lower() or search_term in shelf.get_name().lower()
		]
		
		return filtered_shelves

	def add_book(self, shelf_id: str, book: Book) -> bool:
		"""Add a book to a shelf with capacity validation.
		
		Attempts to add a book to the specified shelf. Delegates to service
		layer which performs validation (capacity check, duplicate prevention).
		Changes are automatically persisted on success.
		
		Validation (via service):
			- Shelf exists
			- Book weight doesn't exceed remaining capacity
			- No duplicate book ID on shelf
		
		Args:
			shelf_id (str): Identifier of the target shelf.
			book (Book): Book instance to add.

		Returns:
			bool: True if book was successfully added and persisted,
				False if validation failed or shelf not found.
		
		Side Effects:
			- On success: Modifies shelf and persists to shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> controller.create_shelf(id="S001", capacity=8.0)
			>>> 
			>>> book = Book("B001", "978-0-123", "Title", "Author", 2.5, 19.99)
			>>> success = controller.add_book("S001", book)
			>>> success
			True
			>>> 
			>>> # Duplicate - rejected
			>>> success = controller.add_book("S001", book)
			>>> success
			False
		
		See Also:
			- service.add_book: Business logic and validation
			- remove_book: Remove book from shelf
		"""
		# service persists changes
		return self.service.add_book(shelf_id, book)

	def remove_book(self, shelf_id: str, isbn: str) -> Optional[Book]:
		"""Remove a book from a shelf by ISBN and return it.
		
		Removes the first book matching the given ISBN from the specified
		shelf. Changes are automatically persisted on success.
		
		Args:
			shelf_id (str): Identifier of the shelf.
			isbn (str): ISBN code of the book to remove.

		Returns:
			Optional[Book]: The removed Book instance if found and removed,
				None if shelf not found or book not on shelf.
		
		Side Effects:
			- On success: Modifies shelf and persists to shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.create_shelf(id="S001")
			>>> book = Book("B001", "978-0-123-45678-9", "Title", "Author", 1.5, 19.99)
			>>> controller.add_book("S001", book)
			>>> 
			>>> # Remove by ISBN
			>>> removed = controller.remove_book("S001", "978-0-123-45678-9")
			>>> removed.get_id()
			'B001'
			>>> 
			>>> # Not found
			>>> result = controller.remove_book("S001", "978-9-999-99999-9")
			>>> result is None
			True
		
		See Also:
			- service.remove_book_by_isbn: Business logic implementation
			- add_book: Add book to shelf
			- move_book: Move book between shelves
		"""
		# service persists changes
		return self.service.remove_book_by_isbn(shelf_id, isbn)

	def move_book(self, from_shelf_id: str, to_shelf_id: str, isbn: str) -> bool:
		"""Move a book from one shelf to another with transactional rollback.
		
		Attempts to move a book between shelves atomically. If the destination
		cannot accept the book, the operation is rolled back automatically.
		Changes are persisted on success.
		
		Transactional Behavior (via service):
			1. Remove from source shelf
			2. Try to add to destination shelf
			3. If fails: restore to source shelf
		
		Args:
			from_shelf_id (str): Source shelf identifier.
			to_shelf_id (str): Destination shelf identifier.
			isbn (str): ISBN code of the book to move.

		Returns:
			bool: True if move succeeded, False if:
				- Book not found on source shelf
				- Destination shelf doesn't exist
				- Destination at capacity
				- Duplicate book ID on destination
		
		Side Effects:
			- On success: Modifies both shelves and persists
			- On failure: Restores original state and persists
		
		Example:
			>>> controller = ShelfController()
			>>> controller.create_shelf(id="S001")
			>>> controller.create_shelf(id="S002")
			>>> 
			>>> book = Book("B001", "978-0-123", "Title", "Author", 2.0, 19.99)
			>>> controller.add_book("S001", book)
			>>> 
			>>> # Successful move
			>>> success = controller.move_book("S001", "S002", "978-0-123")
			>>> success
			True
		
		See Also:
			- service.move_book: Transactional implementation
			- add_book: Add to shelf
			- remove_book: Remove from shelf
		"""
		# service persists changes
		return self.service.move_book(from_shelf_id, to_shelf_id, isbn)

	def set_capacity(self, shelf_id: str, capacity: float) -> bool:
		"""Update a shelf's maximum weight capacity.
		
		Modifies the capacity limit for a shelf. Changes are persisted on success.
		
		Validation (via service/model):
			- Must be > 0
			- Must be <= 8.0 kg (Shelf.MAX_CAPACITY)
		
		Warning:
			Does not validate if current books exceed new capacity.
		
		Args:
			shelf_id (str): Identifier of the shelf to modify.
			capacity (float): New maximum capacity in kilograms.

		Returns:
			bool: True if capacity updated successfully, False if:
				- Shelf not found
				- Capacity validation fails
		
		Side Effects:
			- On success: Modifies shelf capacity and persists
		
		Example:
			>>> controller = ShelfController()
			>>> controller.create_shelf(id="S001", capacity=8.0)
			>>> 
			>>> success = controller.set_capacity("S001", 5.0)
			>>> success
			True
		
		See Also:
			- service.set_capacity: Business logic and validation
		"""
		# service persists changes
		return self.service.set_capacity(shelf_id, capacity)

	def get_books(self, shelf_id: str) -> List[Book]:
		"""Retrieve all books currently on a shelf.
		
		Returns a copy of the books list to prevent external modification.
		
		Args:
			shelf_id (str): Identifier of the shelf.

		Returns:
			List[Book]: List of Book instances on shelf.
				Returns empty list if shelf not found.
		
		Side Effects:
			None (read-only)
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.create_shelf(id="S001")
			>>> book1 = Book("B001", "978-0-123", "Title1", "Author", 1.5, 19.99)
			>>> controller.add_book("S001", book1)
			>>> 
			>>> books = controller.get_books("S001")
			>>> len(books)
			1
		
		See Also:
			- service.get_books: Service implementation
		"""
		return self.service.get_books(shelf_id)

	def is_book_assigned(self, book_id: str) -> bool:
		"""Check if a book is assigned to any shelf in the system.
		
		Delegates to service layer to check if book exists on any shelf.
		Useful for validation before deleting books from library.
		
		Error Handling:
			Returns True (conservative default) if any exception occurs during
			the check, preventing accidental deletion of potentially assigned books.
		
		Args:
			book_id (str): Book identifier to search for.

		Returns:
			bool: True if book found on any shelf or if error occurs,
				False if book definitely not assigned.
		
		Side Effects:
			None (read-only)
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.create_shelf(id="S001")
			>>> book = Book("B001", "978-0-123", "Title", "Author", 1.5, 19.99)
			>>> controller.add_book("S001", book)
			>>> 
			>>> # Book is assigned
			>>> controller.is_book_assigned("B001")
			True
			>>> 
			>>> # Book not assigned
			>>> controller.is_book_assigned("B999")
			False
		
		Note:
			The controller implements defensive error handling here,
			returning True on exceptions to prevent accidental deletions.
		
		See Also:
			- service.is_book_assigned: Actual search logic
		"""
		try:
			return self.service.is_book_assigned(book_id)
		except Exception:
			# conservative default
			return True

	def clear_shelf(self, shelf_id: str) -> List[Book]:
		"""Remove all books from a shelf and return them.
		
		Clears all books from the specified shelf while preserving the shelf
		itself. Changes are automatically persisted.
		
		Args:
			shelf_id (str): Identifier of the shelf to clear.

		Returns:
			List[Book]: List of all removed Book objects.
				Returns empty list if shelf not found.
		
		Side Effects:
			- On success: Clears shelf and persists to shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.create_shelf(id="S001")
			>>> controller.add_book("S001", book1)
			>>> controller.add_book("S001", book2)
			>>> 
			>>> removed = controller.clear_shelf("S001")
			>>> len(removed)
			2
			>>> len(controller.get_books("S001"))
			0
		
		See Also:
			- service.clear_shelf: Business logic implementation
			- remove_book: Remove single book
		"""
		# service persists changes
		return self.service.clear_shelf(shelf_id)

	def save_shelves(self, path: str) -> None:
		"""Explicitly persist all shelves to storage.
		
		Forces an immediate save of all shelves to the default storage location.
		This is typically not needed as modifications auto-persist, but can be
		useful for explicit save operations or data backup scenarios.
		
		Note:
			The `path` parameter is accepted for interface compatibility but
			currently ignored - saves always go to the default shelves.json
			configured in FilePaths.SHELVES.
		
		Args:
			path (str): Intended file path (currently ignored, uses default).

		Returns:
			None
		
		Raises:
			Exceptions from file I/O are propagated to caller.
		
		Side Effects:
			- Writes to shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> # ... make changes ...
			>>> controller.save_shelves("shelves.json")  # Force save
		
		See Also:
			- service._save_shelves: Underlying save operation
			- load_shelves: Load from storage
		"""
		# explicit save: delegate to service persistence helper
		self.service._save_shelves()

	def load_shelves(self, path: str) -> None:
		"""Reload shelves from persistent storage.
		
		Reloads all shelves from the default storage location, replacing
		the current in-memory collection. This is typically not needed as
		loading happens automatically during initialization.
		
		Warning:
			This will discard any unsaved changes in memory (though most
			operations auto-persist, so this is rarely an issue).
		
		Note:
			The `path` parameter is accepted for interface compatibility but
			currently ignored - loads always from the default shelves.json
			configured in FilePaths.SHELVES.
		
		Args:
			path (str): Intended file path (currently ignored, uses default).

		Returns:
			None
		
		Side Effects:
			- Replaces in-memory shelves with data from storage
			- Reads from shelves.json
		
		Example:
			>>> controller = ShelfController()
			>>> # ... shelves loaded automatically ...
			>>> controller.load_shelves("shelves.json")  # Force reload
		
		See Also:
			- service._load_shelves: Underlying load operation
			- save_shelves: Save to storage
		"""
		# load into service memory
		self.service._load_shelves()

	def delete_shelf(self, id: str) -> bool:
		"""Delete a shelf from the system by its identifier.
		
		Removes a shelf from the in-memory collection and persists the change
		to storage. The shelf must exist to be deleted.
		
		Warning:
			This operation does NOT check if books are on the shelf before
			deleting. Callers should verify the shelf is empty or clear it
			first to avoid losing book assignments.
		
		Recommended Pattern:
			```python
			# Safe deletion
			if len(controller.get_books(shelf_id)) > 0:
			    controller.clear_shelf(shelf_id)
			controller.delete_shelf(shelf_id)
			```
		
		Algorithm:
			1. Iterate through service._shelves
			2. Find shelf with matching ID
			3. Remove shelf from list
			4. Persist changes (catch and ignore errors)
			5. Return True if found and removed
			6. Return False if not found
		
		Args:
			id (str): Identifier of the shelf to delete.

		Returns:
			bool: True if shelf was found and deleted successfully,
				False if shelf not found or removal failed.
		
		Side Effects:
			- On success: Removes shelf from collection and persists
			- On failure: No changes
		
		Example:
			>>> controller = ShelfController()
			>>> shelf = controller.create_shelf(id="S001", name="Test")
			>>> 
			>>> # Delete empty shelf
			>>> success = controller.delete_shelf("S001")
			>>> success
			True
			>>> controller.find_shelf("S001") is None
			True
			>>> 
			>>> # Delete non-existent shelf
			>>> success = controller.delete_shelf("S999")
			>>> success
			False
			>>> 
			>>> # Safe deletion with books
			>>> shelf2 = controller.create_shelf(id="S002")
			>>> controller.add_book("S002", book1)
			>>> removed_books = controller.clear_shelf("S002")
			>>> controller.delete_shelf("S002")
			True
		
		Note:
			This method accesses the private _shelves list directly rather
			than using a service method, as deletion logic is simple and
			doesn't require business logic abstraction.
		
		See Also:
			- clear_shelf: Remove books before deletion
			- get_books: Check if shelf has books
			- create_shelf: Create new shelf
		"""
		shelves = self.service._shelves
		for s in list(shelves):
			if s.get_id() == id:
				try:
					shelves.remove(s)
					# service persists changes
					try:
						self.service._save_shelves()
					except Exception:
						pass
					return True
				except Exception:
					# If removal itself fails, continue and report not found below
					pass
		# not found
		return False
