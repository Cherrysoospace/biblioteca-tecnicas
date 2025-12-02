"""AlgoritmosOrdenamiento.py

Módulo de algoritmos de ordenamiento para el Sistema de Gestión de Bibliotecas.

Este módulo implementa Merge Sort para ordenar el Inventario General de libros
por precio (valor en COP). El algoritmo se implementa manualmente sin usar
las funciones built-in sorted() o .sort() de Python.

Características:
- Merge Sort: Algoritmo de ordenamiento estable O(n log n)
- Ordena objetos Book por precio (menor a mayor)
- Genera reportes globales serializables
- Código modular y reutilizable

¿Por qué Merge Sort?
====================
1. ESTABILIDAD: Merge Sort es un algoritmo estable, lo que significa que preserva
   el orden relativo de elementos con el mismo precio. Ejemplo:
   - Libro A: $10,000 (posición 1)
   - Libro B: $10,000 (posición 2)
   Después del ordenamiento, A seguirá antes que B.

2. COMPLEJIDAD GARANTIZADA: O(n log n) en TODOS los casos (mejor, promedio, peor).
   No hay degradación de rendimiento como en QuickSort (que puede ser O(n²) en
   el peor caso).

3. PREDECIBILIDAD: Ideal para inventarios grandes donde necesitamos rendimiento
   consistente sin importar el estado inicial de los datos.

4. DIVIDE Y CONQUISTA: Facilita el debugging y pruebas al dividir el problema
   en subproblemas más pequeños.

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List, Dict, Any
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)

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



def merge_sort_books_by_price(lista_libros: List[Any]) -> List[Any]:
    """Ordenar una lista de objetos Book por precio usando Merge Sort.
    
    ALGORITMO:
    ==========
    Merge Sort es un algoritmo de ordenamiento basado en el paradigma "Divide y Conquista":
    
    1. DIVIDIR: Dividir la lista en dos mitades aproximadamente iguales
    2. CONQUISTAR: Ordenar recursivamente cada mitad
    3. COMBINAR: Mezclar (merge) las dos mitades ordenadas en una lista ordenada
    
    CASO BASE:
    ----------
    Si la lista tiene 0 o 1 elementos, ya está ordenada (retornar directamente).
    
    PASO RECURSIVO:
    ---------------
    - Dividir lista en mitad izquierda y mitad derecha
    - Ordenar recursivamente cada mitad
    - Combinar las mitades ordenadas usando merge()
    
    COMPLEJIDAD:
    ============
    - Tiempo: O(n log n) en TODOS los casos
      * n divisiones de la lista (cada nivel del árbol de recursión)
      * log n niveles de recursión (altura del árbol)
    - Espacio: O(n) para almacenar las sublistas temporales
    
    ESTABILIDAD:
    ============
    Merge Sort es ESTABLE porque:
    - Durante el merge, cuando dos elementos tienen el mismo precio, siempre
      se toma primero el de la lista izquierda (que venía antes en la lista original)
    - Esto preserva el orden relativo de elementos iguales
    
    PARÁMETROS:
    ===========
    lista_libros : List[Any]
        Lista de objetos Book a ordenar. Cada objeto debe tener el método
        get_price() que retorna el precio como int o float.
        
    RETORNO:
    ========
    List[Any]
        Nueva lista con los mismos objetos Book ordenados por precio
        de menor a mayor (orden ascendente).
        
    EXCEPCIONES:
    ============
    - AttributeError: si algún objeto no tiene el método get_price()
    - TypeError: si get_price() no retorna un valor comparable
    
    EJEMPLO:
    ========
    >>> from models.Books import Book
    >>> libros = [
    ...     Book("B001", "978-1", "Libro C", "Autor", 1.0, 50000, False),
    ...     Book("B002", "978-2", "Libro A", "Autor", 1.0, 20000, False),
    ...     Book("B003", "978-3", "Libro B", "Autor", 1.0, 35000, False),
    ... ]
    >>> ordenados = merge_sort_books_by_price(libros)
    >>> [b.get_price() for b in ordenados]
    [20000, 35000, 50000]
    """
    # CASO BASE: Lista vacía o de un solo elemento ya está ordenada
    if len(lista_libros) <= 1:
        return lista_libros
    
    # DIVIDIR: Encontrar el punto medio de la lista
    punto_medio = len(lista_libros) // 2
    
    # Dividir la lista en dos mitades
    mitad_izquierda = lista_libros[:punto_medio]
    mitad_derecha = lista_libros[punto_medio:]
    
    logger.debug(f"Dividiendo lista de {len(lista_libros)} libros en {len(mitad_izquierda)} + {len(mitad_derecha)}")
    
    # CONQUISTAR: Ordenar recursivamente cada mitad
    # Estas llamadas recursivas seguirán dividiendo hasta llegar al caso base
    izquierda_ordenada = merge_sort_books_by_price(mitad_izquierda)
    derecha_ordenada = merge_sort_books_by_price(mitad_derecha)
    
    # COMBINAR: Mezclar las dos mitades ordenadas
    resultado = merge(izquierda_ordenada, derecha_ordenada)
    
    return resultado


def merge(left: List[Any], right: List[Any]) -> List[Any]:
    """Combinar dos listas ordenadas de Books en una sola lista ordenada por precio.
    
    ALGORITMO:
    ==========
    Este es el corazón de Merge Sort. Combina dos listas ya ordenadas en una
    sola lista ordenada mediante un proceso de "intercalación" (interleaving):
    
    1. Comparar los elementos en las posiciones actuales de ambas listas
    2. Tomar el menor de los dos y agregarlo al resultado
    3. Avanzar el índice de la lista de donde se tomó el elemento
    4. Repetir hasta que se hayan procesado todos los elementos
    5. Agregar los elementos restantes de la lista que aún tenga elementos
    
    INVARIANTE:
    -----------
    En cada iteración del bucle while:
    - El resultado contiene los elementos más pequeños vistos hasta ahora, ordenados
    - left[i:] y right[j:] contienen los elementos aún no procesados
    - Ambas sublistas left y right están ordenadas
    
    PRESERVACIÓN DE ESTABILIDAD:
    ============================
    Cuando left[i].get_price() == right[j].get_price():
    - Siempre tomamos el elemento de LEFT primero
    - Esto preserva el orden original porque left contiene elementos que
      aparecían ANTES en la lista original
    
    PARÁMETROS:
    ===========
    left : List[Any]
        Primera lista de objetos Book, ya ordenada por precio (ascendente)
    right : List[Any]
        Segunda lista de objetos Book, ya ordenada por precio (ascendente)
        
    RETORNO:
    ========
    List[Any]
        Nueva lista que contiene todos los elementos de left y right,
        ordenados por precio de menor a mayor.
        
    COMPLEJIDAD:
    ============
    - Tiempo: O(n + m) donde n = len(left), m = len(right)
      Cada elemento se visita exactamente una vez
    - Espacio: O(n + m) para la lista resultado
    
    EJEMPLO:
    ========
    >>> # Supongamos que tenemos dos listas ordenadas
    >>> left = [libro_20k, libro_35k]   # Precios: [20000, 35000]
    >>> right = [libro_25k, libro_50k]  # Precios: [25000, 50000]
    >>> resultado = merge(left, right)
    >>> [b.get_price() for b in resultado]
    [20000, 25000, 35000, 50000]
    """
    # Lista resultado que contendrá los elementos combinados y ordenados
    resultado = []
    
    # Índices para recorrer las listas left y right
    i = 0  # Índice para la lista left
    j = 0  # Índice para la lista right
    
    # FASE 1: Intercalar elementos mientras ambas listas tengan elementos
    # -----------------------------------------------------------------------
    # Comparamos los elementos actuales de cada lista y tomamos el menor
    while i < len(left) and j < len(right):
        # Obtener precios de los elementos actuales
        precio_izq = left[i].get_price()
        precio_der = right[j].get_price()
        
        # IMPORTANTE: Usar <= en lugar de < garantiza ESTABILIDAD
        # Si los precios son iguales, tomamos el de la izquierda primero
        # (que apareció antes en la lista original)
        if precio_izq <= precio_der:
            resultado.append(left[i])
            i += 1  # Avanzar el índice de la lista izquierda
        else:
            resultado.append(right[j])
            j += 1  # Avanzar el índice de la lista derecha
    
    # FASE 2: Agregar elementos restantes de la lista izquierda
    # ----------------------------------------------------------
    # Si la lista derecha se agotó primero, quedan elementos en left
    while i < len(left):
        resultado.append(left[i])
        i += 1
    
    # FASE 3: Agregar elementos restantes de la lista derecha
    # --------------------------------------------------------
    # Si la lista izquierda se agotó primero, quedan elementos en right
    while j < len(right):
        resultado.append(right[j])
        j += 1
    
    # INVARIANTE POSTCONDICIÓN:
    # - len(resultado) == len(left) + len(right)
    # - resultado está ordenado por precio
    # - todos los elementos de left y right están en resultado
    
    return resultado


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
    - isbn: str - Código ISBN
    - titulo: str - Título del libro
    - autor: str - Nombre del autor
    - peso: float - Peso en kilogramos
    - precio: int - Precio en pesos colombianos (COP)
    - prestado: bool - Estado de préstamo
    
    USO TÍPICO:
    ===========
    1. Ordenar inventario:
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
        'isbn': '978-1234567890',
        'titulo': 'El Quijote',
        'autor': 'Miguel de Cervantes',
        'peso': 1.2,
        'precio': 25000,
        'prestado': False
    }
    """
    reporte = []
    
    logger.info(f"Generando reporte global de {len(lista_ordenada)} libros ordenados por precio")
    
    for libro in lista_ordenada:
        try:
            # Extraer información de cada libro usando sus getters
            libro_dict = {
                'id': libro.get_id(),
                'isbn': libro.get_ISBNCode(),
                'titulo': libro.get_title(),
                'autor': libro.get_author(),
                'peso': libro.get_weight(),
                'precio': libro.get_price(),
                'prestado': libro.get_isBorrowed(),
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


# ==================== FUNCIONES DE UTILIDAD ====================

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
    >>> ordenados = merge_sort_books_by_price(libros)
    >>> assert verificar_ordenamiento(ordenados), "Error: lista no está ordenada"
    """
    if len(lista) <= 1:
        return True
    
    for i in range(len(lista) - 1):
        if lista[i].get_price() > lista[i + 1].get_price():
            return False
    
    return True


__all__ = [
    'insercion_ordenada',
    'merge_sort_books_by_price',
    'merge',
    'generar_reporte_global',
    'ordenar_y_generar_reporte',
    'verificar_ordenamiento',
]

