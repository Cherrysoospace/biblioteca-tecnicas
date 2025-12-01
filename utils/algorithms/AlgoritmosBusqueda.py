"""
AlgoritmosBusqueda.py

Módulo que contiene algoritmos de búsqueda para el Sistema de Gestión de Bibliotecas.
Este archivo implementa algoritmos de búsqueda puros (sin dependencias externas)
que pueden ser utilizados para buscar libros en colecciones ordenadas.

PREREQUISITO IMPORTANTE:
========================
Los algoritmos de búsqueda binaria requieren que la lista esté ORDENADA.
Se asume que la lista ha sido previamente ordenada usando el módulo
AlgoritmosOrdenamiento.py (función insercion_ordenada).

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-01
"""


def busqueda_binaria_recursiva(lista_libros, isbn_buscado, inicio=0, fin=None):
    """
    Busca un libro en una lista ORDENADA por ISBNCode usando Búsqueda Binaria Recursiva.
    
    PROPÓSITO:
    ==========
    La búsqueda binaria es un algoritmo eficiente para encontrar un elemento en una
    lista ordenada. Funciona dividiendo repetidamente el espacio de búsqueda a la mitad,
    descartando la mitad donde el elemento no puede estar. La implementación recursiva
    expresa este concepto de forma natural: cada llamada recursiva trabaja sobre una
    mitad más pequeña del problema original.
    
    PREREQUISITO CRÍTICO:
    =====================
    *** LA LISTA DEBE ESTAR ORDENADA POR ISBNCode ***
    
    Si la lista NO está ordenada, el algoritmo NO funcionará correctamente.
    Antes de usar esta función, asegúrate de ordenar la lista usando:
    
        from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
        insercion_ordenada(lista_libros)
    
    ¿POR QUÉ REQUIERE ORDEN?
    La búsqueda binaria asume que si el elemento del medio es mayor que el buscado,
    TODOS los elementos a la derecha también son mayores (y viceversa). Esta propiedad
    solo es válida en listas ordenadas.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista ORDENADA de objetos Book. Cada objeto debe tener el atributo ISBNCode.
        IMPORTANTE: Si la lista no está ordenada, el resultado será incorrecto.
        
    isbn_buscado : str
        El código ISBN del libro que se desea encontrar. Debe ser un string que
        coincida exactamente con el atributo ISBNCode de algún libro en la lista.
        Ejemplo: "978-3-16-148410-0"
        
    inicio : int, opcional
        Índice donde comienza el segmento de búsqueda en la lista.
        Default: 0 (búsqueda desde el principio de la lista)
        En las llamadas recursivas, este valor cambia para reducir el espacio de búsqueda.
        IMPORTANTE: No modificar este valor en la llamada inicial desde código externo.
        
    fin : int, opcional
        Índice donde termina el segmento de búsqueda en la lista (inclusive).
        Default: None (se calcula como len(lista_libros) - 1 en la primera llamada)
        En las llamadas recursivas, este valor cambia para reducir el espacio de búsqueda.
        IMPORTANTE: No modificar este valor en la llamada inicial desde código externo.
    
    RETORNO:
    ========
    int
        - Si el libro es encontrado: retorna el ÍNDICE (posición) del libro en la lista
        - Si el libro NO es encontrado: retorna -1
        
    EJEMPLO DE RETORNO:
        Si retorna 5: el libro está en lista_libros[5]
        Si retorna -1: el libro no existe en la lista
    
    COMPLEJIDAD:
    ============
    - Tiempo: O(log n) - En cada paso descartamos la mitad de los elementos
    - Espacio: O(log n) - Por la pila de recursión (cada llamada recursiva usa memoria)
    - Comparación con búsqueda lineal O(n): 
      * Para 1,000 libros: búsqueda lineal hace hasta 1,000 comparaciones
                           búsqueda binaria hace máximo 10 comparaciones
      * Para 1,000,000 libros: búsqueda lineal hace hasta 1,000,000 comparaciones
                                búsqueda binaria hace máximo 20 comparaciones
    
    CÓMO FUNCIONA LA RECURSIÓN:
    ============================
    1. CASO BASE (condición de parada):
       - Si inicio > fin: el segmento está vacío, el elemento no existe
       
    2. CASO RECURSIVO (llamada a sí misma):
       - Calcular el punto medio del segmento
       - Comparar el ISBN del medio con el ISBN buscado
       - Si coinciden: retornar el índice medio (ENCONTRADO)
       - Si el ISBN del medio es MAYOR: buscar en la mitad IZQUIERDA (llamada recursiva)
       - Si el ISBN del medio es MENOR: buscar en la mitad DERECHA (llamada recursiva)
    
    EJEMPLO DE EJECUCIÓN:
    =====================
    Lista ordenada por ISBN: [Book("978-0-..."), Book("978-1-..."), Book("978-2-..."), 
                              Book("978-3-..."), Book("978-4-...")]
    Buscando: "978-3-..."
    
    Llamada 1: busqueda_binaria_recursiva(lista, "978-3-...", 0, 4)
        - mid = 2, lista[2].ISBNCode = "978-2-..."
        - "978-2-..." < "978-3-..." → buscar en mitad derecha
        
    Llamada 2: busqueda_binaria_recursiva(lista, "978-3-...", 3, 4)
        - mid = 3, lista[3].ISBNCode = "978-3-..."
        - "978-3-..." == "978-3-..." → ENCONTRADO, retorna 3
    
    VENTAJAS DE LA VERSIÓN RECURSIVA:
    ==================================
    - Código más limpio y legible
    - Expresa naturalmente el concepto de "divide y conquista"
    - Fácil de entender y explicar en sustentaciones
    
    DESVENTAJAS DE LA VERSIÓN RECURSIVA:
    =====================================
    - Usa más memoria (pila de recursión)
    - Puede causar stack overflow en listas MUY grandes (> 10,000 elementos en Python)
    - Ligeramente más lenta que la versión iterativa
    
    USO EN EL SISTEMA:
    ==================
    >>> from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    >>> from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria_recursiva
    >>> 
    >>> # 1. Ordenar la lista primero (REQUISITO)
    >>> insercion_ordenada(lista_libros)
    >>> 
    >>> # 2. Buscar un libro por ISBN
    >>> indice = busqueda_binaria_recursiva(lista_libros, "978-3-16-148410-0")
    >>> 
    >>> # 3. Verificar el resultado
    >>> if indice != -1:
    ...     libro_encontrado = lista_libros[indice]
    ...     print(f"Libro encontrado: {libro_encontrado.title}")
    ... else:
    ...     print("Libro no encontrado")
    
    MODIFICACIONES FUTURAS SUGERIDAS (PARA SUSTENTACIÓN):
    ======================================================
    1. CAMBIAR ATRIBUTO DE BÚSQUEDA:
       - Línea clave: isbn_medio = lista_libros[mid].ISBNCode
       - Cambiar a: titulo_medio = lista_libros[mid].title
       - Requiere que la lista esté ordenada por ese atributo
    
    2. BÚSQUEDA INSENSIBLE A MAYÚSCULAS/MINÚSCULAS:
       - Modificar comparaciones para usar .lower()
       - Ejemplo: isbn_medio.lower() == isbn_buscado.lower()
    
    3. BÚSQUEDA PARCIAL (CONTIENE):
       - Modificar condición de encontrado
       - Ejemplo: isbn_buscado in isbn_medio
       - NOTA: Esto rompe la garantía de O(log n)
    
    4. RETORNAR EL OBJETO EN LUGAR DEL ÍNDICE:
       - Cambiar: return mid
       - Por: return lista_libros[mid]
       - Y retornar None en lugar de -1
    
    5. VERSIÓN GENÉRICA CON PARÁMETRO ATRIBUTO:
       - Agregar parámetro: atributo='ISBNCode'
       - Usar: getattr(lista_libros[mid], atributo)
    """
    
    # =========================================================================
    # INICIALIZACIÓN DEL PARÁMETRO 'fin' EN LA PRIMERA LLAMADA
    # =========================================================================
    # Si es la primera llamada (fin es None), inicializar fin al último índice
    # Esto permite llamar la función sin especificar inicio y fin:
    # busqueda_binaria_recursiva(lista_libros, isbn_buscado)
    if fin is None:
        fin = len(lista_libros) - 1
    
    # =========================================================================
    # CASO BASE 1: LISTA VACÍA
    # =========================================================================
    # Si la lista está vacía, no hay nada que buscar
    # Esta verificación evita errores de índice cuando fin = -1
    if not lista_libros:
        return -1
    
    # =========================================================================
    # CASO BASE 2: SEGMENTO VACÍO (ELEMENTO NO ENCONTRADO)
    # =========================================================================
    # Si inicio > fin, significa que hemos agotado el espacio de búsqueda
    # sin encontrar el elemento. Esta es la condición de parada principal
    # de la recursión.
    #
    # EXPLICACIÓN:
    # - Inicialmente: inicio=0, fin=len-1 (segmento completo)
    # - En cada recursión, reducimos el segmento: inicio aumenta O fin disminuye
    # - Cuando inicio > fin: el segmento se "cruzó", no hay más elementos que revisar
    if inicio > fin:
        return -1
    
    # =========================================================================
    # CALCULAR EL PUNTO MEDIO DEL SEGMENTO ACTUAL
    # =========================================================================
    # El índice medio divide el segmento en dos mitades aproximadamente iguales
    # Usamos división entera (//) para obtener un índice entero
    #
    # EJEMPLO:
    # - Si inicio=0, fin=9 → mid = (0+9)//2 = 4
    # - Si inicio=5, fin=9 → mid = (5+9)//2 = 7
    #
    # NOTA PARA SUSTENTACIÓN:
    # La fórmula (inicio + fin) // 2 puede causar overflow en lenguajes con
    # enteros de tamaño fijo. Una alternativa más segura es:
    # mid = inicio + (fin - inicio) // 2
    # En Python esto no es necesario porque los enteros tienen precisión arbitraria
    mid = (inicio + fin) // 2
    
    # =========================================================================
    # OBTENER EL ISBN DEL LIBRO EN LA POSICIÓN MEDIA
    # =========================================================================
    # Accedemos al objeto Book en la posición media y extraemos su ISBNCode
    #
    # IMPORTANTE PARA SUSTENTACIÓN:
    # Esta línea asume que:
    # 1. lista_libros[mid] es un objeto de la clase Book
    # 2. El objeto tiene un atributo ISBNCode de tipo String
    # 3. La lista está ordenada por ISBNCode en orden ascendente
    #
    # MODIFICACIÓN FUTURA SUGERIDA:
    # Para buscar por otro atributo (ej: title), cambiar esta línea a:
    # valor_medio = lista_libros[mid].title
    # Y asegurarse de que la lista esté ordenada por ese atributo
    isbn_medio = lista_libros[mid].ISBNCode
    
    # =========================================================================
    # COMPARACIÓN 1: ¿ENCONTRAMOS EL LIBRO?
    # =========================================================================
    # Si el ISBN del libro en el medio coincide exactamente con el ISBN buscado,
    # hemos encontrado el libro. Retornamos el índice donde se encuentra.
    #
    # CASO ENCONTRADO - FIN DE LA RECURSIÓN
    if isbn_medio == isbn_buscado:
        return mid  # Retorna el índice donde está el libro
    
    # =========================================================================
    # COMPARACIÓN 2: ¿BUSCAR EN LA MITAD IZQUIERDA?
    # =========================================================================
    # Si el ISBN del medio es MAYOR que el ISBN buscado, sabemos que:
    # - El libro buscado (si existe) debe estar en la mitad IZQUIERDA
    # - Esto es porque la lista está ordenada ascendentemente
    #
    # EXPLICACIÓN DEL ORDEN:
    # En una lista ordenada por ISBN:
    # [978-0-..., 978-1-..., 978-2-..., 978-3-..., 978-4-...]
    #                         ↑ mid
    # Si buscamos "978-1-..." y mid tiene "978-2-...", entonces:
    # - "978-2-..." > "978-1-..." → buscar a la IZQUIERDA de mid
    # - Todos los elementos a la DERECHA de mid son >= "978-2-..."
    # - Por lo tanto, el elemento buscado NO puede estar a la derecha
    #
    # LLAMADA RECURSIVA: Buscar en [inicio, mid-1]
    # - Nuevo segmento: desde 'inicio' hasta 'mid-1' (excluimos mid)
    # - La función se llama a sí misma con un segmento más pequeño
    elif isbn_medio > isbn_buscado:
        # RECURSIÓN: Buscar en la mitad IZQUIERDA
        # Nuevo fin = mid - 1 (excluimos el elemento del medio)
        return busqueda_binaria_recursiva(lista_libros, isbn_buscado, inicio, mid - 1)
    
    # =========================================================================
    # COMPARACIÓN 3: BUSCAR EN LA MITAD DERECHA
    # =========================================================================
    # Si llegamos aquí, es porque isbn_medio < isbn_buscado
    # Esto significa que el libro buscado (si existe) debe estar en la mitad DERECHA
    #
    # EXPLICACIÓN DEL ORDEN:
    # En una lista ordenada por ISBN:
    # [978-0-..., 978-1-..., 978-2-..., 978-3-..., 978-4-...]
    #                         ↑ mid
    # Si buscamos "978-3-..." y mid tiene "978-2-...", entonces:
    # - "978-2-..." < "978-3-..." → buscar a la DERECHA de mid
    # - Todos los elementos a la IZQUIERDA de mid son <= "978-2-..."
    # - Por lo tanto, el elemento buscado NO puede estar a la izquierda
    #
    # LLAMADA RECURSIVA: Buscar en [mid+1, fin]
    # - Nuevo segmento: desde 'mid+1' hasta 'fin' (excluimos mid)
    # - La función se llama a sí misma con un segmento más pequeño
    else:  # isbn_medio < isbn_buscado
        # RECURSIÓN: Buscar en la mitad DERECHA
        # Nuevo inicio = mid + 1 (excluimos el elemento del medio)
        return busqueda_binaria_recursiva(lista_libros, isbn_buscado, mid + 1, fin)


# ==============================================================================
# FUNCIÓN AUXILIAR: BÚSQUEDA BINARIA ITERATIVA (ALTERNATIVA)
# ==============================================================================

def busqueda_binaria_iterativa(lista_libros, isbn_buscado):
    """
    Implementación ITERATIVA de búsqueda binaria (alternativa a la recursiva).
    
    PROPÓSITO:
    ==========
    Esta función hace lo mismo que busqueda_binaria_recursiva, pero usando
    un bucle while en lugar de recursión. Es más eficiente en memoria y
    no tiene riesgo de stack overflow.
    
    VENTAJAS SOBRE LA VERSIÓN RECURSIVA:
    =====================================
    - Usa menos memoria (no hay pila de recursión)
    - Ligeramente más rápida
    - No tiene límite de profundidad de recursión
    - Más eficiente para listas muy grandes
    
    DESVENTAJAS:
    ============
    - Código menos elegante y más "imperativo"
    - Menos intuitiva para entender el concepto "divide y conquista"
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista ORDENADA de objetos Book.
    isbn_buscado : str
        ISBN del libro a buscar.
        
    RETORNO:
    ========
    int
        Índice del libro si se encuentra, -1 en caso contrario.
    
    EJEMPLO:
    ========
    >>> indice = busqueda_binaria_iterativa(lista_libros, "978-3-16-148410-0")
    """
    if not lista_libros:
        return -1
    
    inicio = 0
    fin = len(lista_libros) - 1
    
    # Bucle while: se ejecuta mientras haya elementos por revisar
    while inicio <= fin:
        # Calcular punto medio
        mid = (inicio + fin) // 2
        isbn_medio = lista_libros[mid].ISBNCode
        
        # Comparar con el ISBN buscado
        if isbn_medio == isbn_buscado:
            return mid  # Encontrado
        elif isbn_medio > isbn_buscado:
            fin = mid - 1  # Buscar en mitad izquierda
        else:
            inicio = mid + 1  # Buscar en mitad derecha
    
    # Si salimos del while, el elemento no existe
    return -1


# ==============================================================================
# FUNCIÓN AUXILIAR: BÚSQUEDA BINARIA GENÉRICA POR CUALQUIER ATRIBUTO
# ==============================================================================

def busqueda_binaria_por_atributo(lista_libros, valor_buscado, atributo='ISBNCode'):
    """
    Búsqueda binaria que permite buscar por cualquier atributo del objeto Book.
    
    PROPÓSITO:
    ==========
    Versión flexible que permite buscar libros por diferentes atributos
    (ISBNCode, title, author, etc.) sin necesidad de escribir una función
    separada para cada caso.
    
    PREREQUISITO:
    =============
    La lista DEBE estar ordenada por el mismo atributo que se usa para buscar.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista ORDENADA de objetos Book.
    valor_buscado : str
        Valor del atributo que se desea encontrar.
    atributo : str, opcional
        Nombre del atributo por el cual buscar (default: 'ISBNCode').
        Ejemplos: 'ISBNCode', 'title', 'author', 'price'
        
    RETORNO:
    ========
    int
        Índice del libro si se encuentra, -1 en caso contrario.
        
    EJEMPLO:
    ========
    >>> # Buscar por ISBN
    >>> indice = busqueda_binaria_por_atributo(libros, "978-3-16-148410-0", 'ISBNCode')
    >>> 
    >>> # Buscar por título (lista debe estar ordenada por title)
    >>> indice = busqueda_binaria_por_atributo(libros, "El Quijote", 'title')
    """
    if not lista_libros:
        return -1
    
    inicio = 0
    fin = len(lista_libros) - 1
    
    while inicio <= fin:
        mid = (inicio + fin) // 2
        
        # Obtener el valor del atributo usando getattr
        valor_medio = getattr(lista_libros[mid], atributo)
        
        if valor_medio == valor_buscado:
            return mid
        elif valor_medio > valor_buscado:
            fin = mid - 1
        else:
            inicio = mid + 1
    
    return -1


# ==============================================================================
# FUNCIÓN DE UTILIDAD: VERIFICAR SI LA LISTA ESTÁ ORDENADA
# ==============================================================================

def verificar_lista_ordenada(lista_libros, atributo='ISBNCode'):
    """
    Verifica si una lista de libros está ordenada por un atributo específico.
    
    PROPÓSITO:
    ==========
    Útil para validar el prerequisito de la búsqueda binaria antes de ejecutarla.
    Ayuda a detectar errores de programación donde se intenta buscar en una
    lista no ordenada.
    
    PARÁMETROS:
    ===========
    lista_libros : list
        Lista de objetos Book a verificar.
    atributo : str, opcional
        Atributo por el cual verificar el orden (default: 'ISBNCode').
        
    RETORNO:
    ========
    bool
        True si la lista está ordenada ascendentemente, False en caso contrario.
        
    EJEMPLO DE USO CON BÚSQUEDA BINARIA:
    =====================================
    >>> if not verificar_lista_ordenada(lista_libros):
    ...     print("ERROR: La lista debe estar ordenada antes de buscar")
    ...     insercion_ordenada(lista_libros)
    >>> 
    >>> indice = busqueda_binaria_recursiva(lista_libros, isbn_buscado)
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

1. DIFERENCIA ENTRE BÚSQUEDA LINEAL Y BINARIA:
   - Búsqueda Lineal: O(n) - revisa cada elemento uno por uno
   - Búsqueda Binaria: O(log n) - divide el espacio de búsqueda a la mitad
   
   Ejemplo con 1,000 libros:
   - Lineal: hasta 1,000 comparaciones
   - Binaria: máximo 10 comparaciones (log₂(1000) ≈ 10)

2. PREREQUISITO DEL ORDEN:
   - La búsqueda binaria SOLO funciona en listas ordenadas
   - Si la lista no está ordenada, el resultado es INCORRECTO (no solo lento)
   - Siempre ordenar primero con insercion_ordenada()

3. RECURSIÓN vs ITERACIÓN:
   - Recursiva: Más elegante, más fácil de entender
   - Iterativa: Más eficiente, no usa pila de recursión
   - Ambas tienen la misma complejidad O(log n)

4. ANATOMÍA DE LA RECURSIÓN:
   - Caso base: inicio > fin (segmento vacío)
   - Caso recursivo: dividir en mitad izquierda o derecha
   - Cada llamada reduce el problema a la mitad

5. COMPARACIÓN DE STRINGS EN PYTHON:
   - Los ISBN son strings, Python los compara lexicográficamente
   - "978-0-..." < "978-1-..." < "978-2-..." (orden alfabético/numérico)
   - Esta propiedad permite ordenar y buscar por ISBN

6. CUÁNDO USAR BÚSQUEDA BINARIA:
   - Listas grandes (> 100 elementos)
   - Búsquedas frecuentes
   - Cuando la lista se ordena una vez y se busca muchas veces

7. CUÁNDO NO USAR BÚSQUEDA BINARIA:
   - Listas pequeñas (< 50 elementos) → búsqueda lineal es suficiente
   - Lista cambia constantemente → costo de ordenar supera beneficio
   - Búsquedas infrecuentes → no vale la pena ordenar

8. INTEGRACIÓN CON EL SISTEMA:
   - Ordenar al cargar libros desde JSON
   - Usar búsqueda binaria en formularios de búsqueda
   - Combinar con autocompletado de ISBN

9. POSIBLES MEJORAS:
   - Búsqueda binaria con interpolación (para datos uniformemente distribuidos)
   - Búsqueda binaria exponencial (cuando no se conoce el tamaño)
   - Índices B-tree para búsquedas más complejas

10. MANEJO DE ERRORES:
    - Verificar que la lista no esté vacía
    - Verificar que los objetos tengan el atributo ISBNCode
    - Verificar que la lista esté ordenada (usar verificar_lista_ordenada)
"""
