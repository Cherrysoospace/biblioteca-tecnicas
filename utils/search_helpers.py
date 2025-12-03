"""search_helpers.py

Funciones auxiliares para validación y soporte de búsquedas en el sistema.

Incluye:
- Normalización de texto para búsquedas insensibles a mayúsculas y acentos
- Validación de listas ordenadas para prerequisitos de búsqueda binaria

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-03
"""


def normalizar_texto(texto):
    """Normaliza texto para búsquedas insensibles a mayúsculas y acentos.
    
    PROPÓSITO:
    ==========
    Facilita la búsqueda de libros permitiendo que el usuario busque sin
    preocuparse por mayúsculas, minúsculas o acentos.
    
    TRANSFORMACIONES:
    =================
    1. Convierte a minúsculas
    2. Elimina acentos (á→a, é→e, í→i, ó→o, ú→u, ñ→n)
    3. Elimina espacios extra
    
    PARÁMETROS:
    ===========
    texto : str
        Texto a normalizar (título, autor, criterio de búsqueda).
        
    RETORNO:
    ========
    str
        Texto normalizado en minúsculas sin acentos.
        
    EJEMPLO DE USO:
    ===============
    >>> from utils.search_helpers import normalizar_texto
    >>> 
    >>> # Normalizar para comparación
    >>> titulo = "Cien Años de Soledad"
    >>> busqueda = "cien anos"
    >>> 
    >>> if normalizar_texto(busqueda) in normalizar_texto(titulo):
    ...     print("¡Coincidencia encontrada!")
    
    CASOS DE PRUEBA:
    ================
    >>> normalizar_texto("García Márquez")
    'garcia marquez'
    >>> normalizar_texto("JOSÉ")
    'jose'
    >>> normalizar_texto("Año Nuevo")
    'ano nuevo'
    """
    if not texto:
        return ""
    
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Tabla de reemplazo para acentos comunes en español
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ñ': 'n', 'ç': 'c'
    }
    
    # Aplicar reemplazos
    for acento, sin_acento in reemplazos.items():
        texto = texto.replace(acento, sin_acento)
    
    # Eliminar espacios extra
    texto = ' '.join(texto.split())
    
    return texto


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


__all__ = ['normalizar_texto', 'verificar_lista_ordenada']
