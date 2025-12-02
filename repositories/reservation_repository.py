"""reservation_repository.py

Repositorio para la persistencia de reservaciones.
Responsabilidad Única: Persistencia de datos de reservaciones en reservations.json

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List
from datetime import datetime
from models.reservation import Reservation
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _reservation_from_dict(data: dict) -> Reservation:
    """Convertir diccionario a objeto Reservation."""
    reservation = Reservation(
        data.get('reservation_id'),
        data.get('user_id'),
        data.get('isbn'),
        datetime.fromisoformat(data['reserved_date']) if 'reserved_date' in data and data['reserved_date'] else None,
        data.get('status', 'pending')
    )
    
    # Restaurar fecha de asignación si existe
    if 'assigned_date' in data and data['assigned_date']:
        try:
            reservation.set_assigned_date(datetime.fromisoformat(data['assigned_date']))
        except Exception:
            pass
    
    # Restaurar posición si existe
    if 'position' in data:
        try:
            reservation.set_position(data['position'])
        except Exception:
            pass
    
    return reservation


def _reservation_to_dict(reservation: Reservation) -> dict:
    """Convertir objeto Reservation a diccionario."""
    return {
        'reservation_id': reservation.get_reservation_id(),
        'user_id': reservation.get_user_id(),
        'isbn': reservation.get_isbn(),
        'reserved_date': reservation.get_reserved_date().isoformat() if reservation.get_reserved_date() else None,
        'status': reservation.get_status(),
        'assigned_date': reservation.get_assigned_date().isoformat() if reservation.get_assigned_date() else None,
        'position': reservation.get_position()
    }


class ReservationRepository(BaseRepository[Reservation]):
    """Repositorio para persistencia de reservaciones.
    
    RESPONSABILIDAD única: Leer/escribir reservations.json
    """
    
    def __init__(self, file_path: str = None):
        """Inicializar repositorio de reservaciones."""
        path = file_path or FilePaths.RESERVATIONS
        super().__init__(path, _reservation_from_dict, _reservation_to_dict)


__all__ = ['ReservationRepository']
