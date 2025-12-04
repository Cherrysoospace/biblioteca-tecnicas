"""
User Form Window Module

This module provides a graphical user interface for creating and editing user records
in the library management system. It supports both creation and edit modes, allowing
users to manage user information including name. User IDs are automatically generated
in create mode to ensure uniqueness and consistency.
"""

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
    """
    A top-level window for creating or editing user records.

    This class provides a simple interface for user management with two modes: 'create'
    for adding new users and 'edit' for modifying existing ones. The form includes a
    name field and handles user ID generation automatically in create mode. The window
    loads optional Twemoji assets for visual enhancement and properly manages focus
    when closing.

    Attributes:
        _parent_window: Reference to the parent window that opened this dialog
        mode (str): Operation mode, either "create" or "edit"
        user: The user object being edited (only used in edit mode, None in create mode)
        controller (UserController): The user controller instance for database operations
        icon_user (CTkImage or None): Optional user icon image loaded from Twemoji assets
        label_title (CTkLabel): Title label displaying "Create User" or "Edit User"
        label_name (CTkLabel): Label for the name entry field
        entry_name (CTkEntry): Entry field for the user's name
        btn_submit (CTkButton): Submit button displaying "Create" or "Update"
    """

    def __init__(self, parent=None, mode="create", user=None):
        """
        Initialize the user form window.

        Sets up the window layout with a title, name entry field, and submit button.
        In create mode, the form is empty and ready for new user data with auto-generated ID.
        In edit mode, the form is pre-populated with the existing user's name. Attempts to
        load user icon from Twemoji assets directory.

        Parameters:
            parent: The parent window that opened this dialog. Can be None if opened
                   as a standalone window. Used for window management and focus control
            mode (str): Operation mode - "create" for new users or "edit" for existing users.
                       Defaults to "create"
            user: The user object to edit. Only used when mode is "edit". Should have
                 get_id() and get_name() methods. Ignored in create mode

        Returns:
            None

        Side Effects:
            - Creates and displays a new top-level window (400x300)
            - Initializes UserController for database operations
            - Attempts to load user.png icon from assets/twemoji directory
            - Applies application theme to the window
            - Makes the window transient to the parent if provided
            - Pre-populates name field if in edit mode with valid user object
            - Sets up window close handler to restore parent focus

        Raises:
            Exception: Catches and handles various exceptions during initialization
                      to ensure the window opens even if some operations fail (e.g., icon loading)
        """
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)

        # keep parent reference to restore focus on close
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass

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

    # ----------- FORM LOGIC ------------
    def submit(self):
        """
        Handle the form submission for creating or updating a user.

        Validates that the name field is not empty, then either creates a new user with
        auto-generated ID (create mode) or updates an existing user's name (edit mode).
        Displays the auto-generated user ID in create mode. Closes the window and restores
        focus to the parent after successful operation.

        Parameters:
            None

        Returns:
            None

        Side Effects:
            - Extracts and trims name from entry_name field
            - Shows error message if name is empty
            - In create mode:
              - Creates new user via controller with auto-generated ID
              - Shows success message with generated user ID if available
            - In edit mode:
              - Updates existing user's name via controller
              - Shows success message
            - Destroys the window after successful operation
            - Lifts and focuses the parent window
            - Shows error message box if operation fails

        Raises:
            Exception: Catches and displays exceptions via message box
        """
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
        """
        Handle the window close event.

        Properly closes the user form window and returns focus to the parent window.
        Attempts multiple cleanup methods to ensure the window is properly destroyed
        even if some operations fail. This method is called when the user clicks the
        window's close button.

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
