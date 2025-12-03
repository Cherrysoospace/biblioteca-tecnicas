"""
Demostración del método get_id() agregado al modelo Shelf.

Este script muestra cómo usar el nuevo método get_id() de forma limpia
en lugar de acceder directamente al atributo privado mediante name mangling.
"""

from models.shelf import Shelf
from models.Books import Book


def demo_get_id():
    print("="*70)
    print("DEMOSTRACIÓN DEL MÉTODO get_id() EN SHELF")
    print("="*70)
    
    # Crear una estantería
    shelf = Shelf(id="S001", capacity=8.0)
    shelf.set_name("Estantería de Ficción")
    
    print("\n1. CREACIÓN DE ESTANTERÍA")
    print(f"   - ID (usando get_id()): {shelf.get_id()}")
    print(f"   - Nombre (usando get_name()): {shelf.get_name()}")
    print(f"   - Capacidad: {shelf.capacity} kg")
    
    # Agregar algunos libros
    book1 = Book('B001', '978-1234567890', 'Libro 1', 'Autor 1', 0.5, 100, False)
    book2 = Book('B002', '978-0987654321', 'Libro 2', 'Autor 2', 0.8, 150, False)
    
    print("\n2. ACCESO AL ID EN DIFERENTES CONTEXTOS")
    print(f"   - ID para búsqueda: {shelf.get_id()}")
    print(f"   - ID para logging: Shelf {shelf.get_id()} tiene capacidad de {shelf.capacity}kg")
    print(f"   - ID para serialización: {{'id': '{shelf.get_id()}', 'name': '{shelf.get_name()}'}}")
    
    print("\n3. COMPARACIÓN: ANTES vs DESPUÉS")
    print("   ANTES (name mangling - no recomendado):")
    print("   └─> shelf_id = shelf._Shelf__id")
    print()
    print("   DESPUÉS (método público - recomendado):")
    print("   └─> shelf_id = shelf.get_id()")
    
    print("\n4. VENTAJAS DEL MÉTODO get_id()")
    print("   ✓ Más limpio y legible")
    print("   ✓ Consistente con get_name() y set_name()")
    print("   ✓ No depende de la implementación interna")
    print("   ✓ Encapsula el acceso al atributo privado")
    print("   ✓ Facilita el mantenimiento del código")
    
    print("\n5. INMUTABILIDAD DEL ID")
    print("   - El ID es de solo lectura (no existe set_id())")
    print("   - Esto garantiza que el identificador no cambie después de la creación")
    print("   - Es una buena práctica para mantener la integridad de los datos")
    
    print("\n" + "="*70)
    print("✅ DEMOSTRACIÓN COMPLETADA")
    print("="*70)


if __name__ == "__main__":
    demo_get_id()
