"""utils.config.py

Centralized file path configuration for the Library Management System.

This module defines absolute paths to the JSON data files and commonly used
directories. Providing a single place for paths reduces duplication, eases
testing, and avoids typos when accessing data files across the project.

Public classes:
 - FilePaths: constants for specific JSON files and helper to build custom
   paths inside the data directory.
 - DirectoryPaths: directory paths derived from FilePaths and a helper to
   ensure required directories exist on disk.

Example:
    >>> from utils.config import FilePaths
    >>> print(FilePaths.BOOKS)
    >>> backup = FilePaths.get_custom_path('books_backup.json', subdir='backups')
"""

from __future__ import annotations

import os
from typing import Optional


class FilePaths:
    """File path constants and helpers for JSON data used by the system.

    Attributes
    ----------
    BASE_DIR: str
        Absolute path to the project root (parent directory of `utils/`).
    DATA_DIR: str
        Absolute path to the `data/` directory where JSON files are stored.
    BOOKS, USERS, LOANS, RESERVATIONS, SHELVES: str
        Absolute paths to common JSON files used by services and repositories.
    INVENTORY_GENERAL, INVENTORY_SORTED, INVENTORY_VALUE_REPORT: str
        Absolute paths to inventory-related JSON reports.
    REPORTS_DIR: str
        Absolute path to the `reports/` directory used for generated reports.

    Methods
    -------
    get_custom_path(filename: str, subdir: Optional[str] = None) -> str
        Build an absolute path for `filename` inside `data/` or a subdirectory
        of `data/`.

    Notes
    -----
    This class is purely a container of constants and a small helper. It
    does not perform any I/O on import, making it safe to import from
    anywhere in the project.
    """

    # Project base directory (parent of utils/)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # Data directory for JSON files
    DATA_DIR = os.path.join(BASE_DIR, 'data')

    # Primary JSON data file paths
    BOOKS = os.path.join(DATA_DIR, 'books.json')
    USERS = os.path.join(DATA_DIR, 'users.json')
    LOANS = os.path.join(DATA_DIR, 'loan.json')
    RESERVATIONS = os.path.join(DATA_DIR, 'reservations.json')
    SHELVES = os.path.join(DATA_DIR, 'shelves.json')

    # Inventory-related files
    INVENTORY_GENERAL = os.path.join(DATA_DIR, 'inventory_general.json')
    INVENTORY_SORTED = os.path.join(DATA_DIR, 'inventory_sorted.json')
    INVENTORY_VALUE_REPORT = os.path.join(DATA_DIR, 'inventory_value.json')

    # Directory for generated reports
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

    @staticmethod
    def get_custom_path(filename: str, subdir: Optional[str] = None) -> str:
        """Return an absolute path for a file inside the `data/` directory.

        Parameters
        ----------
        filename:
            The filename to join (for example, 'custom_data.json').
        subdir:
            Optional subdirectory under `data/` (for example, 'backups'). If
            omitted, the file is placed directly under `data/`.

        Returns
        -------
        str
            Absolute path pointing to the constructed location.

        Examples
        --------
        >>> FilePaths.get_custom_path('books_backup.json', 'backups')
        '/path/to/project/data/backups/books_backup.json'
        """
        if subdir:
            directory = os.path.join(FilePaths.DATA_DIR, subdir)
        else:
            directory = FilePaths.DATA_DIR

        return os.path.join(directory, filename)


class DirectoryPaths:
    """Common directory paths derived from `FilePaths`.

    This complement class exposes directory-level paths that are frequently
    useful to other modules (models, services, controllers, UI, etc.). It
    also provides a helper to create the `data/` and `reports/` directories
    if they do not exist.

    Attributes
    ----------
    BASE, DATA, REPORTS: str
        Absolute paths for base project directory, data directory and
        reports directory respectively.
    MODELS, SERVICES, CONTROLLERS, UI, UTILS: str
        Absolute paths for common code directories inside the project.
    """

    # Primary directories
    BASE = FilePaths.BASE_DIR
    DATA = FilePaths.DATA_DIR
    REPORTS = FilePaths.REPORTS_DIR

    # Code directories
    MODELS = os.path.join(FilePaths.BASE_DIR, 'models')
    SERVICES = os.path.join(FilePaths.BASE_DIR, 'services')
    CONTROLLERS = os.path.join(FilePaths.BASE_DIR, 'controllers')
    UI = os.path.join(FilePaths.BASE_DIR, 'ui')
    UTILS = os.path.join(FilePaths.BASE_DIR, 'utils')

    @staticmethod
    def ensure_data_directories() -> None:
        """Create `data/` and `reports/` directories when missing.

        This is a convenience initialization helper used at startup or in
        tests to ensure the filesystem layout required by the application
        exists. The method is idempotent and will not raise if the
        directories already exist.

        Returns
        -------
        None
        """
        for directory in [DirectoryPaths.DATA, DirectoryPaths.REPORTS]:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)


# Public API exports
__all__ = ['FilePaths', 'DirectoryPaths']
