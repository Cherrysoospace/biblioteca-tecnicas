import customtkinter as ctk
from tkinter import messagebox
from controllers.loan_controller import LoanController
from ui import theme
from ui import widget_factory as wf


class LoanForm(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        # attach to parent and set basic geometry
        self._parent_window = parent
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

        # Loan ID
        self.entry_loan_id = ctk.CTkEntry(form_frame, placeholder_text="Loan ID")
        self.entry_loan_id.pack(pady=6, fill="x")

        # User ID
        self.entry_user_id = ctk.CTkEntry(form_frame, placeholder_text="User ID")
        self.entry_user_id.pack(pady=6, fill="x")

        # ISBN
        self.entry_isbn = ctk.CTkEntry(form_frame, placeholder_text="ISBN")
        self.entry_isbn.pack(pady=6, fill="x")

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
        loan_id = self.entry_loan_id.get().strip()
        user_id = self.entry_user_id.get().strip()
        isbn = self.entry_isbn.get().strip()

        if not loan_id or not user_id or not isbn:
            messagebox.showerror("Error", "All fields are required")
            return

        res = self.controller.create_loan(loan_id, user_id, isbn)
        if res.get('success'):
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
