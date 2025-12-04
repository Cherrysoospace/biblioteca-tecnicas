"""file_handler.py

Centralized JSON file utilities for the Library Management System.

This module provides a small, focused helper class used across services
to ensure files exist, and to read/write JSON with consistent error handling.

Responsibilities:
- Ensure required directories and JSON files exist
- Load JSON data with validation and clear error messages
- Save JSON data with readable formatting

Author: Library Management System
Date: 2025-12-02
"""

import os
import json
from typing import Any, List, Optional


class JSONFileHandler:
    """A small utility class for JSON file operations.

    All methods are provided as statics; the class groups related helpers
    for ensuring files exist and for reading/writing JSON in a uniform way.

    Usage examples:
        JSONFileHandler.ensure_file('/path/to/data.json', default_content=[])
        data = JSONFileHandler.load_json('/path/to/data.json', expected_type=list)
        JSONFileHandler.save_json('/path/to/data.json', data)
    """

    @staticmethod
    def ensure_file(file_path: str, default_content: Any = None) -> None:
        """Ensure a JSON file and its parent directory exist.

        If the parent directory does not exist it will be created. If the file
        does not exist it will be created and initialized with
        ``default_content`` (defaults to an empty list).

        Parameters
        ----------
        file_path : str
            Absolute or relative path to the JSON file to ensure exists.
        default_content : Any, optional
            Default content to write when creating a new file. Defaults to ``[]``.

        Raises
        ------
        Exception
            When the directory or file cannot be created due to an I/O error.

        Examples
        --------
        >>> JSONFileHandler.ensure_file('/tmp/books.json', [])
        >>> JSONFileHandler.ensure_file('config/settings.json', {})
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
        """Load and return JSON data from a file.

        The file is opened and parsed. If ``expected_type`` is provided the
        deserialized value is validated to be an instance of that type and a
        ValueError is raised when the type does not match.

        Parameters
        ----------
        file_path : str
            Path to the JSON file to read.
        expected_type : Optional[type]
            If provided, assert that the loaded value is an instance of this
            type (for example ``list`` or ``dict``).

        Returns
        -------
        Any
            The Python object resulting from JSON deserialization.

        Raises
        ------
        ValueError
            If the file contains invalid JSON or the type does not match
            ``expected_type``.
        FileNotFoundError
            If the given file does not exist.
        Exception
            For other I/O related errors when opening/reading the file.

        Examples
        --------
        >>> data = JSONFileHandler.load_json('data/books.json', expected_type=list)
        >>> cfg = JSONFileHandler.load_json('config.json', expected_type=dict)
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
        """Serialize Python data to JSON and write it to a file.

        The output is written with UTF-8 encoding and formatted using the
        provided indentation level to keep files human readable.

        Parameters
        ----------
        file_path : str
            Destination path for the JSON file.
        data : Any
            JSON-serializable Python object to write.
        indent : int, optional
            Number of spaces to use for indentation (default: 2).

        Raises
        ------
        TypeError
            If ``data`` is not JSON serializable.
        Exception
            For other I/O related errors when opening/writing the file.

        Examples
        --------
        >>> JSONFileHandler.save_json('data/books.json', books_list)
        >>> JSONFileHandler.save_json('config.json', {'theme': 'dark'})
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
        """Ensure multiple JSON files exist, creating them with default content.

        This is a convenience wrapper that iterates over ``file_paths`` and
        calls :meth:`ensure_file` for each path. Useful when the application
        manages several JSON files with the same initial content.

        Parameters
        ----------
        file_paths : List[str]
            Iterable of file paths to ensure.
        default_content : Any, optional
            Default content to write to any missing files (default: []).

        Raises
        ------
        Exception
            If creating any directory or file fails.

        Examples
        --------
        >>> JSONFileHandler.ensure_multiple_files(['data/a.json', 'data/b.json'], [])
        """
        for path in file_paths:
            JSONFileHandler.ensure_file(path, default_content)


__all__ = ['JSONFileHandler']
