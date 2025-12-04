"""
User List Window Module

This module provides a graphical user interface for viewing and managing all user
records in the library management system. It displays users in a table format with
search functionality and full CRUD operations including viewing, searching, editing,
and deleting users. The module includes comprehensive logging and error handling
for robust operation.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from ui.user.user_form import UserForm
from controllers.user_controller import UserController
from utils.logger import LibraryLogger, UIErrorHandler

# Configure logger for this module
logger = LibraryLogger.get_logger(__name__)


class UserList(ctk.CTkToplevel):
    """
    A top-level window for displaying and managing all user records.

    This class provides a comprehensive interface for user management with a searchable
    table displaying all users and action buttons for refreshing, editing, and deleting
    records. Users can double-click a row to edit a user or use the action buttons. The
    table shows user ID and name. Includes search functionality by ID or name with Enter
    key support. All operations are logged and errors are handled gracefully using the
    UIErrorHandler.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        controller (UserController): The user controller instance for database operations
        search_entry (CTkEntry): Entry field for search input (ID or name)
        tree (ttk.Treeview): Table widget displaying all user records with columns
                            for id and name
    """

    def __init__(self, parent=None):
        """
        Initialize the user list window.

        Sets up the window layout with a search bar at the top, a table displaying all
        users, and action buttons for managing users. Applies styling, configures the table,
        and loads all users from the database. Sets up event handlers for search (Enter key),
        double-click editing, and window closing. All initialization errors are logged and
        handled gracefully.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (600x420)
            - Initializes UserController for database operations
            - Loads all user records from the database
            - Applies application theme to the window and table
            - Makes the window transient to the parent if provided
            - Binds Enter key in search field to perform search
            - Binds double-click event to open edit dialog
            - Applies alternating row colors for readability
            - Logs all significant events and errors

        Raises:
            Exception: Catches and logs various exceptions during initialization,
                      continues execution to ensure the window opens even if some
                      non-critical operations fail
        """
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "aplicar window scaling", e)
        
        try:
            theme.apply_theme(self)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "aplicar tema", e)
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception as config_e:
                UIErrorHandler.log_and_pass(logger, "configurar color de fondo", config_e)

        self.title("Listado de Usuarios")
        self.geometry("600x420")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "configurar ventana transient", e)

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Usuarios")
        title_lbl.pack(side="left")

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        search_frame.pack(fill="x", pady=(0, 8))

        search_label = ctk.CTkLabel(search_frame, text="Buscar:", 
                                    font=theme.get_font(self, size=11))
        search_label.pack(side="left", padx=(0, 8))

        self.search_entry = ctk.CTkEntry(search_frame, width=300, 
                                         placeholder_text="Buscar por ID o nombre...")
        self.search_entry.pack(side="left", padx=(0, 8))
        
        # Bind Enter key to search
        try:
            self.search_entry.bind("<Return>", lambda e: self.search_users())
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "bind Enter key en search_entry", e)

        search_btn = wf.create_small_button(search_frame, text="Buscar", command=self.search_users)
        search_btn.pack(side="left", padx=(0, 8))

        clear_btn = wf.create_small_button(search_frame, text="Limpiar", command=self.clear_search)
        clear_btn.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("id", "name")

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "configurar tema ttk 'clam'", e)

        try:
            fam, fsize, fweight = theme.get_font(self, size=10)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "obtener font de tema", e)
            fam, fsize, fweight = ("Segoe UI", 10, "normal")
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=24, fieldbackground=theme.BG_COLOR)

        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "obtener font bold de tema", e)
            hfam, hfsize = (fam, fsize + 1)
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        try:
            style.map("Treeview",
                      background=[('selected', theme.ACCENT_RED)],
                      foreground=[('selected', '#ffffff')])
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "mapear colores de Treeview", e)

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")
        headings = {"id": "ID", "name": "Nombre"}
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "id":
                self.tree.column(c, width=110, anchor="center")
            else:
                self.tree.column(c, width=400, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_users)
        refresh_btn.pack(side="left", padx=(0, 8))

        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = UserController()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "configurar protocolo WM_DELETE_WINDOW", e)

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "bind double-click en tree", e)

        # initial load
        self.load_users()

    def load_users(self):
        """
        Load and display all user records in the table.

        Clears the current table contents and retrieves all users from the controller,
        then populates the table with user data including ID and name. Applies alternating
        row colors for better readability. Logs the number of users loaded and any errors
        encountered during the process.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all existing rows from the table
            - Retrieves all users from UserController
            - Populates table with user records
            - Applies alternating row background colors (odd/even)
            - Logs info message with user count
            - Shows error message box if loading fails
            - Logs warning for individual user insertion failures

        Raises:
            Exception: Catches and handles errors via UIErrorHandler, logs warnings
                      for individual user insertion failures and continues processing
        """
        # clear rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            users = self.controller.get_all_users()
            logger.info(f"Cargados {len(users)} usuarios")
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al cargar usuarios",
                user_message="No se pudo cargar la lista de usuarios. Por favor, intente nuevamente."
            )
            return

        for i, u in enumerate(users):
            try:
                uid = u.get_id()
                name = u.get_name()
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=(uid, name), tags=(tag,))
            except Exception as e:
                logger.warning(f"Error insertando usuario en tabla (índice {i}): {e}")
                continue

        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "configurar tags de colores en tree", e)

    def search_users(self):
        """
        Search for users by ID or name.

        Extracts the search term from the search entry field and performs searches using
        both find_by_id and find_by_name controller methods. Combines results and removes
        duplicates. Displays filtered results in the table. Logs search operations and
        result counts. This method is triggered by clicking the search button or pressing
        Enter in the search field.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if search term is empty
            - Clears all existing rows from the table
            - Extracts and trims search term from search_entry field
            - Calls controller.find_by_id to search by ID
            - Calls controller.find_by_name to search by name
            - Combines results and removes duplicates
            - Logs info message with search term and result count
            - Shows info message if no users match the search term
            - Populates table with filtered user records
            - Applies alternating row background colors (odd/even)
            - Shows error message box if search operation fails
            - Logs all operations and errors

        Raises:
            Exception: Catches and handles errors via UIErrorHandler, logs warnings
                      for individual user insertion failures
        """
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showinfo("Info", "Ingrese un término de búsqueda.")
            return
        
        # clear rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            # Usar los métodos existentes del controlador (find_by_id y find_by_name)
            filtered_users = []
            
            # Buscar por ID
            user_by_id = self.controller.find_by_id(search_term)
            if user_by_id:
                filtered_users.append(user_by_id)
            
            # Buscar por nombre (puede retornar múltiples usuarios)
            users_by_name = self.controller.find_by_name(search_term)
            if users_by_name:
                # Evitar duplicados si ya se encontró por ID
                for u in users_by_name:
                    if u not in filtered_users:
                        filtered_users.append(u)
            
            logger.info(f"Búsqueda '{search_term}': {len(filtered_users)} resultados")
            
            if not filtered_users:
                messagebox.showinfo("Búsqueda", f"No se encontraron usuarios que coincidan con '{search_term}'.")
                return

            for i, u in enumerate(filtered_users):
                try:
                    uid = u.get_id()
                    name = u.get_name()
                    tag = 'even' if i % 2 == 0 else 'odd'
                    self.tree.insert("", "end", values=(uid, name), tags=(tag,))
                except Exception as e:
                    logger.warning(f"Error insertando usuario en tabla (índice {i}): {e}")
                    continue

            try:
                self.tree.tag_configure('odd', background='#F7F1E6')
                self.tree.tag_configure('even', background=theme.BG_COLOR)
            except Exception as e:
                UIErrorHandler.log_and_pass(logger, "configurar tags de colores en tree", e)

        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al buscar usuarios",
                user_message="No se pudo realizar la búsqueda. Por favor, intente nuevamente."
            )

    def clear_search(self):
        """
        Clear the search field and reload all users.

        Removes the search term from the search entry field and reloads the complete
        user list, effectively resetting the view to show all users. Logs the clear
        operation.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all text from the search_entry field
            - Reloads and displays all users via load_users
            - Logs info message about clearing search
            - Shows error message box if clear operation fails
            - Logs errors via UIErrorHandler

        Raises:
            Exception: Catches and handles exceptions via UIErrorHandler
        """
        try:
            self.search_entry.delete(0, 'end')
            self.load_users()
            logger.info("Búsqueda limpiada, mostrando todos los usuarios")
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al limpiar búsqueda",
                user_message="No se pudo limpiar la búsqueda."
            )

    def _on_close(self):
        """
        Handle the window close event.

        Properly closes the user list window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        return button or the window's close button. All errors are logged.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Destroys the current window
            - If destroy fails, attempts to withdraw (hide) the window
            - Lifts and focuses the parent window if it exists
            - Restores the parent window to the foreground
            - Logs all errors via UIErrorHandler

        Raises:
            Exception: Catches and logs all exceptions during cleanup to ensure
                      the method completes without errors
        """
        try:
            self.destroy()
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "destroy ventana", e)
            try:
                self.withdraw()
            except Exception as withdraw_e:
                UIErrorHandler.log_and_pass(logger, "withdraw ventana", withdraw_e)

        try:
            if getattr(self, '_parent_window', None):
                try:
                    self._parent_window.lift()
                    self._parent_window.focus_force()
                except Exception as e:
                    UIErrorHandler.log_and_pass(logger, "retornar foco a ventana padre", e)
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "_on_close manejo de ventana padre", e)

    def open_selected_for_edit(self):
        """
        Open the edit dialog for the selected user record.

        Retrieves the user ID from the selected table row, fetches the full user object
        from the controller, and opens the UserForm dialog in edit mode. Binds a destroy
        event handler to refresh the user table when the edit dialog is closed. Also handles
        double-click events on table rows. Logs all operations and handles errors gracefully.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no user is selected
            - Shows error message if the selected row cannot be read
            - Shows error message if user is not found in the database
            - Retrieves user object from UserController
            - Opens UserForm window in edit mode as a top-level dialog
            - Binds destroy event to refresh the user table when edit window closes
            - Logs info message with user ID being edited
            - Automatically refreshes the user list after editing
            - Shows error message box if edit window cannot be opened
            - Logs all operations and errors via UIErrorHandler

        Raises:
            Exception: Catches and handles exceptions via UIErrorHandler with appropriate
                      user messages
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un usuario en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            user_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            user = self.controller.find_by_id(user_id)
            if user is None:
                UIErrorHandler.handle_error(
                    logger, ValueError(f"Usuario no encontrado: {user_id}"),
                    title="Usuario no encontrado",
                    user_message=f"El usuario {user_id} no fue encontrado en el sistema."
                )
                return

            parent = self._parent_window or self
            win = UserForm(parent, mode="edit", user=user)
            logger.info(f"Ventana de edición abierta para usuario: {user_id}")

            # refresh the list when the edit window is closed
            try:
                def _on_child_destroy(event=None):
                    # guard: the tree may have been destroyed if the parent is closing
                    try:
                        if getattr(self, 'tree', None) and self.tree.winfo_exists():
                            self.load_users()
                    except Exception as e:
                        UIErrorHandler.log_and_pass(logger, "reload después de editar", e)

                win.bind('<Destroy>', _on_child_destroy)
            except Exception as e:
                UIErrorHandler.log_and_pass(logger, "bind destroy para refresh", e)

        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al editar usuario",
                user_message=f"No se pudo abrir el formulario de edición.\nError: {str(e)}"
            )

    def delete_selected(self):
        """
        Delete the selected user record from the database.

        Validates that a user is selected, retrieves the user ID from the selected table row,
        prompts the user for confirmation, and deletes the user if confirmed. Warns the user
        that this action cannot be undone. Refreshes the table after successful deletion.
        Logs all operations including user cancellations.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Shows info message if no user is selected
            - Shows error message if the selected row cannot be read
            - Shows confirmation dialog warning about irreversible action
            - Logs info message if user cancels deletion
            - Deletes the user record from the database via controller
            - Logs info message with deleted user ID
            - Shows success message box if deletion succeeds
            - Shows error message box if deletion fails
            - Refreshes the user list after successful deletion
            - Logs all operations and errors via UIErrorHandler

        Raises:
            Exception: Catches and handles exceptions via UIErrorHandler with appropriate
                      user messages including the user ID and error details
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un usuario en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            user_id = values[0]
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error de selección",
                user_message="No se pudo leer la fila seleccionada. Intente nuevamente."
            )
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el usuario {user_id}? Esta acción no se puede deshacer?"):
            logger.info(f"Usuario canceló eliminación de {user_id}")
            return

        try:
            self.controller.delete_user(user_id)
            logger.info(f"Usuario eliminado: {user_id}")
            messagebox.showinfo("Borrado", "Usuario eliminado correctamente.")
            self.load_users()
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al eliminar usuario",
                user_message=f"No se pudo eliminar el usuario {user_id}.\nError: {str(e)}"
            )


__all__ = ["UserList"]
