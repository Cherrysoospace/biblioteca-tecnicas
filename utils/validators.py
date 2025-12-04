"""validators.py

DEPRECATED: This module is maintained for backward compatibility only.

All validation classes have been moved to separate modules in the
validators package following the Single Responsibility Principle.

New imports should use:
    from utils.validators import BookValidator, UserValidator, etc.

This module re-exports all validators from the new package structure.
"""

# Re-export all validators from the new package structure
# This maintains backward compatibility with existing code
from utils.validators.exceptions import (
    ValidationError,
    ISBNValidationError,
    PriceValidationError,
    WeightValidationError,
    NameValidationError,
    IDValidationError,
)
from utils.validators.book_validator import BookValidator
from utils.validators.user_validator import UserValidator
from utils.validators.loan_validator import LoanValidator
from utils.validators.reservation_validator import ReservationValidator
from utils.validators.shelf_validator import ShelfValidator


__all__ = [
    'ValidationError',
    'ISBNValidationError',
    'PriceValidationError',
    'WeightValidationError',
    'NameValidationError',
    'IDValidationError',
    'BookValidator',
    'UserValidator',
    'LoanValidator',
    'ReservationValidator',
]
