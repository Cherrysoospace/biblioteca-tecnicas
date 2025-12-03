"""
Test para verificar que el reporte de inventario se actualiza correctamente
después de crear, modificar y eliminar libros.
"""
from services.report_service import ReportService
from controllers.book_controller import BookController

def contar_libros_en_reporte():
    """Cuenta los libros en el reporte actual"""
    rs = ReportService()
    reporte = rs.generate_inventory_value_report()
    return reporte['total_books']  # Actualizado a 'total_books' (inglés)

print("\n=== TEST: AUTO-ACTUALIZACIÓN DE REPORTE ===\n")

# 1. Contar libros iniciales
libros_inicial = contar_libros_en_reporte()
print(f"📊 Libros en reporte inicial: {libros_inicial}")

# 2. Crear un libro nuevo
print(f"\n→ Creando nuevo libro TEST-FINAL...")
controller = BookController()
data = {
    "ISBNCode": "TEST999999",
    "title": "Libro de Prueba Final",
    "author": "Test Author",
    "edition": "1ra Edición",
    "editorial": "Test Editorial",
    "year": 2024,
    "price": 75000,
    "weight": 0.5,
    "stock": 2
}
book_id = controller.create_book(data)
print(f"✓ Libro creado: {book_id}")

# 3. Contar libros después de crear
libros_despues_crear = contar_libros_en_reporte()
print(f"📊 Libros después de crear: {libros_despues_crear}")

# 4. Verificar
if libros_despues_crear == libros_inicial + 1:  # +1 porque add_item agrega 1 copia
    print(f"✅ ÉXITO: Reporte se actualizó correctamente (+1 libro)")
else:
    print(f"❌ ERROR: Esperaba {libros_inicial + 1}, obtuvo {libros_despues_crear}")

# 5. Eliminar el libro creado
print(f"\n→ Eliminando libro {book_id}...")
controller.delete_book(book_id)
print(f"✓ Libro eliminado")

# 6. Contar después de eliminar
libros_despues_eliminar = contar_libros_en_reporte()
print(f"📊 Libros después de eliminar: {libros_despues_eliminar}")

# 7. Verificar que volvió al original
if libros_despues_eliminar == libros_inicial:
    print(f"✅ ÉXITO: Reporte volvió al estado original")
else:
    print(f"❌ ERROR: Esperaba {libros_inicial}, obtuvo {libros_despues_eliminar}")

print("\n=== FIN DEL TEST ===\n")
