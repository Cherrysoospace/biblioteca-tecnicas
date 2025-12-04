from typing import List, Optional
from .Books import Book

class Inventory:
	"""Represents an inventory group for books with the same ISBN.

	This model groups multiple physical copies (Books) of the same ISBN together,
	providing a unified interface for managing stock levels and tracking borrowing
	status across all copies of the same book.
	
	Key Concepts:
		- An Inventory group contains all physical copies of books with the same ISBN
		- Each physical copy is represented by a separate Book object
		- Stock represents the number of AVAILABLE (not borrowed) copies
		- Multiple copies of the same book can exist in different states (borrowed/available)
	
	Attributes:
		__stock (int): Count of available (not borrowed) copies
		__items (List[Book]): List of all Book objects (physical copies) in this group
	
	Example:
		>>> book1 = Book("B001", "978-123", "Title", "Author", 1.5, 25000, False)
		>>> book2 = Book("B002", "978-123", "Title", "Author", 1.5, 25000, True)
		>>> inventory = Inventory(stock=1, items=[book1, book2])
		>>> inventory.get_available_count()  # Returns 1 (only book1 is available)
		1
		>>> inventory.get_borrowed_count()  # Returns 1 (book2 is borrowed)
		1
	"""

	def __init__(self, stock: int = 0, items: List[Book] = None):
		"""Initialize an Inventory group.
		
		Creates a new inventory group that manages multiple physical copies of books
		with the same ISBN. The stock is automatically calculated based on the number
		of available (not borrowed) copies unless explicitly provided.
		
		Stock Calculation Logic:
			- If stock=0 and items are provided: Calculate from available copies
			- If stock is provided: Use the provided value
			- Stock represents AVAILABLE copies, not total copies
		
		Args:
			stock (int, optional): Initial stock count (available copies).
				If 0 and items are provided, will be calculated automatically.
				Defaults to 0.
			items (List[Book], optional): List of Book objects representing physical
				copies. All books should have the same ISBN. Defaults to None (empty list).
		
		Returns:
			None
		
		Example:
			>>> # Auto-calculate stock from items
			>>> books = [Book("B1", "978-123", "Title", "Author", 1.0, 1000, False),
			...          Book("B2", "978-123", "Title", "Author", 1.0, 1000, True)]
			>>> inv = Inventory(stock=0, items=books)  # Stock will be 1 (1 available)
			>>> inv.get_stock()
			1
			>>> 
			>>> # Explicit stock value
			>>> inv2 = Inventory(stock=5, items=[])
			>>> inv2.get_stock()
			5
		"""
		# Lista de libros (copias físicas) con el mismo ISBN
		self.__items = items if items is not None else []
		
		# Stock: number of AVAILABLE (not borrowed) copies by default.
		# If a specific stock is provided, respect it; otherwise compute
		# available count from items so that "stock" represents availability.
		if stock == 0 and self.__items:
			# available = count of items not borrowed
			self.__stock = sum(1 for b in self.__items if not b.get_isBorrowed())
		else:
			self.__stock = int(stock)

	# Getters
	def get_items(self) -> List[Book]:
		"""Get all Book items (physical copies) in this inventory group.
		
		Returns a reference to the internal list of Book objects. Each Book
		represents a physical copy of the same ISBN. The list includes both
		available and borrowed copies.
		
		Args:
			None
		
		Returns:
			List[Book]: List of all Book objects in this inventory group.
				Includes both borrowed and available copies.
		
		Example:
			>>> inventory = Inventory(stock=2, items=[book1, book2])
			>>> all_books = inventory.get_items()
			>>> len(all_books)
			2
			>>> for book in all_books:
			...     print(f"{book.get_id()}: Borrowed={book.get_isBorrowed()}")
		"""
		return self.__items

	def get_book(self) -> Optional[Book]:
		"""Get a representative Book from this inventory group.
		
		Returns the first Book object from the items list, which serves as a
		representative sample for this inventory group. This is useful for
		accessing common properties like ISBN, title, author, etc. that are
		identical across all copies.
		
		Note:
			The returned Book may be borrowed or available. Check isBorrowed
			if you need a specific state.
		
		Args:
			None
		
		Returns:
			Optional[Book]: First Book object in the inventory, or None if the
				inventory group is empty (no items).
		
		Example:
			>>> inventory = Inventory(stock=3, items=[book1, book2, book3])
			>>> sample = inventory.get_book()
			>>> if sample:
			...     print(f"ISBN: {sample.get_ISBNCode()}")
			...     print(f"Title: {sample.get_title()}")
		"""
		if self.__items:
			return self.__items[0]
		return None

	def get_stock(self) -> int:
		"""Get the current stock count (available copies).
		
		Returns the number of available (not borrowed) copies in this inventory
		group. This represents how many copies can be borrowed right now.
		
		Important:
			Stock represents AVAILABLE copies, not total copies.
			To get total copies, use len(inventory.get_items())
			To get borrowed copies, use inventory.get_borrowed_count()
		
		Args:
			None
		
		Returns:
			int: Number of available (not borrowed) copies.
		
		Example:
			>>> inventory = Inventory(stock=2, items=[book1, book2, book3])
			>>> inventory.get_stock()
			2
			>>> # Total copies = 3, Available = 2, Borrowed = 1
		"""
		return self.__stock

	def get_isbn(self) -> str:
		"""Get the ISBN code for this inventory group.
		
		Returns the ISBN code from the first book in the items list. Since all
		books in an inventory group should have the same ISBN, this represents
		the ISBN for the entire group.
		
		Args:
			None
		
		Returns:
			str: ISBN code of the books in this group, or empty string "" if
				the inventory group is empty (no items).
		
		Example:
			>>> book1 = Book("B1", "978-0-306-40615-7", "Title", "Author", 1.0, 1000, False)
			>>> inventory = Inventory(stock=1, items=[book1])
			>>> inventory.get_isbn()
			'978-0-306-40615-7'
			>>> 
			>>> empty_inv = Inventory()
			>>> empty_inv.get_isbn()
			''
		"""
		if self.__items and len(self.__items) > 0:
			return self.__items[0].get_ISBNCode()
		return ""

	# Setters
	def set_items(self, items: List[Book]):
		"""Set the list of Book items and automatically recalculate stock.
		
		Replaces the current items list with a new list of Books and automatically
		recalculates the stock based on the number of available (not borrowed) copies.
		
		Stock Recalculation:
			1. Counts how many books are NOT borrowed
			2. Sets stock to that count
			3. If counting fails, falls back to total item count
		
		Args:
			items (List[Book]): New list of Book objects to set. All books should
				have the same ISBN to maintain inventory group integrity.
		
		Returns:
			None
		
		Side Effects:
			- Replaces the internal items list
			- Recalculates and updates stock count
		
		Example:
			>>> inventory = Inventory()
			>>> new_books = [book1, book2, book3]
			>>> inventory.set_items(new_books)
			>>> inventory.get_stock()  # Will be count of non-borrowed books
		"""
		self.__items = items
		# Recompute stock as available copies (not borrowed)
		try:
			self.__stock = sum(1 for b in items if not b.get_isBorrowed())
		except Exception:
			# fallback: use total items
			self.__stock = len(items)

	def set_stock(self, stock: int):
		"""Set the stock count manually.
		
		Directly sets the stock count without validating against the actual
		number of available books. Use with caution as this can lead to
		inconsistencies if not managed properly.
		
		Warning:
			This method does NOT validate that the stock matches the actual
			number of available books in items. Prefer using set_items() which
			automatically calculates stock, or use add_item()/remove_item() which
			update stock automatically.
		
		Args:
			stock (int): New stock count. Will be converted to int if needed.
		
		Returns:
			None
		
		Example:
			>>> inventory = Inventory()
			>>> inventory.set_stock(10)
			>>> inventory.get_stock()
			10
		"""
		self.__stock = int(stock)

	def add_item(self, book: Book):
		"""Add a new Book to this inventory group and update stock.
		
		Appends a Book object to the items list and recalculates the stock
		to reflect the new total number of copies. The stock is set to the
		total number of items (both borrowed and available).
		
		Note:
			This method sets stock to len(items), which includes ALL copies
			(borrowed + available). This differs from the auto-calculation in
			__init__ and set_items() which count only available copies.
		
		Args:
			book (Book): Book object to add to this inventory group.
				Should have the same ISBN as existing books in the group.
		
		Returns:
			None
		
		Side Effects:
			- Appends book to items list
			- Updates stock to total item count
		
		Example:
			>>> inventory = Inventory(stock=2, items=[book1, book2])
			>>> new_book = Book("B3", "978-123", "Title", "Author", 1.0, 1000, False)
			>>> inventory.add_item(new_book)
			>>> len(inventory.get_items())
			3
			>>> inventory.get_stock()
			3
		"""
		self.__items.append(book)
		self.__stock = len(self.__items)

	def remove_item(self, book_id: str) -> bool:
		"""Remove a Book from this inventory group by its ID.
		
		Searches for a Book with the specified ID in the items list. If found,
		removes it and updates the stock count to reflect the new total.
		
		Search Algorithm:
			Linear search through items list by book ID.
			Time Complexity: O(n) where n is the number of items.
		
		Args:
			book_id (str): Unique identifier of the Book to remove.
		
		Returns:
			bool: True if the book was found and removed, False if the book
				with the specified ID was not found in this inventory group.
		
		Side Effects:
			- If found: Removes book from items list and updates stock
			- If not found: No changes made
		
		Example:
			>>> inventory = Inventory(stock=2, items=[book1, book2])
			>>> inventory.remove_item("B001")
			True
			>>> len(inventory.get_items())
			1
			>>> inventory.get_stock()
			1
			>>> inventory.remove_item("NONEXISTENT")
			False
		"""
		for i, book in enumerate(self.__items):
			if book.get_id() == book_id:
				self.__items.pop(i)
				self.__stock = len(self.__items)
				return True
		return False

	def get_available_count(self) -> int:
		"""Get the number of available (not borrowed) copies.
		
		Counts how many books in the items list have isBorrowed=False.
		This represents the actual number of copies that can be borrowed
		right now.
		
		Note:
			This may differ from get_stock() if stock was manually set or
			updated via add_item() which sets stock to total count.
		
		Args:
			None
		
		Returns:
			int: Number of books with isBorrowed=False.
		
		Example:
			>>> book1 = Book("B1", "978-123", "Title", "Author", 1.0, 1000, False)
			>>> book2 = Book("B2", "978-123", "Title", "Author", 1.0, 1000, True)
			>>> book3 = Book("B3", "978-123", "Title", "Author", 1.0, 1000, False)
			>>> inventory = Inventory(items=[book1, book2, book3])
			>>> inventory.get_available_count()
			2
		"""
		return sum(1 for book in self.__items if not book.get_isBorrowed())

	def get_borrowed_count(self) -> int:
		"""Get the number of currently borrowed copies.
		
		Counts how many books in the items list have isBorrowed=True.
		This represents the number of copies that are currently on loan
		and not available for borrowing.
		
		Relationship:
			get_available_count() + get_borrowed_count() = len(get_items())
		
		Args:
			None
		
		Returns:
			int: Number of books with isBorrowed=True.
		
		Example:
			>>> book1 = Book("B1", "978-123", "Title", "Author", 1.0, 1000, False)
			>>> book2 = Book("B2", "978-123", "Title", "Author", 1.0, 1000, True)
			>>> book3 = Book("B3", "978-123", "Title", "Author", 1.0, 1000, True)
			>>> inventory = Inventory(items=[book1, book2, book3])
			>>> inventory.get_borrowed_count()
			2
			>>> inventory.get_available_count()
			1
			>>> len(inventory.get_items())
			3
		"""
		return sum(1 for book in self.__items if book.get_isBorrowed())

	def __str__(self):
		"""Get a human-readable string representation of this inventory group.
		
		Provides a formatted string showing the ISBN, stock count, number of
		available copies, and number of borrowed copies. Useful for debugging
		and logging.
		
		Args:
			None
		
		Returns:
			str: Formatted string with inventory details.
		
		Example:
			>>> inventory = Inventory(stock=2, items=[book1, book2, book3])
			>>> print(inventory)
			Inventory[ISBN: 978-0-306-40615-7, Stock: 2, Available: 2, Borrowed: 1]
		"""
		isbn = self.get_isbn()
		available = self.get_available_count()
		borrowed = self.get_borrowed_count()
		return f"Inventory[ISBN: {isbn}, Stock: {self.__stock}, Available: {available}, Borrowed: {borrowed}]"




