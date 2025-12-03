"""Test rápido para verificar que busqueda_binaria funciona correctamente."""

from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria
from services.inventory_service import InventoryService

print("=== TEST: BÚSQUEDA BINARIA ===\n")

# 1. Cargar inventario ordenado
inv_service = InventoryService()
inventario = inv_service.inventory_sorted

print(f"Total de inventarios cargados: {len(inventario)}")

if len(inventario) == 0:
    print("⚠️ No hay inventarios para probar")
else:
    # 2. Probar búsqueda del primer elemento
    isbn_primero = inventario[0].get_isbn()
    pos = busqueda_binaria(inventario, isbn_primero)
    print(f"\n→ Buscando primer ISBN: {isbn_primero}")
    print(f"   Encontrado en posición: {pos}")
    print(f"   ✅ CORRECTO" if pos == 0 else f"   ❌ ERROR: esperaba 0")
    
    # 3. Probar búsqueda del último elemento
    isbn_ultimo = inventario[-1].get_isbn()
    pos = busqueda_binaria(inventario, isbn_ultimo)
    print(f"\n→ Buscando último ISBN: {isbn_ultimo}")
    print(f"   Encontrado en posición: {pos}")
    print(f"   ✅ CORRECTO" if pos == len(inventario) - 1 else f"   ❌ ERROR: esperaba {len(inventario) - 1}")
    
    # 4. Probar búsqueda de elemento del medio
    if len(inventario) > 2:
        mid_idx = len(inventario) // 2
        isbn_medio = inventario[mid_idx].get_isbn()
        pos = busqueda_binaria(inventario, isbn_medio)
        print(f"\n→ Buscando ISBN del medio: {isbn_medio}")
        print(f"   Encontrado en posición: {pos}")
        print(f"   ✅ CORRECTO" if pos == mid_idx else f"   ❌ ERROR: esperaba {mid_idx}")
    
    # 5. Probar búsqueda de ISBN inexistente
    isbn_falso = "ISBN-NO-EXISTE-999"
    pos = busqueda_binaria(inventario, isbn_falso)
    print(f"\n→ Buscando ISBN inexistente: {isbn_falso}")
    print(f"   Resultado: {pos}")
    print(f"   ✅ CORRECTO (retorna -1)" if pos == -1 else f"   ❌ ERROR: debería retornar -1")

print("\n=== FIN DEL TEST ===")
