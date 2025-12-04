"""Book validator module.

This module provides validation for Book entities, following the
Single Responsibility Principle.

Business rules:
- ISBN: at most 13 digits (may include hyphens)
- Title: non-empty, not whitespace
- Author: non-empty, not whitespace
- Weight: > 0 (kg)
- Price: > 0 (COP)
"""

from typing import Any, Optional
import re
from utils.logger import LibraryLogger
from .exceptions import (
    ISBNValidationError,
    PriceValidationError,
    WeightValidationError,
    NameValidationError,
    IDValidationError,
)

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class BookValidator:
    """Validator for the Book entity.

    Provides static methods to validate book-related data.
    """
    
    @staticmethod
    def validate_isbn(isbn: str) -> str:
        """Validate an ISBN string.

        Rules
        -----
        - Must not be empty
        - At most 13 digits (ignoring hyphens/spaces)
        - May include hyphens and spaces

        Parameters
        ----------
        isbn : str
            ISBN to validate

        Returns
        -------
        str
            The validated and trimmed ISBN

        Raises
        ------
        ISBNValidationError
            If the ISBN does not meet the rules

        Example
        -------
        >>> BookValidator.validate_isbn("978-3-16-148410-0")  # valid
        '978-3-16-148410-0'
        >>> BookValidator.validate_isbn("12345678901234")     # 14 digits
        ISBNValidationError: ISBN must have at most 13 digits
        """
        if not isbn or not isinstance(isbn, str):
            raise ISBNValidationError("ISBN must not be empty")
        
        isbn_clean = isbn.strip()
        if not isbn_clean:
            raise ISBNValidationError("ISBN must not be empty")
        
        # Extraer solo dígitos (ignorar guiones y espacios)
        digits_only = re.sub(r'[^0-9]', '', isbn_clean)
        
        if not digits_only:
            raise ISBNValidationError("ISBN must contain at least one digit")
        
        if len(digits_only) > 13:
            raise ISBNValidationError(
                f"ISBN must have at most 13 digits (found: {len(digits_only)})"
            )

        logger.debug(f"Validated ISBN: {isbn_clean} ({len(digits_only)} digits)")
        return isbn_clean
    
    @staticmethod
    def validate_title(title: str) -> str:
        """Validate a book title.

        Rules
        -----
        - Must not be empty
        - Must not be only whitespace
        - Minimum length: 1 character (excluding spaces)

        Parameters
        ----------
        title : str
            Title to validate

        Returns
        -------
        str
            Validated title with normalized whitespace

        Raises
        ------
        NameValidationError
            If the title is empty or invalid
        """
        if not title or not isinstance(title, str):
            raise NameValidationError("Title must not be empty")
        
        title_clean = title.strip()
        if not title_clean:
            raise NameValidationError("Title must not be empty or whitespace only")

        logger.debug(f"Validated title: '{title_clean}'")
        return title_clean
    
    @staticmethod
    def validate_author(author: str) -> str:
        """Validate an author name.

        Rules
        -----
        - Must not be empty
        - Must not be only whitespace

        Parameters
        ----------
        author : str
            Author name to validate

        Returns
        -------
        str
            Validated author name with normalized whitespace

        Raises
        ------
        NameValidationError
            If the name is empty or invalid
        """
        if not author or not isinstance(author, str):
            raise NameValidationError("Author name must not be empty")
        
        author_clean = author.strip()
        if not author_clean:
            raise NameValidationError("Author name must not be empty or whitespace only")

        logger.debug(f"Validated author: '{author_clean}'")
        return author_clean
    
    @staticmethod
    def validate_weight(weight: Any) -> float:
        """Validate the book weight.

        Rules
        -----
        - Must be convertible to float
        - Must be > 0 (weight in kg)

        Parameters
        ----------
        weight : Any
            Weight to validate (int, float, or str)

        Returns
        -------
        float
            Validated weight

        Raises
        ------
        WeightValidationError
            If weight is <= 0 or not convertible to a number
        """
        try:
            weight_float = float(weight)
        except (ValueError, TypeError):
            raise WeightValidationError(
                f"Weight must be a valid number (received: {weight})"
            )
        
        if weight_float <= 0:
            raise WeightValidationError(
                f"Weight must be greater than 0 kg (received: {weight_float})"
            )

        logger.debug(f"Validated weight: {weight_float} kg")
        return weight_float
    
    @staticmethod
    def validate_price(price: Any) -> int:
        """Validate the book price.

        Rules
        -----
        - Must be convertible to int
        - Must be > 0 (price in COP)

        Parameters
        ----------
        price : Any
            Price to validate (int, float, or str)

        Returns
        -------
        int
            Validated price

        Raises
        ------
        PriceValidationError
            If the price is <= 0 or not convertible to a number
        """
        try:
            price_int = int(price)
        except (ValueError, TypeError):
            raise PriceValidationError(
                f"Price must be a valid integer (received: {price})"
            )
        
        if price_int <= 0:
            raise PriceValidationError(
                f"Price must be greater than 0 COP (received: {price_int})"
            )

        logger.debug(f"Validated price: {price_int} COP")
        return price_int
    
    @staticmethod
    def validate_book_data(
        isbn: str,
        title: str,
        author: str,
        weight: Any,
        price: Any,
        book_id: Optional[str] = None
    ) -> dict:
        """Validate all fields of a book.

        Parameters
        ----------
        isbn : str
        title : str
        author : str
        weight : Any
        price : Any
        book_id : str, optional
            Book ID (validated only if provided)

        Returns
        -------
        dict
            Dictionary with validated data:
            {
                'isbn': str,
                'title': str,
                'author': str,
                'weight': float,
                'price': int,
                'book_id': str (if provided)
            }

        Raises
        ------
        ValidationError
            If any field is invalid
        """
        validated = {
            'isbn': BookValidator.validate_isbn(isbn),
            'title': BookValidator.validate_title(title),
            'author': BookValidator.validate_author(author),
            'weight': BookValidator.validate_weight(weight),
            'price': BookValidator.validate_price(price),
        }
        
        if book_id is not None:
            validated['book_id'] = BookValidator.validate_id(book_id)

        logger.info(f"Book data validated: ISBN={validated['isbn']}, Title={validated['title']}")
        return validated
    
    @staticmethod
    def validate_id(book_id: str) -> str:
        """Validate a book ID.

        Rules
        -----
        - Must not be empty
        - Must not be only whitespace

        Parameters
        ----------
        book_id : str
            ID to validate

        Returns
        -------
        str
            Validated ID

        Raises
        ------
        IDValidationError
            If the ID is invalid
        """
        if not book_id or not isinstance(book_id, str):
            raise IDValidationError("Book ID must not be empty")
        
        id_clean = book_id.strip()
        if not id_clean:
            raise IDValidationError("Book ID must not be empty or whitespace only")

        return id_clean
