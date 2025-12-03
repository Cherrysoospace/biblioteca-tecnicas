import customtkinter as ctk
from tkinter import messagebox
from ui import theme
from services.user_service import UserService
from datetime import datetime
from services.inventory_service import InventoryService


class LoanEdit(ctk.CTkToplevel):
    """Small editor for an existing loan.

    Allows changing the user and toggling returned status.
    """
    def __init__(self, parent, loan, controller=None):
        super().__init__(parent)
        self._parent_window = parent
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.title("Editar Préstamo")
        # aumentar tamaño de la ventana para dar más espacio a los campos
        # Se incrementa a 820x420 para mejorar la usabilidad al editar préstamos
        self.geometry("820x420")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        self.controller = controller
        self.loan = loan

        # Form container
        frame = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=8)
        frame.pack(expand=True, fill="both", padx=12, pady=12)

        # User selector
        self._user_map = {}
        users = []
        try:
            usvc = UserService()
            for u in usvc.get_all_users():
                disp = f"{u.get_name()} ({u.get_id()})"
                users.append(disp)
                self._user_map[disp] = u.get_id()
        except Exception:
            users = []

        lbl = ctk.CTkLabel(frame, text="Usuario:")
        lbl.pack(anchor="w", pady=(6, 2))

        if users:
            # opción más ancha para facilitar la selección y lectura
            try:
                self.user_selector = ctk.CTkOptionMenu(frame, values=users, width=420)
            except Exception:
                self.user_selector = ctk.CTkOptionMenu(frame, values=users)
            # select current user
            try:
                cur_disp = next(k for k, v in self._user_map.items() if v == self.loan.get_user_id())
                self.user_selector.set(cur_disp)
            except Exception:
                try:
                    self.user_selector.set(users[0])
                except Exception:
                    pass
        else:
            self.user_selector = ctk.CTkLabel(frame, text="No hay usuarios disponibles")
        self.user_selector.pack(fill="x", pady=(0, 8))

        # --- Book selector: allow changing book on loan (only available ISBNs)
        self._book_map = {}
        book_label = ctk.CTkLabel(frame, text="Libro (ISBN):")
        book_label.pack(anchor="w", pady=(6, 2))

        books = []
        cur_isbn = None
        try:
            cur_isbn = self.loan.get_isbn()
        except Exception:
            pass

        try:
            invs = InventoryService()
            # First, add the current book of the loan (even if not available)
            if cur_isbn:
                try:
                    current_inventories = invs.find_by_isbn(cur_isbn)
                    if current_inventories:
                        inv = current_inventories[0]
                        book = inv.get_book()
                        if book:
                            title = book.get_title() if hasattr(book, 'get_title') else None
                            bid = book.get_id() if hasattr(book, 'get_id') else None
                            disp = f"{title} ({cur_isbn}) [{bid}]" if title else f"{cur_isbn} [{bid}]"
                            books.append(disp)
                            self._book_map[disp] = cur_isbn
                except Exception:
                    pass
            
            # Then add all available books (avoiding duplicates)
            for isbn, title, bid in invs.get_isbns_with_available_copies():
                try:
                    if isbn == cur_isbn:
                        continue  # Skip if already added
                    disp = f"{title} ({isbn}) [{bid}]" if title else f"{isbn} [{bid}]"
                    books.append(disp)
                    self._book_map[disp] = isbn
                except Exception:
                    continue
        except Exception:
            books = []

        if books:
            try:
                self.book_selector = ctk.CTkOptionMenu(frame, values=books, width=420)
            except Exception:
                self.book_selector = ctk.CTkOptionMenu(frame, values=books)
            # set current book selection (should be first in list now)
            try:
                if cur_isbn:
                    # find display matching cur_isbn
                    for k, v in self._book_map.items():
                        if v == cur_isbn:
                            try:
                                self.book_selector.set(k)
                            except Exception:
                                pass
                            break
                else:
                    self.book_selector.set(books[0])
            except Exception:
                try:
                    self.book_selector.set(books[0])
                except Exception:
                    pass
        else:
            self.book_selector = ctk.CTkLabel(frame, text="No hay libros disponibles")
        self.book_selector.pack(fill="x", pady=(0, 8))

        # Returned checkbox
        self.return_var = ctk.BooleanVar(value=self.loan.is_returned())
        cb = ctk.CTkCheckBox(frame, text="Devuelto", variable=self.return_var)
        cb.pack(anchor="w", pady=(4, 12))

        # Loan date field
        try:
            cur_date = self.loan.get_loan_date()
            try:
                cur_date_str = cur_date.isoformat()
            except Exception:
                cur_date_str = str(cur_date)
        except Exception:
            cur_date_str = datetime.utcnow().date().isoformat()

        lbl_date = ctk.CTkLabel(frame, text="Fecha (YYYY-MM-DD):")
        lbl_date.pack(anchor="w", pady=(4, 2))
        # entrada de fecha con mayor ancho
        try:
            self.date_entry = ctk.CTkEntry(frame, width=420)
        except Exception:
            self.date_entry = ctk.CTkEntry(frame)
        try:
            self.date_entry.insert(0, cur_date_str)
        except Exception:
            pass
        self.date_entry.pack(fill="x", pady=(0, 8))

        # Action buttons
        btn_frame = ctk.CTkFrame(frame, fg_color=theme.BG_COLOR, corner_radius=0)
        btn_frame.pack(fill="x", pady=(8, 2))

        save_btn = ctk.CTkButton(btn_frame, text="Guardar", command=self._on_save)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancelar", command=self._on_close)
        save_btn.pack(side="left", padx=(0, 8))
        cancel_btn.pack(side="left")

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def _on_save(self):
        # Map selected user
        try:
            if isinstance(self.user_selector, ctk.CTkLabel):
                messagebox.showerror("Error", "No hay usuarios disponibles")
                return
            sel = self.user_selector.get().strip()
            user_id = self._user_map.get(sel)
        except Exception:
            user_id = None

        returned = bool(self.return_var.get())

        if not user_id:
            messagebox.showerror("Error", "Selecciona un usuario válido")
            return

        date_str = None
        try:
            date_str = self.date_entry.get().strip()
        except Exception:
            date_str = None

        try:
            # Determine selected book (if OptionMenu present)
            isbn = None
            try:
                if not isinstance(self.book_selector, ctk.CTkLabel):
                    sel_book = self.book_selector.get().strip()
                    if sel_book and not sel_book.startswith("(No books"):
                        isbn = self._book_map.get(sel_book)
            except Exception:
                isbn = None

            # pass loan_date as string in ISO format; service will parse
            res = self.controller.update_loan(self.loan.get_loan_id(), user_id=user_id, isbn=isbn, returned=returned, loan_date=date_str)
            if res.get('success'):
                messagebox.showinfo("Guardado", "Préstamo actualizado correctamente")
                self._on_close()
            else:
                messagebox.showerror("Error", res.get('message'))
        except Exception as e:
            messagebox.showerror("Error", str(e))

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


__all__ = ["LoanEdit"]
