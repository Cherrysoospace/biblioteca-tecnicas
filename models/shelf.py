from .Books import Book

class Shelf:
    """Represents a shelf that holds a Book and tracks the total weight on the shelf.

    Follows the same private-attribute + getter/setter pattern used in `Books.py`.
    """

    def __init__(self, id, book: Book, totalweight: float):
        # private attributes
        self.__id = id
        self.__book = book
        self.__totalweight = totalweight

    # Getters
    def get_id(self):
        return self.__id

    def get_book(self):
        return self.__book

    def get_totalweight(self):
        return self.__totalweight

    # Setters
    def set_id(self, id):
        self.__id = id

    def set_book(self, book: Book):
        self.__book = book

    def set_totalweight(self, totalweight: float):
        self.__totalweight = totalweight

    def __str__(self):
        return f"Shelf[ID: {self.__id}, Book: {self.__book}, TotalWeight: {self.__totalweight}]"
