"""
Shelf Edit Window Module

This module provides a graphical user interface for editing shelf records in the
library management system. It allows users to modify the shelf name and manage
the books assigned to the shelf. Users can add books via the assign book form,
remove selected books, and view all currently assigned books in a table.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont

from ui import theme
from ui import widget_factory as wf
from controllers.shelf_controller import ShelfController
from ui.shelf.assign_book_form import AssignBookForm
from utils.config import FilePaths


class ShelfEdit(ctk.CTkToplevel):
    """
    A top-level window for editing shelf records and managing shelf books.

    This class provides a comprehensive interface for shelf management including editing
    the shelf name and managing the collection of books assigned to the shelf. Users can
    view all books on the shelf in a table, add new books via the assign book form, remove
    selected books, and save name changes. The table supports multi-selection for batch
    removal of books.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        shelf_id (str): The ID of the shelf being edited
        controller (ShelfController): The shelf controller instance for database operations
        entry_id (CTkEntry): Disabled entry field displaying the shelf ID (read-only)
        entry_name (CTkEntry): Entry field for editing the shelf name
        tree (ttk.Treeview): Table widget displaying books assigned to this shelf with
                            columns for id, ISBN, title, and weight
    """

    def __init__(self, parent=None, shelf_id: str = None):
        """
        Initialize the shelf edit window.

        Sets up the window layout with fields for shelf ID (read-only) and shelf name (editable),
        a table displaying all books currently assigned to the shelf, and action buttons for
        managing books and saving changes. Loads the shelf data immediately upon initialization.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control
            shelf_id (str): The ID of the shelf to be edited. Required to load and update
                           the shelf record. If None, the form will display but data loading
                           will be skipped

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (900x520)
            - Initializes ShelfController for database operations
            - Loads shelf data including name and assigned books if shelf_id is provided
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Configures table for multi-selection mode (selectmode='extended')
            - Disables the shelf ID entry field to prevent modification

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail
        """
        super().__init__(parent)
        self._parent_window = parent
        self.shelf_id = shelf_id

        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass

        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.title("Editar Estantería")
        self.geometry("900x520")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        self.controller = ShelfController()

        # layout
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        header = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        header.pack(fill="x", pady=(4, 8))
        title = wf.create_title_label(header, "Editar Estantería")
        title.pack(side="left")

        form = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        form.pack(fill="x", pady=(6, 8))

        lbl = ctk.CTkLabel(form, text="Shelf ID:")
        lbl.pack(side="left", padx=(0, 8))
        self.entry_id = ctk.CTkEntry(form, width=140)
        self.entry_id.pack(side="left")
        try:
            self.entry_id.configure(state="disabled")
        except Exception:
            pass

        name_lbl = ctk.CTkLabel(form, text="Nombre:")
        name_lbl.pack(side="left", padx=(12, 8))
        self.entry_name = ctk.CTkEntry(form, width=320)
        self.entry_name.pack(side="left")

        # table of current books
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both")

        cols = ("id", "ISBN", "title", "weight")
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        try:
            fam, fsize, _ = theme.get_font(self, size=10)
        except Exception:
            fam, fsize = ("Segoe UI", 10)
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=24, fieldbackground=theme.BG_COLOR)

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings", selectmode='extended')
        headings = {"id": "ID", "ISBN": "ISBN", "title": "Título", "weight": "Peso"}
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == 'id':
                self.tree.column(c, width=80, anchor='center')
            elif c == 'ISBN':
                self.tree.column(c, width=120, anchor='center')
            elif c == 'weight':
                self.tree.column(c, width=90, anchor='center')
            else:
                self.tree.column(c, width=360, anchor='w')

        vsb = ttk.Scrollbar(table_holder, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y')
        self.tree.pack(expand=True, fill='both', side='left')

        # actions
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        action_frame.pack(fill='x', pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text='Refrescar', command=self.load_shelf)
        refresh_btn.pack(side='left', padx=(0, 8))

        add_btn = wf.create_primary_button(action_frame, text='Agregar Libros', command=self.open_assign_form)
        add_btn.pack(side='left', padx=(0, 8))

        remove_btn = wf.create_small_button(action_frame, text='Quitar Seleccionados', command=self.remove_selected)
        remove_btn.pack(side='left', padx=(0, 8))

        save_btn = wf.create_primary_button(action_frame, text='Guardar Nombre', command=self.save_name)
        save_btn.pack(side='left', padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text='Regresar', command=self._on_close)
        close_btn.pack(side='left')

        try:
            self.protocol('WM_DELETE_WINDOW', self._on_close)
        except Exception:
            pass

        # load initial data
        if self.shelf_id:
            self.load_shelf()

    def load_shelf(self):
        """
        Load and display the shelf data including name and assigned books.

        Retrieves the shelf record from the controller using the shelf_id, populates the
        ID and name fields, clears the table, and loads all books currently assigned to
        the shelf. Applies alternating row colors to the book table for readability.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Retrieves shelf data from ShelfController
            - Temporarily enables entry_id to populate it, then disables it again
            - Populates entry_id with the shelf ID (read-only)
            - Populates entry_name with the current shelf name
            - Clears all existing rows from the books table
            - Retrieves all books assigned to this shelf via controller
            - Populates table with book data (id, ISBN, title, weight)
            - Applies alternating row background colors (odd/even)
            - Shows error message box if shelf is not found

        Raises:
            Exception: Catches exceptions during field population and book loading,
                      continues processing to display as much data as possible
        """
        s = self.controller.find_shelf(self.shelf_id)
        if not s:
            messagebox.showerror('Error', 'Estantería no encontrada')
            return
        try:
            self.entry_id.configure(state='normal')
            self.entry_id.delete(0, 'end')
            self.entry_id.insert(0, getattr(s, '_Shelf__id', ''))
            self.entry_id.configure(state='disabled')
        except Exception:
            pass
        try:
            name = getattr(s, '_Shelf__name', '')
            self.entry_name.delete(0, 'end')
            self.entry_name.insert(0, str(name))
        except Exception:
            pass

        # populate tree with books in shelf
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            books = self.controller.get_books(self.shelf_id) or []
        except Exception:
            books = []
        for i, b in enumerate(books):
            try:
                bid = b.get_id()
            except Exception:
                bid = getattr(b, '_Book__id', None)
            try:
                isbn = b.get_ISBNCode()
            except Exception:
                isbn = getattr(b, '_Book__ISBNCode', '')
            try:
                title = b.get_title()
            except Exception:
                title = getattr(b, '_Book__title', '')
            try:
                w = b.get_weight()
            except Exception:
                w = getattr(b, '_Book__weight', '')
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert('', 'end', values=(bid, isbn, title, w), tags=(tag,))
        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

    def open_assign_form(self):
        """
        Open the assign book form dialog with the current shelf preselected.

        Creates and displays an AssignBookForm window with the current shelf already
        selected in the dropdown, allowing the user to assign additional books to this
        shelf. Binds a destroy event handler to refresh the shelf book list when the
        assign form is closed.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Creates and displays AssignBookForm as a child window
            - Retrieves current shelf data to format the display value
            - Preselects the current shelf in the assign form's dropdown
            - Binds destroy event to refresh the book table when form closes
            - Shows error message box if the assign form cannot be opened

        Raises:
            Exception: Catches and displays exceptions via message box if the assign
                      form fails to open
        """
        # open existing AssignBookForm and preselect shelf
        try:
            win = AssignBookForm(self)
            # set option menu to our shelf id - find display value
            shelf = self.controller.find_shelf(self.shelf_id)
            if shelf:
                sid = getattr(shelf, '_Shelf__id', '')
                name = shelf.get_name() if hasattr(shelf, 'get_name') else getattr(shelf, '_Shelf__name', '')
                display = f"{sid} - {name}" if name else sid
                try:
                    win.shelf_box.configure(values=[display])
                    win.shelf_var.set(display)
                except Exception:
                    pass
            # when assign form closes, refresh our view
            try:
                def _on_close(event=None):
                    if getattr(self, 'tree', None) and self.tree.winfo_exists():
                        self.load_shelf()
                win.bind('<Destroy>', _on_close)
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo abrir el formulario de asignación: {e}')

    def remove_selected(self):
        """
        Remove the selected books from the shelf.

        Validates that at least one book is selected, then iterates through all selected
        books and removes each from the shelf via the shelf controller. Displays a summary
        of successes and failures with detailed error messages for failed removals. Refreshes
        the shelf data after the operation.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no books are selected
            - Retrieves ISBN from each selected table row
            - Calls shelf_controller.remove_book for each selected book
            - Controller persists changes automatically
            - Shows result message box with success/failure counts and error details
            - Displays up to 10 error details for failed removals
            - Refreshes the shelf book table after the operation

        Raises:
            Exception: Catches exceptions for each book removal individually,
                      continues processing remaining books if one fails
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo('Info', 'Selecciona uno o más libros para quitar de la estantería.')
            return
        successes = 0
        failures = 0
        details = []
        for item in sel:
            try:
                vals = self.tree.item(item, 'values')
                isbn = vals[1]
            except Exception:
                failures += 1
                continue
            try:
                removed = self.controller.remove_book(self.shelf_id, isbn)
                if removed:
                    successes += 1
                else:
                    failures += 1
                    details.append(isbn)
            except Exception as e:
                failures += 1
                details.append(f"{isbn}:{e}")
        msg = f'Quitados: {successes}  Fallidos: {failures}'
        if details:
            msg += "\n" + "; ".join(details[:10])
        messagebox.showinfo('Resultado', msg)
        self.load_shelf()

    def save_name(self):
        """
        Save the updated shelf name to the database.

        Validates that the shelf ID is valid, retrieves the shelf object from the controller,
        updates the shelf name with the value from the entry field, and persists the changes
        to the file system. Displays success or error messages based on the operation result.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message if shelf_id is invalid
            - Extracts name from entry_name field and trims whitespace
            - Retrieves shelf object from ShelfController
            - Shows error message if shelf is not found
            - Updates the shelf name via setter or direct attribute access
            - Persists changes to the shelves file via service.save_to_file
            - Shows success message box if name is updated successfully
            - Shows error message box if update fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sid = self.shelf_id
        if not sid:
            messagebox.showerror('Error', 'Shelf ID inválido')
            return
        name = (self.entry_name.get() or '').strip()
        try:
            shelf = self.controller.find_shelf(sid)
            if shelf is None:
                messagebox.showerror('Error', 'Estantería no encontrada')
                return
            try:
                shelf.set_name(name)
            except Exception:
                try:
                    setattr(shelf, '_Shelf__name', name)
                except Exception:
                    pass
            # persist
            try:
                self.controller.service.save_to_file(FilePaths.SHELVES)
            except Exception:
                pass
            messagebox.showinfo('Guardado', 'Nombre actualizado correctamente')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the shelf edit window and returns focus to the parent window.
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


__all__ = ['ShelfEdit']
