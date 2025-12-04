"""
Assign Book to Shelf Form Module

This module provides a graphical user interface for assigning books to shelves
in the library management system. It displays available (unassigned) books in a
table and allows users to select one or more books to assign to a chosen shelf.
The form validates shelf capacity and prevents double assignment of books.
"""

import os
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import ttk, messagebox

from ui import theme
from ui import widget_factory as wf
from controllers.book_controller import BookController
from controllers.shelf_controller import ShelfController


class AssignBookForm(ctk.CTkToplevel):
    """
    A top-level window for assigning books to shelves.

    This class provides a graphical interface that displays unassigned books in a table
    and allows users to select a shelf from a dropdown, then assign one or more selected
    books to that shelf. The form supports multi-selection and batch assignment, showing
    detailed results of the operation including successes and failures. Only books that
    are not already assigned to any shelf are displayed.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        book_controller (BookController): Controller instance for book database operations
        shelf_controller (ShelfController): Controller instance for shelf database operations
        shelf_var (StringVar): Variable tracking the selected shelf from the dropdown
        shelf_box (CTkOptionMenu): Dropdown widget for selecting the target shelf
        tree (ttk.Treeview): Table widget displaying available (unassigned) books with
                            columns for id, ISBNCode, title, author, weight, and price
    """

    def __init__(self, parent=None):
        """
        Initialize the assign book to shelf form window.

        Sets up the window layout with a shelf selector dropdown at the top, a table
        displaying all unassigned books, and action buttons for assigning selected books.
        Applies styling, configures the table with multi-selection mode, and loads both
        shelves and available books from the database.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (900x520)
            - Initializes BookController and ShelfController for database operations
            - Loads all shelves from the database and populates the dropdown
            - Loads all unassigned books from the database and displays them in the table
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Configures table for multi-selection mode (selectmode='extended')

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
        
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.title("Asignar Libros a Estantería")
        self.geometry("900x520")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        self.book_controller = BookController()
        self.shelf_controller = ShelfController()

        # main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # header
        header = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        header.pack(fill="x", pady=(4, 8))
        title = wf.create_title_label(header, "Asignar Libros a Estantería")
        title.pack(side="left")

        # shelf selector
        sel_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        sel_frame.pack(fill="x", pady=(6, 8))
        lbl = ctk.CTkLabel(sel_frame, text="Seleccionar Estantería:")
        lbl.pack(side="left", padx=(0, 8))
        self.shelf_var = ctk.StringVar()
        self.shelf_box = ctk.CTkOptionMenu(sel_frame, variable=self.shelf_var, values=[], width=300)
        self.shelf_box.pack(side="left")

        refresh_shelves_btn = wf.create_small_button(sel_frame, text="Refrescar Estanterías", command=self.load_shelves)
        refresh_shelves_btn.pack(side="left", padx=(8, 0))

        # table holder for books
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both")

        cols = ("id", "ISBNCode", "title", "author", "weight", "price")

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

        try:
            style.map("Treeview",
                      background=[('selected', theme.ACCENT_RED)],
                      foreground=[('selected', '#ffffff')])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings", selectmode='extended')
        headings = {
            "id": "ID",
            "ISBNCode": "ISBN",
            "title": "Título",
            "author": "Autor",
            "weight": "Peso",
            "price": "Precio",
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "id":
                self.tree.column(c, width=70, anchor="center")
            elif c in ("price", "weight"):
                self.tree.column(c, width=90, anchor="center")
            else:
                self.tree.column(c, width=220, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # actions
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar Libros", command=self.load_books)
        refresh_btn.pack(side="left", padx=(0, 8))

        assign_btn = wf.create_primary_button(action_frame, text="Asignar Seleccionados", command=self.assign_selected)
        assign_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        # initial load
        self.load_shelves()
        self.load_books()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def load_shelves(self):
        """
        Load and populate the shelf selector dropdown with available shelves.

        Retrieves all shelves from the shelf controller and populates the dropdown menu
        with shelf options formatted as "ID - Name". Sets the first shelf as the default
        selection. Displays "(no shelves)" if no shelves are available.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Retrieves all shelves from ShelfController
            - Updates shelf_box dropdown values with formatted shelf options
            - Sets shelf_var to the first shelf by default
            - Shows "(no shelves)" message if no shelves exist
            - Shows error message box if loading fails

        Raises:
            Exception: Catches and displays errors via message box if shelf loading fails
        """
        # populate option menu with 'ID - name' values
        try:
            shelves = self.shelf_controller.list_shelves()
            vals = []
            for s in shelves:
                sid = getattr(s, '_Shelf__id', '')
                name = s.get_name() if hasattr(s, 'get_name') else getattr(s, '_Shelf__name', '')
                display = f"{sid} - {name}" if name else sid
                vals.append(display)
            # update option menu
            if vals:
                self.shelf_box.configure(values=vals)
                # default to first
                try:
                    self.shelf_var.set(vals[0])
                except Exception:
                    pass
            else:
                self.shelf_box.configure(values=["(no shelves)"])
                self.shelf_var.set("(no shelves)")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar estanter\u00edas: {e}")

    def load_books(self):
        """
        Load and display all unassigned books in the table.

        Clears the current table contents and retrieves all books from the book controller.
        Filters out books that are already assigned to any shelf using the shelf controller's
        is_book_assigned check. Populates the table with unassigned books showing ID, ISBN,
        title, author, weight, and price. Applies alternating row colors for readability.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all existing rows from the table
            - Retrieves all books from BookController
            - Checks each book's assignment status via ShelfController
            - Populates table only with unassigned books
            - Applies alternating row background colors (odd/even)
            - Shows error message box if loading fails
            - Skips books that fail assignment check (conservative approach)

        Raises:
            Exception: Catches and displays errors via message box if book loading fails,
                      continues processing remaining books if individual book loading fails
        """
        # clear rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            books = self.book_controller.get_all_books()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los libros: {e}")
            return

        # insert books from controller (Book objects)
        for i, b in enumerate(books):
            try:
                bid = b.get_id()
            except Exception:
                try:
                    bid = getattr(b, '_Book__id', None)
                except Exception:
                    bid = None
            # skip books that are already assigned to any shelf
            try:
                if bid and self.shelf_controller.is_book_assigned(bid):
                    continue
            except Exception:
                # conservative: if check fails, skip the book
                continue

            try:
                row = (
                    b.get_id(),
                    b.get_ISBNCode(),
                    b.get_title(),
                    b.get_author(),
                    b.get_weight(),
                    b.get_price(),
                )
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert('', 'end', values=row, tags=(tag,))
            except Exception:
                continue

        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

    def _selected_shelf_id(self) -> str:
        """
        Extract and return the shelf ID from the selected dropdown value.

        Parses the selected shelf dropdown value which is formatted as "ID - Name" or "ID"
        and extracts just the ID portion by splitting on the delimiter and taking the
        first token.

        Parameters:
            None

        Returns:
            str: The shelf ID extracted from the dropdown selection, or empty string if
                 no valid selection exists

        Side Effects:
            None

        Raises:
            None
        """
        v = self.shelf_var.get() or ''
        # value is either 'ID - name' or 'ID'; take first token split
        return v.split(' - ')[0].strip()

    def assign_selected(self):
        """
        Assign the selected books to the chosen shelf.

        Validates that a valid shelf is selected and that at least one book is selected.
        Iterates through all selected books and attempts to assign each to the shelf via
        the shelf controller. The controller handles capacity validation and persistence.
        Displays a summary of successes and failures with detailed error messages for
        failed assignments.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows error message if no valid shelf is selected
            - Shows info message if no books are selected
            - Retrieves full book objects for each selected book ID
            - Calls shelf_controller.add_book for each selected book
            - Controller validates shelf capacity and prevents double assignment
            - Controller persists changes automatically
            - Shows result message box with success/failure counts and error details
            - Displays up to 10 error details for failed assignments

        Raises:
            Exception: Catches exceptions for each book assignment individually,
                      continues processing remaining books if one fails
        """
        sid = self._selected_shelf_id()
        if not sid or sid == '(no shelves)':
            messagebox.showerror("Error", "Selecciona una estantería válida.")
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona uno o más libros para asignar.")
            return

        successes = 0
        failures = 0
        details = []

        for item in sel:
            try:
                vals = self.tree.item(item, 'values')
                book_id = vals[0]
            except Exception:
                failures += 1
                continue
            try:
                book = self.book_controller.get_book(book_id)
                if book is None:
                    failures += 1
                    details.append(f"{book_id}: no encontrado")
                    continue
                ok = self.shelf_controller.add_book(sid, book)
                if ok:
                    successes += 1
                else:
                    failures += 1
                    details.append(f"{book_id}: no cabe o error")
            except Exception as e:
                failures += 1
                details.append(f"{book_id}: {e}")

        msg = f"Asignados: {successes}  Fallidos: {failures}"
        if details:
            msg += "\n" + "; ".join(details[:10])
        messagebox.showinfo("Resultado", msg)
        # refresh shelf data saved on controller
        try:
            # persist already handled by controller.add_book
            pass
        except Exception:
            pass

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the assign book form window and returns focus to the parent window.
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


__all__ = ["AssignBookForm"]
