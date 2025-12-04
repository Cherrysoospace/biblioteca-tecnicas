"""
Reservation Form Window Module

This module provides a graphical user interface for creating new reservation records
in the library management system. Reservations are specifically designed for books
with zero stock, allowing users to join a waiting list for unavailable books. The
form allows selection of a user and a book (ISBN) with zero stock to create a
reservation.
"""

import os
import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None
from controllers.reservation_controller import ReservationController
from services.user_service import UserService
from services.inventory_service import InventoryService
from tkinter import messagebox
from ui import theme
from ui import widget_factory as wf


class ReservationForm(ctk.CTkToplevel):
    """
    A top-level window for creating new reservation records.

    This class provides a graphical interface that allows users to create reservations
    for books with zero stock. The form displays only books that are currently unavailable
    (total stock == 0), allowing users to join a waiting list. Users select a user from
    the system and a book with zero stock to create the reservation.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (ReservationController): The reservation controller instance for database operations
        user_service (UserService or None): Service for retrieving user data
        inventory_service (InventoryService or None): Service for retrieving books with zero stock
        lbl_user (CTkLabel): Label for the user selector
        opt_user (CTkOptionMenu or CTkEntry): Widget for selecting the user, falls back to
                                             Entry if OptionMenu is not available
        lbl_isbn (CTkLabel): Label for the book selector
        opt_book (CTkOptionMenu or CTkEntry): Widget for selecting the book (only books with
                                             stock 0), falls back to Entry if OptionMenu
                                             is not available
    """

    def __init__(self, parent=None):
        """
        Initialize the reservation creation form window.

        Sets up the window layout with dropdowns for user selection and book selection
        (only books with zero stock). Applies the application theme and configures window
        properties. Initializes services for loading users and books with zero inventory.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (700x420)
            - Initializes ReservationController, UserService, and InventoryService
            - Loads all users from UserService
            - Loads all books with zero stock from InventoryService
            - Applies application theme to the window
            - Makes the window transient to the parent if provided
            - Displays "No users available" or "No books with stock 0" messages if data is unavailable

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail
        """
        super().__init__(parent)
        self._parent_window = parent

        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # Window props (increased size so all buttons are visible on smaller screens)
        self.title("Create Reservation")
        # Wider and taller to avoid needing to maximize
        self.geometry("700x420")

        # Main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=16, pady=16)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 12))
        title_lbl = wf.create_title_label(title_frame, "Crear Reserva")
        title_lbl.pack()

        # Form area
        form_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        form_frame.pack(expand=True, fill="both")

        # User selector (dropdown)
        self.lbl_user = ctk.CTkLabel(form_frame, text="Select User:")
        self.lbl_user.pack(anchor="w", pady=(6, 0))

        # Inventory and user services to populate dropdowns
        try:
            self.user_service = UserService()
        except Exception:
            self.user_service = None
        try:
            self.inventory_service = InventoryService()
        except Exception:
            self.inventory_service = None

        user_values = []
        if self.user_service is not None:
            try:
                users = self.user_service.get_all_users()
                user_values = [f"{u.get_id()} - {u.get_name()}" for u in users]
            except Exception:
                user_values = []

        if not user_values:
            user_values = ["(No users available)"]

        try:
            self.opt_user = ctk.CTkOptionMenu(form_frame, values=user_values)
        except Exception:
            # fallback to simple Entry if OptionMenu not available
            self.opt_user = ctk.CTkEntry(form_frame, placeholder_text="User ID")
            if user_values and user_values[0] != "(No users available)":
                try:
                    # prefill first option
                    self.opt_user.insert(0, user_values[0].split(' - ')[0])
                except Exception:
                    pass

        self.opt_user.pack(pady=6, fill="x")

        # Book selector: only show books with total stock == 0 (waiting list candidates)
        self.lbl_isbn = ctk.CTkLabel(form_frame, text="Select Book (stock 0):")
        self.lbl_isbn.pack(anchor="w", pady=(6, 0))

        # Build book selector values using InventoryService helper
        book_values = []
        if self.inventory_service is not None:
            try:
                zero_list = self.inventory_service.get_isbns_with_zero_stock()
                for isbn, title in zero_list:
                    if title:
                        book_values.append(f"{isbn} - {title}")
                    else:
                        book_values.append(isbn)
            except Exception:
                book_values = []

        if not book_values:
            book_values = ["(No books with stock 0)"]

        try:
            self.opt_book = ctk.CTkOptionMenu(form_frame, values=book_values)
        except Exception:
            self.opt_book = ctk.CTkEntry(form_frame, placeholder_text="ISBN")
            if book_values and book_values[0] != "(No books with stock 0)":
                try:
                    self.opt_book.insert(0, book_values[0].split(' - ')[0])
                except Exception:
                    pass

        self.opt_book.pack(pady=6, fill="x")

        # Actions
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(12, 6))

        create_btn = wf.create_primary_button(action_frame, text="Crear Reserva", command=self.submit, width=260, height=48)
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_cancel, width=120, height=44)

        create_btn.pack(side="left", padx=(0, 8))
        cancel_btn.pack(side="left")

        # controller
        self.controller = ReservationController()

        # WM delete handling
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        except Exception:
            pass

    def submit(self):
        """
        Handle the create reservation button click event.

        Validates the form data, extracts the selected user ID and book ISBN from the
        dropdown menus (or entry fields), then calls the controller to create a new
        reservation in the database. The reservation ID is automatically generated by
        the system. Displays success or error messages based on the operation result.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message box if validation fails (no user or book selected)
            - Shows error message box if user/book unavailable messages are selected
            - Shows success message box if the reservation is created successfully,
              including the generated reservation ID when available
            - Closes the window after successful reservation creation
            - Creates a new reservation record in the database via the controller
            - Parses user_id and isbn from dropdown text format "ID - Name/Title"

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        # Read selected user and book. Support both OptionMenu and Entry fallback.
        try:
            sel_user = self.opt_user.get()
        except Exception:
            sel_user = self.opt_user.get().strip()

        try:
            sel_book = self.opt_book.get()
        except Exception:
            sel_book = self.opt_book.get().strip()

        if not sel_user or sel_user.startswith("(No users"):
            messagebox.showerror("Error", "No user selected or available.")
            return
        if not sel_book or sel_book.startswith("(No books"):
            messagebox.showerror("Error", "No book selected with stock 0.")
            return

        # parse id from option text like 'U001 - Name'
        user_id = sel_user.split(' - ')[0].strip()
        isbn = sel_book.split(' - ')[0].strip()

        try:
            resp = self.controller.create_reservation(user_id, isbn)
            if resp.get('success'):
                # show the reservation id if available
                res = resp.get('reservation')
                try:
                    rid = res.get_reservation_id()
                except Exception:
                    rid = None
                if rid:
                    messagebox.showinfo("Success", f"Reservation {rid} created.")
                else:
                    messagebox.showinfo("Success", "Reservation created.")
                self._on_cancel()
            else:
                messagebox.showerror("Error", resp.get('message') or 'Unknown error')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_cancel(self):
        """
        Handle the window close or cancel event.

        Properly closes the reservation form window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        cancel button or the window's close button.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Destroys the current window
            - If destroy fails, attempts to withdraw (hide) the window
            - Lifts and focuses the parent window if it exists
            - Restores the parent window to the foreground

        Raises:
            Exception: Catches and ignores all exceptions during cleanup to ensure
                      the method completes without errors
        """
        try:
            self.destroy()
        except Exception:
            try:
                self.withdraw()
            except Exception:
                pass

        try:
            if getattr(self, '_parent_window', None):
                try:
                    self._parent_window.lift()
                    self._parent_window.focus_force()
                except Exception:
                    pass
        except Exception:
            pass
