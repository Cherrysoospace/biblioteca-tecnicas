import customtkinter as ctk
from controllers.user_controller import UserController
from tkinter import messagebox


class UserForm(ctk.CTkToplevel):
    def __init__(self, parent=None, mode="create", user=None):
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)

        self.mode = mode       # "create" o "edit"
        self.user = user       # instancia User (solo si edit)
        self.controller = UserController()

        self.title("User Form")
        self.geometry("400x300")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ----------- WIDGETS ------------
        self.label_title = ctk.CTkLabel(self, text=("Create User" if mode=="create" else "Edit User"), font=("Arial", 18))
        self.label_title.pack(pady=15)

        # ID
        self.label_id = ctk.CTkLabel(self, text="ID:")
        self.label_id.pack()
        self.entry_id = ctk.CTkEntry(self, width=250)
        self.entry_id.pack(pady=5)

        # Name
        self.label_name = ctk.CTkLabel(self, text="Name:")
        self.label_name.pack()
        self.entry_name = ctk.CTkEntry(self, width=250)
        self.entry_name.pack(pady=5)

        # Si estamos editando, precargar valores
        if self.mode == "edit" and self.user is not None:
            self.entry_id.insert(0, self.user.get_id())
            self.entry_name.insert(0, self.user.get_name())

        # Botón
        btn_text = "Create" if self.mode == "create" else "Update"
        self.btn_submit = ctk.CTkButton(self, text=btn_text, command=self.submit)
        self.btn_submit.pack(pady=20)

    # ----------- LÓGICA DEL FORM ------------
    def submit(self):
        id_value = self.entry_id.get().strip()
        name_value = self.entry_name.get().strip()

        if not id_value or not name_value:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            if self.mode == "create":
                self.controller.create_user(id_value, name_value)
                messagebox.showinfo("Success", "User created successfully.")
            else:
                self.controller.update_user(
                    self.user.get_id(),
                    {"id": id_value, "name": name_value}
                )
                messagebox.showinfo("Success", "User updated successfully.")

            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))
