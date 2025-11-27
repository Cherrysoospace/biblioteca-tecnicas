from typing import Optional, List
import time
import os

from services.shelf_service import ShelfService
from models.Books import Book


class ShelfController:
	"""Controller to mediate UI/other layers and the ShelfService.

	This controller mirrors the thin style used across the project: it
	delegates behavior to :class:`services.shelf_service.ShelfService` and
	provides small convenience handling (id generation fallback and basic
	error translation).
	"""

	def __init__(self):
		self.service = ShelfService()
		# Attempt to load existing shelves from data/shelves.json on startup
		try:
			data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
			if os.path.exists(data_path):
				# load existing shelves into the service so ids are generated sequentially
				try:
					self.service.load_from_file(data_path)
				except Exception:
					# do not stop initialization if loading fails
					pass
		except Exception:
			# best-effort only
			pass

	def _generate_next_id(self) -> str:
		"""Generate next shelf ID in the form SNNN (zero-padded 3 digits).

		Scans existing shelves and finds the highest numeric suffix, then
		returns the next value. If no valid existing IDs are found returns
		'S001'.
		"""
		max_n = 0
		for s in self.service.list_shelves():
			sid = getattr(s, '_Shelf__id', None)
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
		"""Create and register a new shelf.

		If `id` is omitted or falsy, a simple time-based id is generated to
		avoid blocking callers.

		Returns the created Shelf object.
		"""
		if not id:
			# generate sequential id like S001, S002, ...
			id = self._generate_next_id()
		shelf = self.service.create_shelf(id, capacity=capacity, books=books)
		# set optional human-readable name if provided
		if name is not None:
			try:
				shelf.set_name(name)
			except Exception:
				# best-effort: fallback to setattr if method missing
				try:
					setattr(shelf, '_Shelf__name', name)
				except Exception:
					pass
		# persist shelves to default data file (best-effort)
		try:
			path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
			self.service.save_to_file(path)
		except Exception:
			# do not fail creation if saving fails
			pass
		return shelf

	def list_shelves(self):
		"""Return a list of registered Shelf objects."""
		return self.service.list_shelves()

	def find_shelf(self, id: str):
		"""Return a Shelf by id or None if not found."""
		return self.service.find_shelf(id)

	def add_book(self, shelf_id: str, book: Book) -> bool:
		"""Add a Book instance to a shelf if it fits.

		Returns True on success, False otherwise.
		"""
		res = self.service.add_book(shelf_id, book)
		if res:
			try:
				path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
				self.service.save_to_file(path)
			except Exception:
				pass
		return res

	def remove_book(self, shelf_id: str, isbn: str) -> Optional[Book]:
		"""Remove the first book matching `isbn` from the shelf and return it.

		Returns the removed Book or None.
		"""
		removed = self.service.remove_book_by_isbn(shelf_id, isbn)
		if removed is not None:
			try:
				path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
				self.service.save_to_file(path)
			except Exception:
				pass
		return removed

	def move_book(self, from_shelf_id: str, to_shelf_id: str, isbn: str) -> bool:
		"""Move a book from one shelf to another (atomic-best-effort).

		Returns True on success, False otherwise.
		"""
		res = self.service.move_book(from_shelf_id, to_shelf_id, isbn)
		if res:
			try:
				path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
				self.service.save_to_file(path)
			except Exception:
				pass
		return res

	def set_capacity(self, shelf_id: str, capacity: float) -> bool:
		"""Update shelf capacity (kg). Returns True if updated."""
		ok = self.service.set_capacity(shelf_id, capacity)
		if ok:
			try:
				path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
				self.service.save_to_file(path)
			except Exception:
				pass
		return ok

	def get_books(self, shelf_id: str) -> List[Book]:
		"""Return books currently placed on the shelf (shallow copy)."""
		return self.service.get_books(shelf_id)

	def clear_shelf(self, shelf_id: str) -> List[Book]:
		"""Remove all books from a shelf and return the removed list."""
		removed = self.service.clear_shelf(shelf_id)
		# persist
		try:
			path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'shelves.json')
			self.service.save_to_file(path)
		except Exception:
			pass
		return removed

	def shelf_summary(self, shelf_id: str):
		"""Return a summary dict for a shelf (id, capacity, weights, counts)."""
		return self.service.shelf_summary(shelf_id)

	def save_shelves(self, path: str) -> None:
		"""Persist all shelves to a JSON file.

		This is a thin wrapper that forwards to the service. Exceptions from
		file I/O are propagated to the caller to keep controller small.
		"""
		self.service.save_to_file(path)

	def load_shelves(self, path: str) -> None:
		"""Load shelves from a JSON file, replacing current in-memory set."""
		self.service.load_from_file(path)
