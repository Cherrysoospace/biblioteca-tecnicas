"""Test de integración completo para el flujo de estanterías.

Verifica que crear una estantería, asignarle libros y persistir funcione correctamente.
"""
import os
import tempfile
import json
from controllers.shelf_controller import ShelfController
from models.Books import Book
from utils.config import FilePaths


def test_shelf_lifecycle_with_controller():
    """Test completo: crear shelf con nombre, asignar libro, verificar persistencia."""
    
    # usar un archivo temporal para no sobrescribir data/shelves.json
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_shelves.json")
        
        # monkey-patch FilePaths.SHELVES temporalmente
        original_path = FilePaths.SHELVES
        FilePaths.SHELVES = test_file
        
        try:
            # 1. Crear controlador (cargará desde archivo vacío)
            controller = ShelfController()
            
            # 2. Crear estantería con nombre
            shelf = controller.create_shelf(id="TEST1", name="Estantería de Prueba", capacity=5.0)
            assert shelf is not None
            shelf_id = getattr(shelf, '_Shelf__id')
            shelf_name = shelf.get_name()
            print(f"✓ Shelf creado: {shelf_id}, nombre: {shelf_name}")
            
            # 3. Verificar que el archivo JSON contiene el nombre
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert len(data) == 1, f"Esperaba 1 shelf, encontré {len(data)}"
            assert data[0]['id'] == 'TEST1'
            assert data[0]['name'] == 'Estantería de Prueba', f"Nombre esperado 'Estantería de Prueba', encontrado '{data[0]['name']}'"
            print(f"✓ Archivo JSON contiene el nombre correctamente")
            
            # 4. Asignar un libro a la estantería
            book = Book('B999', '978-TEST', 'Test Book', 'Test Author', 0.5, 100, False)
            result = controller.add_book(shelf_id, book)
            assert result is True, "add_book debería retornar True"
            print(f"✓ Libro asignado correctamente")
            
            # 5. Verificar que el archivo JSON fue actualizado con el libro
            with open(test_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert len(data) == 1
            assert len(data[0]['books']) == 1, f"Esperaba 1 libro, encontré {len(data[0]['books'])}"
            assert data[0]['books'][0]['id'] == 'B999'
            print(f"✓ Archivo JSON actualizado con el libro")
            
            # 6. Crear un nuevo controlador (simulando reinicio de app) y verificar que carga correctamente
            controller2 = ShelfController()
            shelves = controller2.list_shelves()
            assert len(shelves) == 1
            loaded_shelf = shelves[0]
            assert getattr(loaded_shelf, '_Shelf__id') == 'TEST1'
            assert loaded_shelf.get_name() == 'Estantería de Prueba'
            books = controller2.get_books('TEST1')
            assert len(books) == 1
            assert books[0].get_id() == 'B999'
            print(f"✓ Datos cargados correctamente tras reinicio simulado")
            
            print("\n✅ TEST COMPLETO PASÓ - El flujo de persistencia funciona correctamente")
            
        finally:
            # restaurar path original
            FilePaths.SHELVES = original_path


if __name__ == "__main__":
    test_shelf_lifecycle_with_controller()
