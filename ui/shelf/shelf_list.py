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
    """Listado de estanterías con opciones para editar y eliminar."""
    def __init__(self, parent=None):
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
        container.grid_rowconfigure(0, weight=0)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=0)
        container.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(6, 8))
        title_lbl = wf.create_title_label(title_frame, "Listado de Estanterías")
        title_lbl.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.grid(row=1, column=0, sticky="nsew", padx=0, pady=(8, 8))

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
        action_frame.grid(row=2, column=0, sticky="ew", pady=(8, 4))

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

    def load_shelves(self):
        """Carga y muestra las estanterías en la tabla."""
        # Limpiar filas existentes
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
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
        """Elimina la estantería seleccionada."""
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


__all__ = ["ShelfList"]
