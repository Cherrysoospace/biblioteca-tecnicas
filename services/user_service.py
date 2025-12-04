"""Service layer for managing users.

This module implements the application-level operations for a simple
user catalog. Responsibilities include ID generation, input
validation, and maintaining in-memory views that mirror the persisted
data. Persistence is delegated to :class:`repositories.user_repository.UserRepository`.

The service keeps two in-memory lists:
 - ``users_general``: insertion-order list loaded from the repository.
 - ``users_sorted``: name-sorted view, rebuilt when the catalog changes.

The implementation intentionally focuses on business logic and avoids
performing low-level I/O directly.
"""

import os
import json
from typing import List, Optional, Dict, Any

from models.user import User
from repositories.user_repository import UserRepository
from utils.validators import UserValidator, ValidationError
from utils.logger import LibraryLogger

# Configure module logger
logger = LibraryLogger.get_logger(__name__)


class UserService:
    """Service for managing a simple user catalog.

    The service provides CRUD operations and an ID generation helper
    used when creating new users. It validates inputs via
    :mod:`utils.validators` and persists changes through the provided
    repository.
    """

    def __init__(self, repository: UserRepository = None):
        """Initialize the service.

        Args:
            repository (UserRepository, optional): Repository instance to
                use for persistence. If omitted, a default
                :class:`UserRepository` will be created.

        Raises:
            ValueError: If persisted data is malformed when loading.
            Exception: For general I/O errors during initial load.
        """
        self.repository = repository or UserRepository()

        self.users_general: List[User] = []
        self.users_sorted: List[User] = []

        self._load_users()

    # Persistence (delegated to repository)
    def _load_users(self) -> None:
        """Load users from the repository and build the sorted view.

        The method reads all users using the repository's ``load_all``
        and constructs a name-sorted copy for fast read-only access.

        Raises:
            ValueError: If the persisted data is malformed.
            Exception: For I/O-related errors.
        """
        self.users_general = self.repository.load_all()
        # Build sorted list using builtin sort by name
        self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

    def _save_users(self) -> None:
        """Persist the current ``users_general`` list via the repository.

        Raises:
            Exception: For I/O errors while writing.
        """
        self.repository.save_all(self.users_general)

    # CRUD operations
    def add_user(self, user: User) -> None:
        """Validate and add a user to the catalog, then persist.

        Args:
            user (User): User instance to add.

        Raises:
            ValidationError: If the user's data is invalid.
            ValueError: If a user with the same id already exists.
            Exception: For I/O errors while persisting.
        """
        try:
            UserValidator.validate_name(user.get_name())
            UserValidator.validate_id(user.get_id())
        except ValidationError as e:
            logger.error(f"Validation failed while adding user: {e}")
            raise

        if any(u.get_id() == user.get_id() for u in self.users_general):
            raise ValueError(f"A user with id '{user.get_id()}' already exists")

        self.users_general.append(user)
        # Rebuild sorted view
        self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

        self._save_users()
        logger.info(f"User added: id={user.get_id()}, name={user.get_name()}")

    def create_user(self, name: str) -> User:
        """Create, validate, and persist a new user with an auto-generated ID.

        ID generation strategy:
        - Prefer IDs of the form ``U###`` where ``###`` is a zero-padded
          integer. The next integer is computed from existing IDs.
        - If a collision occurs, a suffix such as ``-1`` is appended until
          a unique ID is produced.

        Args:
            name (str): Display name for the new user.

        Returns:
            User: The newly created and persisted user instance.

        Raises:
            ValidationError: If the provided name is invalid.
        """
        try:
            name_clean = UserValidator.validate_name(name)
        except ValidationError as e:
            logger.error(f"Validation failed creating user: {e}")
            raise

        # Collect existing ids
        existing_ids = {u.get_id() for u in self.users_general}
        # Find numeric suffixes for IDs like U123
        max_n = 0
        for uid in existing_ids:
            if isinstance(uid, str) and uid.startswith('U'):
                num_part = uid[1:]
                if num_part.isdigit():
                    try:
                        val = int(num_part)
                        if val > max_n:
                            max_n = val
                    except Exception:
                        pass

        base_num = max_n + 1
        new_id = f"U{base_num:03d}"
        # Ensure uniqueness by appending suffixes if required
        counter = 1
        while new_id in existing_ids:
            new_id = f"U{base_num:03d}-{counter}"
            counter += 1

        from models.user import User as UserModel
        user = UserModel(new_id, name_clean)
        self.add_user(user)
        logger.info(f"User created: id={new_id}, name={name_clean}")
        return user

    def get_all_users(self) -> List[User]:
        """Return all users in insertion order.

        Returns:
            List[User]: A shallow copy of the insertion-order list.
        """
        return list(self.users_general)

    def find_by_id(self, id: str) -> Optional[User]:
        """Find a user by unique identifier using a linear scan.

        Args:
            id (str): Identifier to search for.

        Returns:
            Optional[User]: The matching user or ``None`` if not found.
        """
        for u in self.users_general:
            if u.get_id() == id:
                return u
        return None

    def find_by_name(self, name: str) -> List[User]:
        """Search for users whose name contains the given term (case-insensitive).

        Args:
            name (str): Search term to match within user names.

        Returns:
            List[User]: List of matching users; may be empty.
        """
        if not name:
            return []

        # Normalize search term using provided helper
        from utils.search_helpers import normalizar_texto
        search_term = normalizar_texto(name)

        matching_users: List[User] = []
        for user in self.users_general:
            user_name = normalizar_texto(user.get_name())
            if search_term in user_name:
                matching_users.append(user)

        return matching_users

    def update_user(self, id: str, new_data: Dict[str, Any]) -> None:
        """Update fields of an existing user and persist changes.

        Only keys present in ``new_data`` are updated. Allowed keys:
        ``'id'`` and ``'name'``.

        Args:
            id (str): Identifier of the user to update.
            new_data (dict): Mapping of fields to new values.

        Raises:
            ValueError: If the user is not found or the new id collides
                with an existing user.
            Exception: For I/O errors while persisting.
        """
        user = self.find_by_id(id)
        if user is None:
            raise ValueError(f"No user found with id '{id}'")

        if 'id' in new_data:
            new_id = new_data['id']
            if new_id != id and any(u.get_id() == new_id for u in self.users_general):
                raise ValueError(f"Cannot update id: another user with id '{new_id}' already exists")

        if 'id' in new_data:
            user.set_id(new_data['id'])
        if 'name' in new_data:
            user.set_name(new_data['name'])

        # Rebuild the sorted view after update
        self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

        self._save_users()

    def delete_user(self, id: str) -> None:
        """Remove a user by id from both in-memory lists and persist.

        Args:
            id (str): Identifier of the user to delete.

        Raises:
            ValueError: If no user with the given id exists.
            Exception: For I/O errors while persisting.
        """
        user = self.find_by_id(id)
        if user is None:
            raise ValueError(f"No user found with id '{id}'")

        self.users_general = [u for u in self.users_general if u.get_id() != id]
        self.users_sorted = [u for u in self.users_sorted if u.get_id() != id]

        self._save_users()


# Example usage (commented):
# svc = UserService()
# svc.add_user(User('u1','Alice'))
# print([u.get_name() for u in svc.get_all_users()])

