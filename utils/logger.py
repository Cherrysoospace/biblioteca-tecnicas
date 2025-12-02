"""logger.py

Sistema centralizado de logging para el Sistema de Gestión de Bibliotecas.
Proporciona configuración consistente de logs para toda la aplicación.

Características:
- Logs en archivo con rotación diaria
- Logs en consola con colores
- Niveles configurables (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Formato con timestamps y contexto

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class LibraryLogger:
    """Configurador centralizado de logging para la aplicación.
    
    Crea un sistema de logging dual:
    - Archivo: logs detallados en logs/library_YYYYMMDD.log
    - Consola: logs importantes en stdout
    """
    
    _initialized = False
    
    @classmethod
    def setup(cls, level=logging.INFO):
        """Configurar el sistema de logging global.
        
        PARÁMETROS:
        ===========
        level : int, opcional
            Nivel de logging (default: logging.INFO)
            - DEBUG: información detallada de debugging
            - INFO: confirmación de operaciones normales
            - WARNING: advertencias, funcionalidad no afectada
            - ERROR: errores, funcionalidad afectada
            - CRITICAL: errores críticos, sistema no funcional
            
        RETORNO:
        ========
        None
        
        EJEMPLO:
        ========
        >>> LibraryLogger.setup(logging.DEBUG)  # Modo verbose
        >>> logger = LibraryLogger.get_logger(__name__)
        >>> logger.info("Aplicación iniciada")
        """
        if cls._initialized:
            return
        
        # Crear directorio de logs
        project_root = Path(__file__).parent.parent
        log_dir = project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Archivo de log con fecha
        log_file = log_dir / f'library_{datetime.now():%Y%m%d}.log'
        
        # Formato detallado para archivo
        file_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)-8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formato simplificado para consola
        console_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)-8s] %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Handler para archivo (todos los niveles)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Handler para consola (WARNING y superior)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        
        # Configurar logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        
        # Log de inicialización
        init_logger = logging.getLogger('utils.logger')
        init_logger.info('=' * 80)
        init_logger.info('Sistema de logging inicializado')
        init_logger.info(f'Archivo de log: {log_file}')
        init_logger.info(f'Nivel de log: {logging.getLevelName(level)}')
        init_logger.info('=' * 80)
    
    @staticmethod
    def get_logger(name):
        """Obtener un logger configurado para un módulo.
        
        PARÁMETROS:
        ===========
        name : str
            Nombre del módulo (usar __name__)
            
        RETORNO:
        ========
        logging.Logger
            Logger configurado y listo para usar
            
        EJEMPLO:
        ========
        >>> # En services/book_service.py
        >>> logger = LibraryLogger.get_logger(__name__)
        >>> logger.info("BookService iniciado")
        >>> logger.error("Error al cargar libros", exc_info=True)
        """
        return logging.getLogger(name)


class UIErrorHandler:
    """Manejador especializado de errores para la capa UI.
    
    Proporciona métodos helper para manejar errores en CustomTkinter
    de forma consistente: logging + messagebox al usuario.
    """
    
    @staticmethod
    def handle_error(logger, error, title="Error", user_message=None, show_dialog=True):
        """Manejar error de UI con logging y messagebox.
        
        PARÁMETROS:
        ===========
        logger : logging.Logger
            Logger del módulo que reporta el error
        error : Exception
            Excepción capturada
        title : str, opcional
            Título del messagebox (default: "Error")
        user_message : str, opcional
            Mensaje amigable al usuario. Si es None, usa str(error)
        show_dialog : bool, opcional
            Si True, muestra messagebox (default: True)
            
        RETORNO:
        ========
        None
        
        EJEMPLO:
        ========
        >>> try:
        >>>     book = controller.get_book(id)
        >>> except Exception as e:
        >>>     UIErrorHandler.handle_error(
        >>>         logger, e,
        >>>         title="Error al cargar libro",
        >>>         user_message="No se pudo cargar el libro seleccionado"
        >>>     )
        """
        # Log detallado del error
        logger.error(f"{title}: {error}", exc_info=True)
        
        # Mensaje al usuario
        if show_dialog:
            try:
                from tkinter import messagebox
                msg = user_message if user_message else str(error)
                messagebox.showerror(title, msg)
            except Exception as dialog_error:
                # Si falla el dialog, al menos logear
                logger.error(f"Error mostrando dialog: {dialog_error}")
    
    @staticmethod
    def handle_warning(logger, message, title="Advertencia", show_dialog=True):
        """Manejar advertencia de UI con logging y messagebox.
        
        PARÁMETROS:
        ===========
        logger : logging.Logger
            Logger del módulo que reporta la advertencia
        message : str
            Mensaje de advertencia
        title : str, opcional
            Título del messagebox (default: "Advertencia")
        show_dialog : bool, opcional
            Si True, muestra messagebox (default: True)
            
        RETORNO:
        ========
        None
        
        EJEMPLO:
        ========
        >>> UIErrorHandler.handle_warning(
        >>>     logger,
        >>>     "El libro seleccionado ya está prestado",
        >>>     title="Operación no permitida"
        >>> )
        """
        logger.warning(f"{title}: {message}")
        
        if show_dialog:
            try:
                from tkinter import messagebox
                messagebox.showwarning(title, message)
            except Exception as dialog_error:
                logger.error(f"Error mostrando dialog de advertencia: {dialog_error}")
    
    @staticmethod
    def log_and_pass(logger, context, error):
        """Loggear error y continuar (reemplazo de 'except Exception: pass').
        
        Usar solo cuando el error NO afecta funcionalidad crítica
        (ej: cargar un icono opcional).
        
        PARÁMETROS:
        ===========
        logger : logging.Logger
            Logger del módulo
        context : str
            Descripción del contexto donde ocurrió el error
        error : Exception
            Excepción capturada
            
        RETORNO:
        ========
        None
        
        EJEMPLO:
        ========
        >>> try:
        >>>     self.icon = Image.open("icon.png")
        >>> except Exception as e:
        >>>     UIErrorHandler.log_and_pass(logger, "Cargar icono", e)
        """
        logger.debug(f"Error no crítico en {context}: {error}")


# Inicializar automáticamente al importar
LibraryLogger.setup()


__all__ = ['LibraryLogger', 'UIErrorHandler']
