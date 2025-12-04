"""
Loan List Window Module

This module provides a graphical user interface for viewing and managing all loan
records in the library management system. It displays loans in a table format with
full CRUD operations including viewing, editing, deleting, and searching loans.
The interface includes double-click editing and automatic refresh functionality.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from controllers.loan_controller import LoanController
from ui.loan.loan_edit import LoanEdit


class LoanList(ctk.CTkToplevel):
    """
    A top-level window for displaying and managing all loan records.

    This class provides a comprehensive interface for loan management with a table
    displaying all loans and action buttons for searching, refreshing, editing, and
    deleting records. Users can double-click a row to edit a loan or use the action
    buttons. The table shows loan ID, user ID, ISBN, book ID, loan date, and return status.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (LoanController): The loan controller instance for database operations
        tree (ttk.Treeview): The table widget displaying all loan records with columns
                            for loan_id, user_id, isbn, book_id, loan_date, and returned status
    """

    def __init__(self, parent=None):
        """
        Initialize the loan list window.

        Sets up the window layout with a table displaying all loans and action buttons
        for managing them. Applies styling, configures the table with appropriate columns,
        and loads all loans from the database. Sets up event handlers for double-click
        editing and window closing.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (900x550)
            - Loads all loan records from the database via LoanController
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Binds double-click event to open edit dialog
            - Automatically loads and displays all loans on initialization

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

        self.title("Listado de Préstamos")
        self.geometry("900x550")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Préstamos")
        title_lbl.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("loan_id", "user_id", "isbn", "book_id", "loan_date", "returned")

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

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")
        headings = {"loan_id": "ID", "user_id": "Usuario", "isbn": "ISBN", "book_id": "ID Libro", "loan_date": "Fecha", "returned": "Devuelto"}
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "loan_id":
                self.tree.column(c, width=120, anchor="center")
            elif c == "book_id":
                self.tree.column(c, width=100, anchor="center")
            elif c == "returned":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=140, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        search_btn = wf.create_small_button(action_frame, text="Buscar", command=self.open_search_window)
        search_btn.pack(side="left", padx=(0, 8))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_loans)
        refresh_btn.pack(side="left", padx=(0, 8))

        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        return_btn = wf.create_small_button(action_frame, text="Devolver Libro", command=self.return_selected_loan)
        return_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = LoanController()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

        # initial load
        self.load_loans()

    def load_loans(self):
        """
        Load and display all loan records in the table.

        Clears the current table contents and retrieves all loans from the controller,
        then populates the table with loan data including loan ID, user ID, ISBN,
        loan date, and return status. Applies alternating row colors for better readability.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all existing rows from the table
            - Retrieves all loans from LoanController
            - Populates table with loan records
            - Applies alternating row background colors (odd/even)
            - Shows error message box if loading fails
            - Converts loan dates to ISO format for display

        Raises:
            Exception: Catches and displays errors via message box if loan loading fails
        """
        # clear rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            loans = self.controller.list_loans()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar préstamos: {e}")
            return

        for i, l in enumerate(loans):
            try:
                lid = l.get_loan_id()
                uid = l.get_user_id()
                isbn = l.get_isbn()
                book_id = l.get_book_id() if l.get_book_id() else "N/A"
                ldate = l.get_loan_date()
                try:
                    ldate = ldate.isoformat()
                except Exception:
                    pass
                returned = "Sí" if l.is_returned() else "No"
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=(lid, uid, isbn, book_id, ldate, returned), tags=(tag,))
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

        Properly closes the loan list window and returns focus to the parent window.
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
        Open the edit dialog for the selected loan record.

        Retrieves the loan ID from the selected table row, fetches the full loan object
        from the controller, and opens the LoanEdit dialog. Automatically refreshes the
        table when the edit dialog is closed. Also handles double-click events on table rows.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no loan is selected
            - Shows error message if the selected row cannot be read
            - Shows error message if the loan is not found in the database
            - Opens LoanEdit window as a top-level dialog
            - Binds a destroy event handler to refresh the table when edit window closes
            - Automatically refreshes the loan list after editing

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un préstamo en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            loan_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            loan = self.controller.get_loan(loan_id)
            if loan is None:
                messagebox.showerror("Error", f"Préstamo {loan_id} no encontrado")
                return

            parent = self._parent_window or self
            win = LoanEdit(parent, loan, controller=self.controller)

            # refresh the list when the edit window is closed
            try:
                def _on_child_destroy(event=None):
                    try:
                        if getattr(self, 'tree', None) and self.tree.winfo_exists():
                            self.load_loans()
                    except Exception:
                        pass

                win.bind('<Destroy>', _on_child_destroy)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def return_selected_loan(self):
        """
        Mark the selected loan as returned.

        Retrieves the loan ID from the selected table row, checks if it's already
        returned, and marks it as returned if not. Refreshes the table after
        successful return operation. This updates the book's availability status.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no loan is selected
            - Shows error message if the selected row cannot be read
            - Shows info message if the loan is already marked as returned
            - Shows confirmation dialog before marking as returned
            - Marks the loan as returned via controller
            - Updates book availability in the database
            - Shows success message if return succeeds
            - Shows error message if return fails
            - Refreshes the loan list after successful return

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un préstamo en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            loan_id = values[0]
            returned_status = values[5]  # La columna "returned" está en la posición 5
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        # Verificar si ya está devuelto
        if returned_status == "Sí":
            messagebox.showinfo("Info", f"El préstamo {loan_id} ya fue devuelto anteriormente.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Marcar el préstamo {loan_id} como devuelto?"):
            return

        try:
            res = self.controller.return_loan(loan_id)
            if res.get('success'):
                messagebox.showinfo("Éxito", "Libro devuelto correctamente.")
                self.load_loans()
            else:
                messagebox.showerror("Error", res.get('message'))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        """
        Delete the selected loan record from the database.

        Retrieves the loan ID from the selected table row, prompts the user for
        confirmation, and deletes the loan if confirmed. Refreshes the table after
        successful deletion. Warns the user that this action cannot be undone.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no loan is selected
            - Shows error message if the selected row cannot be read
            - Shows confirmation dialog before deletion
            - Deletes the loan record from the database via controller
            - Shows success message if deletion succeeds
            - Shows error message if deletion fails
            - Refreshes the loan list after successful deletion

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un préstamo en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            loan_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el préstamo {loan_id}? Esta acción no se puede deshacer?"):
            return

        try:
            res = self.controller.delete_loan(loan_id)
            if res.get('success'):
                messagebox.showinfo("Borrado", "Préstamo eliminado correctamente.")
                self.load_loans()
            else:
                messagebox.showerror("Error", res.get('message'))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_search_window(self):
        """
        Open the loan search window for advanced search functionality.

        Creates and displays a new LoanSearch window as a child of this window,
        allowing users to perform advanced searches on loan records using various
        search criteria and algorithms.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Imports the LoanSearch class dynamically
            - Creates and displays a new LoanSearch top-level window
            - Shows error message box if the search window cannot be opened

        Raises:
            Exception: Catches and displays exceptions via message box if
                      the search window fails to open
        """
        try:
            from ui.loan.loan_search import LoanSearch
            search_window = LoanSearch(parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la ventana de búsqueda: {e}")


__all__ = ["LoanList"]
