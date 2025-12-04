"""
book_search.py

Interfaz de búsqueda de libros usando búsqueda lineal recursiva.
Permite buscar por título o autor en el inventario general.

Fecha: 2025-12-03
"""

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.book_controller import BookController


class BookSearch(ctk.CTkToplevel):
    """Ventana de búsqueda de libros usando búsqueda lineal."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling
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

        # Window configuration
        self.title("🔍 Búsqueda de Libros")
        self.geometry("1000x600")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        # Book controller (follows MVC pattern)
        self.controller = BookController()
        self.current_results = []

        # Main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 12), fill="x")
        
        title_lbl = wf.create_title_label(title_frame, "🔍 Búsqueda de Libros")
        title_lbl.pack(side="left")

        # Search controls frame
        search_frame = ctk.CTkFrame(container, fg_color=theme.BUTTON_COLOR, corner_radius=8)
        search_frame.pack(fill="x", pady=(0, 12), padx=8)

        # Search type selector
        type_frame = ctk.CTkFrame(search_frame, fg_color=theme.BUTTON_COLOR)
        type_frame.pack(fill="x", padx=12, pady=(12, 8))
        
        lbl_type = ctk.CTkLabel(type_frame, text="Buscar por:", text_color=theme.TEXT_COLOR)
        lbl_type.pack(side="left", padx=(0, 12))

        self.search_type = ctk.StringVar(value="title")
        
        radio_title = ctk.CTkRadioButton(
            type_frame,
            text="Título",
            variable=self.search_type,
            value="title",
            fg_color=theme.BUTTON_HOVER,
            hover_color=theme.BORDER_COLOR
        )
        radio_title.pack(side="left", padx=8)
        
        radio_author = ctk.CTkRadioButton(
            type_frame,
            text="Autor",
            variable=self.search_type,
            value="author",
            fg_color=theme.BUTTON_HOVER,
            hover_color=theme.BORDER_COLOR
        )
        radio_author.pack(side="left", padx=8)

        # Search input frame
        input_frame = ctk.CTkFrame(search_frame, fg_color=theme.BUTTON_COLOR)
        input_frame.pack(fill="x", padx=12, pady=(8, 12))

        lbl_search = ctk.CTkLabel(input_frame, text="Buscar:", text_color=theme.TEXT_COLOR)
        lbl_search.pack(side="left", padx=(0, 12))

        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Introduce título o autor (búsqueda parcial)...",
            width=400,
            height=36
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        btn_search = wf.create_primary_button(
            input_frame,
            "🔍 Buscar",
            command=self.perform_search,
            width=120,
            height=36
        )
        btn_search.pack(side="left", padx=(0, 8))

        btn_clear = wf.create_small_button(
            input_frame,
            "Limpiar",
            command=self.clear_search,
            width=100,
            height=36
        )
        btn_clear.pack(side="left")

        # Info label
        info_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        info_frame.pack(fill="x", pady=(0, 8))
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales.",
            text_color=theme.TEXT_COLOR
        )
        self.info_label.pack(side="left")

        # Results count label
        self.results_label = ctk.CTkLabel(info_frame, text="", text_color=theme.TEXT_COLOR)
        self.results_label.pack(side="right")

        # Table frame for results
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("isbn", "title", "author", "price", "stock")
        col_widths = [150, 300, 200, 100, 80]

        # Style the Treeview
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
        style.configure("Treeview", font=row_font, rowheight=28, fieldbackground=theme.BG_COLOR)

        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception:
            hfam, hfsize = (fam, fsize + 1)
        
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        try:
            style.map("Treeview", background=[('selected', theme.BUTTON_HOVER)])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("title", text="Título")
        self.tree.heading("author", text="Autor")
        self.tree.heading("price", text="Precio (COP)")
        self.tree.heading("stock", text="Stock")

        for col, w in zip(cols, col_widths):
            self.tree.column(col, width=w, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_holder, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_holder.rowconfigure(0, weight=1)
        table_holder.columnconfigure(0, weight=1)

        # Bottom buttons
        bottom_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        bottom_frame.pack(fill="x", pady=(8, 0))

        btn_close = wf.create_small_button(bottom_frame, "Cerrar", command=self.destroy)
        btn_close.pack(side="right")

    def perform_search(self):
        """Ejecuta la búsqueda usando búsqueda lineal."""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning(
                "Campo vacío",
                "Por favor introduce un término de búsqueda.",
                parent=self
            )
            return

        search_type = self.search_type.get()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Perform search using linear search algorithm through controller
        try:
            if search_type == "title":
                results = self.controller.search_books_by_title(query)
            else:  # author
                results = self.controller.search_books_by_author(query)
            
            self.current_results = results
            
            # Update results label
            self.results_label.configure(
                text=f"📊 {len(results)} resultado(s) encontrado(s)"
            )
            
            if not results:
                self.info_label.configure(
                    text=f"❌ No se encontraron libros con '{query}' en {search_type}"
                )
                return
            
            # Populate table
            for inv in results:
                book = inv.get_book()
                if book:
                    self.tree.insert("", "end", values=(
                        book.get_ISBNCode(),
                        book.get_title(),
                        book.get_author(),
                        f"${book.get_price():,}",
                        inv.get_stock()
                    ))
            
            self.info_label.configure(
                text=f"✅ Búsqueda completada usando algoritmo de búsqueda lineal recursiva"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al realizar la búsqueda: {str(e)}",
                parent=self
            )
            self.info_label.configure(
                text=f"❌ Error en la búsqueda: {str(e)}"
            )

    def clear_search(self):
        """Limpia la búsqueda y los resultados."""
        self.search_entry.delete(0, 'end')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_results = []
        self.results_label.configure(text="")
        self.info_label.configure(
            text="💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales."
        )


__all__ = ['BookSearch']
