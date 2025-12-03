"""
AlgoritmosBusqueda.py

Implementa Búsqueda Binaria Recursiva por ISBN sobre Inventario Ordenado.

USO CRÍTICO:
============
Esta función es crítica para verificar si un libro devuelto tiene reservas 
pendientes en la Cola de Espera. Su resultado (posición o no encontrado) debe 
ser utilizado obligatoriamente para asignar el libro a la persona que solicitó 
la reserva según la prioridad.

PREREQUISITO:
=============
El inventario debe estar ORDENADO por ISBN antes de usar esta función.
Usar: AlgoritmosOrdenamiento.insercion_ordenada(inventario)

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""


def busqueda_binaria(inventario_ordenado, isbn_buscado, inicio=0, fin=None):
    """
    Busca un libro por ISBN en el inventario ordenado usando Búsqueda Binaria Recursiva.
    
    PREREQUISITO CRÍTICO:
    =====================
    El inventario DEBE estar ordenado por ISBN. Si no está ordenado, el resultado
    será incorrecto (no solo lento, sino INCORRECTO).
    
    PARÁMETROS:
    ===========
    inventario_ordenado : list
        Lista ORDENADA de objetos Inventory. Cada objeto debe tener método get_isbn().
        
    isbn_buscado : str
        El código ISBN del libro que se desea encontrar.
        
    inicio : int, opcional
        Índice inicial del segmento de búsqueda (default: 0).
        No modificar en la llamada inicial.
        
    fin : int, opcional
        Índice final del segmento de búsqueda (default: len-1).
        No modificar en la llamada inicial.
    
    RETORNO:
    ========
    int
        - Índice (posición) del libro si es encontrado
        - -1 si el libro NO es encontrado
        
    COMPLEJIDAD:
    ============
    - Tiempo: O(log n) - divide el espacio de búsqueda a la mitad en cada paso
    - Espacio: O(log n) - por la pila de recursión
    
    EJEMPLO DE USO:
    ===============
    >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    >>> from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria
    >>> 
    >>> # 1. Ordenar inventario (PREREQUISITO)
    >>> insercion_ordenada(inventario)
    >>> 
    >>> # 2. Buscar libro por ISBN
    >>> indice = busqueda_binaria(inventario, "978-3-16-148410-0")
    >>> 
    >>> # 3. Verificar resultado
    >>> if indice != -1:
    ...     libro_encontrado = inventario[indice]
    ...     print(f"Libro encontrado en posición {indice}")
    ... else:
    ...     print("Libro no encontrado")
    """
    # Si es el primer llamado, calcular el tamaño de la lista
    if fin is None:
        fin = len(inventario_ordenado) - 1
    
    # Caso base: la lista está vacía
    if not inventario_ordenado:
        return -1
    
    # Caso base: la sublista no tiene elementos
    if inicio > fin:
        return -1
    
    # Calcular el punto medio
    medio = (inicio + fin) // 2
    
    # Obtener el ISBN del inventario en la posición media
    isbn_medio = inventario_ordenado[medio].get_isbn()
    
    # Caso base: hemos encontrado el elemento
    if isbn_medio == isbn_buscado:
        return medio
    
    # Caso recursivo: buscar en la mitad izquierda
    # Se mueve una posición a la izquierda (medio - 1)
    elif isbn_medio > isbn_buscado:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, inicio, medio - 1)
    
    # Caso recursivo: buscar en la mitad derecha
    # Se mueve una posición a la derecha (medio + 1)
    else:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, medio + 1, fin)


__all__ = ['busqueda_binaria']

