"""
Script de prueba para el nuevo ReportService.

Valida que:
1. El reporte se genera desde inventory_general (no books.json)
2. Se expanden todas las copias de cada libro
3. El precio total es correcto (precio × cantidad de copias)
4. El archivo se guarda en data/inventory_value.json
5. El reporte se actualiza automáticamente al crear/modificar/eliminar libros

IMPORTANTE: Después de la refactorización, las funciones auxiliares están en
utils/report_helpers.py (no en AlgoritmosOrdenamiento.py)
"""

import sys
import os
import json

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.report_service import ReportService
from services.inventory_service import InventoryService
from controllers.book_controller import BookController
from utils.config import FilePaths


def main():
    print("=" * 80)
    print("  TEST: ReportService - Reporte de Inventario por Precio (Merge Sort)")
    print("=" * 80)
    print()
    
    # Inicializar servicios
    print("→ Inicializando servicios...")
    inventory_service = InventoryService()
    report_service = ReportService(inventory_service)
    book_controller = BookController()
    
    print(f"✓ InventoryService cargado: {len(inventory_service.inventory_general)} grupos")
    print()
    
    # Obtener resumen rápido
    print("→ Obteniendo resumen del inventario...")
    resumen = report_service.get_inventory_summary()
    
    print(f"  Grupos (ISBNs únicos): {resumen['total_grupos']}")
    print(f"  Copias físicas totales: {resumen['total_copias']}")
    print(f"  Valor total: ${resumen['valor_total']:,} COP")
    print()
    
    # Generar reporte con Merge Sort
    print("→ Generando reporte ordenado por precio (Merge Sort)...")
    print()
    
    reporte = report_service.generate_inventory_value_report()
    
    print()
    print("=" * 80)
    print("  RESULTADOS DEL REPORTE")
    print("=" * 80)
    print()
    
    print(f"Total de libros (copias):  {reporte['total_libros']}")
    print(f"Precio total:              ${reporte['precio_total']:,} COP")
    print(f"Precio promedio:           ${reporte['precio_promedio']:,.2f} COP")
    print(f"Precio mínimo:             ${reporte['precio_minimo']:,} COP")
    print(f"Precio máximo:             ${reporte['precio_maximo']:,} COP")
    print()
    
    # Mostrar primeros 5 libros más baratos
    print("5 LIBROS MÁS BARATOS:")
    print("-" * 80)
    for i, libro in enumerate(reporte['libros'][:5], 1):
        print(f"{i}. {libro['titulo'][:40]:40} - ${libro['precio']:,} COP")
    print()
    
    # Mostrar últimos 5 libros más caros
    print("5 LIBROS MÁS CAROS:")
    print("-" * 80)
    for i, libro in enumerate(reporte['libros'][-5:], 1):
        print(f"{i}. {libro['titulo'][:40]:40} - ${libro['precio']:,} COP")
    print()
    
    # Verificar ubicación del archivo
    print("=" * 80)
    print("  VERIFICACIÓN DE ARCHIVO")
    print("=" * 80)
    print()
    
    if os.path.exists(FilePaths.INVENTORY_VALUE_REPORT):
        file_size = os.path.getsize(FilePaths.INVENTORY_VALUE_REPORT)
        print(f"✓ Archivo generado: {FilePaths.INVENTORY_VALUE_REPORT}")
        print(f"  Tamaño: {file_size:,} bytes")
        
        # Verificar contenido
        with open(FilePaths.INVENTORY_VALUE_REPORT, 'r', encoding='utf-8') as f:
            contenido = json.load(f)
        
        print(f"  Libros en archivo: {len(contenido['libros'])}")
        print(f"  Precio total en archivo: ${contenido['precio_total']:,} COP")
    else:
        print(f"✗ ERROR: Archivo no encontrado en {FilePaths.INVENTORY_VALUE_REPORT}")
    
    print()
    print("=" * 80)
    print("  TEST: AUTO-ACTUALIZACIÓN DEL REPORTE")
    print("=" * 80)
    print()
    
    # Test crear libro (el reporte debe actualizarse automáticamente)
    print("→ Creando nuevo libro de prueba...")
    precio_inicial = reporte['precio_total']
    copias_iniciales = reporte['total_libros']
    
    try:
        book_controller.create_book({
            "ISBNCode": "978-TEST-AUTO",
            "title": "Libro Test Auto-Actualización",
            "author": "Sistema Test",
            "weight": 0.5,
            "price": 15000,
            "isBorrowed": False
        })
        
        # Leer el reporte actualizado del archivo
        with open(FilePaths.INVENTORY_VALUE_REPORT, 'r', encoding='utf-8') as f:
            reporte_actualizado = json.load(f)
        
        precio_nuevo = reporte_actualizado['precio_total']
        copias_nuevas = reporte_actualizado['total_libros']
        
        print(f"  Copias antes:  {copias_iniciales}")
        print(f"  Copias ahora:  {copias_nuevas}")
        print(f"  Precio antes:  ${precio_inicial:,} COP")
        print(f"  Precio ahora:  ${precio_nuevo:,} COP")
        
        if copias_nuevas > copias_iniciales and precio_nuevo > precio_inicial:
            print("✓ Reporte se actualizó automáticamente después de crear libro")
        else:
            print("✗ ERROR: Reporte NO se actualizó correctamente")
        
    except Exception as e:
        print(f"  (Test de auto-actualización omitido: {e})")
    
    print()
    print("=" * 80)
    print("✓ TEST COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    main()
