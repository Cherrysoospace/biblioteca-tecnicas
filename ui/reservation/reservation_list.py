"""
Reservation List Window Module

This module provides a graphical user interface for viewing and managing all
reservation records in the library management system. It displays reservations
in a table format with full CRUD operations including viewing, editing, and
deleting records. The interface shows comprehensive reservation details including
user information, book ISBN, reservation status, and dates.
"""

import os
import tkinter as tk
import tkinter.font as tkfont
import json
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.reservation_controller import ReservationController
from ui.reservation.reservation_edit import ReservationEditForm


class ReservationList(ctk.CTkToplevel):
    """
    A top-level window for displaying and managing all reservation records.

    This class provides a comprehensive interface for reservation management with a table
    displaying all reservations and action buttons for refreshing, editing, and deleting
    records. Users can double-click a row to edit a reservation or use the action buttons.
    The table shows reservation ID, user ID, user name, ISBN, reserved date, status
    (pending/assigned/cancelled), and assigned date.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (ReservationController): The reservation controller instance for database operations
        _open_windows (list): List of child windows opened from this window
        tree (ttk.Treeview): The table widget displaying all reservation records with columns
                            for reservation_id, user_id, user_name, isbn, reserved_date,
                            status, and assigned_date
    """

    def __init__(self, parent=None):
        """
        Initialize the reservation list window.

        Sets up the window layout with a table displaying all reservations and action buttons
        for managing them. Applies styling, configures the table with appropriate columns,
        and loads all reservations from the database. Sets up event handlers for double-click
        editing and window closing.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (900x420)
            - Loads all reservation records from the database via ReservationController
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Binds double-click event to open edit dialog
            - Automatically loads and displays all reservations on initialization

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

        self.title("Listado de Reservas")
        self.geometry("900x420")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Reservas")
        title_lbl.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("reservation_id", "user_id", "user_name", "isbn", "reserved_date", "status", "assigned_date")
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        try:
            fam, fsize, fweight = theme.get_font(self, size=10)
        except Exception:
            fam, fsize, fweight = ("Segoe UI", 10, "normal")
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=24, fieldbackground=theme.BG_COLOR)
        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception:
            hfam, hfsize = (fam, fsize + 1)
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")
        headings = {
            "reservation_id": "ID",
            "user_id": "User ID",
            "user_name": "User",
            "isbn": "ISBN",
            "reserved_date": "Reserved",
            "status": "Status",
            "assigned_date": "Assigned"
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c in ("reservation_id", "user_id"):
                self.tree.column(c, width=90, anchor="center")
            elif c in ("status", "reserved_date", "assigned_date"):
                self.tree.column(c, width=140, anchor="center")
            else:
                self.tree.column(c, width=200, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # Action row
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_reservations)
        refresh_btn.pack(side="left", padx=(0, 8))
        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))
        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))
        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = ReservationController()
        self._open_windows = []

        # load data
        self.load_reservations()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

    def load_reservations(self):
        """
        Load and display all reservation records in the table.

        Clears the current table contents and retrieves all reservations from the controller,
        then populates the table with reservation data including reservation ID, user ID,
        user name (loaded from UserService), ISBN, reserved date, status, and assigned date.
        Applies alternating row colors for better readability.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all existing rows from the table
            - Retrieves all reservations from ReservationController
            - Loads user names from UserService for each reservation
            - Populates table with reservation records
            - Applies alternating row background colors (odd/even)
            - Shows error message box if loading fails
            - Converts dates to ISO format for display
            - Displays empty string for null assigned dates

        Raises:
            Exception: Catches and displays errors via message box if reservation loading fails,
                      continues processing remaining records if individual record loading fails
        """
        # clear
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            res_list = self.controller.list_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        for i, r in enumerate(res_list):
            try:
                rid = r.get_reservation_id()
                uid = r.get_user_id()
                # try to show user name by loading users if possible
                try:
                    from services.user_service import UserService
                    us = UserService()
                    uobj = us.find_by_id(uid)
                    uname = uobj.get_name() if uobj else ""
                except Exception:
                    uname = ""

                isbn = r.get_isbn()
                reserved = r.get_reserved_date()
                try:
                    reserved = reserved.isoformat()
                except Exception:
                    pass
                status = r.get_status()
                assigned = r.get_assigned_date()
                try:
                    assigned = assigned.isoformat() if assigned else ""
                except Exception:
                    pass
                row = (rid, uid, uname, isbn, reserved, status, assigned)
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
            except Exception:
                continue

        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the reservation list window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        return button or the window's close button.

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

    def open_selected_for_edit(self):
        """
        Open the edit dialog for the selected reservation record.

        Retrieves the reservation ID from the selected table row and opens the
        ReservationEditForm dialog. Tracks the opened window in the _open_windows list.
        Also handles double-click events on table rows. The edit form will automatically
        refresh this list when changes are saved.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no reservation is selected
            - Shows error message if the selected row cannot be read
            - Opens ReservationEditForm window as a top-level dialog
            - Adds the edit window to _open_windows list for tracking
            - Deiconifies, lifts, and focuses the edit window

        Raises:
            Exception: Catches and displays exceptions via message box if edit window
                      cannot be opened
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una reserva en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            reservation_id = values[0]
            parent = self._parent_window or self
            win = ReservationEditForm(parent, reservation_id)
            self._open_windows.append(win)
            try:
                win.deiconify()
                win.lift()
                win.focus()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el editor: {e}")

    def delete_selected(self):
        """
        Delete the selected reservation record from the database.

        Retrieves the reservation ID from the selected table row, prompts the user for
        confirmation, and deletes the reservation if confirmed. Refreshes the table after
        successful deletion. Warns the user that this action cannot be undone.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no reservation is selected
            - Shows error message if the selected row cannot be read
            - Shows confirmation dialog before deletion
            - Deletes the reservation record from the database via controller
            - Shows success message if deletion succeeds
            - Shows error message if deletion fails
            - Refreshes the reservation list after successful deletion

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una reserva en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            reservation_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar la reserva {reservation_id}? Esta acción no se puede deshacer?"):
            return

        try:
            resp = self.controller.delete_reservation(reservation_id)
            # controller returns dict
            if resp.get('success'):
                messagebox.showinfo("Borrado", "Reserva eliminada correctamente.")
            else:
                messagebox.showerror("Error", resp.get('message') or 'Error deleting')
            self.load_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["ReservationList"]
