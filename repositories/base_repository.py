"""base_repository.py

Repositorio base para operaciones de persistencia en archivos JSON.
Este módulo implementa el patrón Repository para separar la lógica de negocio
de la lógica de persistencia (Principio de Responsabilidad Única).

Responsabilidad ÚNICA: Persistencia de datos en archivos JSON
"""

from typing import TypeVar, Generic, List, Callable, Optional, Any
from utils.file_handler import JSONFileHandler


T = TypeVar('T')  # Tipo genérico para el modelo


class BaseRepository(Generic[T]):
    """
    Base repository for CRUD operations on JSON files.

    This repository exclusively handles data persistence, separating it from business logic.

    Responsibilities:
    - Load data from JSON files.
    - Save data to JSON files.
    - Convert between model objects and JSON dictionaries.

    Parameters:
    T : TypeVar
        The model type (e.g., Book, User, Loan).
    """

    def __init__(
        self,
        file_path: str,
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        """
        Initialize the repository.

        Args:
            file_path (str): Absolute path to the JSON file.
            from_dict (Callable[[dict], T]): Function to convert a dictionary to a model object.
            to_dict (Callable[[T], dict]): Function to convert a model object to a dictionary.
        """
        self.file_path = file_path
        self._from_dict = from_dict
        self._to_dict = to_dict

    def load_all(self) -> List[T]:
        """
        Load all records from the JSON file.

        Returns:
            List[T]: A list of model objects loaded from the JSON file.

        Raises:
            ValueError: If the JSON is invalid or not a list.
            Exception: If there are I/O errors.
        """
        # Asegurar que el archivo existe
        JSONFileHandler.ensure_file(self.file_path, default_content=[])

        # Cargar datos desde JSON
        data = JSONFileHandler.load_json(self.file_path, expected_type=list)

        # Convertir cada dict a objeto del modelo
        result = []
        for item in data:
            if isinstance(item, dict):
                try:
                    obj = self._from_dict(item)
                    result.append(obj)
                except Exception:
                    # Ignorar registros inválidos (tolerancia a fallos)
                    continue

        return result

    def save_all(self, items: List[T]) -> None:
        """
        Save all records to the JSON file.

        Args:
            items (List[T]): A list of model objects to save.

        Raises:
            Exception: If there are I/O errors during writing.
        """
        # Asegurar que el archivo existe
        JSONFileHandler.ensure_file(self.file_path, default_content=[])

        # Convertir cada objeto a dict
        data = [self._to_dict(item) for item in items]

        # Guardar a JSON
        JSONFileHandler.save_json(self.file_path, data)

    def clear(self) -> None:
        """
        Clear all records from the JSON file.

        Useful for testing or system reset.
        """
        JSONFileHandler.save_json(self.file_path, [])


class DualFileRepository(Generic[T]):
    """
    Repository for models persisted in two files (general and sorted).

    Used by InventoryService to manage inventory_general.json and inventory_sorted.json.

    Responsibilities:
    - Load/save general file.
    - Load/save sorted file.

    Parameters:
    T : TypeVar
        The model type (e.g., Book, User, Loan).
    """

    def __init__(
        self,
        general_path: str,
        sorted_path: str,
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        """
        Initialize the dual-file repository.

        Args:
            general_path (str): Path to the general (unsorted) file.
            sorted_path (str): Path to the sorted file.
            from_dict (Callable[[dict], T]): Function to convert a dictionary to a model object.
            to_dict (Callable[[T], dict]): Function to convert a model object to a dictionary.
        """
        self.general_path = general_path
        self.sorted_path = sorted_path
        self._from_dict = from_dict
        self._to_dict = to_dict

    def load_general(self) -> List[T]:
        """
        Load records from the general file.

        Returns:
            List[T]: A list of model objects loaded from the general file.
        """
        JSONFileHandler.ensure_file(self.general_path, default_content=[])
        data = JSONFileHandler.load_json(self.general_path, expected_type=list)

        result = []
        for item in data:
            if isinstance(item, dict):
                try:
                    result.append(self._from_dict(item))
                except Exception:
                    continue
        return result

    def load_sorted(self) -> List[T]:
        """
        Load records from the sorted file.

        Returns:
            List[T]: A list of model objects loaded from the sorted file.
        """
        JSONFileHandler.ensure_file(self.sorted_path, default_content=[])
        data = JSONFileHandler.load_json(self.sorted_path, expected_type=list)

        result = []
        for item in data:
            if isinstance(item, dict):
                try:
                    result.append(self._from_dict(item))
                except Exception:
                    continue
        return result

    def save_general(self, items: List[T]) -> None:
        """
        Save records to the general file.

        Args:
            items (List[T]): A list of model objects to save.
        """
        JSONFileHandler.ensure_file(self.general_path, default_content=[])
        data = [self._to_dict(item) for item in items]
        JSONFileHandler.save_json(self.general_path, data)

    def save_sorted(self, items: List[T]) -> None:
        """
        Save records to the sorted file.

        Args:
            items (List[T]): A list of model objects to save.
        """
        JSONFileHandler.ensure_file(self.sorted_path, default_content=[])
        data = [self._to_dict(item) for item in items]
        JSONFileHandler.save_json(self.sorted_path, data)

    def save_both(self, general_items: List[T], sorted_items: List[T]) -> None:
        """
        Save both files in one operation.

        Args:
            general_items (List[T]): A list of model objects to save to the general file.
            sorted_items (List[T]): A list of model objects to save to the sorted file.
        """
        self.save_general(general_items)
        self.save_sorted(sorted_items)


__all__ = ['BaseRepository', 'DualFileRepository']
