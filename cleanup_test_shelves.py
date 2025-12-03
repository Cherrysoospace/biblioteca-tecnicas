"""Script para limpiar estanterías de prueba."""

from controllers.shelf_controller import ShelfController

def clean_test_shelves():
    """Eliminar todas las estanterías que comienzan con TEST_"""
    controller = ShelfController()
    shelves = controller.list_shelves()
    
    test_shelves = [s for s in shelves if s.get_id().startswith("TEST_")]
    
    if not test_shelves:
        print("No hay estanterías de prueba para limpiar.")
        return
    
    print(f"Encontradas {len(test_shelves)} estanterías de prueba:")
    for shelf in test_shelves:
        print(f"  - {shelf.get_id()}: {shelf.get_name()}")
    
    for shelf in test_shelves:
        try:
            controller.delete_shelf(shelf.get_id())
            print(f"✓ Eliminada: {shelf.get_id()}")
        except Exception as e:
            print(f"✗ Error al eliminar {shelf.get_id()}: {e}")
    
    print("\nLimpieza completada.")

if __name__ == "__main__":
    clean_test_shelves()
