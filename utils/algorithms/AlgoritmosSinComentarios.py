

def busqueda_binaria_recursiva(lista_libros, isbn_buscado, inicio=0, fin=None):
    if fin is None:
        fin = len(lista_libros) - 1

    if inicio > fin:
        return -1

    mid = (inicio + fin) // 2
    isbn_medio = lista_libros[mid].ISBNCode

    if isbn_medio == isbn_buscado:
        return mid
    elif isbn_medio > isbn_buscado:
        return busqueda_binaria_recursiva(lista_libros, isbn_buscado, inicio, mid - 1)
    else:
        return busqueda_binaria_recursiva(lista_libros, isbn_buscado, mid + 1, fin)


def _comparar_isbn_mayor(isbn1, isbn2):
    try:
        return int(isbn1) > int(isbn2)
    except (ValueError, TypeError):
        return isbn1 > isbn2


def insercion_ordenada(lista_libros):
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros
    
    for i in range(1, len(lista_libros)):
        inventario_actual = lista_libros[i]
        isbn_actual = inventario_actual.get_isbn()
        j = i - 1
        
        while j >= 0 and _comparar_isbn_mayor(lista_libros[j].get_isbn(), isbn_actual):
            lista_libros[j + 1] = lista_libros[j]
            j -= 1
        
        lista_libros[j + 1] = inventario_actual
    
    return lista_libros