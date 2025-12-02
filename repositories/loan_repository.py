"""loan_repository.py

Repositorio para la persistencia de préstamos.
Responsabilidad Única: Persistencia de datos de préstamos en loan.json

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List
from datetime import datetime
from models.loan import Loan
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _loan_from_dict(data: dict) -> Loan:
    """Convertir diccionario a objeto Loan."""
    loan = Loan(
        data.get('loan_id'),
        data.get('user_id'),
        data.get('isbn'),
        datetime.fromisoformat(data['loan_date']) if 'loan_date' in data and data['loan_date'] else None,
        data.get('returned', False)
    )
    
    return loan


def _loan_to_dict(loan: Loan) -> dict:
    """Convertir objeto Loan a diccionario."""
    return {
        'loan_id': loan.get_loan_id(),
        'user_id': loan.get_user_id(),
        'isbn': loan.get_isbn(),
        'loan_date': loan.get_loan_date().isoformat() if loan.get_loan_date() else None,
        'returned': loan.is_returned()
    }


class LoanRepository(BaseRepository[Loan]):
    """Repositorio para persistencia de préstamos.
    
    RESPONSABILIDAD única: Leer/escribir loan.json
    """
    
    def __init__(self, file_path: str = None):
        """Inicializar repositorio de préstamos."""
        path = file_path or FilePaths.LOANS
        super().__init__(path, _loan_from_dict, _loan_to_dict)


__all__ = ['LoanRepository']
