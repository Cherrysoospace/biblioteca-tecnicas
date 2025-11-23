import os
import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None
from ui import theme
from ui import widget_factory as wf
from ui.book_form import BookForm
from ui.user_form import UserForm
from tkinter import messagebox

from ui.loan_form import LoanForm

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Apply theme and sizing
        theme.apply_theme(self)
        self.title("🏮 Biblioteca Mitrauma")
        width, height = 800, 550
        self.geometry(f"{width}x{height}")

        # Center window on screen
        try:
            self.update_idletasks()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            x = (screen_w // 2) - (width // 2)
            y = (screen_h // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        # Main container for vertical centering
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=40, pady=30)

        # Title with lantern icon on the left
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "twemoji")
        try:
            self.icon_lantern = ctk.CTkImage(Image.open(os.path.join(assets_path, "lantern.png")), size=(40, 40))
        except Exception:
            self.icon_lantern = None

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(10, 24))

        if self.icon_lantern is not None:
            icon_lbl = ctk.CTkLabel(title_frame, image=self.icon_lantern, text="")
            icon_lbl.pack(side="left", padx=(0, 12))

        title = wf.create_title_label(title_frame, "Biblioteca Mitrauma")
        title.pack(side="left")

        # Buttons frame (centered column)
        btn_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        btn_frame.pack(expand=True)

        # Primary actions (big, vertical, centered)
        # load icons for buttons
        try:
            # use bookpile icon for "Crear Libro"
            self.icon_book = ctk.CTkImage(Image.open(os.path.join(assets_path, "bookpile.png")), size=(36, 36))
        except Exception:
            self.icon_book = None
        try:
            # use user.png for user-related icons
            self.icon_user = ctk.CTkImage(Image.open(os.path.join(assets_path, "user.png")), size=(36, 36))
        except Exception:
            self.icon_user = None
        try:
            # use openbook icon for "Ver Libros"
            self.icon_view = ctk.CTkImage(Image.open(os.path.join(assets_path, "openbook.png")), size=(36, 36))
        except Exception:
            self.icon_view = None
        try:
            # use prestamos icon for loans
            self.icon_loan = ctk.CTkImage(Image.open(os.path.join(assets_path, "prestamos.png")), size=(36, 36))
        except Exception:
            self.icon_loan = None
        try:
            self.icon_loan = ctk.CTkImage(Image.open(os.path.join(assets_path, "sakura.png")), size=(36, 36))
        except Exception:
            self.icon_loan = None

        b1 = wf.create_primary_button(btn_frame, "Crear Libro", command=self.open_create_book, image=self.icon_book)
        b1.pack(pady=10)
        b2 = wf.create_primary_button(btn_frame, "Crear Usuario", command=self.open_create_user, image=self.icon_user)
        b2.pack(pady=10)
        b3 = wf.create_primary_button(btn_frame, "Ver Libros", command=self.open_view_books, image=self.icon_view)
        b3.pack(pady=10)
        b4 = wf.create_primary_button(btn_frame, "Ver Usuarios", command=self.open_view_users, image=self.icon_user)
        b4.pack(pady=10)

        # Bottom exit button separated
        bottom_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 6))

        # Exit button: no emoji image per user's request (use only specified icons)
        exit_btn = wf.create_small_button(bottom_frame, "Salir", command=self.quit)
        exit_btn.pack(side="bottom", pady=6)

        # Keep references to opened windows to avoid GC
        self._open_windows = []

        # Add loan button to the primary actions frame
        b5 = wf.create_primary_button(btn_frame, "Crear Préstamo", command=self.open_create_loan, image=self.icon_loan)
        b5.pack(pady=10)

    # ------------------- OPEN WINDOWS -------------------
    def _open_toplevel(self, cls, *args, **kwargs):
        try:
            win = cls(self, *args, **kwargs)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana: {e}")
            return None

        # keep reference
        self._open_windows.append(win)
        try:
            win.deiconify()
            win.lift()
            win.focus()
        except Exception:
            pass
        return win

    def open_create_book(self):
        self._open_toplevel(BookForm, mode="create")

    def open_create_user(self):
        self._open_toplevel(UserForm, mode="create")

    def open_view_books(self):
        # Placeholder: this should open a read-only viewer or table
        messagebox.showinfo("Info", "Funcionalidad 'Ver Libros' no implementada aún.")

    def open_view_users(self):
        # Placeholder: this should open a read-only viewer or table
        messagebox.showinfo("Info", "Funcionalidad 'Ver Usuarios' no implementada aún.")
    def open_create_loan(self):
        # Use the generic toplevel opener so errors are handled uniformly
        self._open_toplevel(LoanForm)
        

