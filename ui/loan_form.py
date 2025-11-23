import customtkinter as ctk
from tkinter import messagebox
from controllers.loan_controller import LoanController


class LoanForm(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.title("Create Loan")
        self.geometry("400x300")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.controller = LoanController()

        # Widgets
        self.label_title = ctk.CTkLabel(self, text="Create Loan", font=("Arial", 18))
        self.label_title.pack(pady=10)

        # Loan ID
        self.entry_loan_id = ctk.CTkEntry(self, placeholder_text="Loan ID")
        self.entry_loan_id.pack(pady=5)

        # User ID
        self.entry_user_id = ctk.CTkEntry(self, placeholder_text="User ID")
        self.entry_user_id.pack(pady=5)

        # ISBN
        self.entry_isbn = ctk.CTkEntry(self, placeholder_text="ISBN")
        self.entry_isbn.pack(pady=5)

        # Button
        self.btn_create = ctk.CTkButton(self, text="Create Loan", command=self.create_loan)
        self.btn_create.pack(pady=15)

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
            self.destroy()
        else:
            messagebox.showerror("Error", res.get('message'))
