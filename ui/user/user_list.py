import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from ui.user.user_form import UserForm
from controllers.user_controller import UserController
from utils.logger import LibraryLogger, UIErrorHandler

# Configurar logger para este módulo
logger = LibraryLogger.get_logger(__name__)


class UserList(ctk.CTkToplevel):
    """Listado de usuarios con opciones para editar y eliminar."""
    def __init__(self, parent=None):
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
        """Buscar usuarios por ID o nombre."""
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
        """Limpiar el campo de búsqueda y recargar todos los usuarios."""
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
