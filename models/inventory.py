from .Books import Book

class Inventory:
	"""Represents an inventory item linking a Book to its stock count.

	This model no longer maintains a separate `stock` attribute. Stock is
	delegated to the associated `Book` instance. `get_stock()` accepts an
	optional list of inventories to compute the cumulative stock for the
	same ISBN across the provided inventories.
	"""

	def __init__(self, book: Book, stock: int, isBorrowed: bool = False):
		# private attributes
		self.__book = book
		# Inventory mantiene su propio stock (ahora Book ya no lo contiene)
		self.__stock = int(stock)
		# estado de préstamo para esta entrada de inventario
		self.__isBorrowed = bool(isBorrowed)

	# Getters
	def get_book(self):
		return self.__book

	def get_stock(self, inventories: list = None):
		"""Return the stock for this inventory item.

		If `inventories` is provided (list of Inventory), the method will
		compute and return the total stock across all Inventory entries that
		share the same ISBN as this item's book. If `inventories` is None,
		returns the stock stored in the associated Book.
		"""
		if inventories is None:
			return self.__stock

		# sum stocks for same ISBN across provided inventories
		target_isbn = self.get_book().get_ISBNCode()
		total = 0
		for inv in inventories:
			try:
				if inv.get_book().get_ISBNCode() == target_isbn:
					# sumar el stock de cada Inventory (no del Book)
					total += int(inv.get_stock())
			except Exception:
				# be robust to malformed entries
				continue
		return total

	# Setters
	def set_book(self, book: Book):
		self.__book = book

	def set_stock(self, stock: int):
		self.__stock = int(stock)

	def get_isBorrowed(self):
		return self.__isBorrowed

	def set_isBorrowed(self, isBorrowed: bool):
		self.__isBorrowed = bool(isBorrowed)

	def __str__(self):
		# show stock del Inventory
		return f"Inventory[Book: {self.__book}, Stock: {self.__stock}, isBorrowed: {self.__isBorrowed}]"




