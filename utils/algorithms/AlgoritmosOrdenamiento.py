"""
AlgoritmosOrdenamiento.py

Módulo que contiene algoritmos de ordenamiento para el Sistema de Gestión de Bibliotecas.
Este archivo implementa algoritmos de ordenamiento puros (sin dependencias externas)
que pueden ser utilizados para ordenar colecciones de libros por diferentes atributos.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-11-29
"""


# ==============================================================================
# FUNCIONES AUXILIARES PARA COMPARACIÓN DE ISBNs
# ==============================================================================

def _comparar_isbn_mayor(isbn1, isbn2):
    """
    Compara dos ISBNs numéricamente si es posible, lexicográficamente como fallback.
    
    Esta función resuelve el problema de ordenamiento lexicográfico vs numérico:
    - Lexicográfico: "2" > "123" (incorrecto numéricamente)
    - Numérico: 2 < 123 (correcto)
    
    PARÁMETROS:
    ===========
    isbn1 : str
        Primer ISBN a comparar
    isbn2 : str
        Segundo ISBN a comparar
        
    RETORNO:
    ========
    bool
        True si isbn1 > isbn2 (numéricamente cuando es posible)
    
    EJEMPLOS:
    =========
    >>> _comparar_isbn_mayor("123", "2")
    True  # 123 > 2 (comparación numérica)
    >>> _comparar_isbn_mayor("2", "345")
    False  # 2 < 345 (comparación numérica)
    >>> _comparar_isbn_mayor("ABC", "DEF")
    False  # "ABC" < "DEF" (comparación lexicográfica)
    """
    try:
        # Intentar conversión numérica
        # Si ambos ISBNs son puramente numéricos, compararlos como enteros
        return int(isbn1) > int(isbn2)
    except (ValueError, TypeError):
        # Si la conversión falla (ISBNs con letras o guiones),
        # usar comparación lexicográfica estándar como fallback
        # Esto mantiene compatibilidad con ISBNs con formato "978-..." o similares
        return isbn1 > isbn2


def insercion_ordenada(lista_libros):
    """
    Ordena una lista de objetos Inventory usando el algoritmo de Ordenamiento por Inserción
    (Insertion Sort) basándose en el ISBN en orden ascendente.
    
    PROPÓSITO:
    =========
    El algoritmo de inserción ordena la lista in-place (modifica la lista original)
    comparando cada elemento con los anteriores y desplazándolos para insertar
    el elemento en su posición correcta. Es eficiente para listas pequeñas o
    parcialmente ordenadas.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista de objetos Inventory que se desea ordenar. Cada objeto debe tener
        un método get_isbn() que retorna el ISBN (string o número) que será usado 
        como criterio de ordenamiento.
        
    RETORNO:
    ========
    list
        La misma lista ordenada por ISBN en orden ascendente.
        Nota: La función modifica la lista original (ordenamiento in-place).
    
    COMPLEJIDAD:
    ============
    - Mejor caso: O(n) - cuando la lista ya está ordenada
    - Caso promedio: O(n²)
    - Peor caso: O(n²) - cuando la lista está en orden inverso
    - Espacio: O(1) - no requiere memoria adicional significativa
    
    VENTAJAS:
    =========
    - Simple de implementar y entender
    - Eficiente para listas pequeñas (< 50 elementos)
    - Estable: mantiene el orden relativo de elementos iguales
    - Ordenamiento in-place: no requiere memoria adicional
    - Eficiente para listas parcialmente ordenadas
    
    CASOS DE USO:
    =============
    - Ordenar catálogo de inventarios al cargar desde archivo
    - Mantener lista ordenada al insertar nuevos inventarios
    - Ordenar resultados de búsqueda
    
    EJEMPLO DE USO:
    ===============
    >>> from models.inventory import Inventory
    >>> from models.Books import Book
    >>> inventarios = [
    ...     Inventory(items=[Book(id="B1", ISBNCode="978-3-16-148410-0", ...)]),
    ...     Inventory(items=[Book(id="B2", ISBNCode="978-0-306-40615-7", ...)]),
    ...     Inventory(items=[Book(id="B3", ISBNCode="978-1-234-56789-7", ...)])
    ... ]
    >>> insercion_ordenada(inventarios)
    >>> print([inv.get_isbn() for inv in inventarios])
    ['978-0-306-40615-7', '978-1-234-56789-7', '978-3-16-148410-0']
    """
    
    # VALIDACIÓN INICIAL
    # ==================
    # Si la lista está vacía o tiene un solo elemento, ya está ordenada
    # Esta verificación evita procesar listas triviales y mejora la eficiencia
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros
    
    # ALGORITMO DE INSERCIÓN
    # ======================
    # El algoritmo divide conceptualmente la lista en dos partes:
    # - Parte izquierda: elementos ya ordenados
    # - Parte derecha: elementos por ordenar
    
    # Comenzamos desde el segundo elemento (índice 1) porque el primer elemento
    # (índice 0) se considera trivialmente ordenado por sí solo
    for i in range(1, len(lista_libros)):
        # -----------------------------------------------------------------------
        # PASO 1: SELECCIONAR EL ELEMENTO A INSERTAR
        # -----------------------------------------------------------------------
        # 'inventario_actual' es el inventario que vamos a insertar en su posición correcta
        # dentro de la parte ya ordenada (elementos desde 0 hasta i-1)
        inventario_actual = lista_libros[i]
        
        # Guardamos el ISBN del inventario actual para las comparaciones
        # Usamos get_isbn() que obtiene el ISBN del primer libro en items
        isbn_actual = inventario_actual.get_isbn()
        
        # -----------------------------------------------------------------------
        # PASO 2: ENCONTRAR LA POSICIÓN CORRECTA
        # -----------------------------------------------------------------------
        # 'j' es el índice que usaremos para recorrer la parte ordenada
        # de derecha a izquierda, buscando dónde insertar el inventario_actual
        j = i - 1
        
        # Mientras no lleguemos al inicio de la lista (j >= 0) Y
        # mientras el ISBN del inventario en la posición j sea mayor que el ISBN actual,
        # desplazamos los inventarios una posición a la derecha
        #
        # NOTA IMPORTANTE SOBRE COMPARACIÓN DE ISBNs:
        # Los ISBNs son strings, pero queremos compararlos numéricamente.
        # Usamos una función helper que compara numéricamente cuando es posible,
        # y lexicográficamente como fallback.
        #
        # EXPLICACIÓN DEL DESPLAZAMIENTO:
        # Si el ISBN en posición j es mayor que isbn_actual (comparado numéricamente),
        # significa que el inventario en j debe estar DESPUÉS del inventario_actual.
        # Por lo tanto, movemos lista_libros[j] una posición a la derecha (j+1)
        # para hacer espacio para el inventario_actual.
        while j >= 0 and _comparar_isbn_mayor(lista_libros[j].get_isbn(), isbn_actual):
            # Desplazar el inventario en posición j una posición a la derecha
            lista_libros[j + 1] = lista_libros[j]
            
            # Retroceder el índice para seguir comparando con los elementos anteriores
            j -= 1
        
        # -----------------------------------------------------------------------
        # PASO 3: INSERTAR EL INVENTARIO EN SU POSICIÓN CORRECTA
        # -----------------------------------------------------------------------
        # Cuando salimos del while, tenemos dos posibilidades:
        # 1. j = -1: todos los elementos eran mayores, insertar al inicio
        # 2. j >= 0: encontramos un elemento menor o igual, insertar después de él
        #
        # En ambos casos, la posición correcta es j+1
        lista_libros[j + 1] = inventario_actual
        
        # ESTADO DESPUÉS DE CADA ITERACIÓN:
        # Los elementos desde índice 0 hasta i (inclusive) están ordenados
        # Los elementos desde i+1 hasta el final aún no han sido procesados
    
    # RETORNO
    # =======
    # Retornamos la lista ordenada (aunque la modificación es in-place,
    # retornar la lista permite encadenar operaciones si es necesario)
    return lista_libros


# ==============================================================================
# FUNCIONES AUXILIARES (OPCIONALES - PARA EXTENSIBILIDAD FUTURA)
# ==============================================================================

def insercion_ordenada_reversa(lista_libros):
    """
    Ordena una lista de objetos Libro por ISBN en orden DESCENDENTE.
    
    Esta función es una variante de insercion_ordenada() que ordena
    en sentido inverso. Útil para mostrar los libros más recientes primero
    (asumiendo que ISBNs mayores corresponden a libros más nuevos).
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista de objetos Libro a ordenar.
        
    RETORNO:
    ========
    list
        Lista ordenada por isbn en orden descendente.
    """
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros
    
    for i in range(1, len(lista_libros)):
        libro_actual = lista_libros[i]
        isbn_actual = libro_actual.isbn
        j = i - 1
        
        # CAMBIO CLAVE: Comparación invertida (< en lugar de >)
        while j >= 0 and lista_libros[j].isbn < isbn_actual:
            lista_libros[j + 1] = lista_libros[j]
            j -= 1
        
        lista_libros[j + 1] = libro_actual
    
    return lista_libros


def insercion_ordenada_por_atributo(lista_libros, atributo='isbn', orden='asc'):
    """
    Versión genérica de insercion_ordenada que permite ordenar por cualquier
    atributo y en cualquier dirección.
    
    PROPÓSITO:
    ==========
    Proporciona flexibilidad para ordenar libros por diferentes atributos
    sin necesidad de escribir una función separada para cada caso.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista de objetos Libro a ordenar.
    atributo : str, opcional
        Nombre del atributo por el cual ordenar (default: 'isbn').
        Ejemplos: 'isbn', 'title', 'author', 'price', etc.
    orden : str, opcional
        Dirección del ordenamiento: 'asc' (ascendente) o 'desc' (descendente).
        Default: 'asc'.
        
    RETORNO:
    ========
    list
        Lista ordenada según el atributo y orden especificados.
        
    EJEMPLO:
    ========
    >>> insercion_ordenada_por_atributo(libros, atributo='title', orden='asc')
    >>> insercion_ordenada_por_atributo(libros, atributo='price', orden='desc')
    """
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros
    
    # Determinar la función de comparación según el orden
    if orden.lower() == 'desc':
        comparar = lambda a, b: a < b  # Orden descendente
    else:
        comparar = lambda a, b: a > b  # Orden ascendente (default)
    
    for i in range(1, len(lista_libros)):
        libro_actual = lista_libros[i]
        
        # Obtener el valor del atributo de forma dinámica usando getattr
        # NOTA: Se puede agregar manejo de excepciones aquí si el atributo no existe
        valor_actual = getattr(libro_actual, atributo)
        
        j = i - 1
        
        while j >= 0 and comparar(getattr(lista_libros[j], atributo), valor_actual):
            lista_libros[j + 1] = lista_libros[j]
            j -= 1
        
        lista_libros[j + 1] = libro_actual
    
    return lista_libros


# ==============================================================================
# FUNCIÓN DE VALIDACIÓN (PARA TESTING Y DEBUGGING)
# ==============================================================================

def verificar_ordenamiento(lista_libros, atributo='isbn'):
    """
    Verifica si una lista de libros está ordenada correctamente por un atributo dado.
    
    Útil para testing y validación después de aplicar un algoritmo de ordenamiento.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista de objetos Libro a verificar.
    atributo : str, opcional
        Atributo por el cual verificar el orden (default: 'isbn').
        
    RETORNO:
    ========
    bool
        True si la lista está ordenada en orden ascendente, False en caso contrario.
        
    EJEMPLO:
    ========
    >>> insercion_ordenada(libros)
    >>> if verificar_ordenamiento(libros):
    ...     print("Lista ordenada correctamente")
    """
    if not lista_libros or len(lista_libros) <= 1:
        return True
    
    for i in range(len(lista_libros) - 1):
        valor_actual = getattr(lista_libros[i], atributo)
        valor_siguiente = getattr(lista_libros[i + 1], atributo)
        
        if valor_actual > valor_siguiente:
            return False
    
    return True


# ==============================================================================
# NOTAS PARA SUSTENTACIÓN
# ==============================================================================
"""
PUNTOS CLAVE PARA EXPLICAR EN LA SUSTENTACIÓN:
===============================================

1. COMPLEJIDAD TEMPORAL:
   - Mejor caso O(n): Lista ya ordenada, solo hacemos n-1 comparaciones
   - Peor caso O(n²): Lista en orden inverso, hacemos n*(n-1)/2 comparaciones
   - Caso promedio O(n²): En promedio, cada inserción requiere n/2 comparaciones

2. COMPLEJIDAD ESPACIAL:
   - O(1): Solo usamos variables temporales (libro_actual, j, isbn_actual)
   - No requiere arrays auxiliares ni recursión

3. ESTABILIDAD:
   - El algoritmo es ESTABLE: mantiene el orden relativo de elementos iguales
   - Importante cuando se ordena por un atributo pero se quiere preservar
     el orden de un ordenamiento previo por otro atributo

4. VENTAJAS vs OTROS ALGORITMOS:
   - Más simple que QuickSort o MergeSort
   - Mejor que Selection Sort y Bubble Sort en la práctica
   - Ideal para listas pequeñas o casi ordenadas
   - Usado como sub-rutina en algoritmos híbridos (ej: TimSort de Python)

5. CUÁNDO USAR INSERTION SORT:
   - Listas pequeñas (< 50 elementos)
   - Listas parcialmente ordenadas
   - Cuando se necesita estabilidad
   - Cuando se insertan elementos de forma incremental

6. CUÁNDO NO USAR INSERTION SORT:
   - Listas grandes (> 1000 elementos) -> Usar QuickSort o MergeSort
   - Cuando el rendimiento es crítico -> Usar algoritmos O(n log n)

7. POSIBLES MEJORAS:
   - Binary Insertion Sort: Usar búsqueda binaria para encontrar posición
   - Shell Sort: Variante optimizada de Insertion Sort
   - Ordenamiento adaptativo: Detectar si ya está ordenada

8. INTEGRACIÓN CON EL SISTEMA:
   - Se puede llamar después de cargar libros desde JSON
   - Se puede usar en vistas de listado para mostrar libros ordenados
   - Se puede combinar con algoritmos de búsqueda para mejorar eficiencia
"""
