import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from ui import theme
from ui import widget_factory as wf
from controllers.loan_controller import LoanController
from ui.loan.loan_edit import LoanEdit


class LoanList(ctk.CTkToplevel):
    """Listado de préstamos con opciones para editar y eliminar."""
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

        self.title("Listado de Préstamos")
        self.geometry("700x460")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Préstamos")
        title_lbl.pack(side="left")

        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("loan_id", "user_id", "isbn", "loan_date", "returned")

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

        try:
            style.map("Treeview",
                      background=[('selected', theme.ACCENT_RED)],
                      foreground=[('selected', '#ffffff')])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")
        headings = {"loan_id": "ID", "user_id": "Usuario", "isbn": "ISBN", "loan_date": "Fecha", "returned": "Devuelto"}
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            if c == "loan_id":
                self.tree.column(c, width=130, anchor="center")
            elif c == "returned":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=160, anchor="w")

        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_loans)
        refresh_btn.pack(side="left", padx=(0, 8))

        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        self.controller = LoanController()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

        # initial load
        self.load_loans()

    def load_loans(self):
        # clear rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            loans = self.controller.list_loans()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar préstamos: {e}")
            return

        for i, l in enumerate(loans):
            try:
                lid = l.get_loan_id()
                uid = l.get_user_id()
                isbn = l.get_isbn()
                ldate = l.get_loan_date()
                try:
                    ldate = ldate.isoformat()
                except Exception:
                    pass
                returned = "Sí" if l.is_returned() else "No"
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=(lid, uid, isbn, ldate, returned), tags=(tag,))
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
            messagebox.showinfo("Info", "Selecciona primero un préstamo en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            loan_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        try:
            loan = self.controller.get_loan(loan_id)
            if loan is None:
                messagebox.showerror("Error", f"Préstamo {loan_id} no encontrado")
                return

            parent = self._parent_window or self
            win = LoanEdit(parent, loan, controller=self.controller)

            # refresh the list when the edit window is closed
            try:
                def _on_child_destroy(event=None):
                    try:
                        if getattr(self, 'tree', None) and self.tree.winfo_exists():
                            self.load_loans()
                    except Exception:
                        pass

                win.bind('<Destroy>', _on_child_destroy)
            except Exception:
                pass

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un préstamo en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            loan_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el préstamo {loan_id}? Esta acción no se puede deshacer?"):
            return

        try:
            res = self.controller.delete_loan(loan_id)
            if res.get('success'):
                messagebox.showinfo("Borrado", "Préstamo eliminado correctamente.")
                self.load_loans()
            else:
                messagebox.showerror("Error", res.get('message'))
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["LoanList"]
