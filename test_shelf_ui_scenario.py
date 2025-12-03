"""
Test que simula exactamente el flujo de usuario:
1. Usuario crea una estantería desde la UI
2. Usuario intenta asignarle libros
3. Verificar que los cambios persisten en shelves.json
"""
import json
import os
import tempfile
import shutil
from pathlib import Path

# Monkey-patch FilePaths antes de importar los controladores
from utils.config import FilePaths

# Crear directorio temporal para las pruebas
TEST_DIR = tempfile.mkdtemp()
TEST_SHELVES_FILE = os.path.join(TEST_DIR, "shelves.json")

# Sobrescribir la ruta de shelves
original_shelves_path = FilePaths.SHELVES
FilePaths.SHELVES = TEST_SHELVES_FILE

# Ahora sí importar los controladores (después del monkey-patch)
from controllers.shelf_controller import ShelfController
from controllers.book_controller import BookController
from models.Books import Book

def test_ui_scenario():
    """Simula el escenario completo del usuario."""
    
    print("\n" + "="*70)
    print("SIMULACIÓN DEL ESCENARIO DE USUARIO")
    print("="*70)
    
    # PASO 1: Usuario abre la aplicación y crea una estantería
    print("\n[PASO 1] Usuario crea una nueva estantería...")
    controller1 = ShelfController()
    initial_shelves = controller1.list_shelves()
    print(f"  → Estanterías existentes al inicio: {len(initial_shelves)}")
    
    # Simular creación desde ShelfForm
    new_shelf = controller1.create_shelf(
        capacity=8.0,  # Capacidad máxima permitida
        name="Mi Estantería Nueva"
    )
    # Usar los métodos getter para acceder a los atributos
    shelf_id = new_shelf.get_id()
    shelf_name = new_shelf.get_name()
    print(f"  → Estantería creada: ID={shelf_id}, nombre={shelf_name}")
    
    # Verificar que se guardó inmediatamente
    with open(TEST_SHELVES_FILE, 'r', encoding='utf-8') as f:
        data_after_create = json.load(f)
    print(f"  → Archivo JSON contiene {len(data_after_create)} estantería(s)")
    
    # Verificar que el nombre se guardó
    shelf_data = next((s for s in data_after_create if s['id'] == shelf_id), None)
    assert shelf_data is not None, "❌ Estantería no encontrada en JSON"
    assert shelf_data['name'] == "Mi Estantería Nueva", "❌ Nombre no se guardó correctamente"
    print(f"  ✓ Nombre guardado correctamente: '{shelf_data['name']}'")
    
    # PASO 2: Usuario cierra y reabre la aplicación (simular nuevo controlador)
    print("\n[PASO 2] Usuario cierra y reabre la aplicación...")
    del controller1  # Eliminar referencia al controlador anterior
    
    controller2 = ShelfController()
    reloaded_shelves = controller2.list_shelves()
    print(f"  → Estanterías cargadas: {len(reloaded_shelves)}")
    
    reloaded_shelf = controller2.find_shelf(shelf_id)
    assert reloaded_shelf is not None, "❌ Estantería no se recargó"
    reloaded_name = reloaded_shelf.get_name()
    assert reloaded_name == "Mi Estantería Nueva", f"❌ Nombre no persistió tras recarga: '{reloaded_name}'"
    print(f"  ✓ Estantería recargada correctamente: '{reloaded_name}'")
    
    # PASO 3: Usuario asigna libros (simular AssignBookForm)
    print("\n[PASO 3] Usuario asigna libros a la estantería...")
    
    # Crear algunos libros de prueba
    book1 = Book('B001', '978-1234567890', 'Libro 1', 'Autor 1', 0.5, 100, False)
    book2 = Book('B002', '978-0987654321', 'Libro 2', 'Autor 2', 0.5, 150, False)
    
    # Simular el flujo de AssignBookForm.assign_selected()
    result1 = controller2.add_book(shelf_id, book1)
    result2 = controller2.add_book(shelf_id, book2)
    
    print(f"  → Libro 1 asignado: {result1}")
    print(f"  → Libro 2 asignado: {result2}")
    
    assert result1 == True, "❌ No se pudo asignar libro 1"
    assert result2 == True, "❌ No se pudo asignar libro 2"
    
    # Verificar inmediatamente en el archivo JSON
    with open(TEST_SHELVES_FILE, 'r', encoding='utf-8') as f:
        data_after_assign = json.load(f)
    
    shelf_data = next((s for s in data_after_assign if s['id'] == shelf_id), None)
    assert shelf_data is not None, "❌ Estantería no encontrada en JSON tras asignación"
    
    books_in_json = shelf_data.get('books', [])
    print(f"  → Libros en JSON: {len(books_in_json)}")
    
    assert len(books_in_json) == 2, f"❌ Se esperaban 2 libros, pero hay {len(books_in_json)}"
    
    # Verificar que los libros son los correctos
    isbn_list = [b['ISBNCode'] for b in books_in_json]
    assert '978-1234567890' in isbn_list, "❌ Libro 1 no está en JSON"
    assert '978-0987654321' in isbn_list, "❌ Libro 2 no está en JSON"
    print(f"  ✓ Ambos libros guardados correctamente en JSON")
    
    # PASO 4: Usuario cierra y reabre nuevamente para verificar persistencia
    print("\n[PASO 4] Usuario cierra y reabre nuevamente...")
    del controller2
    
    controller3 = ShelfController()
    final_shelf = controller3.find_shelf(shelf_id)
    
    assert final_shelf is not None, "❌ Estantería no se recargó en segunda apertura"
    final_books = controller3.get_books(shelf_id)
    final_name = final_shelf.get_name()
    
    print(f"  → Estantería recargada: '{final_name}'")
    print(f"  → Libros recargados: {len(final_books)}")
    
    assert len(final_books) == 2, f"❌ Se esperaban 2 libros tras recarga, hay {len(final_books)}"
    assert final_name == "Mi Estantería Nueva", f"❌ Nombre no persistió en segunda recarga: '{final_name}'"
    
    print(f"  ✓ Todo persistió correctamente tras múltiples recargas")
    
    print("\n" + "="*70)
    print("✅ SIMULACIÓN COMPLETA EXITOSA")
    print("="*70)
    print("\nCONCLUSIÓN:")
    print("  • Las estanterías se crean y guardan correctamente")
    print("  • Los nombres persisten")
    print("  • Los libros se asignan y guardan correctamente")
    print("  • Todo persiste tras recargas múltiples")
    print("\nSi el usuario experimenta problemas, puede ser por:")
    print("  1. Archivo shelves.json bloqueado por otro proceso")
    print("  2. Permisos de escritura en el directorio data/")
    print("  3. Múltiples instancias de la aplicación corriendo")
    print("  4. Cache del sistema de archivos")

if __name__ == "__main__":
    try:
        test_ui_scenario()
    finally:
        # Restaurar ruta original
        FilePaths.SHELVES = original_shelves_path
        # Limpiar directorio temporal
        shutil.rmtree(TEST_DIR, ignore_errors=True)
