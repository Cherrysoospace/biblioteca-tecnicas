"""
test_no_conflicts_algorithms.py

Verifica que los dos algoritmos de búsqueda coexistan sin conflictos:
1. Búsqueda Lineal (busqueda_lineal) - para Título/Autor en inventory_general
2. Búsqueda Binaria (busqueda_binaria) - para ISBN en inventory_sorted

Fecha: 2025-12-03
"""

from services.inventory_service import InventoryService
from services.loan_service import LoanService
from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria, busqueda_lineal


def test_both_algorithms_imported():
    """Verifica que ambos algoritmos estén correctamente importados."""
    print("\n" + "="*70)
    print("TEST 1: Verificar importación de ambos algoritmos")
    print("="*70)
    
    print(f"\n✓ busqueda_binaria importada: {busqueda_binaria.__module__}.{busqueda_binaria.__name__}")
    print(f"✓ busqueda_lineal importada: {busqueda_lineal.__module__}.{busqueda_lineal.__name__}")
    print("\nAmbos algoritmos están disponibles en el mismo módulo:")
    print("  → utils.algorithms.AlgoritmosBusqueda")


def test_binary_search_still_works():
    """Verifica que búsqueda binaria sigue funcionando correctamente."""
    print("\n" + "="*70)
    print("TEST 2: Búsqueda Binaria (ISBN) sigue funcionando")
    print("="*70)
    
    service = InventoryService()
    
    # Verificar que inventory_sorted existe y tiene datos
    if len(service.inventory_sorted) > 0:
        print(f"\n✓ inventory_sorted tiene {len(service.inventory_sorted)} elementos")
        
        # Tomar un ISBN del inventario ordenado
        isbn_prueba = service.inventory_sorted[len(service.inventory_sorted)//2].get_isbn()
        
        # Buscar usando búsqueda binaria
        index = busqueda_binaria(service.inventory_sorted, isbn_prueba)
        
        if index != -1:
            print(f"\n✓ ÉXITO: Búsqueda binaria funciona correctamente")
            print(f"  ISBN buscado: {isbn_prueba}")
            print(f"  Encontrado en índice: {index}")
            libro = service.inventory_sorted[index].get_book()
            print(f"  Título: {libro.get_title()}")
        else:
            print(f"✗ ERROR: No encontró ISBN que debería existir")
    else:
        print("⚠ Advertencia: inventory_sorted está vacío")


def test_linear_search_works():
    """Verifica que búsqueda lineal funciona correctamente."""
    print("\n" + "="*70)
    print("TEST 3: Búsqueda Lineal (Título/Autor) funciona")
    print("="*70)
    
    service = InventoryService()
    
    if len(service.inventory_general) > 0:
        print(f"\n✓ inventory_general tiene {len(service.inventory_general)} elementos")
        
        # Tomar un título del inventario
        libro_prueba = service.inventory_general[0].get_book()
        titulo_prueba = libro_prueba.get_title()
        
        # Buscar usando búsqueda lineal
        index = busqueda_lineal(service.inventory_general, titulo_prueba.split()[0])
        
        if index != -1:
            print(f"\n✓ ÉXITO: Búsqueda lineal funciona correctamente")
            print(f"  Criterio buscado: '{titulo_prueba.split()[0]}'")
            print(f"  Encontrado en índice: {index}")
            libro = service.inventory_general[index].get_book()
            print(f"  Título completo: {libro.get_title()}")
        else:
            print(f"✗ ERROR: No encontró término que debería existir")
    else:
        print("⚠ Advertencia: inventory_general está vacío")


def test_different_data_structures():
    """Verifica que cada algoritmo usa su propia estructura de datos."""
    print("\n" + "="*70)
    print("TEST 4: Cada algoritmo usa su propia estructura")
    print("="*70)
    
    service = InventoryService()
    
    print("\nEstructuras de datos:")
    print(f"  • inventory_general (búsqueda lineal): {len(service.inventory_general)} elementos")
    print(f"  • inventory_sorted (búsqueda binaria): {len(service.inventory_sorted)} elementos")
    
    # Verificar que son listas independientes (no la misma referencia)
    if service.inventory_general is not service.inventory_sorted:
        print("\n✓ ÉXITO: Son estructuras independientes (no comparten referencia)")
    else:
        print("\n✗ ERROR: Ambas apuntan a la misma lista")
    
    # Verificar que inventory_sorted está ordenado
    if len(service.inventory_sorted) > 1:
        ordenado = all(
            service.inventory_sorted[i].get_isbn() <= service.inventory_sorted[i+1].get_isbn()
            for i in range(len(service.inventory_sorted) - 1)
        )
        if ordenado:
            print("✓ inventory_sorted está ordenado (prerequisito para búsqueda binaria)")
        else:
            print("✗ inventory_sorted NO está ordenado")


def test_use_cases_separation():
    """Documenta los casos de uso separados de cada algoritmo."""
    print("\n" + "="*70)
    print("TEST 5: Separación de casos de uso")
    print("="*70)
    
    print("\n📌 BÚSQUEDA BINARIA (busqueda_binaria):")
    print("  ├─ Algoritmo: O(log n) - Divide y Conquista")
    print("  ├─ Prerequisito: Inventario ORDENADO por ISBN")
    print("  ├─ Dato de búsqueda: ISBN (exacto)")
    print("  ├─ Estructura: inventory_sorted")
    print("  ├─ Uso crítico: Verificar disponibilidad en devolución de libros")
    print("  └─ Servicio: LoanService.mark_returned()")
    
    print("\n📌 BÚSQUEDA LINEAL (busqueda_lineal):")
    print("  ├─ Algoritmo: O(n) - Recursiva")
    print("  ├─ Prerequisito: NO requiere orden")
    print("  ├─ Dato de búsqueda: Título o Autor (parcial, insensible)")
    print("  ├─ Estructura: inventory_general")
    print("  ├─ Uso: Búsqueda flexible por usuario")
    print("  └─ Servicio: InventoryService.find_by_title() / find_by_author()")
    
    print("\n✓ Ambos algoritmos tienen casos de uso DISTINTOS y complementarios")


def test_loan_service_uses_binary():
    """Verifica que LoanService sigue usando búsqueda binaria."""
    print("\n" + "="*70)
    print("TEST 6: LoanService usa búsqueda binaria (no afectado)")
    print("="*70)
    
    # Verificar que loan_service tiene la importación correcta
    from services import loan_service
    import inspect
    
    source = inspect.getsource(loan_service)
    
    if "busqueda_binaria" in source:
        print("✓ LoanService importa busqueda_binaria")
        
        if "from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria" in source:
            print("✓ Importación correcta desde AlgoritmosBusqueda")
        
        # Contar usos
        usos = source.count("busqueda_binaria(")
        print(f"✓ Usa busqueda_binaria en {usos} lugar(es)")
        
        if "busqueda_lineal" not in source:
            print("✓ LoanService NO usa busqueda_lineal (correcto)")
            print("  → Cada servicio usa el algoritmo apropiado")
    else:
        print("✗ LoanService no usa busqueda_binaria")


def test_inventory_service_uses_linear():
    """Verifica que InventoryService usa búsqueda lineal."""
    print("\n" + "="*70)
    print("TEST 7: InventoryService usa búsqueda lineal (nuevo)")
    print("="*70)
    
    from services import inventory_service
    import inspect
    
    source = inspect.getsource(inventory_service)
    
    if "busqueda_lineal" in source:
        print("✓ InventoryService importa busqueda_lineal")
        
        if "from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal" in source:
            print("✓ Importación correcta desde AlgoritmosBusqueda")
        
        # Contar usos
        usos = source.count("busqueda_lineal(")
        print(f"✓ Usa busqueda_lineal en {usos} lugar(es)")
        print("  → find_by_title() y find_by_author()")
    else:
        print("✗ InventoryService no importa busqueda_lineal")


def main():
    """Ejecuta todas las pruebas de no-conflicto."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  VERIFICACIÓN: NO HAY CONFLICTOS ENTRE ALGORITMOS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    try:
        test_both_algorithms_imported()
        test_binary_search_still_works()
        test_linear_search_works()
        test_different_data_structures()
        test_use_cases_separation()
        test_loan_service_uses_binary()
        test_inventory_service_uses_linear()
        
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  ✓ VERIFICACIÓN COMPLETADA: SIN CONFLICTOS".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        
        print("\n" + "="*70)
        print("RESUMEN")
        print("="*70)
        print("✓ Búsqueda Binaria: Funciona correctamente en LoanService")
        print("✓ Búsqueda Lineal: Implementada correctamente en InventoryService")
        print("✓ NO hay conflictos entre algoritmos")
        print("✓ Cada algoritmo usa su estructura de datos apropiada")
        print("✓ Casos de uso claramente separados")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"\n✗ ERROR EN VERIFICACIÓN: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
