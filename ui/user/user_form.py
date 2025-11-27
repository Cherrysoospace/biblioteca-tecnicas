import os
import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None
from controllers.user_controller import UserController
from tkinter import messagebox
from ui import theme


class UserForm(ctk.CTkToplevel):
    def __init__(self, parent=None, mode="create", user=None):
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)

        # keep parent reference to restore focus on close
        self._parent_window = parent

        self.mode = mode       # "create" o "edit"
        self.user = user       # instancia User (solo si edit)
        self.controller = UserController()

        # Load twemoji assets (defensive)
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "twemoji")
        try:
            # load user.png as requested
            self.icon_user = ctk.CTkImage(Image.open(os.path.join(assets_path, "user.png")), size=(36, 36))
        except Exception:
            self.icon_user = None

        # Basic window properties
        self.title("User Form")
        self.geometry("400x300")

        # Do not change global CTk appearance/theme here; instead apply app theme to this toplevel
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # make this window transient to its parent (better WM behavior)
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        # ----------- WIDGETS ------------
        self.label_title = ctk.CTkLabel(self, text=("Create User" if mode=="create" else "Edit User"), font=("Arial", 18))
        self.label_title.pack(pady=15)

    # NOTE: ID is auto-generated and should not be entered by the user

        # Name
        self.label_name = ctk.CTkLabel(self, text="Name:")
        self.label_name.pack()
        self.entry_name = ctk.CTkEntry(self, width=250)
        self.entry_name.pack(pady=5)

        # Si estamos editando, precargar valores
        if self.mode == "edit" and self.user is not None:
            # ID is read-only / auto-generated; only preload the name
            try:
                self.entry_name.insert(0, self.user.get_name())
            except Exception:
                pass

        # Botón
        btn_text = "Create" if self.mode == "create" else "Update"
        self.btn_submit = ctk.CTkButton(self, text=btn_text, command=self.submit)
        self.btn_submit.pack(pady=20)

        # ensure closing returns focus to parent
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    # ----------- LÓGICA DEL FORM ------------
    def submit(self):
        name_value = self.entry_name.get().strip()


        if not name_value:
            messagebox.showerror("Error", "Name is required.")
            return

        try:
            if self.mode == "create":
                user = self.controller.create_user(name_value)
                # show the generated id to the user
                try:
                    uid = user.get_id()
                except Exception:
                    uid = None
                if uid:
                    messagebox.showinfo("Success", f"User {uid} created successfully.")
                else:
                    messagebox.showinfo("Success", "User created successfully.")
            else:
                # For updates, preserve ability to change id/name via service
                self.controller.update_user(
                    self.user.get_id(),
                    {"id": self.user.get_id(), "name": name_value}
                )
                messagebox.showinfo("Success", "User updated successfully.")

            self.destroy()
            # restore focus to parent after closing
            try:
                if getattr(self, '_parent_window', None):
                    try:
                        self._parent_window.lift()
                        self._parent_window.focus_force()
                    except Exception:
                        pass
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_close(self):
        """Handle close: destroy/withdraw and restore focus to parent."""
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
