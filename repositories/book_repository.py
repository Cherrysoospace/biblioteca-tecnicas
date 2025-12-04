"""book_repository.py

Repository for book persistence.

Single Responsibility: read/write book data to `books.json` via the
base repository implementation.

Author: Library Management System
Date: 2025-12-02
"""

from typing import List
from models.Books import Book
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _book_from_dict(data: dict) -> Book:
    """Convert a dictionary into a Book instance.

    Parameters:
        data (dict): mapping with keys matching the Book serialization

    Returns:
        Book: deserialized Book object
    """
    return Book(
        data['id'],
        data['ISBNCode'],
        data['title'],
        data['author'],
        float(data['weight']),
        int(data['price']),
        bool(data.get('isBorrowed', False))
    )


def _book_to_dict(book: Book) -> dict:
    """Serialize a Book instance to a plain dictionary.

    The resulting dict matches the shape expected by the persistence layer
    (and by `_book_from_dict`).

    Parameters:
        book (Book): Book instance to serialize

    Returns:
        dict: serializable mapping of book fields
    """
    return {
        'id': book.get_id(),
        'ISBNCode': book.get_ISBNCode(),
        'title': book.get_title(),
        'author': book.get_author(),
        'weight': book.get_weight(),
        'price': book.get_price(),
        'isBorrowed': book.get_isBorrowed(),
    }


class BookRepository(BaseRepository[Book]):
    """Repository for persisting Book entities.

    This class specializes the generic BaseRepository to read and write
    Book objects using the JSON file defined in `FilePaths.BOOKS` by default.
    """

    def __init__(self, file_path: str = None):
        """Initialize the BookRepository.

        Parameters:
            file_path (str, optional): explicit path to the books file. If not
                provided, `FilePaths.BOOKS` is used.
        """
        path = file_path or FilePaths.BOOKS
        super().__init__(path, _book_from_dict, _book_to_dict)


__all__ = ['BookRepository']
