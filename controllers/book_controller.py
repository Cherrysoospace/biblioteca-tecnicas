from services.book_service import BookService
from services.inventory_service import InventoryService
from models.Books import Book

class BookController:
    def __init__(self):
        self.service = BookService()

    def create_book(self, data):
        # If caller did not provide an id (or provided an empty one), generate
        # the next chronological id from the service.
        if not data.get("id"):
            try:
                data["id"] = self.service.generate_next_id()
            except Exception:
                # If generation fails for any reason, fall back to a simple
                # timestamp-based id to avoid blocking creation.
                import time

                data["id"] = f"B{int(time.time())}"

        book = Book(
            data["id"],
            data["ISBNCode"],
            data["title"],
            data["author"],
            float(data["weight"]),
            int(data["price"]),
            # stock is managed by Inventory; do not pass it to Book
            bool(data.get("isBorrowed", False))
        )
        # Persist book in catalog
        self.service.add_book(book)

        # Ensure inventory is updated: always add a new inventory entry for the
        # created Book (each physical copy has its own inventory record). The
        # persistence layer will still write a single 'stock' key per ISBN.
        try:
            inv_svc = InventoryService()
            try:
                inv_svc.add_item(book, 1)
            except Exception:
                # If add_item fails (e.g., duplicate id), don't block book creation.
                pass
        except Exception:
            # Do not block book creation if inventory update fails; surface
            # errors elsewhere or log if desired.
            pass

    def update_book(self, book_id, data):
        self.service.update_book(book_id, data)

    def get_book(self, book_id):
        return self.service.find_by_id(book_id)

    def get_all_books(self):
        """Return list of all Book objects from the service."""
        return self.service.get_all_books()
