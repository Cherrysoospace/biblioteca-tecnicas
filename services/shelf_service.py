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
import json

from models.shelf import Shelf
from models.Books import Book


class ShelfService:
	"""Service managing multiple Shelf instances and book placement.

	This class keeps an in-memory list of `Shelf` objects and provides basic
	operations that the rest of the application can call. It intentionally
	avoids changing Book or Shelf internals beyond using their getters and
	constructors.

	Methods are straightforward and documented per-function.
	"""

	def __init__(self, shelves: Optional[List[Shelf]] = None):
		self._shelves: List[Shelf] = shelves if shelves is not None else []

	def create_shelf(self, id, capacity: float = 8.0, books: Optional[List[Book]] = None) -> Shelf:
		"""Create and register a new Shelf.

		Args:
			id: Identifier for the shelf (str|int).
			capacity: Maximum weight capacity in kilograms (default 8.0).
			books: Optional initial list of Book objects to place on the shelf.

		Returns:
			The created :class:`models.shelf.Shelf` instance.
		"""
		shelf = Shelf(id, books=books, capacity=capacity)
		self._shelves.append(shelf)
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
		capacity = getattr(shelf, '_Shelf__capacity', 0.0)
		try:
			w = book.get_weight()
		except Exception:
			# invalid book weight
			return False

		if total + w <= capacity:
			books_list: List[Book] = getattr(shelf, '_Shelf__books')
			books_list.append(book)
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
				return books_list.pop(i)
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
		capacity = getattr(shelf, '_Shelf__capacity', 0.0)
		return capacity - self.total_weight(shelf_id)

	# Serialization helpers
	def shelf_to_dict(self, shelf: Shelf) -> Dict[str, Any]:
		"""Serialize a Shelf to a JSON-friendly dictionary.

		The returned dict contains shelf id, capacity and a list of serialized
		books (basic properties are extracted via Book getters).

		Args:
			shelf: Shelf instance to serialize.

		Returns:
			A dictionary ready to be passed to :func:`json.dump`.
		"""
		books_list: List[Book] = getattr(shelf, '_Shelf__books')
		books_serialized = []
		for b in books_list:
			books_serialized.append({
				'id': b.get_id(),
				'ISBNCode': b.get_ISBNCode(),
				'title': b.get_title(),
				'author': b.get_author(),
				'weight': b.get_weight(),
				'price': b.get_price(),
				'isBorrowed': b.get_isBorrowed(),
			})
		return {
			'id': getattr(shelf, '_Shelf__id', None),
			'capacity': getattr(shelf, '_Shelf__capacity', None),
			'books': books_serialized,
		}

	def shelf_from_dict(self, data: Dict[str, Any]) -> Shelf:
		"""Create a Shelf (and Book instances) from a dictionary.

		Args:
			data: Dictionary with keys 'id', 'capacity' and 'books' as produced by
			:shelf_to_dict:.

		Returns:
			The created Shelf (also registered in the service's internal list).
		"""
		books = []
		for bd in data.get('books', []):
			book = Book(
				bd.get('id'), bd.get('ISBNCode'), bd.get('title'), bd.get('author'), bd.get('weight'), bd.get('price'), bd.get('isBorrowed')
			)
			books.append(book)
		shelf = Shelf(data.get('id'), books=books, capacity=data.get('capacity', 8.0))
		self._shelves.append(shelf)
		return shelf

	def save_to_file(self, path: str) -> None:
		"""Save all registered shelves to a JSON file.

		Args:
			path: Filesystem path where JSON will be written.
		"""
		payload = [self.shelf_to_dict(s) for s in self._shelves]
		with open(path, 'w', encoding='utf-8') as fh:
			json.dump(payload, fh, ensure_ascii=False, indent=2)

	def load_from_file(self, path: str) -> None:
		"""Load shelves from a JSON file and register them.

		This will clear any currently registered shelves before loading.

		Args:
			path: Path to JSON file produced by :meth:`save_to_file`.
		"""
		with open(path, 'r', encoding='utf-8') as fh:
			payload = json.load(fh)
		# clear existing
		self._shelves = []
		for sd in payload:
			self.shelf_from_dict(sd)


__all__ = ['ShelfService']

