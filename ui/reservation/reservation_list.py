import os
import tkinter as tk
import tkinter.font as tkfont
import json
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.reservation_controller import ReservationController
from ui.reservation.reservation_edit import ReservationEditForm


class ReservationList(ctk.CTkToplevel):
    """List all reservations in a table with edit and delete actions."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent_window = parent
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        self.title("Listado de Reservas")
        self.geometry("900x420")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Reservas")
        title_lbl.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("reservation_id", "user_id", "user_name", "isbn", "reserved_date", "status", "assigned_date")
        
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

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

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")
        headings = {
            "reservation_id": "ID",
            "user_id": "User ID",
            "user_name": "User",
            "isbn": "ISBN",
            "reserved_date": "Reserved",
            "status": "Status",
            "assigned_date": "Assigned"
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c in ("reservation_id", "user_id"):
                self.tree.column(c, width=90, anchor="center")
            elif c in ("status", "reserved_date", "assigned_date"):
                self.tree.column(c, width=140, anchor="center")
            else:
                self.tree.column(c, width=200, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # Action row
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_reservations)
        refresh_btn.pack(side="left", padx=(0, 8))
        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))
        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))
        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = ReservationController()
        self._open_windows = []

        # load data
        self.load_reservations()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

    def load_reservations(self):
        # clear
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            res_list = self.controller.list_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        for i, r in enumerate(res_list):
            try:
                rid = r.get_reservation_id()
                uid = r.get_user_id()
                # try to show user name by loading users if possible
                try:
                    from services.user_service import UserService
                    us = UserService()
                    uobj = us.find_by_id(uid)
                    uname = uobj.get_name() if uobj else ""
                except Exception:
                    uname = ""

                isbn = r.get_isbn()
                reserved = r.get_reserved_date()
                try:
                    reserved = reserved.isoformat()
                except Exception:
                    pass
                status = r.get_status()
                assigned = r.get_assigned_date()
                try:
                    assigned = assigned.isoformat() if assigned else ""
                except Exception:
                    pass
                row = (rid, uid, uname, isbn, reserved, status, assigned)
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
            except Exception:
                continue

        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

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

    def open_selected_for_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una reserva en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            reservation_id = values[0]
            parent = self._parent_window or self
            win = ReservationEditForm(parent, reservation_id)
            self._open_windows.append(win)
            try:
                win.deiconify()
                win.lift()
                win.focus()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el editor: {e}")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero una reserva en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            reservation_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar la reserva {reservation_id}? Esta acción no se puede deshacer?"):
            return

        try:
            resp = self.controller.delete_reservation(reservation_id)
            # controller returns dict
            if resp.get('success'):
                messagebox.showinfo("Borrado", "Reserva eliminada correctamente.")
            else:
                messagebox.showerror("Error", resp.get('message') or 'Error deleting')
            self.load_reservations()
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["ReservationList"]
