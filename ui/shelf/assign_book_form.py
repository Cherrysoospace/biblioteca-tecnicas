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
    """Form to assign one or more books to a selected shelf.

    UI pattern follows existing list forms: left treeview with books, top
    combobox to select shelf, and action buttons to assign selected books.
    """

    def __init__(self, parent=None):
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
            messagebox.showerror("Error", f"No se pudieron cargar estanterías: {e}")

    def load_books(self):
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
        v = self.shelf_var.get() or ''
        # value is either 'ID - name' or 'ID'; take first token split
        return v.split(' - ')[0].strip()

    def assign_selected(self):
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
