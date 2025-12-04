"""Reservation validator module.

This module provides validation for Reservation entities, following the
Single Responsibility Principle.

Business rules:
- user_id: not empty
- isbn: valid format
"""

from utils.logger import LibraryLogger
from .user_validator import UserValidator
from .book_validator import BookValidator

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class ReservationValidator:
    """Validator for the Reservation entity.

    Provides static methods to validate reservation-related data.
    """
    
    @staticmethod
    def validate_reservation_data(user_id: str, isbn: str) -> dict:
        """Validate reservation data.

        Parameters
        ----------
        user_id : str
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
            'isbn': BookValidator.validate_isbn(isbn),
        }
        
        logger.info(f"Reservation data validated: user={validated['user_id']}, isbn={validated['isbn']}")
        return validated
