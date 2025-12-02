"""file_handler.py

Módulo centralizado para el manejo de archivos JSON en el Sistema de Gestión de Bibliotecas.
Este módulo elimina la duplicación de código de operaciones de archivos en los servicios.

Responsabilidades:
- Asegurar que archivos y directorios existan
- Leer y escribir archivos JSON con manejo de errores consistente
- Proveer una interfaz unificada para operaciones de persistencia

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import os
import json
from typing import Any, List, Optional


class JSONFileHandler:
    """Manejador centralizado para operaciones de archivos JSON.
    
    Esta clase provee métodos estáticos para operaciones comunes de archivos
    que son usadas por todos los servicios del sistema.
    """

    @staticmethod
    def ensure_file(file_path: str, default_content: Any = None) -> None:
        """Asegurar que un archivo JSON y su directorio existan.
        
        Si el archivo no existe, lo crea con el contenido por defecto.
        Si el directorio no existe, lo crea recursivamente.
        
        PARÁMETROS:
        ===========
        file_path : str
            Ruta absoluta del archivo JSON a asegurar.
        default_content : Any, opcional
            Contenido por defecto para inicializar el archivo si no existe.
            Por defecto es una lista vacía [].
            
        RETORNO:
        ========
        None
        
        EXCEPCIONES:
        ============
        Exception
            Si no se puede crear el directorio o el archivo.
            
        EJEMPLO:
        ========
        >>> JSONFileHandler.ensure_file('/path/to/books.json', [])
        >>> JSONFileHandler.ensure_file('/path/to/config.json', {})
        """
        if default_content is None:
            default_content = []
            
        # Crear directorio si no existe
        directory = os.path.dirname(file_path)
        if directory and not os.path.isdir(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                raise Exception(f"Unable to create directory '{directory}': {e}")
        
        # Crear archivo con contenido por defecto si no existe
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(default_content, f, ensure_ascii=False, indent=2)
            except Exception as e:
                raise Exception(f"Unable to create file '{file_path}': {e}")

    @staticmethod
    def load_json(file_path: str, expected_type: Optional[type] = None) -> Any:
        """Cargar datos desde un archivo JSON.
        
        Lee el archivo JSON y opcionalmente valida que el tipo de datos
        sea el esperado.
        
        PARÁMETROS:
        ===========
        file_path : str
            Ruta absoluta del archivo JSON a leer.
        expected_type : type, opcional
            Tipo esperado de los datos (list, dict, etc.).
            Si se provee y no coincide, lanza ValueError.
            
        RETORNO:
        ========
        Any
            Datos deserializados desde el archivo JSON.
            
        EXCEPCIONES:
        ============
        ValueError
            Si el JSON es inválido o el tipo no coincide con expected_type.
        Exception
            Si hay errores de I/O al leer el archivo.
            
        EJEMPLO:
        ========
        >>> data = JSONFileHandler.load_json('/path/to/books.json', expected_type=list)
        >>> config = JSONFileHandler.load_json('/path/to/config.json', expected_type=dict)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"File '{file_path}' contains invalid JSON: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: '{file_path}'")
        except Exception as e:
            raise Exception(f"Unable to read file '{file_path}': {e}")
        
        # Validar tipo si se especificó
        if expected_type is not None and not isinstance(data, expected_type):
            raise ValueError(
                f"File '{file_path}' must contain {expected_type.__name__}, "
                f"but found {type(data).__name__}"
            )
        
        return data

    @staticmethod
    def save_json(file_path: str, data: Any, indent: int = 2) -> None:
        """Guardar datos a un archivo JSON.
        
        Serializa los datos a JSON y los escribe al archivo con formato
        legible (indentación).
        
        PARÁMETROS:
        ===========
        file_path : str
            Ruta absoluta del archivo JSON donde guardar.
        data : Any
            Datos a serializar (debe ser JSON-serializable).
        indent : int, opcional
            Número de espacios para indentar (default: 2).
            
        RETORNO:
        ========
        None
        
        EXCEPCIONES:
        ============
        TypeError
            Si los datos no son serializables a JSON.
        Exception
            Si hay errores de I/O al escribir el archivo.
            
        EJEMPLO:
        ========
        >>> JSONFileHandler.save_json('/path/to/books.json', [{'id': 'B001', ...}])
        >>> JSONFileHandler.save_json('/path/to/config.json', {'theme': 'dark'})
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
        except TypeError as e:
            raise TypeError(f"Data is not JSON serializable: {e}")
        except Exception as e:
            raise Exception(f"Unable to write to file '{file_path}': {e}")

    @staticmethod
    def ensure_multiple_files(file_paths: List[str], default_content: Any = None) -> None:
        """Asegurar que múltiples archivos JSON existan.
        
        Versión optimizada para crear varios archivos con el mismo contenido
        por defecto (útil para inventory_service que maneja 2 archivos).
        
        PARÁMETROS:
        ===========
        file_paths : List[str]
            Lista de rutas absolutas de archivos a asegurar.
        default_content : Any, opcional
            Contenido por defecto para todos los archivos (default: []).
            
        RETORNO:
        ========
        None
        
        EXCEPCIONES:
        ============
        Exception
            Si no se puede crear algún directorio o archivo.
            
        EJEMPLO:
        ========
        >>> paths = ['/path/to/general.json', '/path/to/sorted.json']
        >>> JSONFileHandler.ensure_multiple_files(paths, [])
        """
        for path in file_paths:
            JSONFileHandler.ensure_file(path, default_content)


__all__ = ['JSONFileHandler']
