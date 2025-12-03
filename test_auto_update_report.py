"""
Test de Auto-Actualización del Reporte Global.

Este script verifica que el reporte global se actualiza automáticamente
cuando se crean, modifican o eliminan libros a través del BookController.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import sys
import os
import json
import time

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.book_controller import BookController
from utils.config import FilePaths


def leer_reporte():
    """Leer el reporte actual del archivo."""
    with open(FilePaths.INVENTORY_VALUE_REPORT, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    print("=" * 80)
    print("  TEST: Auto-Actualización del Reporte Global")
    print("=" * 80)
    print()
    
    controller = BookController()
    
    # Regenerar reporte para tener estado fresco
    print("→ Regenerando reporte inicial...")
    controller.report_service.generate_inventory_value_report()
    
    # 1. ESTADO INICIAL
    print("→ Estado inicial del reporte...")
    reporte_inicial = leer_reporte()
    print(f"  Total de libros: {reporte_inicial['total_libros']}")
    print(f"  Precio total: ${reporte_inicial['precio_total']:,} COP")
    print()
    
    # 2. CREAR NUEVO LIBRO
    print("→ Test 1: Crear nuevo libro...")
    timestamp = int(time.time() * 1000) % 100000  # Solo últimos 5 dígitos para mantener ISBN corto
    test_id = f"TEST{timestamp}"
    test_price = 99999
    
    try:
        controller.create_book({
            "id": test_id,
            "ISBNCode": f"978{timestamp}",  # ISBN corto válido (3 + 5 = 8 dígitos)
            "title": f"Test Auto-Update {timestamp}",
            "author": "Sistema Test",
            "weight": 0.5,
            "price": test_price,
            "isBorrowed": False
        })
        
        reporte_despues_crear = leer_reporte()
        
        print(f"  Libros antes:  {reporte_inicial['total_libros']}")
        print(f"  Libros ahora:  {reporte_despues_crear['total_libros']}")
        print(f"  Precio antes:  ${reporte_inicial['precio_total']:,} COP")
        print(f"  Precio ahora:  ${reporte_despues_crear['precio_total']:,} COP")
        
        if (reporte_despues_crear['total_libros'] == reporte_inicial['total_libros'] + 1 and
            reporte_despues_crear['precio_total'] == reporte_inicial['precio_total'] + test_price):
            print("  ✓ Reporte actualizado correctamente después de CREAR")
        else:
            print("  ✗ ERROR: Reporte NO se actualizó correctamente después de CREAR")
        
        print()
        
        # 3. MODIFICAR LIBRO
        print("→ Test 2: Modificar libro existente...")
        nuevo_precio = 55555
        
        controller.update_book(test_id, {"price": nuevo_precio})
        
        reporte_despues_modificar = leer_reporte()
        
        print(f"  Precio esperado: ${reporte_despues_crear['precio_total'] - test_price + nuevo_precio:,} COP")
        print(f"  Precio actual:   ${reporte_despues_modificar['precio_total']:,} COP")
        
        if reporte_despues_modificar['precio_total'] == reporte_despues_crear['precio_total'] - test_price + nuevo_precio:
            print("  ✓ Reporte actualizado correctamente después de MODIFICAR")
        else:
            print("  ✗ ERROR: Reporte NO se actualizó correctamente después de MODIFICAR")
        
        print()
        
        # 4. ELIMINAR LIBRO
        print("→ Test 3: Eliminar libro...")
        
        controller.delete_book(test_id)
        
        reporte_despues_eliminar = leer_reporte()
        
        print(f"  Libros antes de eliminar: {reporte_despues_modificar['total_libros']}")
        print(f"  Libros ahora:             {reporte_despues_eliminar['total_libros']}")
        print(f"  Precio antes de eliminar: ${reporte_despues_modificar['precio_total']:,} COP")
        print(f"  Precio ahora:             ${reporte_despues_eliminar['precio_total']:,} COP")
        
        if (reporte_despues_eliminar['total_libros'] == reporte_despues_modificar['total_libros'] - 1 and
            reporte_despues_eliminar['precio_total'] == reporte_despues_modificar['precio_total'] - nuevo_precio):
            print("  ✓ Reporte actualizado correctamente después de ELIMINAR")
        else:
            print("  ✗ ERROR: Reporte NO se actualizó correctamente después de ELIMINAR")
        
        print()
        
        # VERIFICAR QUE VOLVEMOS AL ESTADO INICIAL
        if (reporte_despues_eliminar['total_libros'] == reporte_inicial['total_libros'] and
            reporte_despues_eliminar['precio_total'] == reporte_inicial['precio_total']):
            print("✓ Estado final coincide con estado inicial (libro test eliminado)")
        else:
            print("⚠ Estado final difiere del inicial (puede haber otros cambios concurrentes)")
        
    except Exception as e:
        print(f"✗ ERROR durante el test: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✓ TEST COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    main()
