"""Custom validation exceptions for the Library Management System.

This module defines all validation-related exceptions used across
the validation framework.
"""


class ValidationError(ValueError):
    """Base exception for validation errors.

    Raised when input data does not meet business rules.
    """
    pass


class ISBNValidationError(ValidationError):
    """Raised when an ISBN is invalid or malformed."""
    pass


class PriceValidationError(ValidationError):
    """Raised when a price is invalid (negative, zero, or non-numeric)."""
    pass


class WeightValidationError(ValidationError):
    """Raised when a weight is invalid (negative or non-numeric)."""
    pass


class NameValidationError(ValidationError):
    """Raised when a name is invalid (empty or whitespace only)."""
    pass


class IDValidationError(ValidationError):
    """Raised when an identifier is invalid (empty or incorrect format)."""
    pass
