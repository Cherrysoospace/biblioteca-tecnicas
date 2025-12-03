"""
Script simple para probar la ventana de listado de estanterías.
"""
import customtkinter as ctk
from ui.shelf.shelf_list import ShelfList

def test_shelf_list_window():
    """Prueba la ventana de listado de estanterías."""
    print("Iniciando aplicación de prueba...")
    print("NOTA: Cierra la ventana para terminar el test")
    
    # Configurar modo de apariencia
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Crear ventana principal (necesaria como parent)
    root = ctk.CTk()
    root.title("Test - Listado de Estanterías")
    root.geometry("300x200")
    
    def open_shelf_list():
        """Abre la ventana de listado de estanterías."""
        try:
            shelf_window = ShelfList(root)
            shelf_window.focus()
        except Exception as e:
            print(f"❌ Error al abrir ShelfList: {e}")
            import traceback
            traceback.print_exc()
    
    # Botón para abrir la lista
    btn = ctk.CTkButton(
        root,
        text="Abrir Lista de Estanterías",
        command=open_shelf_list,
        width=200,
        height=40
    )
    btn.place(relx=0.5, rely=0.5, anchor="center")
    
    # Abrir automáticamente
    root.after(100, open_shelf_list)
    
    print("✓ Ventana iniciada")
    print("  → Si ves las estanterías en la tabla, ¡todo funciona!")
    print("  → Si la tabla está vacía, revisa la consola para errores")
    
    root.mainloop()

if __name__ == "__main__":
    test_shelf_list_window()
