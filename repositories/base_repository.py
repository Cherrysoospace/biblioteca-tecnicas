"""base_repository.py

Repositorio base para operaciones de persistencia en archivos JSON.
Este módulo implementa el patrón Repository para separar la lógica de negocio
de la lógica de persistencia (Principio de Responsabilidad Única).

Responsabilidad ÚNICA: Persistencia de datos en archivos JSON

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import TypeVar, Generic, List, Callable, Optional, Any
from utils.file_handler import JSONFileHandler


T = TypeVar('T')  # Tipo genérico para el modelo


class BaseRepository(Generic[T]):
    """Repositorio base genérico para operaciones CRUD en archivos JSON.
    
    Este repositorio maneja EXCLUSIVAMENTE la persistencia de datos,
    sin lógica de negocio. Los servicios son responsables de la lógica.
    
    RESPONSABILIDAD ÚNICA:
    ======================
    - Cargar datos desde archivo JSON
    - Guardar datos a archivo JSON
    - Convertir entre objetos del modelo y diccionarios JSON
    
    NO ES RESPONSABLE DE:
    =====================
    - Validaciones de negocio
    - Generación de IDs
    - Ordenamiento o búsquedas
    - Sincronización entre archivos
    
    PARÁMETROS GENÉRICOS:
    =====================
    T : TypeVar
        Tipo del modelo (ej: Book, User, Loan)
    """
    
    def __init__(
        self,
        file_path: str,
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        """Inicializar repositorio.
        
        PARÁMETROS:
        ===========
        file_path : str
            Ruta absoluta al archivo JSON.
        from_dict : Callable[[dict], T]
            Función para convertir dict → objeto del modelo.
        to_dict : Callable[[T], dict]
            Función para convertir objeto del modelo → dict.
        """
        self.file_path = file_path
        self._from_dict = from_dict
        self._to_dict = to_dict
    
    def load_all(self) -> List[T]:
        """Cargar todos los registros desde el archivo JSON.
        
        RETORNO:
        ========
        List[T]
            Lista de objetos del modelo cargados desde JSON.
            
        EXCEPCIONES:
        ============
        ValueError
            Si el JSON es inválido o no es una lista.
        Exception
            Si hay errores de I/O.
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
        """Guardar todos los registros al archivo JSON.
        
        PARÁMETROS:
        ===========
        items : List[T]
            Lista de objetos del modelo a guardar.
            
        RETORNO:
        ========
        None
        
        EXCEPCIONES:
        ============
        Exception
            Si hay errores de I/O al escribir.
        """
        # Asegurar que el archivo existe
        JSONFileHandler.ensure_file(self.file_path, default_content=[])
        
        # Convertir cada objeto a dict
        data = [self._to_dict(item) for item in items]
        
        # Guardar a JSON
        JSONFileHandler.save_json(self.file_path, data)
    
    def clear(self) -> None:
        """Limpiar todos los registros del archivo.
        
        Útil para testing o reset del sistema.
        """
        JSONFileHandler.save_json(self.file_path, [])


class DualFileRepository(Generic[T]):
    """Repositorio para modelos que se persisten en 2 archivos (general + sorted).
    
    Usado por InventoryService que maneja inventory_general.json e inventory_sorted.json.
    
    RESPONSABILIDAD ÚNICA:
    ======================
    - Cargar/guardar archivo general
    - Cargar/guardar archivo ordenado
    
    NO ES RESPONSABLE DE:
    =====================
    - Algoritmos de ordenamiento (responsabilidad del servicio)
    - Sincronización entre archivos (responsabilidad del servicio)
    """
    
    def __init__(
        self,
        general_path: str,
        sorted_path: str,
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        """Inicializar repositorio de doble archivo.
        
        PARÁMETROS:
        ===========
        general_path : str
            Ruta al archivo general (sin ordenar).
        sorted_path : str
            Ruta al archivo ordenado.
        from_dict : Callable[[dict], T]
            Función para convertir dict → objeto.
        to_dict : Callable[[T], dict]
            Función para convertir objeto → dict.
        """
        self.general_path = general_path
        self.sorted_path = sorted_path
        self._from_dict = from_dict
        self._to_dict = to_dict
    
    def load_general(self) -> List[T]:
        """Cargar registros del archivo general."""
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
        """Cargar registros del archivo ordenado."""
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
        """Guardar registros al archivo general."""
        JSONFileHandler.ensure_file(self.general_path, default_content=[])
        data = [self._to_dict(item) for item in items]
        JSONFileHandler.save_json(self.general_path, data)
    
    def save_sorted(self, items: List[T]) -> None:
        """Guardar registros al archivo ordenado."""
        JSONFileHandler.ensure_file(self.sorted_path, default_content=[])
        data = [self._to_dict(item) for item in items]
        JSONFileHandler.save_json(self.sorted_path, data)
    
    def save_both(self, general_items: List[T], sorted_items: List[T]) -> None:
        """Guardar ambos archivos en una operación."""
        self.save_general(general_items)
        self.save_sorted(sorted_items)


__all__ = ['BaseRepository', 'DualFileRepository']
