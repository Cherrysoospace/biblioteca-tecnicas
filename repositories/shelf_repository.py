"""shelf_repository.py

Repositorio para la persistencia de estanterías (shelves.json).

Implementa la conversión dict <-> Shelf y delega la lectura/escritura a
`BaseRepository` y `JSONFileHandler` siguiendo el patrón de `book_repository`.
"""

from typing import List
from models.shelf import Shelf
from models.Books import Book
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _shelf_from_dict(data: dict) -> Shelf:
    """Convertir dict a objeto Shelf (reconstruye también Book instances).

    Intenta crear objetos Book con los campos esperados; si algún registro
    está mal formado se ignora pero la carga continúa (tolerancia a fallos).
    """
    books: List[Book] = []
    for bd in data.get('books', []) or []:
        # ignore non-dict entries quickly
        if not isinstance(bd, dict):
            continue
        # require minimal fields to consider a book valid
        if bd.get('id') is None or bd.get('ISBNCode') is None or bd.get('title') is None:
            # skip entries that lack essential information
            continue
        try:
            book = Book(
                bd.get('id'),
                bd.get('ISBNCode'),
                bd.get('title'),
                bd.get('author'),
                bd.get('weight'),
                bd.get('price'),
                bd.get('isBorrowed', False),
            )
            books.append(book)
        except Exception:
            # ignorar libro inválido pero continuar
            continue

    shelf = Shelf(data.get('id'), books=books, capacity=data.get('capacity', 8.0))
    if data.get('name') is not None:
        try:
            shelf.set_name(data.get('name', ''))
        except Exception:
            pass
    return shelf


def _shelf_to_dict(shelf: Shelf) -> dict:
    """Convertir Shelf a dict JSON-serializable.

    Serializa los libros contenidos usando los getters del objeto Book
    cuando estén disponibles; en caso contrario, cae a representaciones
    alternativas para mantener estabilidad en el archivo JSON.
    """
    books_serialized = []
    books_list = getattr(shelf, '_Shelf__books', []) or []
    for b in books_list:
        try:
            books_serialized.append({
                'id': b.get_id(),
                'ISBNCode': b.get_ISBNCode(),
                'title': b.get_title(),
                'author': b.get_author(),
                'weight': b.get_weight(),
                'price': b.get_price(),
                'isBorrowed': b.get_isBorrowed(),
            })
        except Exception:
            # Fallbacks: to_dict, __dict__, or str
            if hasattr(b, 'to_dict'):
                try:
                    books_serialized.append(b.to_dict())
                    continue
                except Exception:
                    pass
            if hasattr(b, '__dict__'):
                books_serialized.append(b.__dict__)
            else:
                books_serialized.append(str(b))

    return {
        'id': getattr(shelf, '_Shelf__id', None),
        'name': getattr(shelf, '_Shelf__name', ''),
        'capacity': shelf.capacity,
        'books': books_serialized,
    }


class ShelfRepository(BaseRepository[Shelf]):
    """Repositorio para persistencia de estanterías.

    Por defecto usa la ruta definida en `utils.config.FilePaths.SHELVES`.
    """

    def __init__(self, file_path: str = None):
        path = file_path or FilePaths.SHELVES
        super().__init__(path, _shelf_from_dict, _shelf_to_dict)


__all__ = ['ShelfRepository']
