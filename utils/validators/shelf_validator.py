"""Shelf validator module.

This module provides validation for Shelf entities, following the
Single Responsibility Principle.

Business rules:
- Name: optional, but if provided must not be only whitespace

Note:
- ID is generated automatically by the system (no validation needed)
- Capacity is a constant (MAX_CAPACITY = 8.0 kg, no user input)
"""

from typing import Optional
from utils.logger import LibraryLogger
from .exceptions import ValidationError

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class ShelfValidator:
    """Validator for the Shelf entity.

    Since ID is auto-generated and capacity is a constant,
    this validator only validates the optional shelf name.
    """
    
    @staticmethod
    def validate_name(name: Optional[str]) -> str:
        """Validate a shelf name.

        Rules
        -----
        - If provided, must not be only whitespace
        - Can be None or empty string
        - Must be a string type if not None

        Parameters
        ----------
        name : str or None
            Name to validate

        Returns
        -------
        str
            Validated name (empty string if None was provided)

        Raises
        ------
        ValidationError
            If the name is not a string or is whitespace only

        Examples
        --------
        >>> ShelfValidator.validate_name("Main Shelf")
        'Main Shelf'
        >>> ShelfValidator.validate_name(None)
        ''
        >>> ShelfValidator.validate_name("")
        ''
        >>> ShelfValidator.validate_name("   ")  # Raises ValidationError
        """
        if name is None:
            logger.debug("Shelf name is None, returning empty string")
            return ""
        
        if not isinstance(name, str):
            raise ValidationError("Shelf name must be a string")
        
        name_clean = name.strip()
        # Allow empty string, but not whitespace-only string
        if name and not name_clean:
            raise ValidationError("Shelf name must not be whitespace only")

        logger.debug(f"Validated shelf name: '{name_clean}'")
        return name_clean
