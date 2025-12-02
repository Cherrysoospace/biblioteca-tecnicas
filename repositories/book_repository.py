"""book_repository.py

Repositorio para la persistencia de libros.
Responsabilidad ÚNICA: Persistencia de datos de libros en books.json

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List
from models.Books import Book
from repositories.base_repository import BaseRepository
from utils.config import FilePaths


def _book_from_dict(data: dict) -> Book:
    """Convertir diccionario a objeto Book."""
    return Book(
        data['id'],
        data['ISBNCode'],
        data['title'],
        data['author'],
        float(data['weight']),
        int(data['price']),
        bool(data.get('isBorrowed', False))
    )


def _book_to_dict(book: Book) -> dict:
    """Convertir objeto Book a diccionario."""
    return {
        'id': book.get_id(),
        'ISBNCode': book.get_ISBNCode(),
        'title': book.get_title(),
        'author': book.get_author(),
        'weight': book.get_weight(),
        'price': book.get_price(),
        'isBorrowed': book.get_isBorrowed(),
    }


class BookRepository(BaseRepository[Book]):
    """Repositorio para persistencia de libros.
    
    RESPONSABILIDAD ÚNICA: Leer/escribir books.json
    """
    
    def __init__(self, file_path: str = None):
        """Inicializar repositorio de libros."""
        path = file_path or FilePaths.BOOKS
        super().__init__(path, _book_from_dict, _book_to_dict)


__all__ = ['BookRepository']
