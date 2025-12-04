"""
Shelf Form Window Module

This module provides a graphical user interface for creating and editing shelf records
in the library management system. It supports both creation and edit modes, allowing users
to manage shelf properties including ID and name. The form includes utilities for saving/loading
shelves to/from JSON files, displaying shelf summaries, and clearing shelf contents.
"""

import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
try:
    from PIL import Image
except Exception:
    Image = None

from controllers.shelf_controller import ShelfController
from ui import theme
from ui import widget_factory as wf


class ShelfForm(ctk.CTkToplevel):
    """
    A top-level window for creating or editing shelf records.

    This class provides a comprehensive interface for shelf management with two modes:
    'create' for adding new shelves and 'edit' for modifying existing ones. The form includes
    fields for shelf ID (auto-generated in create mode) and name, along with utility buttons
    for saving/loading shelves to/from JSON files, displaying shelf summaries with capacity
    information, and clearing all books from a shelf. Shelf capacity is fixed at 8.0 kg per
    project requirements.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (ShelfController): The shelf controller instance for database operations
        mode (str): Operation mode, either "create" or "edit"
        shelf_id: The ID of the shelf being edited (only used in edit mode)
        entry_id (CTkEntry): Entry field for shelf ID (disabled in create mode)
        entry_name (CTkEntry): Entry field for shelf name
        summary_lbl (CTkLabel): Label for displaying shelf summary information
    """

    def __init__(self, parent=None, mode="create", shelf_id=None):
        """
        Initialize the shelf form window.

        Sets up the window layout with input fields for shelf ID and name, and action buttons
        for create/update operations, file operations, summary display, and shelf clearing.
        In create mode, the ID field is disabled as IDs are auto-generated. In edit mode,
        loads existing shelf data.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control
            mode (str): Operation mode - "create" for new shelves or "edit" for existing shelves.
                       Defaults to "create"
            shelf_id: The ID of the shelf to edit. Only used when mode is "edit".
                     Ignored in create mode

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (480x360)
            - Initializes ShelfController for database operations
            - Applies application theme to the window
            - Disables ID field in create mode
            - Loads shelf data if in edit mode with valid shelf_id
            - Makes the window transient to the parent if provided

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail
        """
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass
        
        self.controller = ShelfController()
        self.mode = mode
        self.shelf_id = shelf_id

        # Apply theme
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # window basics
        self.title("Shelf Manager")
        self.geometry("480x360")

        # header
        header = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        header.pack(fill="x", padx=16, pady=12)
        title_lbl = wf.create_title_label(header, "Shelf")
        title_lbl.pack(side="left")

        # form frame
        form = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        form.pack(expand=True, fill="both", padx=16, pady=8)

        id_placeholder = "Auto (se asignará)" if mode == "create" else "ID"
        self.entry_id = ctk.CTkEntry(form, placeholder_text=id_placeholder)
        self.entry_id.pack(pady=6, fill="x")
        if mode == "create":
            try:
                self.entry_id.configure(state="disabled")
            except Exception:
                pass

        # Human-readable name for the shelf
        self.entry_name = ctk.CTkEntry(form, placeholder_text="Nombre (ej. Estantería A1)")
        self.entry_name.pack(pady=6, fill="x")

        # action buttons
        actions = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        actions.pack(pady=12)

        if mode == "create":
            primary = wf.create_primary_button(actions, text="Create Shelf", command=self.create_shelf)
        else:
            primary = wf.create_primary_button(actions, text="Update Shelf", command=self.update_shelf)
        primary.pack(side="left", padx=(0, 8))

        small_save = wf.create_small_button(actions, text="Save All", command=self.save_shelves)
        small_save.pack(side="left", padx=(0, 8))

        small_load = wf.create_small_button(actions, text="Load File", command=self.load_shelves)
        small_load.pack(side="left", padx=(0, 8))

        summary_btn = wf.create_small_button(actions, text="Show Summary", command=self.show_summary)
        summary_btn.pack(side="left", padx=(0, 8))

        clear_btn = wf.create_small_button(actions, text="Clear Shelf", command=self.clear_shelf)
        clear_btn.pack(side="left")

        # area to show summary text
        self.summary_lbl = ctk.CTkLabel(self, text="")
        self.summary_lbl.pack(padx=16, pady=(6, 12), fill="x")

        # close handler
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # If editing, load existing values
        if mode == "edit" and shelf_id:
            self.load_shelf()

    def create_shelf(self):
        """
        Create a new shelf with auto-generated ID and user-provided name.

        Creates a new shelf with a fixed capacity of 8.0 kg (per project requirements)
        and an optional name from the entry field. The shelf ID is automatically generated
        by the controller. Displays success or error messages and closes the window after
        successful creation.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Extracts name from entry_name field and trims whitespace
            - Creates new shelf via controller with fixed capacity of 8.0 kg
            - Shows success message box with generated shelf ID if creation succeeds
            - Shows error message box if creation fails
            - Closes the window after successful creation

        Raises:
            None
        """
        # Capacity is fixed to 8.0 per project requirements (max weight per shelf)
        cap = 8.0
        name = (self.entry_name.get() or '').strip()
        shelf = self.controller.create_shelf(None, capacity=cap, name=name if name else None)
        if shelf:
            messagebox.showinfo("Success", f"Shelf {getattr(shelf, '_Shelf__id', 'unknown')} created.")
            self._on_close()
        else:
            messagebox.showerror("Error", "Failed to create shelf.")

    def update_shelf(self):
        """
        Update an existing shelf's name.

        Validates that a shelf ID is provided, retrieves the shelf object, and updates
        its name with the value from the entry field. Shelf capacity remains fixed at 8.0 kg
        per project requirements and cannot be modified. Persists changes to the shelves
        JSON file.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message if shelf ID is missing
            - Extracts name from entry_name field and trims whitespace
            - Retrieves shelf object from ShelfController
            - Updates shelf name via setter or direct attribute access
            - Persists changes to shelves.json file
            - Shows success message box if update succeeds
            - Shows error message box if shelf is not found

        Raises:
            Exception: Catches exceptions during name update and file persistence
        """
        sid = self.entry_id.get()
        if not sid:
            messagebox.showerror("Error", "Shelf ID required for update.")
            return
        # Capacity is fixed (8.0) by project rules; only update name here
        ok = True
        # update name as well
        try:
            name = (self.entry_name.get() or '').strip()
            if name:
                shelf = self.controller.find_shelf(sid)
                if shelf is not None:
                    try:
                        shelf.set_name(name)
                    except Exception:
                        try:
                            setattr(shelf, '_Shelf__name', name)
                        except Exception:
                            pass
        except Exception:
            pass
        # feedback always success if shelf exists
        if self.controller.find_shelf(sid) is not None:
            messagebox.showinfo("Success", "Shelf updated.")
            # persist change
            try:
                path = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.dirname(__file__)), 'data', 'shelves.json')
                self.controller.service.save_to_file(path)
            except Exception:
                pass
        else:
            messagebox.showerror("Error", "Shelf not found.")

    def load_shelf(self):
        """
        Load and display the shelf data in edit mode.

        Retrieves the shelf record from the controller using shelf_id and populates
        the form fields with the shelf's ID and name. The ID field is temporarily
        enabled to populate it, then disabled again to prevent modification.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Retrieves shelf data from ShelfController
            - Temporarily enables entry_id to populate it
            - Populates entry_id with the shelf ID
            - Disables entry_id again to make it read-only
            - Populates entry_name with the shelf name if available
            - Returns silently if shelf is not found

        Raises:
            Exception: Catches exceptions during field population to ensure
                      partial data is displayed even if some operations fail
        """
        shelf = self.controller.find_shelf(self.shelf_id)
        if not shelf:
            return
        # fill values
        try:
            self.entry_id.configure(state="normal")
            self.entry_id.delete(0, 'end')
            self.entry_id.insert(0, getattr(shelf, '_Shelf__id', ''))
            self.entry_id.configure(state="disabled")
        except Exception:
            pass
        # load name if present
        try:
            name = getattr(shelf, '_Shelf__name', '')
            if name:
                try:
                    self.entry_name.delete(0, 'end')
                except Exception:
                    pass
                self.entry_name.insert(0, str(name))
        except Exception:
            pass

    def show_summary(self):
        """
        Display a summary of the shelf's capacity and contents.

        Retrieves and displays shelf information including ID, total capacity, current
        total weight of books, remaining capacity, and book count. The summary is shown
        in the summary_lbl label below the form fields.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message if shelf ID is missing
            - Retrieves shelf summary from ShelfController
            - Updates summary_lbl with formatted summary text including:
              - Shelf ID
              - Total capacity (8.0 kg)
              - Current total weight of all books
              - Remaining capacity available
              - Number of books on the shelf
            - Displays "Shelf not found" if shelf doesn't exist

        Raises:
            None
        """
        sid = self.entry_id.get() if self.entry_id.get() else self.shelf_id
        if not sid:
            messagebox.showerror("Error", "Shelf ID required to show summary.")
            return
        s = self.controller.shelf_summary(sid)
        if not s:
            self.summary_lbl.configure(text="Shelf not found")
            return
        txt = f"ID: {s.get('id')}  Capacity: {s.get('capacity')}kg  Total: {s.get('total_weight')}kg  Remaining: {s.get('remaining_capacity')}kg  Count: {s.get('books_count')}"
        self.summary_lbl.configure(text=txt)

    def clear_shelf(self):
        """
        Remove all books from the shelf.

        Validates that a shelf ID is provided, then removes all books currently assigned
        to the shelf via the shelf controller. Displays the number of books removed.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message if shelf ID is missing
            - Calls shelf_controller.clear_shelf to remove all books
            - Controller returns list of removed books
            - Shows info message box with count of removed books

        Raises:
            None
        """
        sid = self.entry_id.get() if self.entry_id.get() else self.shelf_id
        if not sid:
            messagebox.showerror("Error", "Shelf ID required to clear.")
            return
        removed = self.controller.clear_shelf(sid)
        messagebox.showinfo("Cleared", f"Removed {len(removed)} books from shelf.")

    def save_shelves(self):
        """
        Save all shelves to a JSON file.

        Opens a file save dialog allowing the user to choose the destination path,
        then saves all shelf data to the selected JSON file via the shelf controller.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Opens a save file dialog (defaulting to .json extension)
            - Returns without action if user cancels the dialog
            - Calls shelf_controller.save_shelves with the selected path
            - Shows success message box with the file path if save succeeds
            - Shows error message box if save fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            self.controller.save_shelves(path)
            messagebox.showinfo("Saved", f"Shelves saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_shelves(self):
        """
        Load shelves from a JSON file.

        Opens a file open dialog allowing the user to choose a JSON file containing
        shelf data, then loads all shelves from that file via the shelf controller.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Opens an open file dialog (filtering for .json files)
            - Returns without action if user cancels the dialog
            - Calls shelf_controller.load_shelves with the selected path
            - Shows success message box with the file path if load succeeds
            - Shows error message box if load fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        path = filedialog.askopenfilename(filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            self.controller.load_shelves(path)
            messagebox.showinfo("Loaded", f"Shelves loaded from {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the shelf form window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        window's close button.

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
