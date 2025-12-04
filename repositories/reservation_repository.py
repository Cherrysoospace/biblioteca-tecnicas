"""repositories.reservation_repository

Repository responsible for persistence of Reservation objects.

This module provides helpers to convert between plain dictionaries (as used
for JSON storage) and the `Reservation` model, and a small concrete
`ReservationRepository` implementation that delegates to the project's
`BaseRepository`.

Single responsibility: read/write operations for `reservations.json`.
"""

from typing import List
from datetime import datetime
from models.reservation import Reservation
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _reservation_from_dict(data: dict) -> Reservation:
    """Create a `Reservation` instance from a dictionary.

    The input dictionary is expected to follow the JSON storage format used
    by the repository (ISO-8601 date strings for datetimes). Missing or
    empty date fields are handled gracefully.

    Parameters
    ----------
    data : dict
        Dictionary with keys: reservation_id, user_id, isbn, reserved_date,
        status, assigned_date.

    Returns
    -------
    Reservation
        A populated Reservation object.
    """
    reservation = Reservation(
        data.get('reservation_id'),
        data.get('user_id'),
        data.get('isbn'),
        datetime.fromisoformat(data['reserved_date']) if 'reserved_date' in data and data['reserved_date'] else None,
        data.get('status', 'pending')
    )

    # Restore assigned_date if present
    if 'assigned_date' in data and data['assigned_date']:
        try:
            reservation.set_assigned_date(datetime.fromisoformat(data['assigned_date']))
        except Exception:
            # If parsing fails, leave the raw value (or None) as-is
            pass

    return reservation


def _reservation_to_dict(reservation: Reservation) -> dict:
    """Serialize a Reservation object to a plain dictionary for JSON storage.

    Datetime fields are converted to ISO 8601 strings when present; otherwise
    they are stored as None.

    Parameters
    ----------
    reservation : Reservation
        The reservation object to serialize.

    Returns
    -------
    dict
        Dictionary suitable for JSON encoding.
    """
    return {
        'reservation_id': reservation.get_reservation_id(),
        'user_id': reservation.get_user_id(),
        'isbn': reservation.get_isbn(),
        'reserved_date': reservation.get_reserved_date().isoformat() if reservation.get_reserved_date() else None,
        'status': reservation.get_status(),
        'assigned_date': reservation.get_assigned_date().isoformat() if reservation.get_assigned_date() else None
    }


class ReservationRepository(BaseRepository[Reservation]):
    """Repository for Reservation persistence.

    Single responsibility: load and save reservation records from the
    configured `reservations.json` file. This class adapts the generic
    `BaseRepository` with the appropriate (de)serialization helpers.
    """

    def __init__(self, file_path: str = None):
        """Initialize the reservation repository.

        Parameters
        ----------
        file_path : str, optional
            Optional path to the reservations file. If omitted the default
            path from `FilePaths.RESERVATIONS` will be used.
        """
        path = file_path or FilePaths.RESERVATIONS
        super().__init__(path, _reservation_from_dict, _reservation_to_dict)


__all__ = ['ReservationRepository']
