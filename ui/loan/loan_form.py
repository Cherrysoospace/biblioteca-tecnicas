import customtkinter as ctk
from tkinter import messagebox
from controllers.loan_controller import LoanController
from services.user_service import UserService
from services.inventory_service import InventoryService
from ui import theme
from ui import widget_factory as wf


class LoanForm(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # attach to parent and set basic geometry
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass
        
        self.title("Create Loan")
        self.geometry("400x300")
        try:
            # make the toplevel transient so window managers treat it as related
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass
        # apply theme for consistent colors/layout
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.controller = LoanController()

        # Main container to match MainMenu layout
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=16, pady=16)

        # Title area (consistent with widget factory)
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(8, 12))
        title_lbl = wf.create_title_label(title_frame, "Crear Préstamo")
        title_lbl.pack(side="left")

        # Form area
        form_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        form_frame.pack(expand=True, fill="both")

    # NOTE: loan id is now generated automatically; user should not enter it

        # --- User selector (display: "Name (ID)")
        self._user_map = {}  # display -> user_id
        users = []
        try:
            usvc = UserService()
            for u in usvc.get_all_users():
                disp = f"{u.get_name()} ({u.get_id()})"
                users.append(disp)
                self._user_map[disp] = u.get_id()
        except Exception:
            users = []

        if users:
            self.user_selector = ctk.CTkOptionMenu(form_frame, values=users)
            # select first by default
            try:
                self.user_selector.set(users[0])
            except Exception:
                pass
        else:
            self.user_selector = ctk.CTkLabel(form_frame, text="No hay usuarios disponibles")
        self.user_selector.pack(pady=6, fill="x")

        # --- Book selector (only available copies with stock>0)
        self._book_map = {}  # display -> isbn
        books = []
        try:
            inv_svc = InventoryService()
            for inv in inv_svc.inventory_general:
                try:
                    if inv.get_stock() > 0 and not inv.get_isBorrowed():
                        b = inv.get_book()
                        # show title (ISBN) [book_id]
                        disp = f"{b.get_title()} ({b.get_ISBNCode()}) [{b.get_id()}]"
                        # Keep only one entry per ISBN display (avoid duplicates)
                        if disp not in self._book_map:
                            books.append(disp)
                            self._book_map[disp] = b.get_ISBNCode()
                except Exception:
                    continue
        except Exception:
            books = []

        if books:
            self.book_selector = ctk.CTkOptionMenu(form_frame, values=books)
            try:
                self.book_selector.set(books[0])
            except Exception:
                pass
        else:
            self.book_selector = ctk.CTkLabel(form_frame, text="No hay libros disponibles")
        self.book_selector.pack(pady=6, fill="x")

        # Action area with primary and cancel buttons
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(12, 6))

        self.btn_create = wf.create_primary_button(action_frame, text="Crear Préstamo", command=self.create_loan)
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)

        self.btn_create.pack(side="left", padx=(0, 8), pady=6)
        cancel_btn.pack(side="left", pady=6)

        # ensure closing returns focus to parent
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def create_loan(self):
        # Map selected display values to actual ids
        try:
            # user_selector may be a label if no users
            if isinstance(self.user_selector, ctk.CTkLabel):
                messagebox.showerror("Error", "No hay usuarios disponibles")
                return
            sel_user = self.user_selector.get().strip()
            user_id = self._user_map.get(sel_user)
        except Exception:
            user_id = None

        try:
            if isinstance(self.book_selector, ctk.CTkLabel):
                messagebox.showerror("Error", "No hay libros disponibles")
                return
            sel_book = self.book_selector.get().strip()
            isbn = self._book_map.get(sel_book)
        except Exception:
            isbn = None

        if not user_id or not isbn:
            messagebox.showerror("Error", "Debe seleccionar usuario y libro disponibles")
            return

        # controller.create_loan expects (user_id, isbn)
        res = self.controller.create_loan(user_id, isbn)
        if res.get('success'):
            # show created loan id when available
            loan = res.get('loan')
            try:
                loan_id = loan.get_loan_id() if loan else None
            except Exception:
                loan_id = None
            if loan_id:
                messagebox.showinfo("Success", f"Loan {loan_id} created successfully")
            else:
                messagebox.showinfo("Success", "Loan created successfully")
            # optionally close window after creating
            self._on_close()
        else:
            messagebox.showerror("Error", res.get('message'))

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
