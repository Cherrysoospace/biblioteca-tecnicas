"""report_service.py

Servicio dedicado a la generación de reportes del sistema de biblioteca.
Responsabilidad ÚNICA: Generar reportes ordenados del inventario.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import json
from typing import List, Dict, Any

from services.inventory_service import InventoryService
from utils.report_helpers import ordenar_y_generar_reporte
from utils.config import FilePaths
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


class ReportService:
    """Servicio para generación de reportes del inventario.
    
    RESPONSABILIDAD ÚNICA:
    ======================
    Generar Reporte Global de Inventario ordenado por precio usando Merge Sort.
    
    CUMPLE CON EL REQUISITO:
    ========================
    "Ordenamiento por Mezcla (Merge Sort): Este algoritmo debe usarse para generar un
    Reporte Global de inventario, ordenado por el atributo Valor (COP). El reporte
    generado también debe poder almacenarse en un archivo."
    
    DIFERENCIA CON BOOKSERVICE:
    ===========================
    - BookService: Gestiona catálogo de libros (books.json)
    - ReportService: Genera reportes del INVENTARIO REAL con stock
    
    FUNCIONAMIENTO:
    ===============
    1. Obtiene inventario desde InventoryService
    2. Expande todos los grupos a lista plana de Books
    3. Aplica Merge Sort por precio
    4. Genera reporte con estadísticas
    5. Exporta a data/inventory_value.json
    """
    
    def __init__(self, inventory_service: InventoryService = None):
        """Inicializar ReportService.
        
        Parameters:
        -----------
        inventory_service : InventoryService, opcional
            Servicio de inventario. Si es None, se crea uno nuevo.
        """
        self.inventory_service = inventory_service or InventoryService()
    
    def generate_inventory_value_report(self) -> Dict[str, Any]:
        """Generar reporte global de inventario ordenado por precio usando Merge Sort.
        
        PROPÓSITO:
        ==========
        Este método cumple con el requisito del proyecto:
        "Ordenamiento por Mezcla (Merge Sort): Este algoritmo debe usarse para generar un
        Reporte Global de inventario, ordenado por el atributo Valor (COP)."
        
        DIFERENCIA CLAVE CON IMPLEMENTACIÓN ANTERIOR:
        ==============================================
        ANTES (incorrecto):
        - Ordenaba books.json (catálogo de 33 libros únicos)
        - No consideraba stock
        - Valor total: suma de precios únicos
        
        AHORA (correcto):
        - Ordena inventory_general.json (inventario con stock)
        - Expande todas las copias (si hay 3 copias, aparecen 3 veces)
        - Valor total: suma de (precio × cantidad de copias)
        
        EJEMPLO:
        ========
        Inventory_general tiene:
        - Grupo 1: "El Quijote" - Stock 3 - $25,000 c/u
        - Grupo 2: "Cien Años" - Stock 2 - $30,000 c/u
        
        El reporte tendrá 5 libros (3 + 2):
        [
          {"titulo": "El Quijote", "precio": 25000},  # Copia 1
          {"titulo": "El Quijote", "precio": 25000},  # Copia 2
          {"titulo": "El Quijote", "precio": 25000},  # Copia 3
          {"titulo": "Cien Años", "precio": 30000},   # Copia 1
          {"titulo": "Cien Años", "precio": 30000}    # Copia 2
        ]
        
        Precio total: $135,000 (no $55,000)
        
        FUNCIONAMIENTO:
        ===============
        1. Obtiene inventory_general desde InventoryService
        2. Expande cada grupo (Inventory) a sus items (List[Book])
        3. Crea lista plana con TODAS las copias de TODOS los libros
        4. Aplica Merge Sort para ordenar por precio (menor a mayor)
        5. Genera reporte serializable con estadísticas
        6. Exporta a data/inventory_value.json
        
        FORMATO DEL REPORTE:
        ====================
        {
            "total_libros": 50,  // Total de COPIAS físicas
            "precio_total": 1250000,  // Suma de TODAS las copias
            "precio_promedio": 25000.0,
            "precio_minimo": 5000,
            "precio_maximo": 120000,
            "libros": [
                {
                    "id": "B001",
                    "isbn": "978-1234567890",
                    "titulo": "Libro A",
                    "autor": "Autor A",
                    "peso": 1.2,
                    "precio": 5000,
                    "prestado": false
                },
                // ... más copias ordenadas por precio ...
            ]
        }
        
        RETORNO:
        ========
        Dict[str, Any]
            Diccionario con el reporte completo (también se guarda en archivo)
        
        EXCEPCIONES:
        ============
        - IOError: si no se puede escribir el archivo de reporte
        """
        try:
            logger.info("Iniciando generación de reporte de inventario por precio...")
            
            # IMPORTANTE: Recargar inventario desde disco para obtener cambios más recientes
            # Esto asegura que el reporte refleje los últimos cambios en el inventario
            # (libros agregados/eliminados desde BookService)
            self.inventory_service._load_inventories()
            self.inventory_service.synchronize_inventories()
            
            # PASO 1: Obtener inventario general (grupos de libros por ISBN)
            inventory_groups = self.inventory_service.inventory_general
            
            # PASO 2: Expandir grupos a lista plana de Books
            # Cada grupo (Inventory) tiene múltiples items (Books)
            # Necesitamos una lista con TODAS las copias individuales
            todos_los_libros = []
            
            for grupo in inventory_groups:
                # grupo.get_items() retorna List[Book]
                # Cada Book es una copia física del libro
                libros_del_grupo = grupo.get_items()
                todos_los_libros.extend(libros_del_grupo)
            
            logger.info(
                f"Inventario expandido: {len(inventory_groups)} grupos → "
                f"{len(todos_los_libros)} copias físicas"
            )
            
            # PASO 3: Verificar si hay libros
            if len(todos_los_libros) == 0:
                logger.warning("Inventario vacío, generando reporte vacío")
                reporte_final = {
                    'total_libros': 0,
                    'precio_total': 0,
                    'precio_promedio': 0.0,
                    'precio_minimo': 0,
                    'precio_maximo': 0,
                    'libros': []
                }
            else:
                # PASO 4: Aplicar Merge Sort para ordenar por precio
                # ordenar_y_generar_reporte() hace:
                # 1. merge_sort_books_by_price(todos_los_libros)
                # 2. generar_reporte_global(libros_ordenados)
                # 3. Calcular estadísticas (total, promedio, min, max)
                resultado = ordenar_y_generar_reporte(todos_los_libros)
                
                # PASO 5: Construir estructura final del reporte
                reporte_final = {
                    'total_libros': resultado['total_libros'],
                    'precio_total': resultado['precio_total'],
                    'precio_promedio': resultado['precio_promedio'],
                    'precio_minimo': resultado['precio_minimo'],
                    'precio_maximo': resultado['precio_maximo'],
                    'libros': resultado['reporte']  # Lista de diccionarios ordenada
                }
                
                logger.info(
                    f"Reporte generado: {resultado['total_libros']} libros, "
                    f"precio total: ${resultado['precio_total']:,}, "
                    f"promedio: ${resultado['precio_promedio']:,.2f}, "
                    f"rango: ${resultado['precio_minimo']:,} - ${resultado['precio_maximo']:,}"
                )
            
            # PASO 6: Exportar a archivo JSON en data/
            with open(FilePaths.INVENTORY_VALUE_REPORT, 'w', encoding='utf-8') as f:
                json.dump(reporte_final, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Reporte exportado a: {FilePaths.INVENTORY_VALUE_REPORT}")
            
            return reporte_final
            
        except Exception as e:
            logger.error(f"Error al generar reporte de inventario: {e}")
            raise
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """Obtener resumen rápido del inventario sin ordenar.
        
        Útil para dashboards o vistas rápidas sin el overhead del Merge Sort.
        
        RETORNO:
        ========
        Dict[str, Any]
            {
                'total_grupos': int,  // Cantidad de grupos (ISBNs únicos)
                'total_copias': int,  // Cantidad de copias físicas
                'valor_total': int    // Suma de precios de todas las copias
            }
        """
        inventory_groups = self.inventory_service.inventory_general
        
        total_grupos = len(inventory_groups)
        total_copias = 0
        valor_total = 0
        
        for grupo in inventory_groups:
            libros = grupo.get_items()
            total_copias += len(libros)
            
            for libro in libros:
                valor_total += libro.get_price()
        
        return {
            'total_grupos': total_grupos,
            'total_copias': total_copias,
            'valor_total': valor_total
        }


__all__ = ['ReportService']
