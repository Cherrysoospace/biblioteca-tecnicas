from typing import List, Optional
from .Books import Book


class Shelf:
    """Shelf model that stores metadata and a collection of Book objects.

    Intentionally minimal: this class only holds data (id, books list and capacity).
    All behaviors/operations (add/remove/weight calculations) are expected to
    live in a corresponding shelf service module.
    """

    def __init__(self, id, books: Optional[List[Book]] = None, capacity: float = 8.0):
        # private attributes
        self.__id = id
        # store books as a simple list; service layer will manipulate it
        self.__books: List[Book] = books if books is not None else []
        self.__capacity: float = capacity

    def __str__(self):
        return f"Shelf[ID: {self.__id}, books: {len(self.__books)} items, capacity: {self.__capacity}kg]"
