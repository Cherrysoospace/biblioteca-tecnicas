"""
Demo interactiva de búsqueda lineal

Este programa demuestra el algoritmo de búsqueda lineal recursiva
implementado para buscar libros por título o autor.

Características:
- Búsqueda recursiva O(n)
- Insensible a mayúsculas y acentos
- Búsqueda parcial (no necesita título completo)

Fecha: 2025-12-03
"""

from services.inventory_service import InventoryService


def mostrar_resultados(resultados, criterio):
    """Muestra los resultados de búsqueda de forma formateada."""
    if not resultados:
        print(f"\n❌ No se encontraron libros con '{criterio}'")
        return
    
    print(f"\n✅ Se encontraron {len(resultados)} libro(s) con '{criterio}':")
    print("="*70)
    
    for i, inv in enumerate(resultados, 1):
        libro = inv.get_book()
        print(f"\n📚 {i}. {libro.get_title()}")
        print(f"   👤 Autor: {libro.get_author()}")
        print(f"   📖 ISBN: {libro.get_ISBNCode()}")
        print(f"   💰 Precio: ${libro.get_price():,} COP")
        print(f"   📦 Stock disponible: {inv.get_stock()} copias")


def buscar_por_titulo(service):
    """Función para buscar libros por título."""
    print("\n" + "─"*70)
    print("🔍 BÚSQUEDA POR TÍTULO")
    print("─"*70)
    print("💡 Puedes buscar por título completo o parcial")
    print("💡 No importan mayúsculas ni acentos")
    print("\nEjemplos: 'odyssey', 'quijote', 'programacion', 'the'")
    
    titulo = input("\n📝 Introduce el título a buscar: ").strip()
    
    if not titulo:
        print("⚠️  No introdujiste ningún título")
        return
    
    print(f"\n⏳ Buscando '{titulo}' usando búsqueda lineal recursiva...")
    resultados = service.find_by_title(titulo)
    mostrar_resultados(resultados, titulo)


def buscar_por_autor(service):
    """Función para buscar libros por autor."""
    print("\n" + "─"*70)
    print("🔍 BÚSQUEDA POR AUTOR")
    print("─"*70)
    print("💡 Puedes buscar por nombre completo o parcial")
    print("💡 No importan mayúsculas ni acentos")
    print("\nEjemplos: 'garcía', 'orwell', 'homer', 'cervantes'")
    
    autor = input("\n📝 Introduce el autor a buscar: ").strip()
    
    if not autor:
        print("⚠️  No introdujiste ningún autor")
        return
    
    print(f"\n⏳ Buscando '{autor}' usando búsqueda lineal recursiva...")
    resultados = service.find_by_author(autor)
    mostrar_resultados(resultados, autor)


def mostrar_estadisticas(service):
    """Muestra estadísticas del inventario."""
    print("\n" + "─"*70)
    print("📊 ESTADÍSTICAS DEL INVENTARIO")
    print("─"*70)
    
    total_grupos = len(service.inventory_general)
    total_libros = sum(inv.get_stock() for inv in service.inventory_general)
    
    print(f"\n📚 Total de grupos de libros (ISBN únicos): {total_grupos}")
    print(f"📖 Total de copias en inventario: {total_libros}")
    
    if total_grupos > 0:
        print("\n🎯 Primeros 5 libros en el inventario:")
        for i, inv in enumerate(service.inventory_general[:5], 1):
            libro = inv.get_book()
            print(f"   {i}. {libro.get_title()} - {libro.get_author()}")


def mostrar_menu():
    """Muestra el menú principal."""
    print("\n" + "="*70)
    print("📚 DEMOSTRACIÓN DE BÚSQUEDA LINEAL RECURSIVA")
    print("="*70)
    print("\nOpciones:")
    print("  1️⃣  Buscar por título")
    print("  2️⃣  Buscar por autor")
    print("  3️⃣  Ver estadísticas del inventario")
    print("  4️⃣  Salir")
    print("="*70)


def main():
    """Función principal del programa."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  🔍 DEMO: BÚSQUEDA LINEAL RECURSIVA".center(68) + "█")
    print("█" + "  Sistema de Gestión de Bibliotecas".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    print("\n⏳ Cargando inventario...")
    try:
        service = InventoryService()
        print("✅ Inventario cargado correctamente")
    except Exception as e:
        print(f"❌ Error al cargar inventario: {e}")
        return
    
    while True:
        mostrar_menu()
        opcion = input("\n👉 Elige una opción (1-4): ").strip()
        
        if opcion == "1":
            buscar_por_titulo(service)
        
        elif opcion == "2":
            buscar_por_autor(service)
        
        elif opcion == "3":
            mostrar_estadisticas(service)
        
        elif opcion == "4":
            print("\n" + "─"*70)
            print("👋 ¡Gracias por usar el sistema de búsqueda!")
            print("🎓 Búsqueda Lineal Recursiva - O(n)")
            print("─"*70)
            print()
            break
        
        else:
            print("\n❌ Opción inválida. Por favor elige un número entre 1 y 4.")
        
        # Pausa antes de volver al menú
        input("\n⏎ Presiona Enter para continuar...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario. ¡Hasta luego!")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
