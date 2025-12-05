"""loan_history_repository.py

Repository for persisting loan history per user (Stacks).
Single Responsibility: Persistence of history data in loan_history.json

The history is an organized view of loan.json by user in LIFO structure.
It is automatically updated when loans change.

File structure (Array/Stack format):
[
  "user_stacks",
  [
    {
      "U001": [
        {
          "user_id": "U001",
          "isbn": "978...",
          "loan_date": "2025-12-03",
          "loan_id": "L002",
          "returned": true
        },
        ...
      ],
      "U002": [...]
    }
  ]
]
"""

import json
import os
from typing import Dict, List, Any
from utils.config import FilePaths
from utils.logger import LibraryLogger

logger = LibraryLogger.get_logger(__name__)


class LoanHistoryRepository:
    """Repository for persisting loan history per user.
    
    SINGLE RESPONSIBILITY: Read/write loan_history.json
    Does NOT contain business logic or Stack structure handling.
    """
    
    def __init__(self, file_path: str = None):
        """Initialize loan history repository.
        
        Args:
            file_path: Path to JSON file. If None, uses default path
        """
        if file_path is None:
            data_dir = os.path.dirname(FilePaths.LOANS)
            file_path = os.path.join(data_dir, 'loan_history.json')
        
        self.file_path = file_path
        self._ensure_file()
    
    def _ensure_file(self) -> None:
        """Ensure that the history file exists."""
        if not os.path.exists(self.file_path):
            logger.info(f"Creando archivo de historial: {self.file_path}")
            self._write_raw_data({})
    
    def _read_raw_data(self) -> Dict[str, Any]:
        """Read raw data from JSON file.
        
        Returns:
            Dict with user stacks extracted from array format
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # El archivo debe ser un array: ["user_stacks", [{...}]]
                if isinstance(data, list) and len(data) >= 2:
                    if data[0] == "user_stacks":
                        # data[1] debe ser un array con un dict dentro
                        if isinstance(data[1], list) and len(data[1]) > 0:
                            if isinstance(data[1][0], dict):
                                return data[1][0]
                        # O puede ser directamente un dict (formato anterior)
                        elif isinstance(data[1], dict):
                            return data[1]
                    logger.warning(f"Estructura inválida en {self.file_path}, inicializando vacío")
                    return {}
                # Compatibilidad con formato antiguo {"user_stacks": {...}}
                elif isinstance(data, dict) and 'user_stacks' in data:
                    logger.warning(f"Convirtiendo formato antiguo de {self.file_path}")
                    return data['user_stacks']
                # Compatibilidad con formato [{user_stacks: {...}}]
                elif isinstance(data, list) and len(data) > 0:
                    obj = data[0]
                    if isinstance(obj, dict) and 'user_stacks' in obj:
                        return obj['user_stacks']
                    logger.warning(f"Estructura inválida en {self.file_path}, inicializando vacío")
                    return {}
                else:
                    logger.warning(f"Estructura inválida en {self.file_path}, inicializando vacío")
                    return {}
        except FileNotFoundError:
            logger.debug(f"Archivo {self.file_path} no encontrado, retornando vacío")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON en {self.file_path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error leyendo {self.file_path}: {e}")
            return {}
    
    def _write_raw_data(self, user_stacks: Dict[str, List[Dict[str, Any]]]) -> None:
        """Write raw data to JSON file.
        
        Args:
            user_stacks: Dict with user stacks to save
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            # Formato de pila: ["user_stacks", [{...}]]
            data = ["user_stacks", [user_stacks]]
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Historial guardado en {self.file_path}")
        except Exception as e:
            logger.error(f"Error escribiendo {self.file_path}: {e}")
            raise
    
    def load_all_user_stacks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load all user stacks from the file.
        
        Returns:
            Dict[user_id, List[Dict]] where each list is that user's stack
            (index 0 = bottom, index -1 = top of stack)
        """
        user_stacks = self._read_raw_data()
        
        result = {}
        for user_id, stack_items in user_stacks.items():
            if isinstance(stack_items, list):
                result[user_id] = stack_items
            else:
                logger.warning(f"Stack para usuario {user_id} no es lista, ignorando")
                result[user_id] = []
        
        return result
    
    def save_all_user_stacks(self, user_stacks: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save all user stacks to the file.
        
        Args:
            user_stacks: Dict[user_id, List[Dict]] with each user's stacks
        """
        self._write_raw_data(user_stacks)
    
    def load_user_stack(self, user_id: str) -> List[Dict[str, Any]]:
        """Load a specific user's stack.
        
        Args:
            user_id: User ID
            
        Returns:
            List representing the user's stack (empty if it doesn't exist)
        """
        all_stacks = self.load_all_user_stacks()
        return all_stacks.get(user_id, [])
    
    def save_user_stack(self, user_id: str, stack_items: List[Dict[str, Any]]) -> None:
        """Save a specific user's stack.
        
        Args:
            user_id: User ID
            stack_items: List representing the user's stack
        """
        all_stacks = self.load_all_user_stacks()
        all_stacks[user_id] = stack_items
        self.save_all_user_stacks(all_stacks)


__all__ = ['LoanHistoryRepository']
