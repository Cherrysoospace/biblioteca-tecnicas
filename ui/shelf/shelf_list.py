"""
Shelf List Window Module

This module provides a graphical user interface for viewing and managing all shelf
records in the library management system. It displays shelves in a table format with
detailed information including assigned books, capacity, weight statistics, and search
functionality. The interface supports full CRUD operations including viewing, searching,
editing, and deleting shelves.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from ui.shelf.shelf_edit import ShelfEdit
from controllers.shelf_controller import ShelfController
from utils.config import FilePaths


class ShelfList(ctk.CTkToplevel):
    """
    A top-level window for displaying and managing all shelf records.

    This class provides a comprehensive interface for shelf management with a searchable
    table displaying all shelves and action buttons for refreshing, editing, and deleting
    records. Users can double-click a row to edit a shelf or use the action buttons.
    The table shows detailed information for each shelf including ID, name, list of assigned
    books with weights, total capacity, book count, total weight, and remaining capacity.
    Supports dynamic row height adjustment based on the number of books displayed.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (ShelfController): The shelf controller instance for database operations
        _tree_style (ttk.Style): Reference to the ttk style for dynamic row height adjustment
        search_entry (CTkEntry): Entry field for search input (ID or name)
        tree (ttk.Treeview): Table widget displaying all shelf records with columns for
                            id, name, books (with weights), capacity, books_count,
                            total_weight, and remaining capacity
    """

    def __init__(self, parent=None):
        """
        Initialize the shelf list window.

        Sets up the window layout with a search bar at the top, a table displaying all
        shelves with detailed information, and action buttons for managing shelves. Applies
        styling, configures the table with dynamic row heights based on book count, and
        loads all shelves from the database. Sets up event handlers for search (Enter key),
        double-click editing, and window closing.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (1000x700, min 800x500)
            - Initializes ShelfController for database operations
            - Loads all shelf records from the database
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Binds Enter key in search field to perform search
            - Binds double-click event to open edit dialog
            - Configures grid layout for responsive sizing
            - Automatically calculates and sets dynamic row heights based on book count

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail
        """
        super().__init__(parent)
        self._parent_window = parent

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

        self.title("Listado de Estanterías")
        # increase default size so action buttons remain visible when rows are tall
        self.geometry("1000x700")
        try:
            # reasonable minimum to avoid truncating controls
            self.minsize(800, 500)
        except Exception:
            pass
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Use grid inside container so we can reserve a fixed row for actions
        # and let the table expand in the middle row.
        container.grid_rowconfigure(0, weight=0)  # título
        container.grid_rowconfigure(1, weight=0)  # búsqueda
        container.grid_rowconfigure(2, weight=1)  # tabla
        container.grid_rowconfigure(3, weight=0)  # acciones
        container.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(6, 8))
        title_lbl = wf.create_title_label(title_frame, "Listado de Estanterías")
        title_lbl.pack(side="left")

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        search_label = ctk.CTkLabel(search_frame, text="Buscar:", 
                                    font=theme.get_font(self, size=11))
        search_label.pack(side="left", padx=(0, 8))

        self.search_entry = ctk.CTkEntry(search_frame, width=300, 
                                         placeholder_text="Buscar por ID o nombre...")
        self.search_entry.pack(side="left", padx=(0, 8))
        
        # Bind Enter key to search
        try:
            self.search_entry.bind("<Return>", lambda e: self.search_shelves())
        except Exception:
            pass

        search_btn = wf.create_small_button(search_frame, text="Buscar", command=self.search_shelves)
        search_btn.pack(side="left", padx=(0, 8))

        clear_btn = wf.create_small_button(search_frame, text="Limpiar", command=self.clear_search)
        clear_btn.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.grid(row=2, column=0, sticky="nsew", padx=0, pady=(8, 8))

        cols = ("id", "name", "books", "capacity", "books_count", "total_weight", "remaining")

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
        # keep a reference to the ttk style so we can adjust rowheight dynamically
        self._tree_style = style

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
        headings = {
            "id": "ID",
            "name": "Nombre",
            "books": "Libros (ID(peso))",
            "capacity": "Capacidad(kg)",
            "books_count": "# Libros",
            "total_weight": "Peso total(kg)",
            "remaining": "Restante(kg)",
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "id":
                self.tree.column(c, width=90, anchor="center")
            elif c == "books":
                self.tree.column(c, width=280, anchor="w")
            elif c in ("capacity", "books_count", "total_weight", "remaining"):
                self.tree.column(c, width=110, anchor="center")
            else:
                self.tree.column(c, width=160, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        # place the action frame in the bottom grid row so it stays visible
        action_frame.grid(row=3, column=0, sticky="ew", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_shelves)
        refresh_btn.pack(side="left", padx=(0, 8))

        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = ShelfController()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

        self.load_shelves()

    def load_shelves(self, shelves=None):
        """
        Load and display shelf records in the table with detailed information.

        Clears the current table contents and retrieves all shelves (or uses provided filtered
        shelves). For each shelf, displays ID, name, a formatted list of books with their weights,
        capacity, book count, total weight, and remaining capacity. Dynamically calculates and
        sets row height based on the maximum number of book lines displayed (capped at 10 books
        per shelf to prevent excessive row heights). Applies alternating row colors for readability.

        Parameters:
            shelves (list, optional): Pre-filtered list of shelf objects to display. If None,
                                     loads all shelves from the controller. Defaults to None

        Returns:
            None

        Side Effects:
            - Clears all existing rows from the table
            - Retrieves all shelves from ShelfController if shelves parameter is None
            - For each shelf, retrieves assigned books via controller
            - Formats book information as "id: X, peso: Ykg" with line breaks
            - Limits display to 10 books per shelf, showing "... y N más" for overflow
            - Calculates statistics: total weight and remaining capacity
            - Dynamically adjusts table row height (22px per line + 8px padding)
            - Applies alternating row background colors (odd/even)
            - Shows error message box if loading fails
            - Continues processing remaining shelves if individual shelf loading fails

        Raises:
            Exception: Catches and displays errors via message box if shelf loading fails,
                      continues processing remaining shelves if individual shelf fails
        """
        # Limpiar filas existentes
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            if shelves is None:
                shelves = self.controller.list_shelves()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las estanterías: {e}")
            return

        # Preparar filas y determinar altura necesaria basada en número de líneas
        rows = []
        max_lines = 1
        LINE_CAP = 10  # evitar filas extremadamente altas

        def fmt_weight(v):
            """Formatear peso para mostrar"""
            try:
                fv = float(v)
                s = f"{fv:.2f}".rstrip('0').rstrip('.')
                return s
            except Exception:
                return str(v)

        for i, shelf in enumerate(shelves):
            try:
                # Obtener datos básicos de la estantería usando getters
                sid = shelf.get_id()
                name = shelf.get_name()
                capacity = shelf.capacity

                # Obtener libros de la estantería
                try:
                    books_objs = self.controller.get_books(sid)
                    lines = []
                    for b in books_objs:
                        try:
                            bid = b.get_id()
                            w = fmt_weight(b.get_weight())
                            if w == '':
                                lines.append(f"id: {bid}, peso: -")
                            else:
                                lines.append(f"id: {bid}, peso: {w}kg")
                        except Exception:
                            continue
                except Exception:
                    lines = []
                    books_objs = []

                # Aplicar límite y calcular string de visualización con saltos de línea
                extra = 0
                if len(lines) > LINE_CAP:
                    extra = len(lines) - LINE_CAP
                    disp_lines = lines[:LINE_CAP]
                    disp_lines.append(f"... y {extra} más")
                else:
                    disp_lines = lines

                books_display = "\n".join(disp_lines) if disp_lines else "-"
                line_count = max(1, len(disp_lines))
                if line_count > max_lines:
                    max_lines = line_count

                # Calcular estadísticas usando métodos del servicio
                books_count = len(books_objs)
                try:
                    total_w = fmt_weight(self.controller.service.total_weight(sid))
                except Exception:
                    total_w = '0'
                
                try:
                    remaining = fmt_weight(self.controller.service.remaining_capacity(sid))
                except Exception:
                    remaining = fmt_weight(capacity)

                tag = 'even' if i % 2 == 0 else 'odd'
                rows.append((sid, name, books_display, fmt_weight(capacity), books_count, total_w, remaining, tag))
            except Exception as e:
                # Si hay error con una estantería específica, continuar con las demás
                continue

        # Actualizar altura de fila para ajustar líneas (22px por línea + padding adicional)
        try:
            height = max(24, 22 * max_lines + 8)
            self._tree_style.configure("Treeview", rowheight=height)
        except Exception:
            pass

        # Insertar filas en la tabla
        for row in rows:
            try:
                self.tree.insert("", "end", values=row[:-1], tags=(row[-1],))
            except Exception:
                continue

        # Configurar colores alternados para las filas
        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the shelf list window and returns focus to the parent window.
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
        Open the edit dialog for the selected shelf record.

        Retrieves the shelf ID from the selected table row and opens the ShelfEdit dialog
        which allows editing the shelf name and managing assigned books. Binds a destroy
        event handler to refresh the shelf list when the edit dialog is closed. Also handles
        double-click events on table rows.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no shelf is selected
            - Shows error message if the selected row cannot be read
            - Opens ShelfEdit window as a top-level dialog with the shelf_id
            - Binds destroy event to refresh the shelf table when edit window closes
            - Automatically refreshes the shelf list after editing

        Raises:
            Exception: Catches and displays exceptions via message box if edit window
                      cannot be opened
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una estantería en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            shelf_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            parent = self._parent_window or self
            # open the ShelfEdit dialog which supports editing name and books
            win = ShelfEdit(parent, shelf_id=shelf_id)

            try:
                def _on_child_destroy(event=None):
                    try:
                        if getattr(self, 'tree', None) and self.tree.winfo_exists():
                            self.load_shelves()
                    except Exception:
                        pass

                win.bind('<Destroy>', _on_child_destroy)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el formulario de edición.\n{e}")

    def delete_selected(self):
        """
        Delete the selected shelf record from the database.

        Validates that a shelf is selected, retrieves the shelf ID from the selected table row,
        prompts the user for confirmation, and deletes the shelf if confirmed. Warns the user
        that this action will delete both the shelf and all its assigned books. Refreshes the
        table after successful deletion.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no shelf is selected
            - Shows error message if the selected row cannot be read
            - Shows confirmation dialog warning about shelf and content deletion
            - Deletes the shelf record from the database via controller
            - Shows error message if shelf is not found or deletion fails
            - Shows success message if deletion succeeds
            - Refreshes the shelf list after successful deletion

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una estantería en la tabla.")
            return
        
        try:
            values = self.tree.item(sel[0], "values")
            shelf_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar la estantería {shelf_id}? Esta acción eliminará la estantería y su contenido."):
            return

        try:
            deleted = self.controller.delete_shelf(shelf_id)
            
            if not deleted:
                messagebox.showerror("Error", "Estantería no encontrada o no se pudo eliminar.")
                return

            messagebox.showinfo("Borrado", "Estantería eliminada correctamente.")
            self.load_shelves()
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar la estantería: {e}")

    def search_shelves(self):
        """
        Search for shelves by ID or name.

        Extracts the search term from the search entry field, delegates the search operation
        to the controller (following OOP principles), and displays the filtered results in
        the table. Shows an info message if no matches are found. This method is triggered
        by clicking the search button or pressing Enter in the search field.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if search term is empty
            - Extracts and trims search term from search_entry field
            - Calls shelf_controller.search_shelves with the search term
            - Displays filtered shelves in the table via load_shelves
            - Shows info message if no shelves match the search term
            - Shows empty table if no results found
            - Shows error message box if search operation fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showinfo("Info", "Ingrese un término de búsqueda.")
            return
        
        try:
            # Delegar la búsqueda al controlador (principio de POO)
            filtered_shelves = self.controller.search_shelves(search_term)
            
            if not filtered_shelves:
                messagebox.showinfo("Búsqueda", f"No se encontraron estanterías que coincidan con '{search_term}'.")
                self.load_shelves([])  # Mostrar tabla vacía
                return

            self.load_shelves(filtered_shelves)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")

    def clear_search(self):
        """
        Clear the search field and reload all shelves.

        Removes the search term from the search entry field and reloads the complete
        shelf list, effectively resetting the view to show all shelves.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all text from the search_entry field
            - Reloads and displays all shelves via load_shelves
            - Shows error message box if clear operation fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
        try:
            self.search_entry.delete(0, 'end')
            self.load_shelves()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo limpiar la búsqueda: {e}")


__all__ = ["ShelfList"]
