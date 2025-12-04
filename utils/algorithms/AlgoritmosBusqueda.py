"""
AlgoritmosBusqueda.py

Recursive search algorithms used by the library management system:
1. Binary Search: by ISBN over a sorted inventory (O(log n))
2. Linear Search: by Title or Author over the general inventory (O(n))

Binary Search - Critical Use:
-----------------------------
The binary search function is critical for checking whether a returned book
has pending reservations on the waiting queue. Its result (index or not found)
must be used to allocate the book to the person who requested the reservation
according to priority.

Binary Search Precondition:
---------------------------
The inventory MUST be sorted by ISBN before using binary search. Use
AlgoritmosOrdenamiento.insercion_ordenada(inventario) to prepare the list.

Linear Search - Use:
-------------------
Use the linear search to find books by partial Title or Author in the general
inventory. It does not require sorting and is useful for flexible text searches.

Author: Library Management System
Date: 2025-12-03
"""


def busqueda_binaria(inventario_ordenado, isbn_buscado, inicio=0, fin=None):
    """
    Search for a book by ISBN in a sorted inventory using recursive binary search.

    Important precondition:
    - The inventory MUST be sorted by ISBN prior to calling this function. If the
      inventory is not sorted, the result will be incorrect (not merely slower).

    Parameters
    ----------
    inventario_ordenado : list
        A list (sorted by ISBN) of inventory objects. Each inventory object must
        expose a get_isbn() method that returns a comparable ISBN string.

    isbn_buscado : str
        The ISBN string to search for.

    inicio : int, optional
        The starting index for the search range (default: 0). This is intended for
        internal recursive calls and should not be modified by external callers.

    fin : int, optional
        The ending index for the search range (default: len(inventario)-1). This
        is intended for internal recursive calls and should not be modified by
        external callers.

    Returns
    -------
    int
        The index of the matching inventory element if found, otherwise -1.

    Example
    -------
    >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    >>> from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria
    >>>
    >>> # 1. Sort inventory (PRECONDITION)
    >>> insercion_ordenada(inventario)
    >>>
    >>> # 2. Search by ISBN
    >>> index = busqueda_binaria(inventario, "978-3-16-148410-0")
    >>>
    >>> if index != -1:
    ...     found = inventario[index]
    ...     print(f"Book found at index {index}")
    ... else:
    ...     print("Book not found")
    """
    # If this is the first call, determine the list size
    if fin is None:
        fin = len(inventario_ordenado) - 1
    
    # Base case: empty list
    if not inventario_ordenado:
        return -1
    
    # Base case: sublist has no elements
    if inicio > fin:
        return -1
    
    # Compute the midpoint
    medio = (inicio + fin) // 2
    
    # Get the ISBN at the midpoint
    isbn_medio = inventario_ordenado[medio].get_isbn()
    
    # Base case: element found
    if isbn_medio == isbn_buscado:
        return medio
    
    # Recursive case: search left half (move to medio - 1)
    elif isbn_medio > isbn_buscado:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, inicio, medio - 1)
    
    # Recursive case: search right half (move to medio + 1)
    else:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, medio + 1, fin)


def busqueda_lineal(inventario, criterio_busqueda, indice=0):
    """
    Search inventory recursively by partial Title or Author using linear search.

    Characteristics
    ---------------
    - Does NOT require the inventory to be sorted.
    - Performs partial, case- and accent-insensitive matching.
    - Implemented recursively as a simple linear scan.

    Parameters
    ----------
    inventario : list
        A list of inventory objects. Each inventory element is expected to have
        a get_book() method that returns a book object (or None).

    criterio_busqueda : str
        The text to search for within book title or author. Partial matches are
        supported (e.g. "Quijote" matches "Don Quijote de la Mancha").

    indice : int, optional
        Current index used by recursion (default: 0). Do not change when calling
        externally; this parameter is for internal recursion only.

    Returns
    -------
    int
        The index of the first inventory element whose book's title or author
        contains the normalized search criterion; returns -1 if none found.

    Complexity
    ----------
    Time: O(n) worst-case (scans all elements).
    Space: O(n) due to recursion depth in the worst case.

    Notes
    -----
    This function relies on helper routines to normalize text for
    case- and accent-insensitive comparisons. See: utils.search_helpers.normalizar_texto()
    """
    # Base case: reached end of list without finding element
    if indice >= len(inventario):
        return -1
    
    # Get current inventory's book
    libro_actual = inventario[indice].get_book()
    
    # If there is no book at this inventory position, continue
    if libro_actual is None:
        # Recursive case: continue scanning the rest of the list
        return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
    
    # Get current book's title and author
    titulo = libro_actual.get_title() or ""
    autor = libro_actual.get_author() or ""
    
    # Import helper to normalize text (case and accent insensitive)
    from utils.search_helpers import normalizar_texto
    
    # Normalize strings for comparison
    criterio_norm = normalizar_texto(criterio_busqueda)
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    
    # Base case: found the element (partial match in title or author)
    if criterio_norm in titulo_norm or criterio_norm in autor_norm:
        return indice
    
    # Recursive case: continue searching the remainder of the list
    return busqueda_lineal(inventario, criterio_busqueda, indice + 1)


__all__ = ['busqueda_binaria', 'busqueda_lineal']

