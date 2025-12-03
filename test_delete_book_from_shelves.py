"""Test para verificar que al eliminar un libro, se elimina de todas las estanterías."""

import os
import json
from models.Books import Book
from models.shelf import Shelf
from services.book_service import BookService
from services.shelf_service import ShelfService
from controllers.book_controller import BookController
from controllers.shelf_controller import ShelfController


def test_delete_book_removes_from_shelves():
    """Verificar que eliminar un libro lo remueve de todas las estanterías."""
    
    print("\n" + "="*80)
    print("TEST: Eliminar libro debe removerlo de estanterías")
    print("="*80)
    
    # 1. Crear un libro de prueba
    book_controller = BookController()
    shelf_controller = ShelfController()
    
    test_book_data = {
        "id": "TEST_DEL_001",
        "ISBNCode": "978-0-TEST-DEL",
        "title": "Libro de Prueba para Eliminar",
        "author": "Test Author",
        "weight": 0.5,
        "price": 15000,
        "isBorrowed": False
    }
    
    print("\n1. Creando libro de prueba...")
    try:
        book_controller.create_book(test_book_data)
        print(f"   ✓ Libro creado: {test_book_data['id']}")
    except Exception as e:
        print(f"   ✗ Error al crear libro: {e}")
        return False
    
    # 2. Crear estanterías de prueba
    print("\n2. Creando estanterías de prueba...")
    shelf_ids = []
    try:
        for i in range(3):
            shelf_id = f"TEST_SHELF_{i+1}"
            shelf = shelf_controller.create_shelf(shelf_id, capacity=8.0, name=f"Estantería Test {i+1}")
            shelf_ids.append(shelf_id)
            print(f"   ✓ Estantería creada: {shelf_id}")
    except Exception as e:
        print(f"   ✗ Error al crear estanterías: {e}")
        return False
    
    # 3. Asignar el libro a las estanterías
    print("\n3. Asignando libro a las estanterías...")
    book = book_controller.get_book(test_book_data['id'])
    for shelf_id in shelf_ids:
        try:
            success = shelf_controller.add_book(shelf_id, book)
            if success:
                print(f"   ✓ Libro asignado a {shelf_id}")
            else:
                print(f"   ✗ No se pudo asignar libro a {shelf_id}")
        except Exception as e:
            print(f"   ✗ Error al asignar libro a {shelf_id}: {e}")
    
    # 4. Verificar que el libro está en las estanterías
    print("\n4. Verificando que el libro está en las estanterías...")
    book_found_count = 0
    for shelf_id in shelf_ids:
        books = shelf_controller.get_books(shelf_id)
        for b in books:
            if b.get_id() == test_book_data['id']:
                book_found_count += 1
                print(f"   ✓ Libro encontrado en {shelf_id}")
                break
    
    if book_found_count == 0:
        print("   ✗ El libro no se encontró en ninguna estantería")
        return False
    
    print(f"\n   Total: Libro encontrado en {book_found_count} estantería(s)")
    
    # 5. Eliminar el libro del catálogo
    print("\n5. Eliminando el libro del catálogo...")
    try:
        book_controller.delete_book(test_book_data['id'])
        print(f"   ✓ Libro {test_book_data['id']} eliminado del catálogo")
    except Exception as e:
        print(f"   ✗ Error al eliminar libro: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. Verificar que el libro YA NO está en las estanterías
    print("\n6. Verificando que el libro fue eliminado de las estanterías...")
    # Recargar el controlador para asegurarse de que lee desde el disco
    shelf_controller = ShelfController()
    book_still_found = 0
    for shelf_id in shelf_ids:
        books = shelf_controller.get_books(shelf_id)
        for b in books:
            if b.get_id() == test_book_data['id']:
                book_still_found += 1
                print(f"   ✗ ERROR: Libro todavía encontrado en {shelf_id}")
                break
    
    if book_still_found == 0:
        print(f"   ✓ Libro eliminado correctamente de todas las estanterías")
    else:
        print(f"   ✗ ERROR: Libro todavía presente en {book_still_found} estantería(s)")
        return False
    
    # 7. Verificar que el libro no existe en el catálogo
    print("\n7. Verificando que el libro no existe en el catálogo...")
    try:
        deleted_book = book_controller.get_book(test_book_data['id'])
        if deleted_book is None:
            print(f"   ✓ Libro no encontrado en el catálogo (correcto)")
        else:
            print(f"   ✗ ERROR: Libro todavía existe en el catálogo")
            return False
    except Exception as e:
        print(f"   ✗ Error al verificar catálogo: {e}")
        return False
    
    # 8. Limpiar: eliminar estanterías de prueba
    print("\n8. Limpiando estanterías de prueba...")
    for shelf_id in shelf_ids:
        try:
            shelf_controller.delete_shelf(shelf_id)
            print(f"   ✓ Estantería {shelf_id} eliminada")
        except Exception as e:
            print(f"   ✗ Error al eliminar estantería {shelf_id}: {e}")
    
    print("\n" + "="*80)
    print("✓ TEST EXITOSO: El libro se elimina correctamente de estanterías")
    print("="*80 + "\n")
    return True


if __name__ == "__main__":
    test_delete_book_removes_from_shelves()
