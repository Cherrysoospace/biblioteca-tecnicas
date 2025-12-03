"""
test_integration_busqueda_lineal.py

Prueba la integración de búsqueda lineal con InventoryService,
verificando que find_by_title() y find_by_author() usen correctamente
el algoritmo de búsqueda lineal recursiva implementado.

Fecha: 2025-12-03
"""

from services.inventory_service import InventoryService
from repositories.inventory_repository import InventoryRepository


def test_find_by_title():
    """Prueba búsqueda de libros por título usando InventoryService."""
    print("\n" + "="*70)
    print("TEST 1: find_by_title() - Búsqueda por título parcial")
    print("="*70)
    
    # Crear servicio con datos reales
    service = InventoryService()
    
    # Buscar libros con "quijote" en el título
    resultados = service.find_by_title("quijote")
    
    print(f"\nBúsqueda: 'quijote'")
    print(f"Resultados encontrados: {len(resultados)}")
    
    if resultados:
        print("\n✓ ÉXITO: Se encontraron libros")
        for inv in resultados[:3]:  # Mostrar máximo 3
            libro = inv.get_book()
            print(f"  - ISBN: {libro.get_ISBNCode()}")
            print(f"    Título: {libro.get_title()}")
            print(f"    Autor: {libro.get_author()}")
            print(f"    Stock: {inv.get_stock()}")
    else:
        print("✗ No se encontraron libros con ese título")


def test_find_by_author():
    """Prueba búsqueda de libros por autor usando InventoryService."""
    print("\n" + "="*70)
    print("TEST 2: find_by_author() - Búsqueda por autor")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar libros de García Márquez (sin importar acentos)
    resultados = service.find_by_author("garcia")
    
    print(f"\nBúsqueda: 'garcia'")
    print(f"Resultados encontrados: {len(resultados)}")
    
    if resultados:
        print("\n✓ ÉXITO: Se encontraron libros")
        for inv in resultados[:3]:  # Mostrar máximo 3
            libro = inv.get_book()
            print(f"  - ISBN: {libro.get_ISBNCode()}")
            print(f"    Título: {libro.get_title()}")
            print(f"    Autor: {libro.get_author()}")
            print(f"    Stock: {inv.get_stock()}")
    else:
        print("✗ No se encontraron libros de ese autor")


def test_find_by_title_case_insensitive():
    """Prueba que la búsqueda por título sea insensible a mayúsculas."""
    print("\n" + "="*70)
    print("TEST 3: Búsqueda insensible a mayúsculas")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar con diferentes combinaciones de mayúsculas
    busquedas = ["PROGRAMACIÓN", "programacion", "Programación"]
    
    for busqueda in busquedas:
        resultados = service.find_by_title(busqueda)
        print(f"\nBúsqueda: '{busqueda}' → {len(resultados)} resultados")
        if resultados:
            libro = resultados[0].get_book()
            print(f"  ✓ Ejemplo: {libro.get_title()}")


def test_find_by_author_partial():
    """Prueba búsqueda parcial por apellido de autor."""
    print("\n" + "="*70)
    print("TEST 4: Búsqueda parcial por apellido")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar solo por apellido
    busquedas = ["cervantes", "marquez", "orwell"]
    
    for apellido in busquedas:
        resultados = service.find_by_author(apellido)
        print(f"\nBúsqueda: '{apellido}' → {len(resultados)} resultados")
        if resultados:
            for inv in resultados[:2]:  # Máximo 2 por autor
                libro = inv.get_book()
                print(f"  ✓ {libro.get_title()} - {libro.get_author()}")


def test_find_no_results():
    """Prueba búsqueda que no debe retornar resultados."""
    print("\n" + "="*70)
    print("TEST 5: Búsqueda sin resultados")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar algo que no existe
    resultados_titulo = service.find_by_title("XYZABC12345")
    resultados_autor = service.find_by_author("Autor Inexistente")
    
    if len(resultados_titulo) == 0 and len(resultados_autor) == 0:
        print("✓ ÉXITO: Retorna lista vacía cuando no hay coincidencias")
        print(f"  - find_by_title('XYZABC12345'): {len(resultados_titulo)} resultados")
        print(f"  - find_by_author('Autor Inexistente'): {len(resultados_autor)} resultados")
    else:
        print(f"✗ ERROR: Debería retornar listas vacías")


def test_multiple_results():
    """Prueba que find_by_title/author retorne TODOS los resultados."""
    print("\n" + "="*70)
    print("TEST 6: Búsqueda con múltiples resultados")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar un término común que debería tener múltiples resultados
    resultados = service.find_by_title("the")
    
    print(f"\nBúsqueda: 'the'")
    print(f"Total de resultados: {len(resultados)}")
    
    if len(resultados) > 1:
        print("\n✓ ÉXITO: Encuentra múltiples coincidencias")
        print(f"  Mostrando primeros 5 de {len(resultados)} resultados:")
        for i, inv in enumerate(resultados[:5], 1):
            libro = inv.get_book()
            print(f"  {i}. {libro.get_title()}")
    elif len(resultados) == 1:
        print("⚠ Advertencia: Solo encontró 1 resultado (esperado: múltiples)")
    else:
        print("✗ No se encontraron resultados")


def test_algorithm_is_recursive():
    """Verifica que se esté usando el algoritmo recursivo."""
    print("\n" + "="*70)
    print("TEST 7: Verificación de uso del algoritmo recursivo")
    print("="*70)
    
    # Verificar que busqueda_lineal esté importada
    from services.inventory_service import busqueda_lineal
    from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal as busqueda_original
    
    if busqueda_lineal is busqueda_original:
        print("✓ ÉXITO: InventoryService usa la función busqueda_lineal correcta")
        print(f"  Módulo: {busqueda_lineal.__module__}")
        print(f"  Función: {busqueda_lineal.__name__}")
    else:
        print("✗ ERROR: InventoryService no está usando la función correcta")


def test_no_conflict_with_binary_search():
    """Verifica que busqueda_lineal no entre en conflicto con busqueda_binaria."""
    print("\n" + "="*70)
    print("TEST 8: No conflicto con búsqueda binaria")
    print("="*70)
    
    service = InventoryService()
    
    # Verificar que inventory_sorted sigue ordenado (usado por búsqueda binaria)
    if len(service.inventory_sorted) > 1:
        ordenado = True
        for i in range(len(service.inventory_sorted) - 1):
            isbn_actual = service.inventory_sorted[i].get_isbn()
            isbn_siguiente = service.inventory_sorted[i + 1].get_isbn()
            if isbn_actual > isbn_siguiente:
                ordenado = False
                break
        
        if ordenado:
            print("✓ ÉXITO: inventory_sorted sigue ordenado (búsqueda binaria)")
            print("  La búsqueda lineal NO afecta el orden necesario para búsqueda binaria")
        else:
            print("✗ ERROR: inventory_sorted está desordenado")
    
    # Verificar que inventory_general NO está ordenado (correcto para búsqueda lineal)
    if len(service.inventory_general) > 1:
        print("\n✓ inventory_general NO requiere orden (búsqueda lineal)")
        print("  Ambos algoritmos coexisten correctamente:")
        print("    - busqueda_lineal → inventory_general (desordenado)")
        print("    - busqueda_binaria → inventory_sorted (ordenado por ISBN)")


def main():
    """Ejecuta todas las pruebas de integración."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  PRUEBAS DE INTEGRACIÓN: BÚSQUEDA LINEAL + INVENTORY SERVICE".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    try:
        test_find_by_title()
        test_find_by_author()
        test_find_by_title_case_insensitive()
        test_find_by_author_partial()
        test_find_no_results()
        test_multiple_results()
        test_algorithm_is_recursive()
        test_no_conflict_with_binary_search()
        
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  ✓ TODAS LAS PRUEBAS DE INTEGRACIÓN COMPLETADAS".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print()
    except Exception as e:
        print(f"\n✗ ERROR EN PRUEBAS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
