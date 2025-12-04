"""search_helpers.py

Helper utilities for search validation and support.

This module contains small helpers used by the search subsystem:
- text normalization for case- and accent-insensitive searches
- validation of ordered lists (precondition for binary search)

Author: Library Management System
Date: 2025-12-03
"""


def normalizar_texto(texto):
    """Normalize text for case- and accent-insensitive searches.

    Purpose
    -------
    Make user searches more forgiving by removing case differences,
    common diacritics and extra whitespace.

    Transformations
    ---------------
    1. Convert to lowercase
    2. Remove common accented characters (á→a, é→e, í→i, ó→o, ú→u, ñ→n)
    3. Collapse multiple spaces into a single space

    Parameters
    ----------
    texto : str
        Text to normalize (title, author, search term).

    Returns
    -------
    str
        Normalized lowercase text without accents.

    Examples
    --------
    >>> from utils.search_helpers import normalizar_texto
    >>> title = "Cien Años de Soledad"
    >>> query = "cien anos"
    >>> if normalizar_texto(query) in normalizar_texto(title):
    ...     print("Match found!")

    Test cases
    ----------
    >>> normalizar_texto("García Márquez")
    'garcia marquez'
    >>> normalizar_texto("JOSÉ")
    'jose'
    >>> normalizar_texto("Año Nuevo")
    'ano nuevo'
    """
    if not texto:
        return ""

    # Convert to lowercase
    texto = texto.lower()

    # Replacement table for common accent characters
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ñ': 'n', 'ç': 'c'
    }

    # Apply replacements
    for acento, sin_acento in reemplazos.items():
        texto = texto.replace(acento, sin_acento)

    # Remove extra spaces
    texto = ' '.join(texto.split())

    return texto


def verificar_lista_ordenada(lista, atributo='ISBNCode'):
    """Check whether a list is ordered by a specific attribute.

    Purpose
    -------
    Use this to validate the precondition for binary search. Detects
    cases where a binary search would be attempted on an unordered list.

    Parameters
    ----------
    lista : list
        List of objects to verify (Book, Inventory item, etc.).
    atributo : str, optional
        Attribute name to check ordering by (default: 'ISBNCode').

    Returns
    -------
    bool
        True if the list is ordered ascending by the given attribute,
        False otherwise.

    Example
    -------
    >>> from utils.search_helpers import verificar_lista_ordenada
    >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    >>>
    >>> if not verificar_lista_ordenada(inventory):
    ...     print("Sorting inventory...")
    ...     insercion_ordenada(inventory)
    >>>
    >>> # Now it is safe to use binary search
    >>> index = busqueda_binaria(inventory, searched_isbn)
    """
    if not lista or len(lista) <= 1:
        return True

    for i in range(len(lista) - 1):
        valor_actual = getattr(lista[i], atributo)
        valor_siguiente = getattr(lista[i + 1], atributo)

        if valor_actual > valor_siguiente:
            return False

    return True


__all__ = ['normalizar_texto', 'verificar_lista_ordenada']
