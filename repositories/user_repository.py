"""user_repository.py

Repositorio para la persistencia de usuarios.
Responsabilidad Única: Persistencia de datos de usuarios en users.json

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List
from models.user import User
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _user_from_dict(data: dict) -> User:
    """Convertir diccionario a objeto User."""
    return User(data['id'], data['name'])


def _user_to_dict(user: User) -> dict:
    """Convertir objeto User a diccionario."""
    return {
        'id': user.get_id(),
        'name': user.get_name()
    }


class UserRepository(BaseRepository[User]):
    """Repositorio para persistencia de usuarios.
    
    RESPONSABILIDAD Única: Leer/escribir users.json
    """
    
    def __init__(self, file_path: str = None):
        """Inicializar repositorio de usuarios."""
        path = file_path or FilePaths.USERS
        super().__init__(path, _user_from_dict, _user_to_dict)


__all__ = ['UserRepository']
