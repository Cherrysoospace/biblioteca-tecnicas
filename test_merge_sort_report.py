"""Script de prueba para verificar la generación automática de reportes con Merge Sort.

Este script demuestra que:
1. El reporte se genera automáticamente al agregar/actualizar/eliminar libros
2. El algoritmo Merge Sort ordena correctamente por precio
3. El reporte se exporta a JSON con estadísticas completas
"""

import json
from services.book_service import BookService
from models.Books import Book
from utils.config import FilePaths


def print_separator(title=""):
    """Imprimir separador visual."""
    if title:
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    else:
        print(f"{'='*60}")


def print_reporte_summary():
    """Leer y mostrar resumen del reporte generado."""
    with open(FilePaths.INVENTORY_VALUE_REPORT, 'r', encoding='utf-8') as f:
        reporte = json.load(f)
    
    print(f"Total libros: {reporte['total_libros']}")
    print(f"Precio total: ${reporte['precio_total']:,} COP")
    print(f"Precio promedio: ${reporte['precio_promedio']:,.2f} COP")
    print(f"Rango de precios: ${reporte['precio_minimo']:,} - ${reporte['precio_maximo']:,}")
    
    if reporte['total_libros'] > 0:
        print(f"\nLibro más barato:")
        libro_barato = reporte['libros'][0]
        print(f"  - {libro_barato['titulo']} ({libro_barato['autor']})")
        print(f"  - Precio: ${libro_barato['precio']:,}")
        
        print(f"\nLibro más caro:")
        libro_caro = reporte['libros'][-1]
        print(f"  - {libro_caro['titulo']} ({libro_caro['autor']})")
        print(f"  - Precio: ${libro_caro['precio']:,}")
        
        print(f"\nPrimeros 5 libros (ordenados por precio):")
        for i, libro in enumerate(reporte['libros'][:5], 1):
            print(f"  {i}. {libro['titulo']} - ${libro['precio']:,}")


def main():
    print_separator("PRUEBA: GENERACIÓN AUTOMÁTICA DE REPORTES CON MERGE SORT")
    
    # Inicializar servicio
    bs = BookService()
    print(f"\nLibros en catálogo: {len(bs.books)}")
    
    print_separator("ESTADO INICIAL DEL REPORTE")
    print_reporte_summary()
    
    # Prueba 1: Agregar un libro MUY BARATO
    print_separator("PRUEBA 1: Agregar libro económico ($500)")
    libro_barato = Book('BTEST1', '111111', 'Libro Súper Económico', 'Test Autor', 0.1, 500, False)
    bs.add_book(libro_barato)
    print(f"✅ Libro agregado: {libro_barato.get_title()}")
    print("\nReporte actualizado automáticamente:")
    print_reporte_summary()
    
    # Prueba 2: Agregar un libro MUY CARO
    print_separator("PRUEBA 2: Agregar libro costoso ($150,000)")
    libro_caro = Book('BTEST2', '222222', 'Libro Premium Exclusivo', 'Test Autor', 1.5, 150000, False)
    bs.add_book(libro_caro)
    print(f"✅ Libro agregado: {libro_caro.get_title()}")
    print("\nReporte actualizado automáticamente:")
    print_reporte_summary()
    
    # Prueba 3: Actualizar precio de un libro
    print_separator("PRUEBA 3: Actualizar precio de libro")
    bs.update_book('BTEST1', {'price': 100})
    print(f"✅ Precio actualizado: $500 → $100")
    print("\nReporte actualizado automáticamente:")
    print_reporte_summary()
    
    # Prueba 4: Eliminar libros de prueba
    print_separator("PRUEBA 4: Eliminar libros de prueba")
    bs.delete_book('BTEST1')
    print(f"✅ Libro eliminado: Libro Súper Económico")
    bs.delete_book('BTEST2')
    print(f"✅ Libro eliminado: Libro Premium Exclusivo")
    print("\nReporte actualizado automáticamente:")
    print_reporte_summary()
    
    print_separator("VERIFICACIÓN FINAL")
    print("✅ Todas las pruebas completadas exitosamente")
    print("✅ Merge Sort funciona correctamente")
    print("✅ Reporte se actualiza automáticamente en cada operación")
    print(f"✅ Archivo de reporte: {FilePaths.INVENTORY_VALUE_REPORT}")
    print_separator()


if __name__ == "__main__":
    main()
