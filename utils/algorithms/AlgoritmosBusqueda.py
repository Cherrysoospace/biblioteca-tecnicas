"""
AlgoritmosBusqueda.py

Implementa algoritmos de búsqueda recursivos para el sistema de biblioteca:
1. Búsqueda Binaria: por ISBN sobre Inventario Ordenado (O(log n))
2. Búsqueda Lineal: por Título o Autor sobre Inventario General (O(n))

BÚSQUEDA BINARIA - USO CRÍTICO:
================================
Esta función es crítica para verificar si un libro devuelto tiene reservas 
pendientes en la Cola de Espera. Su resultado (posición o no encontrado) debe 
ser utilizado obligatoriamente para asignar el libro a la persona que solicitó 
la reserva según la prioridad.

PREREQUISITO BÚSQUEDA BINARIA:
===============================
El inventario debe estar ORDENADO por ISBN antes de usar esta función.
Usar: AlgoritmosOrdenamiento.insercion_ordenada(inventario)

BÚSQUEDA LINEAL - USO:
======================
Para buscar libros por Título o Autor en el Inventario General (no requiere 
ordenamiento). Útil para búsquedas flexibles y parciales de texto.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-03
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


def busqueda_lineal(inventario, criterio_busqueda, indice=0):
    """
    Busca libros por Título o Autor en el inventario usando Búsqueda Lineal Recursiva.
    
    CARACTERÍSTICAS:
    ================
    - NO requiere que el inventario esté ordenado (trabaja sobre Inventario General)
    - Búsqueda PARCIAL: encuentra coincidencias aunque no sea texto exacto
    - Insensible a mayúsculas/minúsculas
    - Recursiva: sigue el patrón de búsqueda lineal enseñado en clase
    
    PARÁMETROS:
    ===========
    inventario : list
        Lista de objetos Inventory (NO necesita estar ordenada).
        
    criterio_busqueda : str
        Texto a buscar en el título o autor del libro.
        Puede ser parcial (ej: "Quijote" encontrará "Don Quijote de la Mancha").
        
    indice : int, opcional
        Índice actual de búsqueda (default: 0).
        No modificar en la llamada inicial - uso interno de la recursión.
    
    RETORNO:
    ========
    int
        - Índice (posición) del primer libro que coincida con el criterio
        - -1 si NO se encuentra ninguna coincidencia
        
    COMPLEJIDAD:
    ============
    - Tiempo: O(n) - en el peor caso revisa todos los elementos
    - Espacio: O(n) - por la pila de recursión
    
    EJEMPLO DE USO:
    ===============
    >>> from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal
    >>> 
    >>> # Buscar por título parcial
    >>> indice = busqueda_lineal(inventario_general, "quijote")
    >>> 
    >>> # Buscar por autor
    >>> indice = busqueda_lineal(inventario_general, "garcía márquez")
    >>> 
    >>> # Verificar resultado
    >>> if indice != -1:
    ...     libro_encontrado = inventario_general[indice].get_book()
    ...     print(f"Libro encontrado: {libro_encontrado.get_title()}")
    ... else:
    ...     print("No se encontró ningún libro con ese criterio")
    
    NOTA TÉCNICA:
    =============
    Esta función utiliza funciones auxiliares de normalización de texto
    para hacer la búsqueda insensible a mayúsculas y acentos.
    Ver: utils.search_helpers.normalizar_texto()
    """
    # Caso base: hemos llegado al final de la lista sin encontrar el elemento
    if indice >= len(inventario):
        return -1
    
    # Obtener el libro actual del inventario
    libro_actual = inventario[indice].get_book()
    
    # Si no hay libro en esta posición del inventario, continuar
    if libro_actual is None:
        # Caso recursivo: seguir buscando en el resto de la lista
        return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
    
    # Obtener título y autor del libro actual
    titulo = libro_actual.get_title() or ""
    autor = libro_actual.get_author() or ""
    
    # Importar función auxiliar para normalizar texto (insensible a mayúsculas/acentos)
    from utils.search_helpers import normalizar_texto
    
    # Normalizar todas las cadenas para comparación
    criterio_norm = normalizar_texto(criterio_busqueda)
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    
    # Caso base: hemos encontrado el elemento
    # Buscar coincidencia PARCIAL en título o autor
    if criterio_norm in titulo_norm or criterio_norm in autor_norm:
        return indice
    
    # Caso recursivo: seguir buscando en el resto de la lista
    return busqueda_lineal(inventario, criterio_busqueda, indice + 1)


__all__ = ['busqueda_binaria', 'busqueda_lineal']

