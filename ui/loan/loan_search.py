import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from controllers.loan_controller import LoanController


class LoanSearch(ctk.CTkToplevel):
    """Ventana de búsqueda de préstamos por ID, Usuario o ISBN."""
    
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

        self.title("Buscar Préstamos")
        self.geometry("750x520")
        
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Buscar Préstamos")
        title_lbl.pack(side="left")

        # Search controls frame
        search_frame = ctk.CTkFrame(container, fg_color=theme.BUTTON_COLOR, corner_radius=8)
        search_frame.pack(fill="x", pady=(0, 12), padx=8)
        
        # Search type selector
        type_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=8, padx=12)
        
        type_label = wf.create_body_label(type_frame, "Buscar por:")
        type_label.pack(side="left", padx=(0, 12))
        
        self.search_type = ctk.StringVar(value="id")
        
        id_radio = ctk.CTkRadioButton(
            type_frame,
            text="ID del Préstamo",
            variable=self.search_type,
            value="id",
            font=theme.get_font(type_frame, size=12),
            fg_color=theme.ACCENT_RED,
            hover_color=theme.BUTTON_HOVER
        )
        id_radio.pack(side="left", padx=(0, 12))
        
        user_radio = ctk.CTkRadioButton(
            type_frame,
            text="Usuario (ID)",
            variable=self.search_type,
            value="user",
            font=theme.get_font(type_frame, size=12),
            fg_color=theme.ACCENT_RED,
            hover_color=theme.BUTTON_HOVER
        )
        user_radio.pack(side="left", padx=(0, 12))
        
        isbn_radio = ctk.CTkRadioButton(
            type_frame,
            text="ISBN",
            variable=self.search_type,
            value="isbn",
            font=theme.get_font(type_frame, size=12),
            fg_color=theme.ACCENT_RED,
            hover_color=theme.BUTTON_HOVER
        )
        isbn_radio.pack(side="left", padx=(0, 12))
        
        active_radio = ctk.CTkRadioButton(
            type_frame,
            text="Solo Activos",
            variable=self.search_type,
            value="active",
            font=theme.get_font(type_frame, size=12),
            fg_color=theme.ACCENT_RED,
            hover_color=theme.BUTTON_HOVER
        )
        active_radio.pack(side="left")
        
        # Search input frame
        input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        input_frame.pack(fill="x", pady=(0, 8), padx=12)
        
        input_label = wf.create_body_label(input_frame, "Valor:")
        input_label.pack(side="left", padx=(0, 12))
        
        self.search_entry = wf.create_entry(input_frame, placeholder="Ingrese ID, Usuario o ISBN")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        search_btn = wf.create_small_button(input_frame, text="Buscar", command=self.perform_search)
        search_btn.pack(side="left", padx=(0, 8))
        
        clear_btn = wf.create_small_button(input_frame, text="Limpiar", command=self.clear_search)
        clear_btn.pack(side="left")

        # Results table
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("loan_id", "user_id", "isbn", "loan_date", "returned")

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
        headings = {"loan_id": "ID", "user_id": "Usuario", "isbn": "ISBN", "loan_date": "Fecha", "returned": "Devuelto"}
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "loan_id":
                self.tree.column(c, width=130, anchor="center")
            elif c == "returned":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=160, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # Results label
        self.results_label = wf.create_body_label(container, "")
        self.results_label.pack(pady=(4, 8))

        # Action buttons
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        close_btn = wf.create_small_button(action_frame, text="Cerrar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = LoanController()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass
        
        # Bind Enter key to search
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

    def perform_search(self):
        """Execute search based on selected type."""
        search_type = self.search_type.get()
        search_value = self.search_entry.get().strip()
        
        # Clear previous results
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        try:
            loans = []
            
            if search_type == "active":
                # Search for active loans (no value needed)
                loans = self.controller.find_active_loans()
                search_desc = "Préstamos activos (no devueltos)"
            elif not search_value:
                messagebox.showwarning("Advertencia", "Por favor ingrese un valor de búsqueda")
                return
            elif search_type == "id":
                # Search by loan ID
                loan = self.controller.find_by_id(search_value)
                if loan:
                    loans = [loan]
                search_desc = f"ID: {search_value}"
            elif search_type == "user":
                # Search by user ID
                loans = self.controller.find_by_user(search_value)
                search_desc = f"Usuario: {search_value}"
            elif search_type == "isbn":
                # Search by ISBN
                loans = self.controller.find_by_isbn(search_value)
                search_desc = f"ISBN: {search_value}"
            
            # Display results
            if not loans:
                self.results_label.configure(text=f"No se encontraron préstamos para: {search_desc}")
                messagebox.showinfo("Sin resultados", f"No se encontraron préstamos para: {search_desc}")
                return
            
            for i, l in enumerate(loans):
                try:
                    lid = l.get_loan_id()
                    uid = l.get_user_id()
                    isbn = l.get_isbn()
                    ldate = l.get_loan_date()
                    try:
                        ldate = ldate.isoformat()
                    except Exception:
                        pass
                    returned = "Sí" if l.is_returned() else "No"
                    tag = 'even' if i % 2 == 0 else 'odd'
                    self.tree.insert("", "end", values=(lid, uid, isbn, ldate, returned), tags=(tag,))
                except Exception:
                    continue
            
            try:
                self.tree.tag_configure('odd', background='#F7F1E6')
                self.tree.tag_configure('even', background=theme.BG_COLOR)
            except Exception:
                pass
            
            self.results_label.configure(
                text=f"Se encontraron {len(loans)} préstamo(s) para: {search_desc}"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar: {str(e)}")
            self.results_label.configure(text="Error en la búsqueda")

    def clear_search(self):
        """Clear search input and results."""
        self.search_entry.delete(0, 'end')
        for r in self.tree.get_children():
            self.tree.delete(r)
        self.results_label.configure(text="")

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


__all__ = ["LoanSearch"]
