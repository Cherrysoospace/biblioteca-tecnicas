import customtkinter as ctk
from tkinter import messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.reservation_controller import ReservationController
from services.user_service import UserService
from services.book_service import BookService
from datetime import datetime


class ReservationEditForm(ctk.CTkToplevel):
    """Small editor to update reservation status and optionally assigned date."""
    def __init__(self, parent=None, reservation_id=None):
        super().__init__(parent)
        self._parent_window = parent
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.title("Editar Reserva")
        # Increase the window size so all controls and buttons are visible
        # without needing to maximize the window on small screens.
        self.geometry("820x520")
        self.controller = ReservationController()
        self.reservation_id = reservation_id

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_lbl = wf.create_title_label(container, "Editar Reserva")
        title_lbl.pack(pady=(4, 8))

        self.lbl_id = ctk.CTkLabel(container, text=f"ID: {reservation_id}")
        self.lbl_id.pack(anchor="w")

        # user selector
        self.lbl_user = ctk.CTkLabel(container, text="Usuario:")
        self.lbl_user.pack(anchor="w", pady=(8, 0))
        try:
            self.user_service = UserService()
        except Exception:
            self.user_service = None

        user_values = []
        if self.user_service is not None:
            try:
                users = self.user_service.get_all_users()
                user_values = [f"{u.get_id()} - {u.get_name()}" for u in users]
            except Exception:
                user_values = []

        if not user_values:
            user_values = ["(No users available)"]

        try:
            self.opt_user = ctk.CTkOptionMenu(container, values=user_values)
        except Exception:
            self.opt_user = ctk.CTkEntry(container)
            if user_values and user_values[0] != "(No users available)":
                try:
                    self.opt_user.insert(0, user_values[0].split(' - ')[0])
                except Exception:
                    pass
        self.opt_user.pack(pady=6, fill="x")

        # book selector
        self.lbl_book = ctk.CTkLabel(container, text="Libro (ISBN):")
        self.lbl_book.pack(anchor="w", pady=(8, 0))
        try:
            self.book_service = BookService()
        except Exception:
            self.book_service = None

        book_values = []
        if self.book_service is not None:
            try:
                books = self.book_service.get_all_books()
                # show 'ISBN - Title'
                book_values = [f"{b.get_ISBNCode()} - {b.get_title()}" for b in books]
            except Exception:
                book_values = []

        if not book_values:
            book_values = ["(No books available)"]

        try:
            self.opt_book = ctk.CTkOptionMenu(container, values=book_values)
        except Exception:
            self.opt_book = ctk.CTkEntry(container)
            if book_values and book_values[0] != "(No books available)":
                try:
                    self.opt_book.insert(0, book_values[0].split(' - ')[0])
                except Exception:
                    pass
        self.opt_book.pack(pady=6, fill="x")

        # status selector
        self.lbl_status = ctk.CTkLabel(container, text="Status:")
        self.lbl_status.pack(anchor="w", pady=(8, 0))
        try:
            self.opt_status = ctk.CTkOptionMenu(container, values=["pending", "assigned", "cancelled"])
        except Exception:
            self.opt_status = ctk.CTkEntry(container)
        self.opt_status.pack(pady=6, fill="x")

        # assigned date display / button to set now
        self.lbl_assigned = ctk.CTkLabel(container, text="Assigned date:")
        self.lbl_assigned.pack(anchor="w", pady=(8, 0))
        self.entry_assigned = ctk.CTkEntry(container)
        self.entry_assigned.pack(pady=6, fill="x")

        set_now_btn = wf.create_small_button(container, text="Set Now", command=self._set_now)
        set_now_btn.pack(pady=(0, 6))

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(6, 0))
        save_btn = wf.create_primary_button(action_frame, text="Guardar", command=self.save, width=180, height=44)
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        save_btn.pack(side="left", padx=(0, 8))
        cancel_btn.pack(side="left")

        # load reservation
        self._load()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

    def _load(self):
        try:
            r = self.controller.get_reservation(self.reservation_id)
            if not r:
                messagebox.showerror("Error", "Reservation not found")
                self._on_close()
                return
            # set user selection
            try:
                uid = r.get_user_id()
                try:
                    self.opt_user.set(next(v for v in (self.opt_user._values if hasattr(self.opt_user, '_values') else []) if v.startswith(f"{uid} - ")))
                except Exception:
                    try:
                        # OptionMenu may have get/set API; fallback to matching available list
                        vals = []
                        try:
                            vals = self.opt_user._values
                        except Exception:
                            pass
                        for v in vals:
                            if isinstance(v, str) and v.startswith(f"{uid} - "):
                                try:
                                    self.opt_user.set(v)
                                except Exception:
                                    try:
                                        self.opt_user.delete(0, 'end')
                                        self.opt_user.insert(0, uid)
                                    except Exception:
                                        pass
                                break
                    except Exception:
                        pass
            except Exception:
                pass

            # set book selection
            try:
                isbn = r.get_isbn()
                try:
                    self.opt_book.set(next(v for v in (self.opt_book._values if hasattr(self.opt_book, '_values') else []) if v.startswith(f"{isbn} - ")))
                except Exception:
                    try:
                        vals = []
                        try:
                            vals = self.opt_book._values
                        except Exception:
                            pass
                        for v in vals:
                            if isinstance(v, str) and v.startswith(f"{isbn} - "):
                                try:
                                    self.opt_book.set(v)
                                except Exception:
                                    try:
                                        self.opt_book.delete(0, 'end')
                                        self.opt_book.insert(0, isbn)
                                    except Exception:
                                        pass
                                break
                    except Exception:
                        pass
            except Exception:
                pass

            # set status
            try:
                self.opt_status.set(r.get_status())
            except Exception:
                try:
                    self.opt_status.insert(0, r.get_status())
                except Exception:
                    pass

            ad = r.get_assigned_date()
            if ad:
                try:
                    self.entry_assigned.insert(0, ad.isoformat())
                except Exception:
                    self.entry_assigned.insert(0, str(ad))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_now(self):
        try:
            now = datetime.utcnow().isoformat()
            self.entry_assigned.delete(0, 'end')
            self.entry_assigned.insert(0, now)
        except Exception:
            pass

    def save(self):
        status = None
        try:
            status = self.opt_status.get()
        except Exception:
            status = self.opt_status.get().strip()

        assigned = self.entry_assigned.get().strip()
        kwargs = {}
        # read selected user and book from OptionMenus or Entry fallbacks
        try:
            sel_user = self.opt_user.get()
        except Exception:
            try:
                sel_user = self.opt_user.get().strip()
            except Exception:
                sel_user = None

        try:
            sel_book = self.opt_book.get()
        except Exception:
            try:
                sel_book = self.opt_book.get().strip()
            except Exception:
                sel_book = None

        if sel_user and not sel_user.startswith("(No users"):
            try:
                kwargs['user_id'] = sel_user.split(' - ')[0].strip()
            except Exception:
                kwargs['user_id'] = sel_user

        if sel_book and not sel_book.startswith("(No books"):
            try:
                kwargs['isbn'] = sel_book.split(' - ')[0].strip()
            except Exception:
                kwargs['isbn'] = sel_book
        if status:
            kwargs['status'] = status
            if status == 'assigned' and not assigned:
                # set assigned date if missing
                assigned = datetime.utcnow().isoformat()
        if assigned:
            # pass ISO string; controller/service will parse when possible
            kwargs['assigned_date'] = assigned

        try:
            resp = self.controller.update_reservation(self.reservation_id, **kwargs)
            if resp.get('success'):
                messagebox.showinfo("Saved", "Reservation updated")
                # try to refresh parent list if exists
                try:
                    if getattr(self._parent_window, 'load_reservations', None):
                        self._parent_window.load_reservations()
                except Exception:
                    pass
                self._on_close()
            else:
                messagebox.showerror("Error", resp.get('message') or 'Error updating')
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


__all__ = ["ReservationEditForm"]
