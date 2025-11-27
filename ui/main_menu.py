import os
import customtkinter as ctk
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None
from ui import theme
from ui import widget_factory as wf
from ui.book.book_form import BookForm
from ui.user.user_form import UserForm
from ui.book.book_list import BookList
from ui.user.user_list import UserList
from tkinter import messagebox

from ui.loan.loan_form import LoanForm
from ui.shelf.shelf_form import ShelfForm
from ui.shelf.assign_book_form import AssignBookForm

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

        # ------------------ Background Image (responsive, pixel-art) ------------------
        assets_bg_path = os.path.join(os.path.dirname(__file__), "assets", "backgrounds")
        bg_path = os.path.join(assets_bg_path, "BG-5.jpg")
        self.bg_image = None
        self.bg_photo = None
        self.bg_label = None
        self.bg_pil_original = None

        if Image is not None and os.path.exists(bg_path):
            try:
                pil = Image.open(bg_path)
                # Keep original in memory for responsive resizing
                self.bg_pil_original = pil

                # Resize using NEAREST for pixel-art effect
                init_w, init_h = width, height
                pil_resized = pil.resize((init_w, init_h), Image.NEAREST)

                # Try CTkImage first; if it fails, fallback to ImageTk.PhotoImage
                try:
                    self.bg_image = ctk.CTkImage(pil_resized, size=(init_w, init_h))
                    self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                except Exception:
                    try:
                        if ImageTk is not None:
                            self.bg_photo = ImageTk.PhotoImage(pil_resized)
                            self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
                            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    except Exception:
                        self.bg_label = None

                # Ensure bg_label is behind other widgets
                try:
                    if self.bg_label is not None:
                        self.bg_label.lower()
                except Exception:
                    pass
            except Exception:
                self.bg_pil_original = None

        # bind resize to keep background responsive (pixelated using NEAREST)
        def _on_bg_resize(event):
            if not getattr(self, 'bg_pil_original', None):
                return
            w = max(1, event.width)
            h = max(1, event.height)
            if getattr(self, '_bg_last_size', None) == (w, h):
                return
            self._bg_last_size = (w, h)
            try:
                pil = self.bg_pil_original.resize((w, h), Image.NEAREST)
                try:
                    self.bg_image = ctk.CTkImage(pil, size=(w, h))
                    if self.bg_label is None:
                        self.bg_label = ctk.CTkLabel(self, image=self.bg_image, text="")
                        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                        try:
                            self.bg_label.lower()
                        except Exception:
                            pass
                    else:
                        try:
                            self.bg_label.configure(image=self.bg_image)
                        except Exception:
                            pass
                except Exception:
                    # fallback to ImageTk
                    try:
                        if ImageTk is not None:
                            self.bg_photo = ImageTk.PhotoImage(pil)
                            if self.bg_label is None:
                                self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
                                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                                try:
                                    self.bg_label.lower()
                                except Exception:
                                    pass
                            else:
                                try:
                                    self.bg_label.configure(image=self.bg_photo)
                                except Exception:
                                    pass
                    except Exception:
                        pass
            except Exception:
                pass

        try:
            self.bind('<Configure>', _on_bg_resize)
        except Exception:
            pass

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
        # Try to load loan-related icon. The assets folder contains 'prestamo.png' (singular)
        # so try that first, then fall back to 'sakura.png' if present.
        try:
            self.icon_loan = ctk.CTkImage(Image.open(os.path.join(assets_path, "prestamo.png")), size=(36, 36))
        except Exception:
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
        # Assign books to shelf
        b_assign = wf.create_primary_button(btn_frame, "Asignar Libros", command=self.open_assign_books, image=self.icon_book)
        b_assign.pack(pady=10)

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

        # Shelf manager button
        b6 = wf.create_primary_button(btn_frame, "Gestionar Estanterías", command=self.open_shelf_manager, image=self.icon_view)
        b6.pack(pady=10)

    def open_assign_books(self):
        self._open_toplevel(AssignBookForm)

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
        # Open the provisional book list viewer
        self._open_toplevel(BookList)

    def open_view_users(self):
        # Open the user list viewer
        self._open_toplevel(UserList)
    def open_create_loan(self):
        # Use the generic toplevel opener so errors are handled uniformly
        self._open_toplevel(LoanForm)
    def open_shelf_manager(self):
        # Open the shelf management form (create mode)
        self._open_toplevel(ShelfForm, mode="create")
        

