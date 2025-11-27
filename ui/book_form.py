import os
import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None
from controllers.book_controller import BookController
from ui import theme
from ui import widget_factory as wf

class BookForm(ctk.CTkToplevel):
    def __init__(self, parent=None, mode="create", book_id=None):
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)
        # keep parent reference to restore focus when closing
        self._parent_window = parent
        # Apply theme colors to this window and create a main container to match MainMenu
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # Load twemoji assets (defensive)
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "twemoji")
        try:
            # load bookpile icon for consistency with main menu
            self.icon_book = ctk.CTkImage(Image.open(os.path.join(assets_path, "bookpile.png")), size=(36, 36))
        except Exception:
            self.icon_book = None

        # Ensure window is initially visible and properly titled
        self.title("Book Manager")
        self.geometry("500x600")

        self.controller = BookController()
        self.mode = mode
        self.book_id = book_id

        # Main container (keeps spacing and background consistent)
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title area
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 12))
        if self.icon_book is not None:
            icon_lbl = ctk.CTkLabel(title_frame, image=self.icon_book, text="")
            icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = wf.create_title_label(title_frame, "Crear Libro")
        title_lbl.pack(side="left")

        # Form fields placed in a simple vertical stack inside the container
        form_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        form_frame.pack(expand=True, fill="both")

        # Campos
        # For create mode we show an ID entry but disabled and with a hint
        # (the controller/service will auto-generate the ID). In edit mode we
        # allow showing the current ID but keep it disabled so it can't be
        # changed.
        id_placeholder = "ID" if mode == "edit" else "Auto (se asignará)"
        self.entry_id = ctk.CTkEntry(form_frame, placeholder_text=id_placeholder)
        self.entry_id.pack(pady=6, fill="x")
        if mode == "create":
            try:
                # disable manual editing in create mode
                self.entry_id.configure(state="disabled")
            except Exception:
                pass

        self.entry_isbn = ctk.CTkEntry(form_frame, placeholder_text="ISBN")
        self.entry_isbn.pack(pady=6, fill="x")

        self.entry_title = ctk.CTkEntry(form_frame, placeholder_text="Título")
        self.entry_title.pack(pady=6, fill="x")

        self.entry_author = ctk.CTkEntry(form_frame, placeholder_text="Autor")
        self.entry_author.pack(pady=6, fill="x")

        self.entry_weight = ctk.CTkEntry(form_frame, placeholder_text="Peso")
        self.entry_weight.pack(pady=6, fill="x")

        self.entry_price = ctk.CTkEntry(form_frame, placeholder_text="Precio")
        self.entry_price.pack(pady=6, fill="x")

        # Action button area (primary + small 'Regresar' cancel button)
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(12, 6))

        # Botón según modo
        if mode == "create":
            btn = wf.create_primary_button(action_frame, text="Crear Libro", command=self.create_book)
        else:
            btn = wf.create_primary_button(action_frame, text="Actualizar Libro", command=self.update_book)

        # small cancel/back button to return to main menu
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_cancel)

        # pack side-by-side for better UX
        btn.pack(side="left", padx=(0, 8), pady=6)
        cancel_btn.pack(side="left", pady=6)

        # Si estás en modo edición, carga los datos
        if mode == "edit" and book_id:
            self.load_book()

        # Ensure closing via window manager also triggers our cancel logic
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        except Exception:
            pass

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
        # stock is managed by InventoryService (calculated from inventory entries)
        # the form does not allow editing stock directly

    def create_book(self):
        data = {
            "id": self.entry_id.get(),
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
        }

        try:
            self.controller.create_book(data)
            # Close form after successful creation and restore main menu focus
            try:
                self._on_cancel()
            except Exception:
                try:
                    ctk.CTkLabel(self, text="Libro creado exitosamente!").pack()
                except Exception:
                    pass
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def update_book(self):
        data = {
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
        }

        try:
            self.controller.update_book(self.book_id, data)
            ctk.CTkLabel(self, text="Libro actualizado!").pack()
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def _on_cancel(self):
        """Close this form and return focus to the parent/main menu."""
        try:
            # destroy this toplevel
            self.destroy()
        except Exception:
            try:
                self.withdraw()
            except Exception:
                pass

        # try to restore focus to parent window
        try:
            if getattr(self, '_parent_window', None):
                parent = self._parent_window
                try:
                    parent.deiconify()
                except Exception:
                    pass
                try:
                    parent.lift()
                    parent.focus_force()
                except Exception:
                    pass
        except Exception:
            pass

