"""User model.

This module defines the simple `User` data model used across the
library management system. The model stores a user identifier and a
display name. Accessors and mutators are provided to maintain a small
encapsulation boundary.

Note: The class is intentionally minimal and does not perform
validation; callers are responsible for supplying appropriate values.
"""


class User:
    """Simple user data model.

    Attributes:
        __id (int | str): Unique identifier for the user.
        __name (str): Display/real name of the user.
    """

    def __init__(self, id, name):
        """Create a new User instance.

        Args:
            id (int | str): Unique identifier for the user. The type is
                intentionally flexible to support numeric or string-based
                IDs used elsewhere in the project.
            name (str): Full or display name of the user.
        """
        self.__id = id
        self.__name = name

    def get_id(self):
        """Return the user's identifier.

        Returns:
            int | str: The identifier provided when the user was created
                or last updated.
        """
        return self.__id
    
    def get_name(self):
        """Return the user's display name.

        Returns:
            str: The user's name.
        """
        return self.__name
    
    def set_id(self, id):
        """Set or update the user's identifier.

        Args:
            id (int | str): New identifier to assign to the user.
        """
        self.__id = id

    def set_name(self, name):
        """Set or update the user's display name.

        Args:
            name (str): New name to assign to the user.
        """
        self.__name = name
    
    def __str__(self):
        """Return a compact, human-readable representation of the user.

        This is primarily used for debugging and simple logging.
        """
        return f"User[ID: {self.__id}, Name: {self.__name}]"