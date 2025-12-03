"""search_helpers.py

Funciones auxiliares para validación y soporte de búsquedas en el sistema.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""


def verificar_lista_ordenada(lista, atributo='ISBNCode'):
    """Verifica si una lista está ordenada por un atributo específico.
    
    PROPÓSITO:
    ==========
    Útil para validar el prerequisito de la búsqueda binaria antes de ejecutarla.
    Ayuda a detectar errores donde se intenta buscar en una lista no ordenada.
    
    PARÁMETROS:
    ===========
    lista : list
        Lista de objetos a verificar (Book, Inventory, etc.).
    atributo : str, opcional
        Atributo por el cual verificar el orden (default: 'ISBNCode').
        
    RETORNO:
    ========
    bool
        True si la lista está ordenada ascendentemente, False en caso contrario.
        
    EJEMPLO DE USO:
    ===============
    >>> from utils.search_helpers import verificar_lista_ordenada
    >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    >>> 
    >>> if not verificar_lista_ordenada(inventario):
    ...     print("Ordenando inventario...")
    ...     insercion_ordenada(inventario)
    >>> 
    >>> # Ahora es seguro usar búsqueda binaria
    >>> indice = busqueda_binaria(inventario, isbn_buscado)
    """
    if not lista or len(lista) <= 1:
        return True
    
    for i in range(len(lista) - 1):
        valor_actual = getattr(lista[i], atributo)
        valor_siguiente = getattr(lista[i + 1], atributo)
        
        if valor_actual > valor_siguiente:
            return False
    
    return True


__all__ = ['verificar_lista_ordenada']
