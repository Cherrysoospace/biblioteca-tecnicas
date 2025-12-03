"""
Test para verificar el método get_id() del modelo Shelf.
"""
from models.shelf import Shelf
from models.Books import Book


def test_shelf_get_id():
    """Verifica que el método get_id() funciona correctamente."""
    
    # Crear una estantería con un ID específico
    shelf = Shelf(id="TEST-001", capacity=5.0)
    
    # Verificar que get_id() devuelve el ID correcto
    assert shelf.get_id() == "TEST-001", "El método get_id() no devuelve el ID correcto"
    
    print("✓ get_id() devuelve el ID correcto: TEST-001")
    
    # Crear otra estantería con un ID diferente
    shelf2 = Shelf(id="S999", capacity=8.0)
    assert shelf2.get_id() == "S999", "El método get_id() no funciona para el segundo shelf"
    
    print("✓ get_id() funciona correctamente con diferentes IDs")
    
    # Verificar que el ID es de solo lectura (no debe haber setter)
    assert not hasattr(shelf, 'set_id'), "No debería existir un método set_id() - el ID es inmutable"
    
    print("✓ El ID es de solo lectura (no existe set_id())")
    
    print("\n✅ TODOS LOS TESTS DEL MÉTODO get_id() PASARON")


if __name__ == "__main__":
    test_shelf_get_id()
