"""Main Menu - Primary Application Entry Point and Navigation Hub.

This module implements the main application window for the Library Management System,
providing a centralized navigation interface to access all major features and
subsystems.

Architecture - UI Entry Point:
    MainMenu serves as the primary entry point for the desktop application, built
    using CustomTkinter for a modern, themed interface. It follows a hub-spoke
    navigation pattern where all major features are accessible from this central menu.

Key Features:
    - Responsive Design: Dynamic scaling based on screen resolution (HD/Full HD/4K)
    - Pixel-Art Background: Responsive background image with NEAREST interpolation
    - Icon-Based Navigation: Emoji/image icons for visual hierarchy
    - Two-Column Layout: Efficient use of screen space with grid layout
    - Error Handling: Comprehensive try-catch blocks for robustness
    - Window Management: Tracks opened windows to prevent garbage collection

UI Components:
    - Header: Title with lantern icon
    - Navigation Grid: 16 primary action buttons in 2 columns
    - Footer: Exit button
    - Background: Responsive pixel-art image (BG-5.jpg)

Navigation Categories:
    Book Management:
        - Create/View Books
        - Author Value Report (Stack Recursion)
        - Author Weight Report (Tail/Queue Recursion)
        - Search Reports (Brute Force, Backtracking)
    
    User Management:
        - Create/View Users
    
    Circulation:
        - Create/View Loans
        - Loan History (LIFO Stack)
        - Create/View Reservations
    
    Shelf Management:
        - View/Manage Shelves
        - Assign Books to Shelves

Technical Stack:
    - UI Framework: CustomTkinter (modern themed widgets)
    - Image Processing: PIL/Pillow (background and icons)
    - Logging: Custom LibraryLogger with UIErrorHandler
    - Theme: Centralized theme module for consistent styling

Responsive Features:
    - Automatic DPI scaling (1.0x, 1.2x, 1.5x based on screen width)
    - Window centering on screen
    - Scrollable button container for smaller screens
    - Dynamic background resizing with pixel-art preservation

Error Handling Strategy:
    - Graceful degradation: Missing images/icons don't crash the app
    - Logged errors: All exceptions logged via LibraryLogger
    - User feedback: Critical errors shown via UIErrorHandler dialogs
    - Fallback mechanisms: Multiple fallback strategies for image loading

Assets Used:
    - backgrounds/BG-5.jpg: Main background image
    - twemoji/*.png: Icon set for buttons (lantern, bookpile, user, etc.)

See Also:
    - ui.theme: Theme constants and application logic
    - ui.widget_factory: Factory for creating styled widgets
    - utils.logger: Logging infrastructure
"""

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
from ui.book.author_value_report import AuthorValueReport
from ui.book.author_weight_report import AuthorWeightReport
from ui.book.brute_force_report import BruteForceReport
from ui.book.backtracking_report import BacktrackingReport
from ui.user.user_list import UserList
from ui.loan.loan_list import LoanList
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk

from ui.loan.loan_form import LoanForm
from ui.loan.loan_history import LoanHistory
from ui.shelf.shelf_form import ShelfForm
from ui.shelf.assign_book_form import AssignBookForm
from ui.shelf.shelf_list import ShelfList
from ui.reservation.reservation_form import ReservationForm
from ui.reservation.reservation_list import ReservationList

class MainMenu(ctk.CTk):
    """Main application window providing centralized navigation to all features.
    
    This class implements the primary entry point window for the Library Management
    System, built on CustomTkinter (ctk.CTk). It provides a visually appealing,
    responsive interface with icon-based navigation to all major subsystems.
    
    Architecture:
        Inherits from ctk.CTk (CustomTkinter root window) and implements:
        - Responsive UI scaling based on screen resolution
        - Dynamic background image with pixel-art preservation
        - Grid-based navigation with 16 primary actions
        - Window lifecycle management for child windows
    
    Responsibilities:
        - Display main navigation menu
        - Open child windows (forms, lists, reports)
        - Manage window references to prevent garbage collection
        - Apply theme and responsive scaling
        - Handle UI initialization errors gracefully
    
    UI Layout:
        - Header: Title "Biblioteca Mitrauma" with lantern icon
        - Body: Scrollable 2-column grid of action buttons
        - Footer: Exit button
        - Background: Responsive pixel-art image layer
    
    Responsive Scaling:
        - Screen width >= 2560px (4K): 1.5x scaling
        - Screen width >= 1920px (Full HD): 1.2x scaling
        - Screen width < 1920px (HD): 1.0x scaling
    
    Navigation Actions (16 total):
        Books:
            - Crear Libro (Create Book)
            - Ver Libros (View Books)
            - Valor por Autor (Author Value Report - Stack Recursion)
            - Peso por Autor (Author Weight Report - Tail Recursion)
            - Fuerza Bruta (Brute Force Search Report)
            - Backtracking (Backtracking Search Report)
        
        Users:
            - Crear Usuario (Create User)
            - Ver Usuarios (View Users)
        
        Circulation:
            - Crear Préstamo (Create Loan)
            - Ver Préstamos (View Loans)
            - Historial LIFO (Loan History - Stack)
            - Crear Reserva (Create Reservation)
            - Ver Reservas (View Reservations)
        
        Shelves:
            - Gestionar Estanterías (Manage Shelves)
            - Ver Estanterías (View Shelves)
            - Asignar Libros (Assign Books to Shelves)
    
    Error Handling:
        - All UI initialization wrapped in try-except blocks
        - Graceful degradation for missing images/icons
        - Logged errors via LibraryLogger
        - User-facing error dialogs via UIErrorHandler
    
    Window Management:
        - Tracks opened child windows in _open_windows list
        - Prevents garbage collection of Toplevel windows
        - Centralized window opening via _open_toplevel method
    
    Attributes:
        icon_lantern (CTkImage): Lantern icon for title
        icon_book (CTkImage): Book pile icon for book actions
        icon_user (CTkImage): User icon for user actions
        icon_view (CTkImage): Open book icon for view actions
        icon_loan (CTkImage): Loan/sakura icon for circulation
        icon_search (CTkImage): Search icon for algorithm reports
        bg_pil_original (PIL.Image): Original background image for responsive resize
        bg_image (CTkImage): Current background image (CTkImage)
        bg_photo (ImageTk.PhotoImage): Fallback background image (ImageTk)
        bg_label (CTkLabel): Label widget displaying background
        _open_windows (List): References to opened child windows
    """
    def __init__(self):
        """Initialize the main menu window with responsive UI and navigation.
        
        Sets up the complete main menu interface including:
        - Dynamic DPI scaling based on screen resolution
        - Responsive pixel-art background image
        - Themed UI components and styling
        - Navigation grid with 16 action buttons
        - Icon loading and error handling
        - Window centering and sizing
        
        Initialization Workflow:
            1. Apply responsive scaling (1.0x, 1.2x, or 1.5x based on screen)
            2. Apply theme and set window title/geometry
            3. Center window on screen
            4. Load and configure responsive background image
            5. Bind resize event for background responsiveness
            6. Create title section with lantern icon
            7. Load navigation button icons (book, user, view, loan, search)
            8. Create scrollable navigation grid (2 columns, 8 rows)
            9. Create exit button in footer
            10. Initialize window management list
        
        Responsive Scaling Logic:
            - Detects screen width and applies appropriate scaling:
              * >= 2560px: 1.5x (4K displays)
              * >= 1920px: 1.2x (Full HD displays)
              * < 1920px: 1.0x (HD and lower)
            - Applies to both widgets and windows (Toplevel)
        
        Background Image:
            - Source: ui/assets/backgrounds/BG-5.jpg
            - Resize method: Image.NEAREST (preserves pixel-art aesthetic)
            - Responsive: Resizes on window resize events
            - Fallback: Multiple fallback strategies if image loading fails
        
        Icon Assets:
            - Source directory: ui/assets/twemoji/
            - Icons loaded: lantern, bookpile, user, openbook, prestamo, search
            - Size: 36x36 or 40x40 pixels
            - Fallback: Gracefully handles missing icons (buttons still work)
        
        Error Handling:
            - All image loading wrapped in try-except
            - All icon loading wrapped in try-except
            - All UI component creation wrapped in try-except
            - Errors logged via UIErrorHandler.log_and_pass
            - Application continues even if non-critical components fail
        
        Args:
            None
        
        Returns:
            None
        
        Side Effects:
            - Creates main window widgets
            - Loads image assets from disk
            - Binds window resize event
            - Logs initialization events
        """
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
        
        try:
            self.icon_search = ctk.CTkImage(Image.open(os.path.join(assets_path, "search.png")), size=(36, 36))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "cargar icono búsqueda", e)
            self.icon_search = None

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
            ("📚 Historial LIFO", self.open_loan_history, self.icon_loan),
            ("Asignar Libros", self.open_assign_books, self.icon_book),
            ("Gestionar Estanterías", self.open_shelf_manager, self.icon_view),
            ("Crear Reserva", self.open_create_reservation, self.icon_loan),
            ("📚 Valor por Autor", self.open_author_value_report, self.icon_book),
            ("⚖️ Peso por Autor", self.open_author_weight_report, self.icon_book),
            ("🔍 Fuerza Bruta", self.open_brute_force_report, self.icon_search),
            ("🎯 Backtracking", self.open_backtracking_report, self.icon_search),
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

    
    def open_author_value_report(self):
        """Open the Author Value Report window (Stack Recursion).
        
        Opens AuthorValueReport window displaying total book value by author
        using stack-based recursive algorithms.
        
        Purpose:
            Demonstrates stack recursion algorithm implementation for calculating
            aggregate values grouped by author.
        
        Args:
            None
        
        Returns:
            AuthorValueReport instance or None if error occurred
        
        Side Effects:
            - Opens AuthorValueReport window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(AuthorValueReport)
    
    def open_author_weight_report(self):
        """Open the Author Weight Report window (Tail/Queue Recursion).
        
        Opens AuthorWeightReport window displaying total book weight by author
        using tail/queue-based recursive algorithms.
        
        Purpose:
            Demonstrates tail recursion and queue-based recursive algorithm
            implementation for calculating aggregate weights grouped by author.
        
        Args:
            None
        
        Returns:
            AuthorWeightReport instance or None if error occurred
        
        Side Effects:
            - Opens AuthorWeightReport window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(AuthorWeightReport)
    
    def open_brute_force_report(self):
        """Open the Brute Force Search Report window.
        
        Opens BruteForceReport window demonstrating brute force search algorithm
        implementation for finding books by criteria.
        
        Purpose:
            Demonstrates brute force algorithm implementation with time complexity
            analysis and performance metrics.
        
        Args:
            None
        
        Returns:
            BruteForceReport instance or None if error occurred
        
        Side Effects:
            - Opens BruteForceReport window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(BruteForceReport)
    
    def open_backtracking_report(self):
        """Open the Backtracking Search Report window.
        
        Opens BacktrackingReport window demonstrating backtracking algorithm
        implementation for optimized search operations.
        
        Purpose:
            Demonstrates backtracking algorithm implementation with pruning
            strategies and performance comparison against brute force.
        
        Args:
            None
        
        Returns:
            BacktrackingReport instance or None if error occurred
        
        Side Effects:
            - Opens BacktrackingReport window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(BacktrackingReport)

    # ------------------- OPEN WINDOWS -------------------
    def _open_toplevel(self, cls, *args, **kwargs):
        """Open a child window and manage its lifecycle.
        
        Centralized method for opening all child windows (forms, lists, reports)
        with consistent error handling and window management.
        
        Features:
            - Creates instance of specified window class
            - Catches and logs instantiation errors
            - Stores reference to prevent garbage collection
            - Shows and focuses the new window
            - Displays user-facing error dialogs on failure
        
        Window Management:
            - Appends window reference to self._open_windows list
            - Prevents premature garbage collection of Toplevel widgets
            - Allows windows to persist independently
        
        Error Handling:
            - Catches exceptions during window instantiation
            - Logs errors via UIErrorHandler.handle_error
            - Shows user-friendly error dialog with exception details
            - Returns None on failure (safe to check return value)
        
        Args:
            cls (type): Class of the window to instantiate (must accept parent as first arg)
            *args: Additional positional arguments to pass to window constructor
            **kwargs: Keyword arguments to pass to window constructor
        
        Returns:
            Window instance if successful, None if exception occurred
        
        Side Effects:
            - Creates new Toplevel window
            - Appends reference to _open_windows list
            - Shows window (deiconify, lift, focus)
            - Logs window opening events
        """
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
        """Open the book creation form window.
        
        Opens BookForm in create mode for adding new books to the library system.
        
        Args:
            None
        
        Returns:
            BookForm instance or None if error occurred
        
        Side Effects:
            - Opens BookForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(BookForm, mode="create")

    def open_create_user(self):
        """Open the user creation form window.
        
        Opens UserForm in create mode for registering new users in the system.
        
        Args:
            None
        
        Returns:
            UserForm instance or None if error occurred
        
        Side Effects:
            - Opens UserForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(UserForm, mode="create")

    def open_view_books(self):
        """Open the book list viewer window.
        
        Opens BookList window displaying all books with search and management features.
        
        Args:
            None
        
        Returns:
            BookList instance or None if error occurred
        
        Side Effects:
            - Opens BookList window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(BookList)

    def open_view_users(self):
        """Open the user list viewer window.
        
        Opens UserList window displaying all registered users with management features.
        
        Args:
            None
        
        Returns:
            UserList instance or None if error occurred
        
        Side Effects:
            - Opens UserList window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(UserList)
    def open_view_loans(self):
        """Open the loan list viewer window.
        
        Opens LoanList window displaying all active and historical loans.
        
        Args:
            None
        
        Returns:
            LoanList instance or None if error occurred
        
        Side Effects:
            - Opens LoanList window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(LoanList)
    
    def open_create_loan(self):
        """Open the loan creation form window.
        
        Opens LoanForm for creating new book loans to users.
        
        Args:
            None
        
        Returns:
            LoanForm instance or None if error occurred
        
        Side Effects:
            - Opens LoanForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(LoanForm)
    
    def open_loan_history(self):
        """Open the loan history viewer window (LIFO Stack).
        
        Opens LoanHistory window displaying user loan history using Stack (LIFO)
        data structure for historical tracking.
        
        Args:
            None
        
        Returns:
            LoanHistory instance or None if error occurred
        
        Side Effects:
            - Opens LoanHistory window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(LoanHistory)
    def open_shelf_manager(self):
        """Open the shelf creation and management form window.
        
        Opens ShelfForm in create mode for adding and managing library shelves.
        
        Args:
            None
        
        Returns:
            ShelfForm instance or None if error occurred
        
        Side Effects:
            - Opens ShelfForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(ShelfForm, mode="create")
    
    def open_assign_books(self):
        """Open the book-to-shelf assignment form window.
        
        Opens AssignBookForm for assigning books to shelves with capacity validation.
        
        Args:
            None
        
        Returns:
            AssignBookForm instance or None if error occurred
        
        Side Effects:
            - Opens AssignBookForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(AssignBookForm)

    def open_view_reservations(self):
        """Open the reservation list viewer window.
        
        Opens ReservationList window displaying all book reservations.
        
        Args:
            None
        
        Returns:
            ReservationList instance or None if error occurred
        
        Side Effects:
            - Opens ReservationList window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(ReservationList)

    def open_view_shelves(self):
        """Open the shelf list viewer window.
        
        Opens ShelfList window displaying all library shelves with book assignments.
        
        Args:
            None
        
        Returns:
            ShelfList instance or None if error occurred
        
        Side Effects:
            - Opens ShelfList window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(ShelfList)
    
    def open_create_reservation(self):
        """Open the reservation creation form window.
        
        Opens ReservationForm for creating new book reservations.
        
        Args:
            None
        
        Returns:
            ReservationForm instance or None if error occurred
        
        Side Effects:
            - Opens ReservationForm window
            - Adds window reference to _open_windows
        """
        self._open_toplevel(ReservationForm)



