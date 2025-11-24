import os
import json
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from ui.book_form import BookForm
from controllers.book_controller import BookController


class BookList(ctk.CTkToplevel):
    """Provisional book list viewer using data/books.json and a Treeview table."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_window = parent
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # Window basics
        self.title("Listado de Libros")
        self.geometry("900x500")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        # Main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Libros")
        title_lbl.pack(side="left")

        # Table frame uses a native tk.Frame to hold the ttk.Treeview
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("id", "ISBNCode", "title", "author", "weight", "price", "stock")

        # Style the Treeview to match app fonts and palette
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Use theme font for rows
        try:
            fam, fsize, fweight = theme.get_font(self, size=10)
        except Exception:
            fam, fsize, fweight = ("Segoe UI", 10, "normal")
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=24, fieldbackground=theme.BG_COLOR)

        # Heading font (same family, slightly larger/bold)
        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception:
            hfam, hfsize = (fam, fsize + 1)
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        # Selection color -> use accent red
        try:
            style.map("Treeview",
                      background=[('selected', theme.ACCENT_RED)],
                      foreground=[('selected', '#ffffff')])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")

        # Define headings
        headings = {
            "id": "ID",
            "ISBNCode": "ISBN",
            "title": "Título",
            "author": "Autor",
            "weight": "Peso",
            "price": "Precio",
            "stock": "Stock",
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            # set a reasonable width per column
            if c in ("id", "stock"):
                self.tree.column(c, width=70, anchor="center")
            elif c in ("price", "weight"):
                self.tree.column(c, width=90, anchor="center")
            else:
                self.tree.column(c, width=200, anchor="w")

        # Vertical scrollbar
        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # Action row
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_books)
        refresh_btn.pack(side="left", padx=(0, 8))
        # Edit and Delete buttons operate on the selected row
        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        # Load data initially
        self._books_path = os.path.join(os.path.dirname(__file__), "..", "data", "books.json")
        # normalize path
        self._books_path = os.path.abspath(self._books_path)
        self.load_books()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # bind double-click to open edit for selected row
        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

    def load_books(self):
        # Clear existing rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            with open(self._books_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"No se encontró {self._books_path}")
            return
        except json.JSONDecodeError:
            messagebox.showerror("Error", "books.json no es un JSON válido")
            return
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not isinstance(data, list):
            messagebox.showerror("Error", "Formato de books.json inesperado (se esperaba una lista)")
            return

        # insert rows with alternating tag for subtle row striping
        for i, item in enumerate(data):
            try:
                row = (
                    item.get("id", ""),
                    item.get("ISBNCode", ""),
                    item.get("title", ""),
                    item.get("author", ""),
                    item.get("weight", ""),
                    item.get("price", ""),
                    item.get("stock", ""),
                )
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
            except Exception:
                continue

        # configure row tag colors (subtle beige alternation)
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
            messagebox.showinfo("Info", "Selecciona primero un libro en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            book_id = values[0]
            # open BookForm in edit mode; parent should be main menu if available
            parent = self._parent_window or self
            win = BookForm(parent, mode="edit", book_id=book_id)
            try:
                # keep a reference to avoid GC
                if getattr(self, "_open_windows", None) is None:
                    self._open_windows = []
                self._open_windows.append(win)
                win.deiconify()
                win.lift()
                win.focus()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el editor: {e}")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un libro en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            book_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el libro {book_id}? Esta acción no se puede deshacer?"):
            return

        try:
            # use controller/service to delete
            controller = BookController()
            # BookService.delete_book enforces borrow/stock checks
            controller.service.delete_book(book_id)
            messagebox.showinfo("Borrado", "Libro eliminado correctamente.")
            self.load_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["BookList"]
