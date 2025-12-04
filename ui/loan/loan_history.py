"""
Loan History Window Module

This module provides a graphical user interface for viewing a user's loan history
using a Stack (LIFO) data structure. Loans are displayed in LIFO order with the
most recent loan appearing first (top of stack). The interface allows filtering
by user and displays comprehensive loan information including loan ID, ISBN,
date, and return status.

Author: Library Management System
Date: 2025-12-03
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
    """
    A top-level window for viewing a user's loan history using Stack (LIFO) structure.

    This class provides a graphical interface that displays loan records in LIFO order,
    with the most recent loan at the top of the stack. Users can select a specific user
    to view their complete loan history or view history for a pre-selected user. The
    interface highlights the top of the stack and provides visual organization of the data.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        user_id (str or None): ID of the user whose history is being displayed
        controller (LoanController): The loan controller instance for database operations
        user_service (UserService): Service for user-related operations
        _user_map (dict): Maps user display strings to user IDs (only if no user_id provided)
        user_selector (CTkOptionMenu or None): Widget for selecting users (only if no user_id provided)
        tree (ttk.Treeview): The table widget displaying the loan history
        info_lbl (CTkLabel): Label showing summary information about the history
    """
    
    def __init__(self, parent=None, user_id: Optional[str] = None):
        """
        Initialize the loan history window.

        Sets up the window layout, loads user data, and displays the loan history interface.
        If a user_id is provided, the history is loaded immediately for that user. If not,
        a user selector dropdown is displayed.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control
            user_id (Optional[str]): The ID of the user whose loan history should be displayed.
                                    If None, a user selector will be shown to choose a user

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window
            - Loads user data from UserService if user_id is not provided
            - Automatically loads loan history if user_id is provided
            - Applies application theme to the window
            - Makes the window transient to the parent if provided

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail
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
        """
        Build the complete user interface for the loan history window.

        Creates the main container, title, user selector (if needed), table for displaying
        loan history, and action buttons. Conditionally displays either a user selector
        dropdown or user information label based on whether user_id was provided.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Creates and packs all UI widgets into the window
            - Calls helper methods to build specific UI sections
            - Displays user information if user_id is provided
            - Shows user selector if user_id is not provided
        """
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
        """
        Build the user selection interface.

        Creates a dropdown menu populated with all users in the system, allowing
        the user to select which user's loan history to view. Also includes a button
        to load the selected user's history.

        Parameters:
            container: The parent container widget where the selector will be placed

        Returns:
            None

        Side Effects:
            - Creates and populates the user_selector OptionMenu widget
            - Loads all users from UserService and populates _user_map dictionary
            - Displays "No users available" message if no users exist
            - Adds a "View History" button to trigger history loading

        Raises:
            Exception: Catches and handles exceptions during user loading
        """
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
        """
        Build the table widget for displaying loan history.

        Creates a Treeview table with columns for position (LIFO order), loan ID, ISBN,
        loan date, and return status. Configures styling including fonts, colors, and
        alternating row backgrounds. The top of the stack (most recent loan) receives
        special highlighting.

        Parameters:
            container: The parent container widget where the table will be placed

        Returns:
            None

        Side Effects:
            - Creates and configures the tree (Treeview) widget
            - Applies custom styling to table headers and rows
            - Adds vertical scrollbar to the table
            - Configures column widths and alignments
            - Defines tags for alternating row colors and top-of-stack highlighting

        Raises:
            Exception: Catches and handles exceptions during table configuration
        """
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
        """
        Build the action buttons section at the bottom of the window.

        Creates refresh and close buttons, as well as an information label that displays
        summary statistics about the loan history (total count and ordering information).

        Parameters:
            container: The parent container widget where the buttons will be placed

        Returns:
            None

        Side Effects:
            - Creates "Refresh" button to reload the history
            - Creates "Close" button to close the window
            - Creates info_lbl label for displaying statistics
            - Packs all widgets into the action frame
        """
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
        """
        Callback handler when a user is selected from the dropdown.

        This method is called automatically when the user changes the selection in the
        user selector OptionMenu. Currently serves as a placeholder for potential
        auto-loading functionality.

        Parameters:
            selection: The selected value from the OptionMenu (user display string)

        Returns:
            None

        Side Effects:
            None (method is currently a placeholder)

        Note:
            Could be enhanced to automatically load history when user selection changes
        """
        # Optionally auto-load history when user changes
        pass
    
    def _load_history(self):
        """
        Load and display the loan history for the selected or specified user.

        Retrieves loan history from the controller in LIFO order (most recent first),
        clears the current table, and populates it with the history data. The top of
        the stack (most recent loan) is highlighted with special formatting. Updates
        the information label with total count and ordering details.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Clears all rows from the table
            - Loads history data from LoanController
            - Populates table with loan records in LIFO order
            - Highlights the top of stack (position #1) with special background color
            - Updates info_lbl with summary statistics
            - Shows error message box if loading fails or user is invalid
            - Shows "No loan history" message if history is empty

        Raises:
            Exception: Catches and displays exceptions via message box
        """
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
        """
        Handle the window close event.

        Properly closes the loan history window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        close button or the window's close button.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Destroys the current window
            - If destroy fails, attempts to withdraw (hide) the window
            - Lifts and focuses the parent window if it exists
            - Restores the parent window to the foreground

        Raises:
            Exception: Catches and ignores all exceptions during cleanup to ensure
                      the method completes without errors
        """
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
