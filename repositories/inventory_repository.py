"""inventory_repository.py

Repositorio para la persistencia del inventario.
Responsabilidad Única: Persistencia de datos de inventario en inventory_value.json e inventory_sorted.json

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import List, Dict
from models.inventory import Inventory
from models.Books import Book
from utils.file_handler import JSONFileHandler
from utils.config import FilePaths


class InventoryRepository:
    """Repositorio para persistencia de inventario.
    
    RESPONSABILIDAD única: Leer/escribir inventory_value.json e inventory_sorted.json
    
    Nota: Este repositorio NO usa DualFileRepository porque maneja listas de Inventory,
    no un solo objeto Inventory. El formato es diferente.
    """
    
    def __init__(self, general_path: str = None, sorted_path: str = None):
        """Inicializar repositorio de inventario."""
        self.general_path = general_path or FilePaths.INVENTORY_GENERAL
        self.sorted_path = sorted_path or FilePaths.INVENTORY_SORTED
    
    def load_general(self) -> List[Inventory]:
        """Cargar inventario general desde archivo.
        
        Formato esperado:
        [
          {
            "stock": 2,
            "items": [
              {"id": "B001", "ISBNCode": "...", "title": "...", ...},
              {"id": "B002", "ISBNCode": "...", "title": "...", ...}
            ]
          },
          ...
        ]
        
        Returns:
            List[Inventory]: Lista de grupos de inventario
        """
        try:
            data = JSONFileHandler.load_json(self.general_path, expected_type=list)
        except Exception:
            return []
        
        loaded: List[Inventory] = []
        for group in data:
            if not isinstance(group, dict):
                continue
            
            items_data = group.get('items', [])
            books: List[Book] = []
            
            for item in items_data:
                if not isinstance(item, dict):
                    continue
                try:
                    book = Book(
                        item['id'],
                        item['ISBNCode'],
                        item['title'],
                        item['author'],
                        float(item['weight']),
                        int(item['price']),
                        bool(item.get('isBorrowed', False))
                    )
                    books.append(book)
                except Exception:
                    continue
            
            # Compute stock as AVAILABLE copies (not borrowed) to keep the
            # stored 'stock' field consistent with current borrow flags.
            try:
                stock = sum(1 for b in books if not b.get_isBorrowed())
            except Exception:
                stock = int(group.get('stock', len(books)))
            inventory = Inventory(stock=stock, items=books)
            loaded.append(inventory)
        
        return loaded
    
    def save_general(self, inventories: List[Inventory]) -> None:
        """Guardar inventario general en archivo.
        
        Args:
            inventories: Lista de grupos de inventario a guardar
        """
        data = []
        for inventory in inventories:
            group = {
                'stock': inventory.get_stock(),
                'items': []
            }
            
            for book in inventory.get_items():
                group['items'].append({
                    'id': book.get_id(),
                    'ISBNCode': book.get_ISBNCode(),
                    'title': book.get_title(),
                    'author': book.get_author(),
                    'weight': book.get_weight(),
                    'price': book.get_price(),
                    'isBorrowed': book.get_isBorrowed(),
                })
            
            data.append(group)
        
        JSONFileHandler.save_json(self.general_path, data)
    
    def save_sorted(self, inventories: List[Inventory]) -> None:
        """Guardar inventario ordenado en archivo.
        
        Args:
            inventories: Lista de grupos de inventario ordenados a guardar
        """
        data = []
        for inventory in inventories:
            group = {
                'stock': inventory.get_stock(),
                'items': []
            }
            
            for book in inventory.get_items():
                group['items'].append({
                    'id': book.get_id(),
                    'ISBNCode': book.get_ISBNCode(),
                    'title': book.get_title(),
                    'author': book.get_author(),
                    'weight': book.get_weight(),
                    'price': book.get_price(),
                    'isBorrowed': book.get_isBorrowed(),
                })
            
            data.append(group)
        
        JSONFileHandler.save_json(self.sorted_path, data)
    
    def save_both(self, general_inventories: List[Inventory], sorted_inventories: List[Inventory]) -> None:
        """Guardar ambos archivos de inventario.
        
        Args:
            general_inventories: Inventario general (sin ordenar)
            sorted_inventories: Inventario ordenado por ISBN
        """
        self.save_general(general_inventories)
        self.save_sorted(sorted_inventories)


__all__ = ['InventoryRepository']
