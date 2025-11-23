import customtkinter as ctk
from ui.book_form import BookForm
from ui.user_form import UserForm

class MainMenu(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Library Management System")
        self.geometry("500x400")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        title = ctk.CTkLabel(self, text="Library Management System",
                             font=("Arial", 22))
        title.pack(pady=20)

        # ---------- BOOK SECTION ----------
        book_label = ctk.CTkLabel(self, text="Books", font=("Arial", 18))
        book_label.pack(pady=10)

        btn_create_book = ctk.CTkButton(self, text="Create Book",
                                        command=self.open_create_book)
        btn_create_book.pack(pady=5)

        # ---------- USER SECTION ----------
        user_label = ctk.CTkLabel(self, text="Users", font=("Arial", 18))
        user_label.pack(pady=20)

        btn_create_user = ctk.CTkButton(self, text="Create User",
                                        command=self.open_create_user)
        btn_create_user.pack(pady=5)

    # ------------------- OPEN WINDOWS -------------------
    def open_create_book(self):
        # Create a non-modal CTkToplevel; keep a reference so Python doesn't GC it
        win = BookForm(self, mode="create")
        if not hasattr(self, '_open_windows'):
            self._open_windows = []
        self._open_windows.append(win)
        try:
            win.deiconify()
            win.lift()
            win.focus()
        except Exception:
            pass

    def open_create_user(self):
        # Create a non-modal CTkToplevel; keep a reference so Python doesn't GC it
        win = UserForm(self, mode="create")
        if not hasattr(self, '_open_windows'):
            self._open_windows = []
        self._open_windows.append(win)
        try:
            win.deiconify()
            win.lift()
            win.focus()
        except Exception:
            pass
        

