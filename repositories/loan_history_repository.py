"""loan_history_repository.py

Repositorio para la persistencia del historial de préstamos por usuario (Stacks).
Responsabilidad Única: Persistencia de datos de historial en loan_history.json

El historial es una vista organizada de loan.json por usuario en estructura LIFO.
Se actualiza automáticamente cuando cambian los préstamos.

Estructura del archivo:
{
  "user_stacks": {
    "U001": [
      {
        "user_id": "U001",
        "isbn": "978...",
        "loan_date": "2025-12-03",
        "loan_id": "L002",
        "returned": true
      },
      ...
    ]
  }
}

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-03
"""

import json
import os
from typing import Dict, List, Any
from utils.config import FilePaths
from utils.logger import LibraryLogger

logger = LibraryLogger.get_logger(__name__)


class LoanHistoryRepository:
    """Repositorio para persistir historial de préstamos por usuario.
    
    RESPONSABILIDAD única: Leer/escribir loan_history.json
    NO contiene lógica de negocio ni manejo de estructuras Stack.
    """
    
    def __init__(self, file_path: str = None):
        """Inicializar repositorio de historial de préstamos.
        
        Args:
            file_path: Ruta al archivo JSON. Si es None, usa ruta por defecto
        """
        if file_path is None:
            data_dir = os.path.dirname(FilePaths.LOANS)
            file_path = os.path.join(data_dir, 'loan_history.json')
        
        self.file_path = file_path
        self._ensure_file()
    
    def _ensure_file(self) -> None:
        """Asegurar que el archivo de historial existe."""
        if not os.path.exists(self.file_path):
            logger.info(f"Creando archivo de historial: {self.file_path}")
            self._write_raw_data({"user_stacks": {}})
    
    def _read_raw_data(self) -> Dict[str, Any]:
        """Leer datos crudos del archivo JSON.
        
        Returns:
            Dict con estructura {"user_stacks": {...}}
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, dict) or 'user_stacks' not in data:
                    logger.warning(f"Estructura inválida en {self.file_path}, inicializando vacío")
                    return {"user_stacks": {}}
                return data
        except FileNotFoundError:
            logger.debug(f"Archivo {self.file_path} no encontrado, retornando vacío")
            return {"user_stacks": {}}
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON en {self.file_path}: {e}")
            return {"user_stacks": {}}
        except Exception as e:
            logger.error(f"Error leyendo {self.file_path}: {e}")
            return {"user_stacks": {}}
    
    def _write_raw_data(self, data: Dict[str, Any]) -> None:
        """Escribir datos crudos al archivo JSON.
        
        Args:
            data: Dict con estructura {"user_stacks": {...}}
        """
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Historial guardado en {self.file_path}")
        except Exception as e:
            logger.error(f"Error escribiendo {self.file_path}: {e}")
            raise
    
    def load_all_user_stacks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Cargar todos los stacks de usuarios desde el archivo.
        
        Returns:
            Dict[user_id, List[Dict]] donde cada lista es el stack de ese usuario
            (índice 0 = fondo, índice -1 = tope del stack)
        """
        data = self._read_raw_data()
        user_stacks = data.get('user_stacks', {})
        
        result = {}
        for user_id, stack_items in user_stacks.items():
            if isinstance(stack_items, list):
                result[user_id] = stack_items
            else:
                logger.warning(f"Stack para usuario {user_id} no es lista, ignorando")
                result[user_id] = []
        
        return result
    
    def save_all_user_stacks(self, user_stacks: Dict[str, List[Dict[str, Any]]]) -> None:
        """Guardar todos los stacks de usuarios al archivo.
        
        Args:
            user_stacks: Dict[user_id, List[Dict]] con los stacks de cada usuario
        """
        data = {"user_stacks": user_stacks}
        self._write_raw_data(data)
    
    def load_user_stack(self, user_id: str) -> List[Dict[str, Any]]:
        """Cargar el stack de un usuario específico.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista representando el stack del usuario (vacía si no existe)
        """
        all_stacks = self.load_all_user_stacks()
        return all_stacks.get(user_id, [])
    
    def save_user_stack(self, user_id: str, stack_items: List[Dict[str, Any]]) -> None:
        """Guardar el stack de un usuario específico.
        
        Args:
            user_id: ID del usuario
            stack_items: Lista representando el stack del usuario
        """
        all_stacks = self.load_all_user_stacks()
        all_stacks[user_id] = stack_items
        self.save_all_user_stacks(all_stacks)


__all__ = ['LoanHistoryRepository']
