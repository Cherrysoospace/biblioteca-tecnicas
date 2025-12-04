"""AlgoritmosOrdenamiento.py

Sorting algorithms module for the Library Management System.

This module implements sorting utilities for book inventories. It contains a
hand-implemented Merge Sort to order books by price (in COP). The implementation
avoids Python's built-in sorted() and list.sort() to illustrate algorithmic
behavior and to ensure stable, predictable results for the inventory.

Highlights:
- Merge Sort: stable O(n log n) sorting
- Sorts Book objects by price in ascending order
- Modular, reusable code suitable for reporting and debugging

Why Merge Sort?
---------------
1. Stability: Merge Sort is stable, so items with equal prices preserve their
    original relative order. This is important for deterministic inventory
    outputs and consistent reporting.
2. Guaranteed complexity: O(n log n) in all cases (best, average, worst).
    No worst-case degradation as in naive QuickSort implementations.
3. Predictability: Good for large inventories where consistent performance is
    preferred over average-case-only improvements.
4. Divide and conquer: simplifies testing and reasoning by splitting the
    problem into smaller subproblems.

Author: Library Management System
Date: 2025-12-02
"""

from typing import List, Dict, Any
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)

def _comparar_isbn_mayor(isbn1, isbn2):
    """
    Compare two ISBNs preferring numeric comparison when possible.

    Purpose:
    - If both ISBNs are purely numeric, compare them as integers (numeric
      ordering). This avoids incorrect lexicographic ordering where "2" > "123".
    - If either ISBN contains non-numeric characters (dashes, letters), fall
      back to standard lexicographic comparison. This preserves compatibility
      with common ISBN formats such as "978-...".

    Parameters
    ----------
    isbn1, isbn2 : str
        ISBN values to compare.

    Returns
    -------
    bool
        True if isbn1 > isbn2 (numeric comparison when applicable), otherwise False.
    """
    try:
        # Try numeric conversion; if both are numeric then compare as integers
        return int(isbn1) > int(isbn2)
    except (ValueError, TypeError):
        # Fallback to lexicographic comparison for non-numeric ISBNs
        return isbn1 > isbn2


def insercion_ordenada(lista_libros):
    """
    Sort an inventory list in-place using Insertion Sort by ISBN ascending.

    Purpose
    -------
    This insertion sort implementation modifies the input list in-place.
    It is simple, stable, and efficient for small or nearly-sorted lists.

    Parameters
    ----------
    lista_libros : list
        A list of Inventory objects. Each object must implement get_isbn() and
        return an ISBN value (string or numeric) used as the sorting key.

    Returns
    -------
    list
        The same list sorted in ascending ISBN order. The sort is performed
        in-place and the original list object is returned for convenience.

    Use cases
    ---------
    - Preparing an inventory for binary search by ISBN
    - Maintaining a small sorted list after insertions
    - Sorting small result sets for predictable output
    """

    # Early validation: empty or single-element lists are already sorted
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros

    # Insertion sort: iterate from the second element and insert into the
    # sorted left portion of the list
    for i in range(1, len(lista_libros)):
        # Select the element to insert
        inventario_actual = lista_libros[i]
        isbn_actual = inventario_actual.get_isbn()

        # Find the insertion position by shifting larger elements to the right
        j = i - 1

        # While there are elements to the left and they are greater than the
        # current ISBN, shift them one position to the right. Comparison uses
        # _comparar_isbn_mayor which prefers numeric comparison when possible.
        while j >= 0 and _comparar_isbn_mayor(lista_libros[j].get_isbn(), isbn_actual):
            lista_libros[j + 1] = lista_libros[j]
            j -= 1

        # Insert the current inventory at its correct position
        lista_libros[j + 1] = inventario_actual

    # Return the sorted list (sorting is in-place)
    return lista_libros



def merge_sort_books_by_price(lista_libros: List[Any]) -> List[Any]:
    """
    Sort a list of Book objects by price using Merge Sort.

    Algorithm
    ---------
    Merge Sort follows divide-and-conquer:
    1. Divide the list into two approximately equal halves
    2. Recursively sort each half
    3. Merge the two sorted halves into a fully sorted list

    Base case
    ---------
    If the list has 0 or 1 elements it is already sorted and returned as-is.

    Parameters
    ----------
    lista_libros : List[Any]
        A list of Book objects. Each object must implement get_price() returning
        a numeric price (int or float).

    Returns
    -------
    List[Any]
        A new list containing the same Book objects sorted by ascending price.

    Stability
    ---------
    This implementation is stable: when two elements have equal price the
    element from the left half is chosen first during the merge step, preserving
    relative order from the original list.
    """

    # Base case: empty list or single-element list is already sorted
    if len(lista_libros) <= 1:
        return lista_libros

    # Divide: find the midpoint and split into two halves
    punto_medio = len(lista_libros) // 2
    mitad_izquierda = lista_libros[:punto_medio]
    mitad_derecha = lista_libros[punto_medio:]

    logger.debug(f"Splitting list of {len(lista_libros)} books into {len(mitad_izquierda)} + {len(mitad_derecha)}")

    # Conquer: recursively sort each half
    izquierda_ordenada = merge_sort_books_by_price(mitad_izquierda)
    derecha_ordenada = merge_sort_books_by_price(mitad_derecha)

    # Combine: merge the two sorted halves
    resultado = merge(izquierda_ordenada, derecha_ordenada)

    return resultado


def merge(left: List[Any], right: List[Any]) -> List[Any]:
    """
    Merge two sorted lists of Book objects into a single sorted list by price.

    The merge procedure compares the front elements of both lists and appends
    the smaller price to the result. Using <= when comparing prices ensures
    stability: if prices are equal, the element from the left list is chosen
    first, preserving original relative order.

    Parameters
    ----------
    left, right : List[Any]
        Two lists of Book objects already sorted by ascending price.

    Returns
    -------
    List[Any]
        A new list containing all elements from left and right in ascending price order.
    """

    resultado = []
    i = 0
    j = 0

    # Interleave elements while both lists have remaining items
    while i < len(left) and j < len(right):
        precio_izq = left[i].get_price()
        precio_der = right[j].get_price()

        # Use <= to guarantee stability: left element comes first on ties
        if precio_izq <= precio_der:
            resultado.append(left[i])
            i += 1
        else:
            resultado.append(right[j])
            j += 1

    # Append any remaining elements from left, then right
    while i < len(left):
        resultado.append(left[i])
        i += 1

    while j < len(right):
        resultado.append(right[j])
        j += 1

    return resultado


# NOTE:
# Reporting helper functions (generar_reporte_global,
# ordenar_y_generar_reporte, verificar_ordenamiento) have been moved to
# utils/report_helpers.py to keep this file focused strictly on sorting
# algorithms. To use those helpers import them from utils.report_helpers.

__all__ = [
    'insercion_ordenada',
    'merge_sort_books_by_price',
    'merge',
]

