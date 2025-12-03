from typing import Optional, List

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
		"""Initialize the controller.
		
		The ShelfService automatically loads persisted shelves from the
		default path (FilePaths.SHELVES) in its own __init__, so no
		additional loading is needed here.
		"""
		self.service = ShelfService()

	def _generate_next_id(self) -> str:
		"""Generate next shelf ID in the form SNNN (zero-padded 3 digits).

		Scans existing shelves and finds the highest numeric suffix, then
		returns the next value. If no valid existing IDs are found returns
		'S001'.
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
		"""Create and register a new shelf.

		If `id` is omitted or falsy, a simple time-based id is generated to
		avoid blocking callers.

		Returns the created Shelf object.
		"""
		if not id:
			# generate sequential id like S001, S002, ...
			id = self._generate_next_id()
		# pass the name into the service so it is set before persisting
		shelf = self.service.create_shelf(id, capacity=capacity, books=books, name=name)
		return shelf

	def list_shelves(self):
		"""Return a list of registered Shelf objects."""
		return self.service.list_shelves()

	def find_shelf(self, id: str):
		"""Return a Shelf by id or None if not found."""
		return self.service.find_shelf(id)

	def search_shelves(self, search_term: str) -> List:
		"""Search shelves by ID or name.
		
		Args:
			search_term: Term to search for (case-insensitive)
			
		Returns:
			List of Shelf objects matching the search term
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
		"""Add a Book instance to a shelf if it fits.

		Returns True on success, False otherwise.
		"""
		# service persists changes
		return self.service.add_book(shelf_id, book)

	def remove_book(self, shelf_id: str, isbn: str) -> Optional[Book]:
		"""Remove the first book matching `isbn` from the shelf and return it.

		Returns the removed Book or None.
		"""
		# service persists changes
		return self.service.remove_book_by_isbn(shelf_id, isbn)

	def move_book(self, from_shelf_id: str, to_shelf_id: str, isbn: str) -> bool:
		"""Move a book from one shelf to another (atomic-best-effort).

		Returns True on success, False otherwise.
		"""
		# service persists changes
		return self.service.move_book(from_shelf_id, to_shelf_id, isbn)

	def set_capacity(self, shelf_id: str, capacity: float) -> bool:
		"""Update shelf capacity (kg). Returns True if updated."""
		# service persists changes
		return self.service.set_capacity(shelf_id, capacity)

	def get_books(self, shelf_id: str) -> List[Book]:
		"""Return books currently placed on the shelf (shallow copy)."""
		return self.service.get_books(shelf_id)

	def is_book_assigned(self, book_id: str) -> bool:
		"""Delegates to service implementation to check assignment.

		Keeps controller thin: the actual inspection logic lives in
		the ShelfService.
		"""
		try:
			return self.service.is_book_assigned(book_id)
		except Exception:
			# conservative default
			return True

	def clear_shelf(self, shelf_id: str) -> List[Book]:
		"""Remove all books from a shelf and return the removed list."""
		# service persists changes
		return self.service.clear_shelf(shelf_id)

	def save_shelves(self, path: str) -> None:
		"""Persist all shelves to a JSON file.

		This is a thin wrapper that forwards to the service. Exceptions from
		file I/O are propagated to the caller to keep controller small.
		"""
		# explicit save: delegate to service persistence helper
		self.service._save_shelves()

	def load_shelves(self, path: str) -> None:
		"""Load shelves from a JSON file, replacing current in-memory set."""
		# load into service memory
		self.service._load_shelves()

	def delete_shelf(self, id: str) -> bool:
		"""Delete a shelf by id.

		Removes the shelf from the in-memory list and persists the change to
		the default shelves file. Returns True on success, False if the
		shelf was not found.
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
