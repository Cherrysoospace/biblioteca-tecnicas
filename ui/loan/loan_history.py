"""loan_history.py

UI para visualizar el historial de préstamos de un usuario (Stack LIFO).
Muestra los préstamos en orden LIFO (más reciente primero).

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-03
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from typing import Optional
from ui import theme
from ui import widget_factory as wf
from controllers.loan_controller import LoanController
from services.user_service import UserService


class LoanHistory(ctk.CTkToplevel):
    """Ventana para visualizar el historial de préstamos de un usuario (Stack LIFO)."""
    
    def __init__(self, parent=None, user_id: Optional[str] = None):
        """Inicializar ventana de historial de préstamos.
        
        Args:
            parent: Ventana padre
            user_id: ID del usuario (si es None, muestra selector)
        """
        super().__init__(parent)
        self._parent_window = parent
        self.user_id = user_id
        self.controller = LoanController()
        self.user_service = UserService()
        
        # Apply theme
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass
        
        self.title("Historial de Préstamos (Stack LIFO)")
        self.geometry("800x500")
        
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass
        
        self._build_ui()
        
        # If user_id provided, load history immediately
        if self.user_id:
            self._load_history()
        
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass
    
    def _build_ui(self):
        """Construir interfaz de usuario."""
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)
        
        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "📚 Historial de Préstamos (LIFO)")
        title_lbl.pack(side="left")
        
        # User selection frame (if user_id not provided)
        if not self.user_id:
            self._build_user_selector(container)
        else:
            # Show selected user info
            info_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
            info_frame.pack(pady=(0, 8), fill="x")
            try:
                user = self.user_service.find_by_id(self.user_id)
                user_name = user.get_name() if user else self.user_id
                info_lbl = ctk.CTkLabel(
                    info_frame, 
                    text=f"Usuario: {user_name} ({self.user_id})",
                    font=("Segoe UI", 12, "bold"),
                    text_color=theme.ACCENT_RED
                )
                info_lbl.pack(anchor="w", padx=4)
            except Exception:
                pass
        
        # Table frame
        self._build_table(container)
        
        # Action buttons
        self._build_action_buttons(container)
    
    def _build_user_selector(self, container):
        """Construir selector de usuario."""
        selector_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=8)
        selector_frame.pack(pady=(0, 8), fill="x", padx=4)
        
        lbl = ctk.CTkLabel(selector_frame, text="Seleccionar Usuario:", font=("Segoe UI", 11))
        lbl.pack(side="left", padx=(4, 8))
        
        # Get all users
        self._user_map = {}
        users = []
        try:
            all_users = self.user_service.get_all_users()
            for u in all_users:
                disp = f"{u.get_name()} ({u.get_id()})"
                users.append(disp)
                self._user_map[disp] = u.get_id()
        except Exception:
            users = []
        
        if users:
            self.user_selector = ctk.CTkOptionMenu(
                selector_frame, 
                values=users,
                command=self._on_user_selected
            )
            self.user_selector.pack(side="left", padx=4, fill="x", expand=True)
            try:
                self.user_selector.set(users[0])
            except Exception:
                pass
        else:
            no_users_lbl = ctk.CTkLabel(selector_frame, text="No hay usuarios disponibles")
            no_users_lbl.pack(side="left", padx=4)
        
        # Load button
        load_btn = wf.create_small_button(selector_frame, text="Ver Historial", command=self._load_history)
        load_btn.pack(side="left", padx=4)
    
    def _build_table(self, container):
        """Construir tabla de historial."""
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))
        
        cols = ("position", "loan_id", "isbn", "loan_date", "returned")
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        
        # Configure fonts
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
        headings = {
            "position": "Posición (LIFO)", 
            "loan_id": "ID Préstamo", 
            "isbn": "ISBN", 
            "loan_date": "Fecha",
            "returned": "Devuelto"
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "position":
                self.tree.column(c, width=120, anchor="center")
            elif c == "loan_id":
                self.tree.column(c, width=130, anchor="center")
            elif c == "loan_date":
                self.tree.column(c, width=130, anchor="center")
            elif c == "returned":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=150, anchor="w")
        
        # Scrollbar
        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")
        
        # Configure alternating row colors
        try:
            self.tree.tag_configure('even', background='#f0f0f0')
            self.tree.tag_configure('odd', background='#ffffff')
            self.tree.tag_configure('top', background='#ffe6e6', font=(fam, fsize, 'bold'))  # Highlight top of stack
        except Exception:
            pass
    
    def _build_action_buttons(self, container):
        """Construir botones de acción."""
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))
        
        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self._load_history)
        refresh_btn.pack(side="left", padx=(0, 8))
        
        close_btn = wf.create_small_button(action_frame, text="Cerrar", command=self._on_close)
        close_btn.pack(side="left")
        
        # Info label
        self.info_lbl = ctk.CTkLabel(
            action_frame, 
            text="",
            font=("Segoe UI", 10),
            text_color=theme.TEXT_COLOR
        )
        self.info_lbl.pack(side="right", padx=4)
    
    def _on_user_selected(self, selection):
        """Callback cuando se selecciona un usuario."""
        # Optionally auto-load history when user changes
        pass
    
    def _load_history(self):
        """Cargar historial de préstamos del usuario."""
        # Get user_id
        if self.user_id:
            user_id = self.user_id
        else:
            # Get from selector
            try:
                sel = self.user_selector.get().strip()
                user_id = self._user_map.get(sel)
            except Exception:
                messagebox.showerror("Error", "Selecciona un usuario")
                return
        
        if not user_id:
            messagebox.showerror("Error", "Usuario no válido")
            return
        
        # Clear table
        for r in self.tree.get_children():
            self.tree.delete(r)
        
        # Load history from controller
        try:
            result = self.controller.get_user_loan_history(user_id)
            if not result.get('success'):
                messagebox.showerror("Error", result.get('message', 'Error cargando historial'))
                return
            
            history = result.get('history', [])
            
            if not history:
                self.info_lbl.configure(text="Sin historial de préstamos")
                return
            
            # Populate table (history is already in LIFO order - most recent first)
            for i, entry in enumerate(history):
                position = i + 1
                loan_id = entry.get('loan_id', '-')
                isbn = entry.get('isbn', '-')
                loan_date = entry.get('loan_date', '-')
                returned = "Sí" if entry.get('returned', False) else "No"
                
                # Top of stack (most recent) gets special tag
                if i == 0:
                    tag = 'top'
                else:
                    tag = 'even' if i % 2 == 0 else 'odd'
                
                position_text = f"#{position} (Tope)" if i == 0 else f"#{position}"
                
                self.tree.insert("", "end", values=(position_text, loan_id, isbn, loan_date, returned), tags=(tag,))
            
            # Update info label
            total = len(history)
            self.info_lbl.configure(text=f"Total: {total} préstamo{'s' if total != 1 else ''} | Ordenado LIFO (más reciente primero)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando historial: {e}")
    
    def _on_close(self):
        """Cerrar ventana."""
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


__all__ = ["LoanHistory"]
