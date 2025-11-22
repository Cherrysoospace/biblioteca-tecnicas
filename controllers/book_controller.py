from services.book_service import BookService
from models.Books import Book

class BookController:
    def __init__(self):
        self.service = BookService()

    def create_book(self, data):
        book = Book(
            data["id"],
            data["ISBNCode"],
            data["title"],
            data["author"],
            float(data["weight"]),
            int(data["price"]),
            bool(data.get("isBorrowed", False))
        )
        self.service.add_book(book)

    def update_book(self, book_id, data):
        self.service.update_book(book_id, data)

    def get_book(self, book_id):
        return self.service.find_by_id(book_id)
