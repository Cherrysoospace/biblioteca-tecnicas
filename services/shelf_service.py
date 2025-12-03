"""Shelf service module.

Service for managing Shelf objects with business logic for book placement,
capacity checks, and shelf operations.

Responsibilities:
- BUSINESS LOGIC: Book placement validation, capacity management, book assignment tracking
- Persistence delegated to ShelfRepository (SRP compliance)
"""

from typing import List, Optional

from models.shelf import Shelf
from models.Books import Book
from repositories.shelf_repository import ShelfRepository


class ShelfService:
	"""Service for managing Shelf objects and book placement operations.
	
	Responsibilities:
	- Book placement validation and capacity checks
	- Shelf operations (add/remove books, move books between shelves)
	- Book assignment tracking across shelves
	"""

	def __init__(self, repository: ShelfRepository = None, shelves: Optional[List[Shelf]] = None):
		"""Initialize ShelfService with a repository.

		Parameters:
		- repository: Optional ShelfRepository instance. If None, creates a new one.
		- shelves: Optional initial list of Shelf objects (used for testing).
		"""
		self.repository = repository or ShelfRepository()
		self._shelves: List[Shelf] = shelves if shelves is not None else []
		if shelves is None:
			self._load_shelves()

	def create_shelf(self, id, capacity: float = 8.0, books: Optional[List[Book]] = None, name: Optional[str] = None) -> Shelf:
		"""Create and register a new Shelf.

		Args:
			id: Identifier for the shelf.
			capacity: Maximum weight capacity in kilograms (default 8.0).
			books: Optional initial list of Book objects.
			name: Optional human-readable name for the shelf.

		Returns:
			The created Shelf instance.
		"""
		shelf = Shelf(id, books=books, capacity=capacity)
		if name is not None:
			shelf.set_name(name)
		self._shelves.append(shelf)
		self._save_shelves()
		return shelf

	def list_shelves(self) -> List[Shelf]:
		"""Return all registered shelves."""
		return list(self._shelves)

	def find_shelf(self, id) -> Optional[Shelf]:
		"""Find a shelf by its ID.

		Args:
			id: Shelf identifier to search for.

		Returns:
			The Shelf if found, otherwise None.
		"""
		for s in self._shelves:
			if s.get_id() == id:
				return s
		return None

	def add_book(self, shelf_id, book: Book) -> bool:
		"""Add a Book to the specified shelf with capacity validation.

		Args:
			shelf_id: Identifier of the shelf.
			book: Book instance to add.

		Returns:
			True if added successfully, False otherwise.
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
		"""Calculate total weight of books on a shelf.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			Sum of book weights in kg. Returns 0.0 if shelf not found.
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
		"""Calculate remaining capacity of a shelf.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			Remaining capacity in kg. Returns 0.0 if shelf not found.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return 0.0
		return shelf.capacity - self.total_weight(shelf_id)

	def can_add(self, shelf_id, book: Book) -> bool:
		"""Check if a book can be added to shelf without exceeding capacity.

		Args:
			shelf_id: Identifier of the shelf.
			book: Book instance to check.

		Returns:
			True if book fits, False otherwise.
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
		"""Get all books from a shelf.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			List of Book instances. Returns empty list if shelf not found.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return []
		return list(getattr(shelf, '_Shelf__books'))

	def is_book_assigned(self, book_id: str) -> bool:
		"""Check if a book is assigned to any shelf.

		Args:
			book_id: Book identifier to search for.

		Returns:
			True if book is found in any shelf, False otherwise.
		"""
		for s in self._shelves:
			books = getattr(s, '_Shelf__books', [])
			for b in books:
				if b.get_id() == book_id:
					return True
		return False

	def clear_shelf(self, shelf_id) -> List[Book]:
		"""Remove all books from a shelf.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			List of removed Book objects. Returns empty list if shelf not found.
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
		"""Move a book from one shelf to another.

		Args:
			from_shelf_id: Source shelf identifier.
			to_shelf_id: Destination shelf identifier.
			isbn: ISBN of the book to move.

		Returns:
			True if moved successfully, False otherwise.
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
		"""Update shelf capacity.

		Args:
			shelf_id: Identifier of the shelf.
			capacity: New capacity in kilograms.

		Returns:
			True if updated, False if shelf not found or validation fails.
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
		"""Remove a book from all shelves where it appears.

		Args:
			book_id: Identifier of the book to remove.

		Returns:
			Number of shelves from which the book was removed.
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
		"""Load shelves from repository into memory."""
		self._shelves = self.repository.load_all()

	def _save_shelves(self) -> None:
		"""Persist shelves using repository."""
		self.repository.save_all(self._shelves)


__all__ = ['ShelfService']

