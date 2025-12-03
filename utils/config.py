"""config.py

Configuración centralizada de rutas de archivos para el Sistema de Gestión de Bibliotecas.
Este módulo define todas las rutas de archivos JSON utilizados por el sistema.

Beneficios:
- Centralización de rutas (Principio DRY)
- Fácil mantenimiento y modificación
- Evita errores de typos en nombres de archivos
- Facilita testing con rutas alternativas

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import os
from typing import Optional


class FilePaths:
    """Rutas centralizadas de archivos JSON del sistema.
    
    Esta clase provee constantes con las rutas absolutas a todos los archivos
    JSON utilizados por los servicios del sistema de biblioteca.
    
    ESTRUCTURA:
    ===========
    - BASE_DIR: Directorio raíz del proyecto
    - DATA_DIR: Directorio donde se almacenan los archivos JSON
    - Constantes individuales para cada archivo JSON
    
    EJEMPLO DE USO:
    ===============
    >>> from utils.config import FilePaths
    >>> book_service = BookService(FilePaths.BOOKS)
    >>> user_service = UserService(FilePaths.USERS)
    """
    
    # Directorio base del proyecto (parent de utils/)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # Directorio de datos JSON
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # Rutas de archivos JSON principales
    BOOKS = os.path.join(DATA_DIR, 'books.json')
    USERS = os.path.join(DATA_DIR, 'users.json')
    LOANS = os.path.join(DATA_DIR, 'loan.json')
    RESERVATIONS = os.path.join(DATA_DIR, 'reservations.json')
    SHELVES = os.path.join(DATA_DIR, 'shelves.json')
    
    # Rutas de archivos de inventario
    INVENTORY_GENERAL = os.path.join(DATA_DIR, 'inventory_general.json')
    INVENTORY_SORTED = os.path.join(DATA_DIR, 'inventory_sorted.json')
    INVENTORY_VALUE_REPORT = os.path.join(DATA_DIR, 'inventory_value.json')
    
    # Rutas de reportes
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    @staticmethod
    def get_custom_path(filename: str, subdir: Optional[str] = None) -> str:
        """Construir ruta personalizada en el directorio data/ o subdirectorio.
        
        PARÁMETROS:
        ===========
        filename : str
            Nombre del archivo (ej: 'custom_data.json').
        subdir : str, opcional
            Subdirectorio dentro de data/ (ej: 'backups').
            
        RETORNO:
        ========
        str
            Ruta absoluta al archivo.
            
        EJEMPLO:
        ========
        >>> backup_path = FilePaths.get_custom_path('books_backup.json', 'backups')
        >>> # Retorna: '/project/data/backups/books_backup.json'
        """
        if subdir:
            directory = os.path.join(FilePaths.DATA_DIR, subdir)
        else:
            directory = FilePaths.DATA_DIR
        
        return os.path.join(directory, filename)


class DirectoryPaths:
    """Rutas de directorios importantes del sistema.
    
    Esta clase complementa FilePaths con rutas a directorios
    que pueden necesitarse en el sistema.
    """
    
    # Directorios principales
    BASE = FilePaths.BASE_DIR
    DATA = FilePaths.DATA_DIR
    REPORTS = FilePaths.REPORTS_DIR
    
    # Directorios de código
    MODELS = os.path.join(FilePaths.BASE_DIR, 'models')
    SERVICES = os.path.join(FilePaths.BASE_DIR, 'services')
    CONTROLLERS = os.path.join(FilePaths.BASE_DIR, 'controllers')
    UI = os.path.join(FilePaths.BASE_DIR, 'ui')
    UTILS = os.path.join(FilePaths.BASE_DIR, 'utils')
    
    @staticmethod
    def ensure_data_directories() -> None:
        """Asegurar que los directorios de datos necesarios existan.
        
        Crea los directorios data/ y reports/ si no existen.
        Útil para inicialización del sistema.
        """
        for directory in [DirectoryPaths.DATA, DirectoryPaths.REPORTS]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Exportar las clases principales
__all__ = ['FilePaths', 'DirectoryPaths']
