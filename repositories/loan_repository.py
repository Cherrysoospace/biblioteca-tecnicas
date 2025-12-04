"""Loan repository module.

This module provides a small repository implementation responsible for
reading and writing loan records to the configured JSON file. The
implementation intentionally follows the Single Responsibility Principle:
this repository only handles persistence and conversion between plain
Python dictionaries and :class:`models.loan.Loan` instances.
"""

from typing import List
from datetime import datetime
from models.loan import Loan
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _loan_from_dict(data: dict) -> Loan:
    """Create a :class:`Loan` instance from a dictionary.

    Expected keys in ``data``: ``loan_id``, ``user_id``, ``isbn``,
    ``loan_date`` (ISO string) and ``returned``. The ``loan_date`` field is
    parsed with :meth:`datetime.fromisoformat` when present; if missing or
    falsy, ``None`` is used which lets the :class:`Loan` constructor set the
    current UTC date.
    """
    loan = Loan(
        data.get('loan_id'),
        data.get('user_id'),
        data.get('isbn'),
        datetime.fromisoformat(data['loan_date']) if 'loan_date' in data and data['loan_date'] else None,
        data.get('returned', False)
    )

    return loan


def _loan_to_dict(loan: Loan) -> dict:
    """Serialize a :class:`Loan` instance to a plain dictionary.

    The returned dictionary uses ISO 8601 date strings for ``loan_date``
    when a date value is present; otherwise ``None`` is stored.
    """
    return {
        'loan_id': loan.get_loan_id(),
        'user_id': loan.get_user_id(),
        'isbn': loan.get_isbn(),
        'loan_date': loan.get_loan_date().isoformat() if loan.get_loan_date() else None,
        'returned': loan.is_returned()
    }


class LoanRepository(BaseRepository[Loan]):
    """Repository for loan persistence.

    Single responsibility: read and write loan records to the JSON file
    specified by :class:`utils.config.FilePaths.LOANS`. The class delegates
    conversion to the helper functions :func:`_loan_from_dict` and
    :func:`_loan_to_dict`.
    """

    def __init__(self, file_path: str = None):
        """Initialize the LoanRepository.

        Parameters
        ----------
        file_path : str, optional
            Path to the loans JSON file. If omitted, the default path from
            :class:`utils.config.FilePaths.LOANS` is used.
        """
        path = file_path or FilePaths.LOANS
        super().__init__(path, _loan_from_dict, _loan_to_dict)


__all__ = ['LoanRepository']
