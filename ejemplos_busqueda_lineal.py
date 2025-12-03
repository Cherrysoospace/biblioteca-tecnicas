"""
Ejemplo rápido de uso de búsqueda lineal
Ejecuta este archivo para ver ejemplos de búsqueda
"""

from services.inventory_service import InventoryService


def ejemplo_basico():
    """Ejemplo básico de búsqueda por título."""
    print("\n" + "="*70)
    print("EJEMPLO 1: Búsqueda por título parcial")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar libros con "the" en el título
    print("\n🔍 Buscando libros con 'the' en el título...")
    resultados = service.find_by_title("the")
    
    print(f"✅ Encontrados: {len(resultados)} libros\n")
    
    # Mostrar primeros 5
    for i, inv in enumerate(resultados[:5], 1):
        libro = inv.get_book()
        print(f"{i}. {libro.get_title()}")
        print(f"   Autor: {libro.get_author()}")
        print()


def ejemplo_autor():
    """Ejemplo de búsqueda por autor."""
    print("\n" + "="*70)
    print("EJEMPLO 2: Búsqueda por autor")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar por apellido
    print("\n🔍 Buscando libros de autores con 'orwell'...")
    resultados = service.find_by_author("orwell")
    
    print(f"✅ Encontrados: {len(resultados)} libros\n")
    
    for inv in resultados:
        libro = inv.get_book()
        print(f"📚 {libro.get_title()}")
        print(f"   👤 {libro.get_author()}")
        print(f"   📖 {libro.get_ISBNCode()}")
        print()


def ejemplo_insensible_mayusculas():
    """Ejemplo de búsqueda insensible a mayúsculas."""
    print("\n" + "="*70)
    print("EJEMPLO 3: Búsqueda insensible a mayúsculas")
    print("="*70)
    
    service = InventoryService()
    
    # Probar diferentes variaciones
    busquedas = ["ODYSSEY", "odyssey", "OdYsSeY"]
    
    for busqueda in busquedas:
        print(f"\n🔍 Buscando '{busqueda}'...")
        resultados = service.find_by_title(busqueda)
        if resultados:
            libro = resultados[0].get_book()
            print(f"   ✅ Encontrado: {libro.get_title()}")
        else:
            print(f"   ❌ No encontrado")


def ejemplo_sin_acentos():
    """Ejemplo de búsqueda sin acentos."""
    print("\n" + "="*70)
    print("EJEMPLO 4: Búsqueda sin acentos")
    print("="*70)
    
    service = InventoryService()
    
    # Buscar sin acentos palabras que tienen acentos
    print("\n🔍 Buscando 'garcia' (sin acento, buscará García)...")
    resultados = service.find_by_author("garcia")
    
    if resultados:
        print(f"✅ Encontrados: {len(resultados)} libros\n")
        for inv in resultados[:3]:
            libro = inv.get_book()
            print(f"📚 {libro.get_title()}")
            print(f"   👤 {libro.get_author()}")
            print()
    else:
        print("❌ No se encontraron libros")


def ejemplo_comparacion():
    """Compara búsqueda lineal vs búsqueda por ISBN exacto."""
    print("\n" + "="*70)
    print("EJEMPLO 5: Comparación de algoritmos")
    print("="*70)
    
    service = InventoryService()
    
    print("\n📌 BÚSQUEDA LINEAL (Título/Autor):")
    print("   ✓ Búsqueda parcial: 'odyss' encuentra 'The Odyssey'")
    print("   ✓ Insensible a mayúsculas: 'ODYSSEY' = 'odyssey'")
    print("   ✓ Sin acentos: 'garcia' encuentra 'García'")
    print("   ✓ NO requiere ordenamiento")
    print("   ✓ Complejidad: O(n)")
    
    print("\n📌 BÚSQUEDA BINARIA (ISBN):")
    print("   ✓ Búsqueda exacta: Solo ISBN completo")
    print("   ✓ Requiere lista ordenada")
    print("   ✓ Más rápida: O(log n)")
    print("   ✓ Usada en devolución de libros")
    
    print("\n💡 Ambos algoritmos coexisten sin conflictos")


def main():
    """Ejecuta todos los ejemplos."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  EJEMPLOS DE BÚSQUEDA LINEAL RECURSIVA".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n⏳ Cargando inventario...")
    
    try:
        ejemplo_basico()
        ejemplo_autor()
        ejemplo_insensible_mayusculas()
        ejemplo_sin_acentos()
        ejemplo_comparacion()
        
        print("\n" + "█"*70)
        print("█" + " "*68 + "█")
        print("█" + "  ✅ EJEMPLOS COMPLETADOS".center(68) + "█")
        print("█" + " "*68 + "█")
        print("█"*70)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
