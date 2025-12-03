"""report_helpers.py

Funciones auxiliares para generación de reportes.

Este módulo contiene las funciones auxiliares que NO son algoritmos de ordenamiento
pero que son necesarias para la generación de reportes:
- generar_reporte_global(): Serializar libros ordenados a JSON
- verificar_ordenamiento(): Validar que una lista esté ordenada
- ordenar_y_generar_reporte(): Función de conveniencia que combina ordenamiento + reporte

Los ALGORITMOS puros (Merge Sort, etc.) permanecen en AlgoritmosOrdenamiento.py

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List, Dict, Any
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


def generar_reporte_global(lista_ordenada: List[Any]) -> List[Dict[str, Any]]:
    """Generar un reporte global serializable del inventario ordenado por precio.
    
    PROPÓSITO:
    ==========
    Convertir una lista de objetos Book ordenados en una estructura de datos
    serializable (lista de diccionarios) que puede ser:
    - Guardada en un archivo JSON
    - Enviada como respuesta de API
    - Mostrada en la UI
    - Exportada a otros formatos (CSV, Excel, etc.)
    
    ESTRUCTURA DEL REPORTE:
    =======================
    Cada libro se convierte en un diccionario con los siguientes campos:
    - id: str - Identificador único del libro
    - ISBNCode: str - Código ISBN
    - title: str - Título del libro
    - author: str - Nombre del autor
    - weight: float - Peso en kilogramos
    - price: int - Precio en pesos colombianos (COP)
    - isBorrowed: bool - Estado de préstamo
    
    NOTA: Los nombres de campos están en INGLÉS para mantener consistencia
    con books.json, inventory_general.json y el modelo Book.
    
    USO TÍPICO:
    ===========
    1. Ordenar inventario:
       >>> from utils.algorithms.AlgoritmosOrdenamiento import merge_sort_books_by_price
       >>> libros_ordenados = merge_sort_books_by_price(inventario_general)
    
    2. Generar reporte:
       >>> reporte = generar_reporte_global(libros_ordenados)
    
    3. Guardar en JSON:
       >>> import json
       >>> with open('reporte_inventario.json', 'w') as f:
       ...     json.dump(reporte, f, indent=2, ensure_ascii=False)
    
    PARÁMETROS:
    ===========
    lista_ordenada : List[Any]
        Lista de objetos Book ya ordenados por precio (resultado de
        merge_sort_books_by_price). Cada objeto debe tener los siguientes
        métodos getter:
        - get_id() -> str
        - get_ISBNCode() -> str
        - get_title() -> str
        - get_author() -> str
        - get_weight() -> float
        - get_price() -> int
        - get_isBorrowed() -> bool
        
    RETORNO:
    ========
    List[Dict[str, Any]]
        Lista de diccionarios, donde cada diccionario representa un libro
        con sus atributos. La lista mantiene el orden de lista_ordenada.
        
    EXCEPCIONES:
    ============
    - AttributeError: si algún libro no tiene todos los getters requeridos
    
    EJEMPLO:
    ========
    >>> libros = [libro1, libro2, libro3]  # Ya ordenados por precio
    >>> reporte = generar_reporte_global(libros)
    >>> reporte[0]
    {
        'id': 'B001',
        'ISBNCode': '978-1234567890',
        'title': 'El Quijote',
        'author': 'Miguel de Cervantes',
        'weight': 1.2,
        'price': 25000,
        'isBorrowed': False
    }
    """
    reporte = []
    
    logger.info(f"Generando reporte global de {len(lista_ordenada)} libros ordenados por precio")
    
    for libro in lista_ordenada:
        try:
            # Extraer información de cada libro usando sus getters
            # IMPORTANTE: Usar nombres en INGLÉS para mantener consistencia
            # con books.json, inventory_general.json y el modelo Book
            libro_dict = {
                'id': libro.get_id(),
                'ISBNCode': libro.get_ISBNCode(),
                'title': libro.get_title(),
                'author': libro.get_author(),
                'weight': libro.get_weight(),
                'price': libro.get_price(),
                'isBorrowed': libro.get_isBorrowed(),
            }
            
            reporte.append(libro_dict)
            
        except AttributeError as e:
            # Si un libro no tiene algún getter, loguear error y continuar
            logger.error(f"Error al procesar libro en reporte: {e}")
            # Agregar entrada con información parcial
            reporte.append({
                'error': f'Libro con atributos faltantes: {str(e)}',
                'libro': str(libro)
            })
    
    logger.info(f"Reporte global generado exitosamente con {len(reporte)} entradas")
    
    return reporte


def verificar_ordenamiento(lista: List[Any]) -> bool:
    """Verificar si una lista de Books está ordenada por precio (ascendente).
    
    UTILIDAD:
    =========
    Función de debugging y testing para validar que el ordenamiento funciona
    correctamente. Útil para pruebas unitarias.
    
    PARÁMETROS:
    ===========
    lista : List[Any]
        Lista de objetos Book a verificar
        
    RETORNO:
    ========
    bool
        True si la lista está ordenada por precio (menor a mayor)
        False en caso contrario
        
    EJEMPLO:
    ========
    >>> from utils.algorithms.AlgoritmosOrdenamiento import merge_sort_books_by_price
    >>> ordenados = merge_sort_books_by_price(libros)
    >>> assert verificar_ordenamiento(ordenados), "Error: lista no está ordenada"
    """
    if len(lista) <= 1:
        return True
    
    for i in range(len(lista) - 1):
        if lista[i].get_price() > lista[i + 1].get_price():
            return False
    
    return True


def ordenar_y_generar_reporte(inventario_general: List[Any]) -> Dict[str, Any]:
    """Función de conveniencia: ordenar inventario y generar reporte en un solo paso.
    
    PROPÓSITO:
    ==========
    Combina merge_sort_books_by_price() y generar_reporte_global() en una sola
    función para simplificar el uso común del módulo.
    
    PARÁMETROS:
    ===========
    inventario_general : List[Any]
        Lista desordenada de objetos Book (el Inventario General)
        
    RETORNO:
    ========
    Dict[str, Any]
        Diccionario con dos claves:
        - 'libros_ordenados': List[Any] - Lista ordenada de objetos Book
        - 'reporte': List[Dict[str, Any]] - Reporte serializable
        - 'total_libros': int - Cantidad de libros procesados
        - 'precio_total': int - Suma de todos los precios
        - 'precio_promedio': float - Precio promedio
        - 'precio_minimo': int - Precio más bajo
        - 'precio_maximo': int - Precio más alto
        
    EJEMPLO:
    ========
    >>> resultado = ordenar_y_generar_reporte(inventario_general)
    >>> print(f"Total libros: {resultado['total_libros']}")
    >>> print(f"Precio promedio: ${resultado['precio_promedio']:,.0f}")
    >>> 
    >>> # Guardar reporte en JSON
    >>> import json
    >>> with open('reporte.json', 'w') as f:
    ...     json.dump(resultado['reporte'], f, indent=2, ensure_ascii=False)
    """
    # Importar el algoritmo de ordenamiento
    from utils.algorithms.AlgoritmosOrdenamiento import merge_sort_books_by_price
    
    logger.info(f"Iniciando ordenamiento de {len(inventario_general)} libros por precio")
    
    # Paso 1: Ordenar usando Merge Sort
    libros_ordenados = merge_sort_books_by_price(inventario_general)
    
    # Paso 2: Generar reporte serializable
    reporte = generar_reporte_global(libros_ordenados)
    
    # Paso 3: Calcular estadísticas del inventario
    total_libros = len(libros_ordenados)
    
    if total_libros > 0:
        precios = [libro.get_price() for libro in libros_ordenados]
        precio_total = sum(precios)
        precio_promedio = precio_total / total_libros
        precio_minimo = precios[0]  # Primera posición (ya ordenado)
        precio_maximo = precios[-1]  # Última posición (ya ordenado)
    else:
        precio_total = 0
        precio_promedio = 0.0
        precio_minimo = 0
        precio_maximo = 0
    
    logger.info(f"Ordenamiento completado: {total_libros} libros, precio total: ${precio_total:,}")
    
    return {
        'libros_ordenados': libros_ordenados,
        'reporte': reporte,
        'total_libros': total_libros,
        'precio_total': precio_total,
        'precio_promedio': precio_promedio,
        'precio_minimo': precio_minimo,
        'precio_maximo': precio_maximo,
    }


__all__ = [
    'generar_reporte_global',
    'verificar_ordenamiento',
    'ordenar_y_generar_reporte',
]
