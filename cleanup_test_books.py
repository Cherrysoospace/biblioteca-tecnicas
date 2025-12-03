"""
Limpieza de libros de prueba TEST.

Elimina todos los libros cuyo ID contenga "TEST" del sistema.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from controllers.book_controller import BookController
from services.book_service import BookService

def main():
    print("Eliminando libros TEST...")
    
    service = BookService()
    controller = BookController()
    
    test_books = [b for b in service.get_all_books() if 'TEST' in b.get_id() or 'Test' in b.get_title()]
    
    print(f"Encontrados {len(test_books)} libros TEST")
    
    for book in test_books:
        try:
            book_id = book.get_id()
            # Marcar como no prestado para poder eliminar
            book.set_isBorrowed(False)
            service._save_books()
            
            controller.delete_book(book_id)
            print(f"  ✓ Eliminado: {book_id}")
        except Exception as e:
            print(f"  ✗ Error al eliminar {book_id}: {e}")
    
    print(f"\n✓ Limpieza completada")

if __name__ == "__main__":
    main()
