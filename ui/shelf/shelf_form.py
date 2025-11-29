import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
try:
    from PIL import Image
except Exception:
    Image = None

from controllers.shelf_controller import ShelfController
from ui import theme
from ui import widget_factory as wf


class ShelfForm(ctk.CTkToplevel):
    """Form to create/edit a Shelf and perform simple shelf operations.

    Provides fields for id (auto-generated), capacity, and buttons to
    save/load shelves to JSON, clear the shelf and show a quick summary.
    """

    def __init__(self, parent=None, mode="create", shelf_id=None):
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass
        
        self.controller = ShelfController()
        self.mode = mode
        self.shelf_id = shelf_id

        # Apply theme
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # window basics
        self.title("Shelf Manager")
        self.geometry("480x360")

        # header
        header = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        header.pack(fill="x", padx=16, pady=12)
        title_lbl = wf.create_title_label(header, "Shelf")
        title_lbl.pack(side="left")

        # form frame
        form = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        form.pack(expand=True, fill="both", padx=16, pady=8)

        id_placeholder = "Auto (se asignará)" if mode == "create" else "ID"
        self.entry_id = ctk.CTkEntry(form, placeholder_text=id_placeholder)
        self.entry_id.pack(pady=6, fill="x")
        if mode == "create":
            try:
                self.entry_id.configure(state="disabled")
            except Exception:
                pass

        # Human-readable name for the shelf
        self.entry_name = ctk.CTkEntry(form, placeholder_text="Nombre (ej. Estantería A1)")
        self.entry_name.pack(pady=6, fill="x")

        # action buttons
        actions = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        actions.pack(pady=12)

        if mode == "create":
            primary = wf.create_primary_button(actions, text="Create Shelf", command=self.create_shelf)
        else:
            primary = wf.create_primary_button(actions, text="Update Shelf", command=self.update_shelf)
        primary.pack(side="left", padx=(0, 8))

        small_save = wf.create_small_button(actions, text="Save All", command=self.save_shelves)
        small_save.pack(side="left", padx=(0, 8))

        small_load = wf.create_small_button(actions, text="Load File", command=self.load_shelves)
        small_load.pack(side="left", padx=(0, 8))

        summary_btn = wf.create_small_button(actions, text="Show Summary", command=self.show_summary)
        summary_btn.pack(side="left", padx=(0, 8))

        clear_btn = wf.create_small_button(actions, text="Clear Shelf", command=self.clear_shelf)
        clear_btn.pack(side="left")

        # area to show summary text
        self.summary_lbl = ctk.CTkLabel(self, text="")
        self.summary_lbl.pack(padx=16, pady=(6, 12), fill="x")

        # close handler
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # If editing, load existing values
        if mode == "edit" and shelf_id:
            self.load_shelf()

    def create_shelf(self):
        # Capacity is fixed to 8.0 per project requirements (max weight per shelf)
        cap = 8.0
        name = (self.entry_name.get() or '').strip()
        shelf = self.controller.create_shelf(None, capacity=cap, name=name if name else None)
        if shelf:
            messagebox.showinfo("Success", f"Shelf {getattr(shelf, '_Shelf__id', 'unknown')} created.")
            self._on_close()
        else:
            messagebox.showerror("Error", "Failed to create shelf.")

    def update_shelf(self):
        sid = self.entry_id.get()
        if not sid:
            messagebox.showerror("Error", "Shelf ID required for update.")
            return
        # Capacity is fixed (8.0) by project rules; only update name here
        ok = True
        # update name as well
        try:
            name = (self.entry_name.get() or '').strip()
            if name:
                shelf = self.controller.find_shelf(sid)
                if shelf is not None:
                    try:
                        shelf.set_name(name)
                    except Exception:
                        try:
                            setattr(shelf, '_Shelf__name', name)
                        except Exception:
                            pass
        except Exception:
            pass
        # feedback always success if shelf exists
        if self.controller.find_shelf(sid) is not None:
            messagebox.showinfo("Success", "Shelf updated.")
            # persist change
            try:
                path = __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.dirname(__file__)), 'data', 'shelves.json')
                self.controller.service.save_to_file(path)
            except Exception:
                pass
        else:
            messagebox.showerror("Error", "Shelf not found.")

    def load_shelf(self):
        shelf = self.controller.find_shelf(self.shelf_id)
        if not shelf:
            return
        # fill values
        try:
            self.entry_id.configure(state="normal")
            self.entry_id.delete(0, 'end')
            self.entry_id.insert(0, getattr(shelf, '_Shelf__id', ''))
            self.entry_id.configure(state="disabled")
        except Exception:
            pass
        # load name if present
        try:
            name = getattr(shelf, '_Shelf__name', '')
            if name:
                try:
                    self.entry_name.delete(0, 'end')
                except Exception:
                    pass
                self.entry_name.insert(0, str(name))
        except Exception:
            pass

    def show_summary(self):
        sid = self.entry_id.get() if self.entry_id.get() else self.shelf_id
        if not sid:
            messagebox.showerror("Error", "Shelf ID required to show summary.")
            return
        s = self.controller.shelf_summary(sid)
        if not s:
            self.summary_lbl.configure(text="Shelf not found")
            return
        txt = f"ID: {s.get('id')}  Capacity: {s.get('capacity')}kg  Total: {s.get('total_weight')}kg  Remaining: {s.get('remaining_capacity')}kg  Count: {s.get('books_count')}"
        self.summary_lbl.configure(text=txt)

    def clear_shelf(self):
        sid = self.entry_id.get() if self.entry_id.get() else self.shelf_id
        if not sid:
            messagebox.showerror("Error", "Shelf ID required to clear.")
            return
        removed = self.controller.clear_shelf(sid)
        messagebox.showinfo("Cleared", f"Removed {len(removed)} books from shelf.")

    def save_shelves(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            self.controller.save_shelves(path)
            messagebox.showinfo("Saved", f"Shelves saved to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_shelves(self):
        path = filedialog.askopenfilename(filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            self.controller.load_shelves(path)
            messagebox.showinfo("Loaded", f"Shelves loaded from {path}")
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
