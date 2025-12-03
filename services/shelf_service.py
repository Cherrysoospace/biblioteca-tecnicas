"""Shelf service module.

This module provides a small in-memory service layer that implements the
operational logic for `Shelf` models. The `Shelf` model is intentionally
minimal (it only stores data). This service offers helpers to create/manage
shelves, add/remove books, compute weights/capacities, and serialize
shelves to/from JSON-friendly dicts.

Design notes:
- The service accesses `Shelf` private attributes using name-mangling
	(e.g. ``_Shelf__books``). This keeps the model simple and moves behavior
	to the service layer (as requested).
- Persistence here is a convenience using the built-in :mod:`json` module.
	Integrate with project file utilities if you later provide them.
"""

from typing import List, Optional, Dict, Any

from models.shelf import Shelf
from models.Books import Book
from repositories.shelf_repository import ShelfRepository


class ShelfService:
	"""Service managing multiple Shelf instances and book placement.

	This class keeps an in-memory list of `Shelf` objects and provides basic
	operations that the rest of the application can call. It intentionally
	avoids changing Book or Shelf internals beyond using their getters and
	constructors.

	Methods are straightforward and documented per-function.
	"""

	def __init__(self, repository: ShelfRepository = None, shelves: Optional[List[Shelf]] = None):
		"""Initialize ShelfService.

		Parameters:
		- repository: optional ShelfRepository instance. If None, creates a new one.
		- shelves: optional initial list of Shelf objects (used for testing).
		"""
		self.repository = repository or ShelfRepository()
		self._shelves: List[Shelf] = shelves if shelves is not None else []
		# load persisted shelves unless an initial list was provided
		if shelves is None:
			try:
				self._load_shelves()
			except Exception:
				self._shelves = []

	def create_shelf(self, id, capacity: float = 8.0, books: Optional[List[Book]] = None, name: Optional[str] = None) -> Shelf:
		"""Create and register a new Shelf.

		Args:
			id: Identifier for the shelf (str|int).
			capacity: Maximum weight capacity in kilograms (default 8.0).
			books: Optional initial list of Book objects to place on the shelf.

		Returns:
			The created :class:`models.shelf.Shelf` instance.
		"""
		shelf = Shelf(id, books=books, capacity=capacity)
		# set optional name before persisting so it's saved
		if name is not None:
			try:
				shelf.set_name(name)
			except Exception:
				try:
					setattr(shelf, '_Shelf__name', name)
				except Exception:
					pass
		self._shelves.append(shelf)
		# persist change
		try:
			self._save_shelves()
		except Exception:
			pass
		return shelf

	def list_shelves(self) -> List[Shelf]:
		"""Return a shallow list copy of registered shelves."""
		return list(self._shelves)

	def find_shelf(self, id) -> Optional[Shelf]:
		"""Find a shelf by its id.

		Args:
			id: Shelf identifier to search for.

		Returns:
			The Shelf if found, otherwise ``None``.
		"""
		for s in self._shelves:
			# access private attr via name mangling (model is a simple data holder)
			if getattr(s, '_Shelf__id', None) == id:
				return s
		return None

	def add_book(self, shelf_id, book: Book) -> bool:
		"""Try to place a Book onto the specified shelf.

		This method performs a capacity check using the Book's ``get_weight``
		method. It will append the book to the shelf's internal list only if it
		fits.

		Args:
			shelf_id: Identifier of the shelf where the book should be added.
			book: Book instance to add.

		Returns:
			True if the book was added; False if the shelf doesn't exist or the
			book would exceed the shelf capacity or the book has no valid weight.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False

		# compute current total and remaining capacity
		total = self.total_weight(shelf_id)
		capacity = shelf.capacity

		# Prevent adding duplicate book ids to the same shelf
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		try:
			bid = book.get_id()
		except Exception:
			bid = None
		if bid is not None:
			for existing in books_list:
				try:
					if existing.get_id() == bid:
						# duplicate id found
						return False
				except Exception:
					# if we can't read id, skip comparison
					continue
		try:
			w = book.get_weight()
		except Exception:
			# invalid book weight
			return False

		if total + w <= capacity:
			books_list.append(book)
			# persist change
			try:
				self._save_shelves()
			except Exception:
				pass
			return True
		return False

	def remove_book_by_isbn(self, shelf_id, isbn: str) -> Optional[Book]:
		"""Remove and return the first book matching `isbn` from the shelf.

		Args:
			shelf_id: Identifier of the shelf.
			isbn: ISBN code to match (string).

		Returns:
			The removed Book if found; otherwise ``None``.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return None
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		for i, b in enumerate(books_list):
			if getattr(b, '_Book__ISBNCode', None) == isbn:
				removed = books_list.pop(i)
				# persist change
				try:
					self._save_shelves()
				except Exception:
					pass
				return removed
		return None

	def total_weight(self, shelf_id) -> float:
		"""Compute the total weight of books placed on a shelf.

		Args:
			shelf_id: Identifier of the shelf to compute.

		Returns:
			Sum of weights (float). Returns 0.0 for unknown shelf or if book
			weights cannot be parsed.
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
				# ignore invalid weights but continue
				pass
		return total

	def remaining_capacity(self, shelf_id) -> float:
		"""Return remaining capacity (kg) for a given shelf.

		If the shelf is not found returns 0.0.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return 0.0
		return shelf.capacity - self.total_weight(shelf_id)

	def can_add(self, shelf_id, book: Book) -> bool:
		"""Check whether a Book fits in the shelf without modifying state.

		Args:
			shelf_id: Identifier of the shelf to check.
			book: Book instance to evaluate.

		Returns:
			True if the book can be added without exceeding capacity, False
			if the shelf does not exist or the book weight is invalid or would
			exceed the capacity.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False
		try:
			w = float(book.get_weight())
		except Exception:
			return False
		return self.remaining_capacity(shelf_id) >= w

	def get_books(self, shelf_id) -> List[Book]:
		"""Return a shallow copy of the list of books on the shelf.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			A list of Book instances (possibly empty). Returns an empty list if
			shelf is not found.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return []
		return list(getattr(shelf, '_Shelf__books'))

	def is_book_assigned(self, book_id: str) -> bool:
		"""Return True if a book with given id is present in any registered shelf.

		This searches each shelf's internal books list and compares using the
		Book.get_id() method when available; falls back to the mangled
		attribute `_Book__id` when necessary.
		"""
		try:
			for s in self._shelves:
				books = getattr(s, '_Shelf__books', [])
				for b in books:
					try:
						bid = b.get_id()
					except Exception:
						bid = getattr(b, '_Book__id', None)
					if bid == book_id:
						return True
			return False
		except Exception:
			# Be conservative: if inspection fails, report assigned to avoid
			# showing a book that might already be placed on a shelf.
			return True

	def clear_shelf(self, shelf_id) -> List[Book]:
		"""Remove all books from a shelf and return the removed list.

		Args:
			shelf_id: Identifier of the shelf.

		Returns:
			List of Book objects that were removed (empty if shelf not found or
			already empty).
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return []
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		removed = list(books_list)
		books_list.clear()
		# persist change
		try:
			self._save_shelves()
		except Exception:
			pass
		return removed

	def move_book(self, from_shelf_id, to_shelf_id, isbn: str) -> bool:
		"""Atomically move a book identified by ISBN from one shelf to another.

		The operation removes the book from the source shelf and attempts to add
		it to the destination shelf. If the destination does not have capacity
		(or does not exist), the book is put back in the source shelf to keep
		state consistent.

		Args:
			from_shelf_id: Source shelf identifier.
			to_shelf_id: Destination shelf identifier.
			isbn: ISBN of the book to move.

		Returns:
			True on success, False otherwise.
		"""
		# remove from source first
		book = self.remove_book_by_isbn(from_shelf_id, isbn)
		if book is None:
			return False
		# try to add to destination
		if self.add_book(to_shelf_id, book):
			return True
		# restore back to source (best-effort)
		src = self.find_shelf(from_shelf_id)
		if src is not None:
			getattr(src, '_Shelf__books').append(book)
			try:
				self._save_shelves()
			except Exception:
				pass
		return False

	def set_capacity(self, shelf_id, capacity: float) -> bool:
		"""Update the capacity (kg) of an existing shelf.

		If the new capacity is smaller than current total weight, the change is
		allowed but may cause the shelf to be over-capacity; callers can check
		the remaining_capacity afterwards.

		Args:
			shelf_id: Identifier of the shelf.
			capacity: New capacity in kilograms.

		Returns:
			True if updated, False if shelf not found.
		"""
		shelf = self.find_shelf(shelf_id)
		if shelf is None:
			return False
		# delegate validation to the Shelf model's capacity setter
		try:
			shelf.capacity = float(capacity)
		except Exception:
			# if model validation fails, do not update and return False
			return False
		# persist change
		try:
			self._save_shelves()
		except Exception:
			pass
		return True



	# Persistence helpers using repository

	def _load_shelves(self) -> None:
		"""Load shelves from the repository into memory."""
		self._shelves = self.repository.load_all()

	def _save_shelves(self) -> None:
		"""Persist current in-memory shelves using the repository."""
		self.repository.save_all(self._shelves)




__all__ = ['ShelfService']

