class Book:
    """Represents a book in the system.

    Note: stock is handled by a separate inventory layer, so this class does not
    store stock information.

    Private attributes:
        __id: internal identifier for the book (type is flexible to match the app)
        __ISBNCode: book ISBN code (str)
        __title: book title (str)
        __author: book author (str)
        __weight: book weight (float)
        __price: book price (int or float)
        __isBorrowed: bool indicating whether the book is currently borrowed
    """

    def __init__(self, id, ISBNCode, title, author, weight, price, isBorrowed: bool = False):
        """Initialize a Book instance.

        Parameters:
            id: unique identifier for the book (int or str depending on the app).
            ISBNCode (str): ISBN code of the book.
            title (str): title of the book.
            author (str): author name.
            weight (float): physical weight of the book (consistent unit within project).
            price (int|float): price of the book in the app currency.
            isBorrowed (bool, optional): whether the book is borrowed; defaults to False.

        Returns:
            None
        """
        self.__id = id
        self.__ISBNCode = ISBNCode  # String
        self.__title = title  # String
        self.__author = author  # String
        self.__weight = weight  # float
        self.__price = price  # int
        # stock is managed by Inventory; Book no longer stores stock
        self.__isBorrowed = bool(isBorrowed)

    # Getters
    def get_id(self):
        """Return the book's internal identifier.

        Returns:
            The id value as stored (flexible type).
        """
        return self.__id

    def get_ISBNCode(self):
        """Return the book's ISBN code.

        Returns:
            str: the ISBN code.
        """
        return self.__ISBNCode

    def get_title(self):
        """Return the book's title.

        Returns:
            str: the title.
        """
        return self.__title

    def get_author(self):
        """Return the book's author.

        Returns:
            str: the author.
        """
        return self.__author

    def get_weight(self):
        """Return the book's weight.

        Returns:
            float: the physical weight of the book.
        """
        return self.__weight

    def get_price(self):
        """Return the book's price.

        Returns:
            int|float: the price.
        """
        return self.__price

    def get_isBorrowed(self):
        """Indicate whether the book is currently borrowed.

        Returns:
            bool: True if the book is borrowed, False otherwise.
        """
        return self.__isBorrowed

    # Setters
    def set_ISBNCode(self, ISBNCode):
        """Set or update the book's ISBN code.

        Parameters:
            ISBNCode (str): the new ISBN code.
        """
        self.__ISBNCode = ISBNCode

    def set_title(self, title):
        """Set or update the book's title.

        Parameters:
            title (str): the new title.
        """
        self.__title = title

    def set_author(self, author):
        """Set or update the book's author.

        Parameters:
            author (str): the new author.
        """
        self.__author = author

    def set_weight(self, weight):
        """Set or update the book's weight.

        Parameters:
            weight (float): the new weight.
        """
        self.__weight = weight

    def set_price(self, price):
        """Set or update the book's price.

        Parameters:
            price (int|float): the new price.
        """
        self.__price = price

    def set_isBorrowed(self, isBorrowed):
        """Mark the book as borrowed or available.

        Parameters:
            isBorrowed (bool): True to mark as borrowed, False to mark available.
        """
        self.__isBorrowed = isBorrowed

    def set_id(self, id):
        """Update the book's internal identifier.

        Warning: changing identifiers can break references in other structures
        (for example, repositories or inventories). Use with caution.

        Parameters:
            id: the new identifier (same type expected by the application).
        """
        self.__id = id

    def __str__(self):
        """Human-readable representation of the book.

        Returns a string with the main book fields useful for logging and debugging.
        """
        return f"Book[ID: {self.__id}, ISBNCode: {self.__ISBNCode}, Title: {self.__title}, Author: {self.__author}, Weight: {self.__weight}, Price: {self.__price}]"
