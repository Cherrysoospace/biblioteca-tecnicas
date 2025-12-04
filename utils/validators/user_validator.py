"""User validator module.

This module provides validation for User entities, following the
Single Responsibility Principle.

Business rules:
- Name: not empty, not whitespace only
- ID: not empty (if provided)
"""

from utils.logger import LibraryLogger
from .exceptions import NameValidationError, IDValidationError

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class UserValidator:
    """Validator for the User entity.

    Provides static methods to validate user-related data.
    """
    
    @staticmethod
    def validate_name(name: str) -> str:
        """Validate a user name.

        Rules
        -----
        - Must not be empty
        - Must not be only whitespace
        - Minimum length: 1 character (excluding spaces)

        Parameters
        ----------
        name : str
            Name to validate

        Returns
        -------
        str
            Validated name with normalized whitespace

        Raises
        ------
        NameValidationError
            If the name is empty or invalid
        """
        if not name or not isinstance(name, str):
            raise NameValidationError("User name must not be empty")

        name_clean = name.strip()
        if not name_clean:
            raise NameValidationError("User name must not be empty or whitespace only")

        logger.debug(f"Validated user name: '{name_clean}'")
        return name_clean
    
    @staticmethod
    def validate_id(user_id: str) -> str:
        """Validate a user ID.

        Rules
        -----
        - Must not be empty
        - Must not be only whitespace

        Parameters
        ----------
        user_id : str
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
        if not user_id or not isinstance(user_id, str):
            raise IDValidationError("User ID must not be empty")

        id_clean = user_id.strip()
        if not id_clean:
            raise IDValidationError("User ID must not be empty or whitespace only")

        return id_clean
