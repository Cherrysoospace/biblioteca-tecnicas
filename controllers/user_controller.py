from services.user_service import UserService
from models.user import User

class UserController:
    """Controller that connects the UI with UserService."""

    def __init__(self):
        self.service = UserService()

    def create_user(self, name: str):
        """Create a new user. ID is generated automatically by the service."""
        user = self.service.create_user(name)
        return user

    def update_user(self, original_id: str, new_data: dict):
        """Update an existing user."""
        self.service.update_user(original_id, new_data)

    def delete_user(self, id: str):
        """Delete a user by ID."""
        self.service.delete_user(id)

    def get_all_users(self):
        """Return all users."""
        return self.service.get_all_users()

    def find_by_id(self, id: str):
        """Find user by ID."""
        return self.service.find_by_id(id)

    def find_by_name(self, name: str):
        """Find users by name."""
        return self.service.find_by_name(name)
