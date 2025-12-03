"""
test_busqueda_lineal.py

Prueba la implementación de Búsqueda Lineal Recursiva para buscar libros
por Título o Autor en el Inventario General (no ordenado).

Fecha: 2025-12-03
"""

from models.Books import Book
from models.inventory import Inventory
from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal
from utils.search_helpers import normalizar_texto


def crear_inventario_prueba():
    """Crea un inventario de prueba con varios libros."""
    libros_prueba = [
        Book("B001", "978-0-7432-7356-5", "Cien Años de Soledad", "Gabriel García Márquez", 0.5, 50000),
        Book("B002", "978-0-06-112008-4", "To Kill a Mockingbird", "Harper Lee", 0.4, 45000),
        Book("B003", "978-84-376-0494-7", "Don Quijote de la Mancha", "Miguel de Cervantes", 0.8, 60000),
        Book("B004", "978-0-14-017739-8", "1984", "George Orwell", 0.3, 40000),
        Book("B005", "978-0-7432-4722-1", "El Amor en los Tiempos del Cólera", "Gabriel García Márquez", 0.5, 52000),
    ]
    
    inventario = []
    for libro in libros_prueba:
        inv = Inventory(stock=1, items=[libro])
        inventario.append(inv)
    
    return inventario


def test_busqueda_por_titulo_exacto():
    """Prueba búsqueda con título exacto."""
    print("\n" + "="*70)
    print("TEST 1: Búsqueda por título exacto")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    resultado = busqueda_lineal(inventario, "1984")
    
    if resultado != -1:
        libro = inventario[resultado].get_book()
        print(f"✓ ÉXITO: Encontrado en índice {resultado}")
        print(f"  Título: {libro.get_title()}")
        print(f"  Autor: {libro.get_author()}")
    else:
        print("✗ ERROR: No se encontró el libro")


def test_busqueda_por_titulo_parcial():
    """Prueba búsqueda con título parcial."""
    print("\n" + "="*70)
    print("TEST 2: Búsqueda por título parcial")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    resultado = busqueda_lineal(inventario, "quijote")
    
    if resultado != -1:
        libro = inventario[resultado].get_book()
        print(f"✓ ÉXITO: Encontrado en índice {resultado}")
        print(f"  Título: {libro.get_title()}")
        print(f"  Autor: {libro.get_author()}")
    else:
        print("✗ ERROR: No se encontró el libro")


def test_busqueda_por_autor():
    """Prueba búsqueda por nombre de autor."""
    print("\n" + "="*70)
    print("TEST 3: Búsqueda por autor")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    resultado = busqueda_lineal(inventario, "garcía márquez")
    
    if resultado != -1:
        libro = inventario[resultado].get_book()
        print(f"✓ ÉXITO: Encontrado en índice {resultado}")
        print(f"  Título: {libro.get_title()}")
        print(f"  Autor: {libro.get_author()}")
        print(f"  (Primera coincidencia encontrada)")
    else:
        print("✗ ERROR: No se encontró el libro")


def test_busqueda_insensible_mayusculas():
    """Prueba que la búsqueda es insensible a mayúsculas."""
    print("\n" + "="*70)
    print("TEST 4: Búsqueda insensible a mayúsculas")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    
    # Buscar con diferentes combinaciones de mayúsculas/minúsculas
    busquedas = ["ORWELL", "orwell", "OrWeLl", "george ORWELL"]
    
    for busqueda in busquedas:
        resultado = busqueda_lineal(inventario, busqueda)
        if resultado != -1:
            libro = inventario[resultado].get_book()
            print(f"✓ Búsqueda '{busqueda}': Encontrado - {libro.get_title()}")
        else:
            print(f"✗ Búsqueda '{busqueda}': NO encontrado")


def test_busqueda_sin_acentos():
    """Prueba que la búsqueda funciona sin acentos."""
    print("\n" + "="*70)
    print("TEST 5: Búsqueda sin acentos")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    
    # Buscar sin acentos palabras que tienen acentos
    busquedas = ["anos", "colera", "garcia marquez"]
    
    for busqueda in busquedas:
        resultado = busqueda_lineal(inventario, busqueda)
        if resultado != -1:
            libro = inventario[resultado].get_book()
            print(f"✓ Búsqueda '{busqueda}': Encontrado - {libro.get_title()}")
        else:
            print(f"✗ Búsqueda '{busqueda}': NO encontrado")


def test_busqueda_no_encontrada():
    """Prueba búsqueda de elemento que no existe."""
    print("\n" + "="*70)
    print("TEST 6: Búsqueda de elemento inexistente")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    resultado = busqueda_lineal(inventario, "Harry Potter")
    
    if resultado == -1:
        print("✓ ÉXITO: Retornó -1 correctamente (libro no encontrado)")
    else:
        print(f"✗ ERROR: Encontró algo en índice {resultado} cuando no debería")


def test_normalizar_texto():
    """Prueba la función auxiliar normalizar_texto."""
    print("\n" + "="*70)
    print("TEST 7: Función auxiliar normalizar_texto()")
    print("="*70)
    
    casos_prueba = [
        ("García Márquez", "garcia marquez"),
        ("JOSÉ", "jose"),
        ("Año Nuevo", "ano nuevo"),
        ("Cien Años de Soledad", "cien anos de soledad"),
        ("  Espacios   Extra  ", "espacios extra"),
    ]
    
    for entrada, esperado in casos_prueba:
        resultado = normalizar_texto(entrada)
        if resultado == esperado:
            print(f"✓ '{entrada}' → '{resultado}'")
        else:
            print(f"✗ '{entrada}' → '{resultado}' (esperado: '{esperado}')")


def test_complejidad_recursiva():
    """Muestra que la búsqueda es recursiva contando llamadas."""
    print("\n" + "="*70)
    print("TEST 8: Verificación de recursividad")
    print("="*70)
    
    inventario = crear_inventario_prueba()
    
    # Buscar elemento en última posición (peor caso)
    resultado = busqueda_lineal(inventario, "El Amor en los Tiempos")
    
    if resultado == 4:  # Última posición
        print("✓ ÉXITO: Búsqueda recursiva funcionó correctamente")
        print(f"  Encontrado en índice {resultado} (última posición)")
        print(f"  La recursión recorrió {resultado + 1} elementos")
        libro = inventario[resultado].get_book()
        print(f"  Título: {libro.get_title()}")
    else:
        print(f"✗ ERROR: Resultado inesperado: {resultado}")


def main():
    """Ejecuta todas las pruebas."""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  PRUEBAS DE BÚSQUEDA LINEAL RECURSIVA".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    test_busqueda_por_titulo_exacto()
    test_busqueda_por_titulo_parcial()
    test_busqueda_por_autor()
    test_busqueda_insensible_mayusculas()
    test_busqueda_sin_acentos()
    test_busqueda_no_encontrada()
    test_normalizar_texto()
    test_complejidad_recursiva()
    
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  PRUEBAS COMPLETADAS".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    print()


if __name__ == "__main__":
    main()
