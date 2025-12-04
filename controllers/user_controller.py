"""Controller layer for user-related UI interactions.

The controller provides thin wrappers that connect a presentation
layer (UI) to the :class:`services.user_service.UserService`.
Methods are intentionally simple and delegate validation and
persistence to the service layer.
"""

from services.user_service import UserService
from models.user import User


class UserController:
    """Controller that connects the UI with :class:`UserService`.

    The controller exposes simple methods used by UI components. All
    business logic and validation live in the service layer; the
    controller acts as a call-through adapter.
    """

    def __init__(self):
        """Create a controller instance with a default service.

        For unit testing, consider injecting a mock or test
        :class:`UserService` instance instead of using the default.
        """
        self.service = UserService()

    def create_user(self, name: str) -> User:
        """Create a new user and return the created model.

        Args:
            name (str): Display name for the new user.

        Returns:
            User: The newly created user instance.
        """
        user = self.service.create_user(name)
        return user

    def update_user(self, original_id: str, new_data: dict) -> None:
        """Update an existing user.

        Args:
            original_id (str): Identifier of the user to update.
            new_data (dict): Mapping of fields to update (e.g., {'name': 'New'}).
        """
        self.service.update_user(original_id, new_data)

    def delete_user(self, id: str) -> None:
        """Delete a user by identifier.

        Args:
            id (str): Identifier of the user to delete.
        """
        self.service.delete_user(id)

    def get_all_users(self) -> list:
        """Return all users in insertion order.

        Returns:
            list: A list of :class:`models.user.User` instances.
        """
        return self.service.get_all_users()

    def find_by_id(self, id: str) -> User:
        """Find and return a user by identifier.

        Args:
            id (str): Identifier to search for.

        Returns:
            User | None: Matching user or ``None`` if not found.
        """
        return self.service.find_by_id(id)

    def find_by_name(self, name: str) -> list:
        """Find users whose names match the provided term.

        Args:
            name (str): Search term.

        Returns:
            list: List of matching :class:`models.user.User` instances.
        """
        return self.service.find_by_name(name)
