"""report_helpers.py

Helper functions for report generation.

This module provides small utility functions that are not sorting
algorithms themselves but are used to produce reports from sorted
book lists:
- ``generar_reporte_global``: serialize sorted books into a JSON-ready list
- ``verificar_ordenamiento``: validate that a list is sorted by price
- ``ordenar_y_generar_reporte``: convenience function that sorts and
    generates a report in a single call

Pure sorting algorithms (e.g. merge sort) live in
``utils.algorithms.AlgoritmosOrdenamiento``.

Author: Library Management System
Date: 2025-12-02
"""

from typing import List, Dict, Any
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


def generar_reporte_global(lista_ordenada: List[Any]) -> List[Dict[str, Any]]:
    """Create a serializable global report from a list of books sorted by price.

    Purpose
    -------
    Convert a list of Book objects into a JSON-serializable structure
    (a list of dictionaries) that can be saved to disk, returned from an
    API, shown in the UI, or exported to CSV/Excel.

    Report structure
    ----------------
    Each book is transformed into a dictionary containing the following
    fields (field names use English to match ``books.json`` and the
    Book model): ``id``, ``ISBNCode``, ``title``, ``author``, ``weight``,
    ``price``, ``isBorrowed``.

    Parameters
    ----------
    lista_ordenada : List[Any]
        A list of Book objects already sorted by price. Each object is
        expected to expose these getters:
        ``get_id()``, ``get_ISBNCode()``, ``get_title()``, ``get_author()``,
        ``get_weight()``, ``get_price()``, ``get_isBorrowed()``.

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries where each dictionary represents a book.

    Raises
    ------
    AttributeError
        If a Book object does not implement one of the expected getters.

    Example
    -------
    >>> # Assuming `libros_ordenados` is a list of Book objects sorted by price
    >>> reporte = generar_reporte_global(libros_ordenados)
    >>> reporte[0]
    {
        'id': 'B001',
        'ISBNCode': '978-1234567890',
        'title': 'Don Quixote',
        'author': 'Miguel de Cervantes',
        'weight': 1.2,
        'price': 25000,
        'isBorrowed': False
    }
    """
    reporte = []
    
    logger.info(f"Generating global report for {len(lista_ordenada)} books sorted by price")
    
    for libro in lista_ordenada:
        try:
            # Extract information from each book using its getters.
            # IMPORTANT: Use English field names to remain consistent with
            # books.json, inventory_general.json and the Book model.
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
            # If a book is missing a getter, log the error and continue.
            logger.error(f"Error processing book for report: {e}")
            # Append an entry with partial information so the report remains
            # usable even when some items could not be fully serialized.
            reporte.append({
                'error': f'Missing attributes on book: {str(e)}',
                'book': str(libro)
            })
    
    logger.info(f"Global report successfully generated with {len(reporte)} entries")
    
    return reporte


def verificar_ordenamiento(lista: List[Any]) -> bool:
    """Check whether a list of Book objects is sorted by price (ascending).

    Utility
    -------
    A small helper used for debugging and unit tests to ensure the sorting
    algorithm produced a correctly ordered list.

    Parameters
    ----------
    lista : List[Any]
        List of Book objects to verify.

    Returns
    -------
    bool
        True if the list is sorted by price (lowest to highest), otherwise
        False.

    Example
    -------
    >>> from utils.algorithms.AlgoritmosOrdenamiento import merge_sort_books_by_price
    >>> ordered = merge_sort_books_by_price(books)
    >>> assert verificar_ordenamiento(ordered), "List is not sorted"
    """
    if len(lista) <= 1:
        return True
    
    for i in range(len(lista) - 1):
        if lista[i].get_price() > lista[i + 1].get_price():
            return False
    
    return True


def ordenar_y_generar_reporte(inventario_general: List[Any]) -> Dict[str, Any]:
    """Convenience function: sort the inventory and produce a report.

    Purpose
    -------
    Combines ``merge_sort_books_by_price()`` and ``generar_reporte_global()``
    so callers can obtain sorted objects, a serializable report, and basic
    inventory statistics with a single call.

    Parameters
    ----------
    inventario_general : List[Any]
        Unsorted list of Book objects (the general inventory).

    Returns
    -------
    Dict[str, Any]
        A dictionary containing:
        - ``libros_ordenados``: List[Any] - the sorted Book objects
        - ``reporte``: List[Dict[str, Any]] - JSON-serializable report
        - ``total_libros``: int - number of processed books
        - ``precio_total``: int - sum of all prices
        - ``precio_promedio``: float - average price
        - ``precio_minimo``: int - minimum price
        - ``precio_maximo``: int - maximum price

    Example
    -------
    >>> result = ordenar_y_generar_reporte(inventario_general)
    >>> print(f"Total books: {result['total_libros']}")
    >>> print(f"Average price: ${result['precio_promedio']:,.0f}")
    >>>
    >>> # Save the report as JSON
    >>> import json
    >>> with open('report.json', 'w') as f:
    ...     json.dump(result['reporte'], f, indent=2, ensure_ascii=False)
    """
    # Importar el algoritmo de ordenamiento
    from utils.algorithms.AlgoritmosOrdenamiento import merge_sort_books_by_price
    
    logger.info(f"Starting sort of {len(inventario_general)} books by price")
    
    # Step 1: Sort using Merge Sort
    libros_ordenados = merge_sort_books_by_price(inventario_general)
    
    # Step 2: Generate serializable report
    reporte = generar_reporte_global(libros_ordenados)
    
    # Step 3: Compute inventory statistics
    total_libros = len(libros_ordenados)
    
    if total_libros > 0:
        prices = [libro.get_price() for libro in libros_ordenados]
        precio_total = sum(prices)
        precio_promedio = precio_total / total_libros
        precio_minimo = prices[0]  # first position (already sorted)
        precio_maximo = prices[-1]  # last position (already sorted)
    else:
        precio_total = 0
        precio_promedio = 0.0
        precio_minimo = 0
        precio_maximo = 0
    logger.info(f"Sorting completed: {total_libros} books, total price: ${precio_total:,}")
    
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
