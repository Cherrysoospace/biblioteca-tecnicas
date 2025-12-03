import os
import customtkinter as ctk
try:
    from PIL import Image, ImageTk
except Exception as pil_error:
    Image = None
    ImageTk = None
from ui import theme
from ui import widget_factory as wf
from utils.logger import LibraryLogger, UIErrorHandler

# Configurar logger para este módulo
logger = LibraryLogger.get_logger(__name__)
from ui.book.book_form import BookForm
from ui.user.user_form import UserForm
from ui.book.book_list import BookList
from ui.user.user_list import UserList
from ui.loan.loan_list import LoanList
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

from ui.loan.loan_form import LoanForm
from ui.shelf.shelf_form import ShelfForm
from ui.shelf.assign_book_form import AssignBookForm
from ui.shelf.shelf_list import ShelfList
from ui.reservation.reservation_form import ReservationForm
from ui.reservation.reservation_list import ReservationList

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Apply dynamic scaling based on screen resolution
        try:
            screen_width = self.winfo_screenwidth()
            if screen_width >= 2560:      # 4K
                scale = 1.5
            elif screen_width >= 1920:    # Full HD
                scale = 1.2
            else:                          # HD or lower
                scale = 1.0
            
            ctk.set_widget_scaling(scale)
            ctk.set_window_scaling(scale)  # Also scale toplevel windows
            logger.info(f"Escalado UI configurado: {scale}x (pantalla {screen_width}px)")
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "configurar escalado de UI", e)

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
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "centrar ventana", e)

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
                except Exception as e:
                    UIErrorHandler.log_and_pass(logger, "colocar background al fondo", e)
            except Exception as e:
                UIErrorHandler.log_and_pass(logger, "cargar imagen de fondo", e)
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
                        except Exception as e:
                            UIErrorHandler.log_and_pass(logger, "lower bg_label en resize", e)
                    else:
                        try:
                            self.bg_label.configure(image=self.bg_image)
                        except Exception as e:
                            UIErrorHandler.log_and_pass(logger, "configurar bg_image en resize", e)
                except Exception as ctk_error:
                    # fallback to ImageTk
                    UIErrorHandler.log_and_pass(logger, "CTkImage en resize", ctk_error)
                    try:
                        if ImageTk is not None:
                            self.bg_photo = ImageTk.PhotoImage(pil)
                            if self.bg_label is None:
                                self.bg_label = ctk.CTkLabel(self, image=self.bg_photo, text="")
                                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                                try:
                                    self.bg_label.lower()
                                except Exception as e:
                                    UIErrorHandler.log_and_pass(logger, "lower bg_label ImageTk resize", e)
                            else:
                                try:
                                    self.bg_label.configure(image=self.bg_photo)
                                except Exception as e:
                                    UIErrorHandler.log_and_pass(logger, "configurar bg_photo en resize", e)
                    except Exception as e:
                        UIErrorHandler.log_and_pass(logger, "ImageTk fallback en resize", e)
            except Exception as e:
                UIErrorHandler.log_and_pass(logger, "resize background completo", e)

        try:
            self.bind('<Configure>', _on_bg_resize)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "bind resize event", e)

        # Title with lantern icon on the left
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "twemoji")
        try:
            self.icon_lantern = ctk.CTkImage(Image.open(os.path.join(assets_path, "lantern.png")), size=(40, 40))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono lanterna", e)
            self.icon_lantern = None

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(10, 24))

        if self.icon_lantern is not None:
            icon_lbl = ctk.CTkLabel(title_frame, image=self.icon_lantern, text="")
            icon_lbl.pack(side="left", padx=(0, 12))

        title = wf.create_title_label(title_frame, "Biblioteca Mitrauma")
        title.pack(side="left")

        # Buttons frame (centered). We'll use a scrollable area and arrange
        # primary actions into two columns so options remain visible on
        # smaller screens.
        try:
            btn_frame = ctk.CTkScrollableFrame(container, fg_color=theme.BG_COLOR)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "crear CTkScrollableFrame", e)
            btn_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        btn_frame.pack(expand=True, fill="both")

        # Primary actions: arrange into two columns
        # load icons for buttons
        try:
            self.icon_book = ctk.CTkImage(Image.open(os.path.join(assets_path, "bookpile.png")), size=(36, 36))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono libro", e)
            self.icon_book = None
        
        try:
            self.icon_user = ctk.CTkImage(Image.open(os.path.join(assets_path, "user.png")), size=(36, 36))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono usuario", e)
            self.icon_user = None
        
        try:
            self.icon_view = ctk.CTkImage(Image.open(os.path.join(assets_path, "openbook.png")), size=(36, 36))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono ver", e)
            self.icon_view = None
        
        try:
            self.icon_loan = ctk.CTkImage(Image.open(os.path.join(assets_path, "prestamo.png")), size=(36, 36))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono préstamo", e)
            try:
                self.icon_loan = ctk.CTkImage(Image.open(os.path.join(assets_path, "sakura.png")), size=(36, 36))
            except Exception as fallback_e:
                UIErrorHandler.log_and_pass(logger, "cargar icono sakura (fallback)", fallback_e)
                self.icon_loan = None

        # Build a list of button specs to create and place in a 2-column grid
        button_specs = [
            ("Crear Libro", self.open_create_book, self.icon_book),
            ("Crear Usuario", self.open_create_user, self.icon_user),
            ("Ver Libros", self.open_view_books, self.icon_view),
            ("Ver Usuarios", self.open_view_users, self.icon_user),
            ("Ver Préstamos", self.open_view_loans, self.icon_loan),
            ("Ver Reservas", self.open_view_reservations, self.icon_view),
            ("Ver Estanterías", self.open_view_shelves, self.icon_view),
            ("Crear Préstamo", self.open_create_loan, self.icon_loan),
            ("Asignar Libros", self.open_assign_books, self.icon_book),
            ("Gestionar Estanterías", self.open_shelf_manager, self.icon_view),
            ("Crear Reserva", self.open_create_reservation, self.icon_loan),
        ]

        # Create an inner frame to host the grid inside the scrollable frame
        inner = ctk.CTkFrame(btn_frame, fg_color=theme.BG_COLOR)
        # Use pack here so that if btn_frame is not scrollable it still lays out
        inner.pack(padx=10, pady=6, anchor="n")

        # Place buttons in 2 columns
        for idx, (label, cmd, img) in enumerate(button_specs):
            col = idx % 2
            row = idx // 2
            try:
                btn = wf.create_primary_button(inner, label, command=cmd, image=img)
                btn.grid(row=row, column=col, padx=8, pady=10)
            except Exception as e:
                # fallback to pack if grid fails for the widget
                UIErrorHandler.log_and_pass(logger, f"grid para botón '{label}'", e)
                try:
                    btn = wf.create_primary_button(inner, label, command=cmd, image=img)
                    btn.pack(pady=6)
                except Exception as pack_e:
                    UIErrorHandler.handle_error(
                        logger, pack_e,
                        title="Error creando botón",
                        user_message=f"No se pudo crear el botón '{label}'",
                        show_dialog=False  # No saturar al usuario con múltiples dialogs
                    )

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
        # Reservation form button
        b_res = wf.create_primary_button(btn_frame, "Crear Reserva", command=self.open_create_reservation, image=self.icon_loan)
        b_res.pack(pady=10)

    def open_assign_books(self):
        self._open_toplevel(AssignBookForm)

    def open_view_reservations(self):
        # Open the reservations list viewer
        self._open_toplevel(ReservationList)

    def open_view_shelves(self):
        # Open the shelves list viewer
        self._open_toplevel(ShelfList)

    # ------------------- OPEN WINDOWS -------------------
    def _open_toplevel(self, cls, *args, **kwargs):
        try:
            logger.info(f"Abriendo ventana: {cls.__name__}")
            win = cls(self, *args, **kwargs)
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al abrir ventana",
                user_message=f"No se pudo abrir la ventana {cls.__name__}.\nError: {str(e)}"
            )
            return None

        # keep reference
        self._open_windows.append(win)
        try:
            win.deiconify()
            win.lift()
            win.focus()
            logger.debug(f"Ventana {cls.__name__} abierta exitosamente")
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, f"mostrar ventana {cls.__name__}", e)
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
    def open_view_loans(self):
        # Open the loans list viewer
        self._open_toplevel(LoanList)
    def open_create_loan(self):
        # Use the generic toplevel opener so errors are handled uniformly
        self._open_toplevel(LoanForm)
    def open_shelf_manager(self):
        # Open the shelf management form (create mode)
        self._open_toplevel(ShelfForm, mode="create")
    def open_create_reservation(self):
        self._open_toplevel(ReservationForm)
        

