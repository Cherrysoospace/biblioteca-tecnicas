"""Loan validator module.

This module provides validation for Loan entities, following the
Single Responsibility Principle.

Business rules:
- user_id: not empty
- book_id: not empty
- isbn: valid format
"""

from utils.logger import LibraryLogger
from .user_validator import UserValidator
from .book_validator import BookValidator

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class LoanValidator:
    """Validator for the Loan entity.

    Provides static methods to validate loan-related data.
    """
    
    @staticmethod
    def validate_loan_data(user_id: str, book_id: str, isbn: str) -> dict:
        """Validate loan data.

        Parameters
        ----------
        user_id : str
        book_id : str
        isbn : str

        Returns
        -------
        dict
            Dictionary with validated data

        Raises
        ------
        ValidationError
            If any field is invalid
        """
        validated = {
            'user_id': UserValidator.validate_id(user_id),
            'book_id': BookValidator.validate_id(book_id),
            'isbn': BookValidator.validate_isbn(isbn),
        }
        
        logger.info(f"Loan data validated: user={validated['user_id']}, book={validated['book_id']}")
        return validated
