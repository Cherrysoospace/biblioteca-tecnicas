from typing import List
from .Books import Book

class Inventory:
	"""Represents an inventory group for books with the same ISBN.

	This model groups multiple physical copies (Books) of the same ISBN together.
	- stock: total number of copies
	- items: list of Book objects (each represents a physical copy)
	"""

	def __init__(self, stock: int = 0, items: List[Book] = None):
		"""Initialize an Inventory group.
		
		Parameters:
		- stock: total number of copies (calculated from items if not provided)
		- items: list of Book objects representing physical copies
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
		"""Return the list of Book items (physical copies)."""
		return self.__items

	def get_stock(self) -> int:
		"""Return the total stock count."""
		return self.__stock

	def get_isbn(self) -> str:
		"""Return the ISBN code from the first item, or empty string if no items."""
		if self.__items and len(self.__items) > 0:
			return self.__items[0].get_ISBNCode()
		return ""

	# Setters
	def set_items(self, items: List[Book]):
		"""Set the list of Book items and update stock accordingly."""
		self.__items = items
		# Recompute stock as available copies (not borrowed)
		try:
			self.__stock = sum(1 for b in items if not b.get_isBorrowed())
		except Exception:
			# fallback: use total items
			self.__stock = len(items)

	def set_stock(self, stock: int):
		"""Set the stock count."""
		self.__stock = int(stock)

	def add_item(self, book: Book):
		"""Add a Book item to this inventory group and increment stock."""
		self.__items.append(book)
		self.__stock = len(self.__items)

	def remove_item(self, book_id: str) -> bool:
		"""Remove a Book item by ID and update stock. Returns True if removed."""
		for i, book in enumerate(self.__items):
			if book.get_id() == book_id:
				self.__items.pop(i)
				self.__stock = len(self.__items)
				return True
		return False

	def get_available_count(self) -> int:
		"""Return the count of books that are NOT borrowed."""
		return sum(1 for book in self.__items if not book.get_isBorrowed())

	def get_borrowed_count(self) -> int:
		"""Return the count of books that ARE borrowed."""
		return sum(1 for book in self.__items if book.get_isBorrowed())

	def __str__(self):
		isbn = self.get_isbn()
		available = self.get_available_count()
		borrowed = self.get_borrowed_count()
		return f"Inventory[ISBN: {isbn}, Stock: {self.__stock}, Available: {available}, Borrowed: {borrowed}]"




