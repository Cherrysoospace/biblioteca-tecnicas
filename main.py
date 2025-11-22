import customtkinter as ctk
from ui.book_form import BookForm

ctk.set_appearance_mode("dark")

app = BookForm(mode="create")  # para crear
# app = BookForm(mode="edit", book_id="001")  # para editar
app.mainloop()
