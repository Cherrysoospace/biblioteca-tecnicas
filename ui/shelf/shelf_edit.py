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
    """Edición de una estantería: nombre y libros asociados."""

    def __init__(self, parent=None, shelf_id: str = None):
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
