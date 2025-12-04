import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.book_controller import BookController


class BookClone(ctk.CTkToplevel):
    """Dialog to clone an existing book (same data, different id).

    UI shows a dropdown of existing books and a button to create a cloned copy.
    """

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

        self.title("Agregar libro existente")
        self.geometry("480x160")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        self.book_controller = BookController()

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=8)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title = wf.create_title_label(container, "Agregar libro existente")
        title.pack(pady=(0, 8))

        # Dropdown row
        row = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        row.pack(fill="x", padx=6, pady=6)

        lbl = wf.create_body_label(row, "Seleccione libro a clonar:")
        lbl.pack(side="left", padx=(0, 8))

        # Combobox with "id - title" values
        self.combo_var = tk.StringVar()
        self.combo = ttk.Combobox(row, textvariable=self.combo_var, state="readonly")
        self.combo.pack(side="left", fill="x", expand=True)

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        btn_frame.pack(fill="x", pady=(12, 0))

        clone_btn = wf.create_primary_button(btn_frame, "Clonar libro", command=self._on_clone)
        clone_btn.pack(side="left", padx=(0, 8))

        cancel_btn = wf.create_small_button(btn_frame, "Cancelar", command=self._on_cancel)
        cancel_btn.pack(side="left")

        self._load_books_into_combo()

    def _load_books_into_combo(self):
        try:
            books = self.book_controller.get_all_books()
            items = [f"{b.get_id()} - {b.get_title()}" for b in books]
            self.combo['values'] = items
            if items:
                self.combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los libros: {e}")

    def _selected_id_from_combo(self) -> str:
        v = self.combo_var.get()
        if not v:
            return ""
        return v.split(" - ")[0].strip()

    def _on_clone(self):
        sel = self._selected_id_from_combo()
        if not sel:
            messagebox.showinfo("Información", "Por favor seleccione un libro para clonar.")
            return
        try:
            new_id = self.book_controller.clone_book(sel)
            messagebox.showinfo("Éxito", f"Libro clonado correctamente con id: {new_id}")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error al clonar", str(e))

    def _on_cancel(self):
        self.destroy()
