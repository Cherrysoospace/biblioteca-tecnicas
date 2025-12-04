"""User repository.

This module provides persistence for `User` entities stored in the
`users.json` file. It exposes a lightweight repository class that
specializes the generic `BaseRepository` to perform serialization and
deserialization between Python `User` objects and JSON-compatible
dictionaries.

The repository is responsible only for I/O and transformation; it does
not enforce business rules or validation.

Author: Library Management System
Date: 2025-12-02
"""

from typing import List
from models.user import User
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _user_from_dict(data: dict) -> User:
    """Deserialize a dictionary into a :class:`models.user.User`.

    Args:
        data (dict): A mapping containing at least the keys ``'id'`` and
            ``'name'`` as produced by :func:`_user_to_dict` or by the
            on-disk JSON representation.

    Returns:
        User: A new ``User`` instance populated from ``data``.
    """
    return User(data['id'], data['name'])


def _user_to_dict(user: User) -> dict:
    """Serialize a :class:`models.user.User` into a JSON-compatible dict.

    Args:
        user (User): The user instance to serialize.

    Returns:
        dict: A mapping with the user's fields suitable for JSON
        persistence (keys: ``'id'``, ``'name'``).
    """
    return {
        'id': user.get_id(),
        'name': user.get_name()
    }


class UserRepository(BaseRepository[User]):
    """Repository for persisting :class:`models.user.User` objects.

    This class specializes :class:`repositories.base_repository.BaseRepository`
    by supplying the concrete serialization and deserialization helpers
    for `User` objects and by defaulting the storage path to the
    configured users file.

    The repository delegates all CRUD operations to the base class and
    only provides the conversion functions required by that generic
    implementation.
    """

    def __init__(self, file_path: str = None):
        """Initialize the user repository.

        Args:
            file_path (str, optional): Optional filesystem path to use for
                persistent storage. If not provided, the repository will
                use the default path configured in :mod:`utils.config`.
        """
        path = file_path or FilePaths.USERS
        super().__init__(path, _user_from_dict, _user_to_dict)


__all__ = ['UserRepository']
