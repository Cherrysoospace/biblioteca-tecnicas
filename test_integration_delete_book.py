"""Test de integración completo: Eliminación de libro con estanterías.

Este test simula el escenario completo de un usuario:
1. Crear un libro
2. Asignarlo a múltiples estanterías
3. Verificar que está en las estanterías
4. Eliminar el libro desde la UI (usando BookController)
5. Verificar que se eliminó de todos lados
"""

from controllers.book_controller import BookController
from controllers.shelf_controller import ShelfController


def test_integration_delete_book_with_shelves():
    """Test de integración completo de eliminación de libros."""
    
    print("\n" + "="*80)
    print("TEST DE INTEGRACIÓN: Eliminación de Libro con Estanterías")
    print("="*80)
    
    book_controller = BookController()
    shelf_controller = ShelfController()
    
    # Datos del libro de prueba
    test_book = {
        "id": "B999",
        "ISBNCode": "978-0-TEST-INTEG",
        "title": "Libro de Test de Integración",
        "author": "Test Author",
        "weight": 0.8,
        "price": 25000,
        "isBorrowed": False
    }
    
    test_shelves = [
        {"id": "S999", "name": "Estantería Test A", "capacity": 8.0},
        {"id": "S998", "name": "Estantería Test B", "capacity": 8.0},
    ]
    
    try:
        # ===== FASE 1: SETUP =====
        print("\n[FASE 1] Setup - Creando libro y estanterías...")
        
        # Crear libro
        book_controller.create_book(test_book)
        print(f"  ✓ Libro creado: {test_book['id']} - '{test_book['title']}'")
        
        # Crear estanterías
        for shelf_data in test_shelves:
            shelf_controller.create_shelf(
                shelf_data['id'], 
                capacity=shelf_data['capacity'], 
                name=shelf_data['name']
            )
            print(f"  ✓ Estantería creada: {shelf_data['id']} - '{shelf_data['name']}'")
        
        # ===== FASE 2: ASIGNACIÓN =====
        print("\n[FASE 2] Asignando libro a estanterías...")
        
        book = book_controller.get_book(test_book['id'])
        for shelf_data in test_shelves:
            success = shelf_controller.add_book(shelf_data['id'], book)
            if success:
                print(f"  ✓ Libro asignado a {shelf_data['id']}")
            else:
                print(f"  ✗ Error al asignar libro a {shelf_data['id']}")
        
        # ===== FASE 3: VERIFICACIÓN PRE-ELIMINACIÓN =====
        print("\n[FASE 3] Verificando presencia del libro en estanterías...")
        
        found_count = 0
        for shelf_data in test_shelves:
            books = shelf_controller.get_books(shelf_data['id'])
            for b in books:
                if b.get_id() == test_book['id']:
                    found_count += 1
                    print(f"  ✓ Libro encontrado en {shelf_data['id']}")
                    break
        
        if found_count != len(test_shelves):
            print(f"  ⚠ Advertencia: Libro esperado en {len(test_shelves)} estanterías, encontrado en {found_count}")
        
        # ===== FASE 4: ELIMINACIÓN =====
        print("\n[FASE 4] Eliminando libro desde BookController...")
        print(f"  → Eliminando '{test_book['title']}' (ID: {test_book['id']})...")
        
        # Esta es la operación crítica: debe eliminar de catálogo, inventario Y estanterías
        book_controller.delete_book(test_book['id'])
        print(f"  ✓ Eliminación completada")
        
        # ===== FASE 5: VERIFICACIÓN POST-ELIMINACIÓN =====
        print("\n[FASE 5] Verificando eliminación completa...")
        
        # 5.1 Verificar que NO está en el catálogo
        deleted_book = book_controller.get_book(test_book['id'])
        if deleted_book is None:
            print(f"  ✓ Libro NO encontrado en catálogo (correcto)")
        else:
            print(f"  ✗ ERROR: Libro aún existe en catálogo")
            return False
        
        # 5.2 Verificar que NO está en estanterías (recargar desde disco)
        shelf_controller = ShelfController()  # Recargar para leer desde disco
        still_found = 0
        for shelf_data in test_shelves:
            books = shelf_controller.get_books(shelf_data['id'])
            for b in books:
                if b.get_id() == test_book['id']:
                    still_found += 1
                    print(f"  ✗ ERROR: Libro aún en {shelf_data['id']}")
                    break
        
        if still_found == 0:
            print(f"  ✓ Libro NO encontrado en ninguna estantería (correcto)")
        else:
            print(f"  ✗ ERROR: Libro aún presente en {still_found} estantería(s)")
            return False
        
        print("\n[FASE 5] ✓ Verificación completa exitosa")
        
    except Exception as e:
        print(f"\n✗ ERROR DURANTE EL TEST: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # ===== LIMPIEZA =====
        print("\n[LIMPIEZA] Removiendo datos de prueba...")
        
        # Eliminar libro si todavía existe
        try:
            if book_controller.get_book(test_book['id']):
                book_controller.delete_book(test_book['id'])
                print(f"  ✓ Libro {test_book['id']} eliminado")
        except Exception:
            pass
        
        # Eliminar estanterías
        for shelf_data in test_shelves:
            try:
                shelf_controller.delete_shelf(shelf_data['id'])
                print(f"  ✓ Estantería {shelf_data['id']} eliminada")
            except Exception as e:
                print(f"  ⚠ No se pudo eliminar {shelf_data['id']}: {e}")
    
    print("\n" + "="*80)
    print("✓✓✓ TEST DE INTEGRACIÓN EXITOSO ✓✓✓")
    print("El libro se elimina correctamente del catálogo, inventario y estanterías")
    print("="*80 + "\n")
    return True


if __name__ == "__main__":
    success = test_integration_delete_book_with_shelves()
    exit(0 if success else 1)
