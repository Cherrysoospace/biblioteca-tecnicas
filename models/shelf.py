from typing import List, Optional, Dict, Any
from .Books import Book


class Shelf:
    """Shelf model that stores metadata and a collection of Book objects.

    The model remains intentionally lightweight (data holder). Business rules
    such as "can this book be added?" or operations on book objects are
    implemented in the service layer. However, capacity is a clear property
    of a physical shelf and is therefore defined and validated here.

    Contract (short):
    - inputs: id (str), optional list of Book objects, optional capacity (float)
    - outputs: object exposing read/write accessors for name and capacity
    - error modes: assigning capacity > MAX_CAPACITY or <= 0 raises ValueError
    """

    # maximum allowed capacity per project requirement
    MAX_CAPACITY: float = 8.0

    def __init__(self, id: str, books: Optional[List[Book]] = None, capacity: float = 8.0):
        # private attributes
        self.__id: str = id
        # store books as a simple list; service layer will manipulate it
        self.__books: List[Book] = books if books is not None else []
        # enforce numeric storage and basic validation on construction
        self.__capacity: float = float(capacity)
        if self.__capacity > self.MAX_CAPACITY:
            raise ValueError(f"capacity cannot exceed {self.MAX_CAPACITY} kg")
        if self.__capacity <= 0:
            raise ValueError("capacity must be a positive number")

        # optional human-readable name for the shelf (e.g., "Shelf A1")
        self.__name: str = ""

    # ID accessor
    def get_id(self) -> str:
        """Return the shelf's unique identifier."""
        return self.__id

    # Books accessor
    def get_books(self) -> List[Book]:
        """Return the list of books on this shelf."""
        return self.__books

    # Name accessors (kept for backward compatibility with code that used them)
    def get_name(self) -> str:
        """Return the shelf's human-readable name (may be empty)."""
        return self.__name

    def set_name(self, name: str) -> None:
        """Set a human-readable name for the shelf."""
        self.__name = name

    # Capacity property with validation - centralises the business rule in the model
    @property
    def capacity(self) -> float:
        """Current capacity (kg)."""
        return self.__capacity

    @capacity.setter
    def capacity(self, value: float) -> None:
        """Set capacity with validation against MAX_CAPACITY.

        Raises ValueError when value is invalid.
        """
        val = float(value)
        if val > self.MAX_CAPACITY:
            raise ValueError(f"capacity cannot exceed {self.MAX_CAPACITY} kg")
        if val <= 0:
            raise ValueError("capacity must be a positive number")
        self.__capacity = val

    # Simple helpers for persistence/inspection. Services may still implement
    # richer (book-level) serialization if Book objects require special handling.
    def to_dict(self) -> Dict[str, Any]:
        """Serialize shelf metadata to a plain dict.

        Notes:
        - Books are serialized using Book.to_dict() when available, otherwise
          we fall back to __dict__ or str(book). The service layer can replace
          or augment this strategy if a different representation is required.
        """
        books_serialized = []
        for b in self.__books:
            if hasattr(b, "to_dict"):
                books_serialized.append(b.to_dict())
            elif hasattr(b, "__dict__"):
                books_serialized.append(b.__dict__)
            else:
                books_serialized.append(str(b))

        return {
            "id": self.__id,
            "name": self.__name,
            "capacity": self.__capacity,
            # current_capacity representa la carga actual en kg (suma de pesos de los libros)
            "current_capacity": self.current_capacity(),
            "books": books_serialized,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Shelf":
        """Construct a Shelf from a dict produced by to_dict().

        Important: reconstruction of Book objects from dicts is intentionally
        left to the service layer (which knows the Book class and how to
        recreate instances). Here we only set basic metadata and leave the
        books list empty (or filled with raw dicts depending on use).
        """
        cap = data.get("capacity", cls.MAX_CAPACITY)
        # keep books empty; service should rebuild Book instances if needed
        shelf = cls(id=data.get("id"), books=None, capacity=cap)
        shelf.set_name(data.get("name", ""))
        return shelf

    def __str__(self):
        name_part = f", name: {self.__name}" if getattr(self, '_Shelf__name', None) else ""
        return f"Shelf[ID: {self.__id}{name_part}, books: {len(self.__books)} items, capacity: {self.__capacity}kg]"

    def current_capacity(self) -> float:
        """Return the current total weight (kg) of books on this shelf.

        Iterates over stored book objects (or dicts) and sums their weight when
        available. Silently ignores entries that lack parsable weight.
        """
        total = 0.0
        for b in self.__books:
            try:
                # Book instances expose get_weight(); dictionaries may include 'weight'
                if hasattr(b, 'get_weight'):
                    total += float(b.get_weight())
                elif isinstance(b, dict) and 'weight' in b:
                    total += float(b.get('weight', 0.0))
                else:
                    # try a numeric cast as a last resort
                    total += float(b)
            except Exception:
                # ignore unparseable entries
                continue
        return total
