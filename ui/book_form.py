import customtkinter as ctk
from controllers.book_controller import BookController

class BookForm(ctk.CTkToplevel):
    def __init__(self, parent=None, mode="create", book_id=None):
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)

        # Ensure window is initially visible and properly titled
        self.title("Book Manager")
        self.geometry("500x600")

        self.controller = BookController()
        self.mode = mode
        self.book_id = book_id

        # Campos
        self.entry_id = ctk.CTkEntry(self, placeholder_text="ID")
        self.entry_id.pack(pady=5)

        self.entry_isbn = ctk.CTkEntry(self, placeholder_text="ISBN")
        self.entry_isbn.pack(pady=5)

        self.entry_title = ctk.CTkEntry(self, placeholder_text="Título")
        self.entry_title.pack(pady=5)

        self.entry_author = ctk.CTkEntry(self, placeholder_text="Autor")
        self.entry_author.pack(pady=5)

        self.entry_weight = ctk.CTkEntry(self, placeholder_text="Peso")
        self.entry_weight.pack(pady=5)

        self.entry_price = ctk.CTkEntry(self, placeholder_text="Precio")
        self.entry_price.pack(pady=5)

        self.entry_stock = ctk.CTkEntry(self, placeholder_text="Stock")
        self.entry_stock.pack(pady=5)

        # Botón según modo
        if mode == "create":
            btn = ctk.CTkButton(self, text="Crear Libro", command=self.create_book)
        else:
            btn = ctk.CTkButton(self, text="Actualizar Libro", command=self.update_book)

        btn.pack(pady=20)

        # Si estás en modo edición, carga los datos
        if mode == "edit" and book_id:
            self.load_book()

    def load_book(self):
        book = self.controller.get_book(self.book_id)
        if not book:
            return
        
        self.entry_id.insert(0, book.get_id())
        self.entry_id.configure(state="disabled")

        self.entry_isbn.insert(0, book.get_ISBNCode())
        self.entry_title.insert(0, book.get_title())
        self.entry_author.insert(0, book.get_author())
        self.entry_weight.insert(0, book.get_weight())
        self.entry_price.insert(0, book.get_price())
        self.entry_stock.insert(0, book.get_stock())

    def create_book(self):
        data = {
            "id": self.entry_id.get(),
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
            # parse stock safely; default to 1 when empty
            "stock": int(self.entry_stock.get()) if self.entry_stock.get().strip() else 1,
        }

        try:
            self.controller.create_book(data)
            ctk.CTkLabel(self, text="Libro creado exitosamente!").pack()
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def update_book(self):
        data = {
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
            "stock": int(self.entry_stock.get()) if self.entry_stock.get().strip() else 1,
        }

        try:
            self.controller.update_book(self.book_id, data)
            ctk.CTkLabel(self, text="Libro actualizado!").pack()
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

