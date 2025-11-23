import customtkinter as ctk
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

        # Title
        title = wf.create_title_label(container, "🏮 Biblioteca Mitrauma")
        title.pack(pady=(10, 24))

        # Buttons frame (centered column)
        btn_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        btn_frame.pack(expand=True)

        # Primary actions (big, vertical, centered)
        b1 = wf.create_primary_button(btn_frame, "📚  Crear Libro", command=self.open_create_book)
        b1.pack(pady=10)

        b2 = wf.create_primary_button(btn_frame, "👤  Crear Usuario", command=self.open_create_user)
        b2.pack(pady=10)

        b3 = wf.create_primary_button(btn_frame, "📖  Ver Libros", command=self.open_view_books)
        b3.pack(pady=10)

        b4 = wf.create_primary_button(btn_frame, "🧑‍💼  Ver Usuarios", command=self.open_view_users)
        b4.pack(pady=10)

        # Bottom exit button separated
        bottom_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 6))

        exit_btn = wf.create_small_button(bottom_frame, "🍵  Salir", command=self.quit)
        exit_btn.pack(side="bottom", pady=6)

        # Keep references to opened windows to avoid GC
        self._open_windows = []

        # Add loan button to the primary actions frame
        b5 = wf.create_primary_button(btn_frame, "🔁  Crear Préstamo", command=self.open_create_loan)
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
        

