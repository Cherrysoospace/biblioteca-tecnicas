"""
Reservation Edit Form Module

This module provides a graphical user interface for editing existing reservation
records in the library management system. It allows modification of reservation
details including user assignment, book assignment, status, and assigned date.
The form is specifically designed for managing reservations of books with zero stock.
"""

import customtkinter as ctk
from tkinter import messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.reservation_controller import ReservationController
from services.user_service import UserService
from services.book_service import BookService
from services.inventory_service import InventoryService
from datetime import datetime


class ReservationEditForm(ctk.CTkToplevel):
    """
    A top-level window for editing existing reservation records.

    This class provides a graphical interface that allows users to modify reservation
    details including the assigned user, the reserved book (ISBNs with zero stock),
    reservation status (pending, assigned, cancelled), and the assigned date. The form
    includes validation and error handling for all operations.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (ReservationController): The reservation controller instance for database operations
        reservation_id: The ID of the reservation being edited
        user_service (UserService or None): Service for retrieving user data
        inventory_service (InventoryService or None): Service for retrieving books with zero stock
        lbl_id (CTkLabel): Label displaying the reservation ID
        lbl_user (CTkLabel): Label for the user selector
        opt_user (CTkOptionMenu or CTkEntry): Widget for selecting the user
        lbl_book (CTkLabel): Label for the book selector
        opt_book (CTkOptionMenu or CTkEntry): Widget for selecting the book (ISBNs with zero stock)
        lbl_status (CTkLabel): Label for the status selector
        opt_status (CTkOptionMenu or CTkEntry): Widget for selecting reservation status
        lbl_assigned (CTkLabel): Label for the assigned date field
        entry_assigned (CTkEntry): Entry field for the assigned date
    """

    def __init__(self, parent=None, reservation_id=None):
        """
        Initialize the reservation edit form window.

        Sets up the window layout, loads available users and books with zero stock,
        and populates the form with the current reservation data. Applies the application
        theme and configures window properties. Loads the reservation data immediately
        upon initialization.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control
            reservation_id: The ID of the reservation to be edited. Required to load
                          and update the reservation record

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (820x520)
            - Initializes ReservationController, UserService, and InventoryService
            - Loads all users from UserService
            - Loads all books with zero stock from InventoryService
            - Applies application theme to the window
            - Makes the window transient to the parent if provided
            - Automatically loads the reservation data via _load method

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

        self.title("Editar Reserva")
        # Increase the window size so all controls and buttons are visible
        # without needing to maximize the window on small screens.
        self.geometry("820x520")
        self.controller = ReservationController()
        self.reservation_id = reservation_id

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_lbl = wf.create_title_label(container, "Editar Reserva")
        title_lbl.pack(pady=(4, 8))

        self.lbl_id = ctk.CTkLabel(container, text=f"ID: {reservation_id}")
        self.lbl_id.pack(anchor="w")

        # user selector
        self.lbl_user = ctk.CTkLabel(container, text="Usuario:")
        self.lbl_user.pack(anchor="w", pady=(8, 0))
        try:
            self.user_service = UserService()
        except Exception:
            self.user_service = None

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
            self.opt_user = ctk.CTkOptionMenu(container, values=user_values)
        except Exception:
            self.opt_user = ctk.CTkEntry(container)
            if user_values and user_values[0] != "(No users available)":
                try:
                    self.opt_user.insert(0, user_values[0].split(' - ')[0])
                except Exception:
                    pass
        self.opt_user.pack(pady=6, fill="x")

        # book selector
        self.lbl_book = ctk.CTkLabel(container, text="Libro (ISBN):")
        self.lbl_book.pack(anchor="w", pady=(8, 0))
        # Use InventoryService to list only ISBN groups whose total stock == 0
        try:
            self.inventory_service = InventoryService()
        except Exception:
            self.inventory_service = None

        # Use InventoryService helper to build book selector values (stock == 0)
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
            book_values = ["(No books available)"]

        try:
            self.opt_book = ctk.CTkOptionMenu(container, values=book_values)
        except Exception:
            self.opt_book = ctk.CTkEntry(container)
            if book_values and book_values[0] != "(No books available)":
                try:
                    self.opt_book.insert(0, book_values[0].split(' - ')[0])
                except Exception:
                    pass
        self.opt_book.pack(pady=6, fill="x")

        # status selector
        self.lbl_status = ctk.CTkLabel(container, text="Status:")
        self.lbl_status.pack(anchor="w", pady=(8, 0))
        try:
            self.opt_status = ctk.CTkOptionMenu(container, values=["pending", "assigned", "cancelled"])
        except Exception:
            self.opt_status = ctk.CTkEntry(container)
        self.opt_status.pack(pady=6, fill="x")

        # assigned date display / button to set now
        self.lbl_assigned = ctk.CTkLabel(container, text="Assigned date:")
        self.lbl_assigned.pack(anchor="w", pady=(8, 0))
        self.entry_assigned = ctk.CTkEntry(container)
        self.entry_assigned.pack(pady=6, fill="x")

        set_now_btn = wf.create_small_button(container, text="Set Now", command=self._set_now)
        set_now_btn.pack(pady=(0, 6))

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(6, 0))
        save_btn = wf.create_primary_button(action_frame, text="Guardar", command=self.save, width=180, height=44)
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        save_btn.pack(side="left", padx=(0, 8))
        cancel_btn.pack(side="left")

        # load reservation
        self._load()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def _load(self):
        """
        Load the reservation data and populate the form fields.

        Retrieves the reservation record from the controller using the reservation_id,
        and populates all form fields with the current values including user, book ISBN,
        status, and assigned date. Handles both OptionMenu and Entry widget types for
        compatibility.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Retrieves reservation data from ReservationController
            - Populates opt_user with the current user selection
            - Populates opt_book with the current book ISBN selection
            - Sets opt_status to the current reservation status
            - Populates entry_assigned with the assigned date if available
            - Shows error message and closes window if reservation is not found
            - Shows error message if loading fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        try:
            r = self.controller.get_reservation(self.reservation_id)
            if not r:
                messagebox.showerror("Error", "Reservation not found")
                self._on_close()
                return
            # set user selection
            try:
                uid = r.get_user_id()
                try:
                    self.opt_user.set(next(v for v in (self.opt_user._values if hasattr(self.opt_user, '_values') else []) if v.startswith(f"{uid} - ")))
                except Exception:
                    try:
                        # OptionMenu may have get/set API; fallback to matching available list
                        vals = []
                        try:
                            vals = self.opt_user._values
                        except Exception:
                            pass
                        for v in vals:
                            if isinstance(v, str) and v.startswith(f"{uid} - "):
                                try:
                                    self.opt_user.set(v)
                                except Exception:
                                    try:
                                        self.opt_user.delete(0, 'end')
                                        self.opt_user.insert(0, uid)
                                    except Exception:
                                        pass
                                break
                    except Exception:
                        pass
            except Exception:
                pass

            # set book selection
            try:
                isbn = r.get_isbn()
                try:
                    self.opt_book.set(next(v for v in (self.opt_book._values if hasattr(self.opt_book, '_values') else []) if v.startswith(f"{isbn} - ")))
                except Exception:
                    try:
                        vals = []
                        try:
                            vals = self.opt_book._values
                        except Exception:
                            pass
                        for v in vals:
                            if isinstance(v, str) and v.startswith(f"{isbn} - "):
                                try:
                                    self.opt_book.set(v)
                                except Exception:
                                    try:
                                        self.opt_book.delete(0, 'end')
                                        self.opt_book.insert(0, isbn)
                                    except Exception:
                                        pass
                                break
                    except Exception:
                        pass
            except Exception:
                pass

            # set status
            try:
                self.opt_status.set(r.get_status())
            except Exception:
                try:
                    self.opt_status.insert(0, r.get_status())
                except Exception:
                    pass

            ad = r.get_assigned_date()
            if ad:
                try:
                    self.entry_assigned.insert(0, ad.isoformat())
                except Exception:
                    self.entry_assigned.insert(0, str(ad))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_now(self):
        """
        Set the assigned date field to the current UTC timestamp.

        Clears the assigned date entry field and populates it with the current UTC
        datetime in ISO format. This provides a convenient way to mark when a
        reservation was assigned.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Deletes the current content of entry_assigned field
            - Inserts the current UTC datetime in ISO format (YYYY-MM-DDTHH:MM:SS)

        Raises:
            Exception: Catches and ignores all exceptions to prevent disruption
        """
        try:
            now = datetime.utcnow().isoformat()
            self.entry_assigned.delete(0, 'end')
            self.entry_assigned.insert(0, now)
        except Exception:
            pass

    def save(self):
        """
        Save the changes to the reservation record.

        Validates and extracts data from all form fields, constructs an update request
        with the modified values, and sends it to the controller. Automatically sets
        the assigned date to the current time if the status is changed to 'assigned'
        and no date is provided. Refreshes the parent window's reservation list after
        successful update.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Extracts user_id, isbn, status, and assigned_date from form fields
            - Automatically sets assigned_date to current UTC time if status is 'assigned'
              and no date is provided
            - Updates the reservation record in the database via controller
            - Shows success message box if update succeeds
            - Shows error message box if update fails
            - Refreshes parent window's reservation list if parent has load_reservations method
            - Closes the window after successful update

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        status = None
        try:
            status = self.opt_status.get()
        except Exception:
            status = self.opt_status.get().strip()

        assigned = self.entry_assigned.get().strip()
        kwargs = {}
        # read selected user and book from OptionMenus or Entry fallbacks
        try:
            sel_user = self.opt_user.get()
        except Exception:
            try:
                sel_user = self.opt_user.get().strip()
            except Exception:
                sel_user = None

        try:
            sel_book = self.opt_book.get()
        except Exception:
            try:
                sel_book = self.opt_book.get().strip()
            except Exception:
                sel_book = None

        if sel_user and not sel_user.startswith("(No users"):
            try:
                kwargs['user_id'] = sel_user.split(' - ')[0].strip()
            except Exception:
                kwargs['user_id'] = sel_user

        if sel_book and not sel_book.startswith("(No books"):
            try:
                kwargs['isbn'] = sel_book.split(' - ')[0].strip()
            except Exception:
                kwargs['isbn'] = sel_book
        if status:
            kwargs['status'] = status
            if status == 'assigned' and not assigned:
                # set assigned date if missing
                assigned = datetime.utcnow().isoformat()
        if assigned:
            # pass ISO string; controller/service will parse when possible
            kwargs['assigned_date'] = assigned

        try:
            resp = self.controller.update_reservation(self.reservation_id, **kwargs)
            if resp.get('success'):
                messagebox.showinfo("Saved", "Reservation updated")
                # try to refresh parent list if exists
                try:
                    if getattr(self._parent_window, 'load_reservations', None):
                        self._parent_window.load_reservations()
                except Exception:
                    pass
                self._on_close()
            else:
                messagebox.showerror("Error", resp.get('message') or 'Error updating')
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the reservation edit window and returns focus to the parent window.
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


__all__ = ["ReservationEditForm"]
