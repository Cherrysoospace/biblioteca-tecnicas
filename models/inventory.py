from .Books import Book

class Inventory:
	"""Represents an inventory item linking a Book to its stock count.

	Follows the same private-attribute + getter/setter pattern used in `Books.py`.
	"""

	def __init__(self, book: Book, stock: int):
		# private attributes
		self.__book = book
		self.__stock = stock

	# Getters
	def get_book(self):
		return self.__book

	def get_stock(self):
		return self.__stock

	# Setters
	def set_book(self, book: Book):
		self.__book = book

	def set_stock(self, stock: int):
		self.__stock = stock

	def __str__(self):
		return f"Inventory[Book: {self.__book}, Stock: {self.__stock}]"


        