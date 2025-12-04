"""logger.py

Centralized logging utilities for the Library Management System.

This module provides a consistent logging configuration used across the
application. It configures both file and console handlers and exposes a
small helper class to get configured loggers. The module also includes a
UI-specific error helper that logs exceptions and optionally shows a
user-facing dialog.

Features:
- File logging (daily file with timestamp in filename)
- Console logging (stream handler)
- Configurable log levels
- Structured, informative message formats

Author: Library Management System
Date: 2025-12-02
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class LibraryLogger:
    """Central logger configurator for the application.

    This class is used to initialize and provide access to the application's
    global logging configuration. It sets up a file handler (detailed
    logging) and a console handler (warnings and above) and prevents
    duplicate initialization by tracking an internal flag.
    """
    
    _initialized = False
    
    @classmethod
    def setup(cls, level=logging.INFO):
        """Configure the global logging system for the application.

        Parameters
        ----------
        level : int, optional
            The root logging level to set (default: ``logging.INFO``).
            Typical values include ``logging.DEBUG``, ``logging.INFO``,
            ``logging.WARNING``, ``logging.ERROR`` and ``logging.CRITICAL``.

        Notes
        -----
        This method is idempotent: calling it more than once has no effect
        after the first successful initialization.

        Example
        -------
        >>> LibraryLogger.setup(logging.DEBUG)
        >>> logger = LibraryLogger.get_logger(__name__)
        >>> logger.info("Application started")
        """
        if cls._initialized:
            return
        
        # Create logs directory
        project_root = Path(__file__).parent.parent
        log_dir = project_root / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Log file with date
        log_file = log_dir / f'library_{datetime.now():%Y%m%d}.log'
        
        # Detailed formatter for file
        file_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)-8s] %(name)s:%(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Simple formatter for console
        console_formatter = logging.Formatter(
            fmt='%(asctime)s [%(levelname)-8s] %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler (capture all levels)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler (WARNING and above)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        
        # Initialization log
        init_logger = logging.getLogger('utils.logger')
        init_logger.info('=' * 80)
        init_logger.info('Logging system initialized')
        init_logger.info(f'Log file: {log_file}')
        init_logger.info(f'Log level: {logging.getLevelName(level)}')
        init_logger.info('=' * 80)
    
    @staticmethod
    def get_logger(name):
        """Return a configured Logger instance for the given module name.

        Parameters
        ----------
        name : str
            The logger name, typically the module's ``__name__``.

        Returns
        -------
        logging.Logger
            A logger instance configured according to the global settings.

        Example
        -------
        >>> logger = LibraryLogger.get_logger(__name__)
        >>> logger.info("BookService started")
        >>> logger.error("Failed to load books", exc_info=True)
        """
        return logging.getLogger(name)


class UIErrorHandler:
    """UI-focused error helper.

    This helper provides convenience methods for logging UI errors and
    optionally showing a user-facing dialog (using Tkinter message boxes).
    These helpers make it easy to consistently record exceptions and
    present a friendly message to the user when an error occurs in the UI
    layer.
    """
    
    @staticmethod
    def handle_error(logger, error, title="Error", user_message=None, show_dialog=True):
        """Log an exception and optionally show an error dialog to the user.

        This method records the full exception traceback to the provided
        logger and, when ``show_dialog`` is True, attempts to display a
        Tkinter error message box with a friendly message.

        Parameters
        ----------
        logger : logging.Logger
            The logger to record the error on.
        error : Exception
            The exception instance that was caught.
        title : str, optional
            Title for the message box (default: "Error").
        user_message : str, optional
            Friendly message to show to the user. If ``None``, the string
            representation of ``error`` is used.
        show_dialog : bool, optional
            If True, attempt to show a Tkinter messagebox (default: True).

        Notes
        -----
        The method catches and logs failures raised while trying to show the
        dialog to avoid raising exceptions from the error handler itself.

        Example
        -------
        >>> try:
        >>>     book = controller.get_book(book_id)
        >>> except Exception as e:
        >>>     UIErrorHandler.handle_error(logger, e,
        >>>                                title="Failed to load book",
        >>>                                user_message="Could not load the selected book")
        """
        # Detailed logging of the error
        logger.error(f"{title}: {error}", exc_info=True)

        # Show a user-facing messagebox if requested
        if show_dialog:
            try:
                from tkinter import messagebox
                msg = user_message if user_message else str(error)
                messagebox.showerror(title, msg)
            except Exception as dialog_error:
                # If showing a dialog fails, at least log the failure
                logger.error(f"Error showing dialog: {dialog_error}")
    
    @staticmethod
    def handle_warning(logger, message, title="Warning", show_dialog=True):
        """Log a UI warning and optionally show a warning dialog.

        Parameters
        ----------
        logger : logging.Logger
            Logger instance used to record the warning.
        message : str
            The warning message to log and optionally display.
        title : str, optional
            Title for the dialog (default: "Warning").
        show_dialog : bool, optional
            If True, attempt to show a Tkinter warning dialog (default: True).

        Example
        -------
        >>> UIErrorHandler.handle_warning(logger,
        >>>                              "The selected book is already checked out",
        >>>                              title="Operation not allowed")
        """
        logger.warning(f"{title}: {message}")

        if show_dialog:
            try:
                from tkinter import messagebox
                messagebox.showwarning(title, message)
            except Exception as dialog_error:
                logger.error(f"Error showing warning dialog: {dialog_error}")
    
    @staticmethod
    def log_and_pass(logger, context, error):
        """Log a non-critical error and continue execution.

        This helper is intended as a safer replacement for a silent
        ``except Exception: pass``. Use it when the error does not impact
        core functionality (for example, failing to load an optional icon).

        Parameters
        ----------
        logger : logging.Logger
            Logger instance to record the debug message.
        context : str
            Short description of where the error occurred.
        error : Exception
            The caught exception instance.

        Example
        -------
        >>> try:
        >>>     self.icon = Image.open("icon.png")
        >>> except Exception as e:
        >>>     UIErrorHandler.log_and_pass(logger, "Load icon", e)
        """
        logger.debug(f"Non-critical error in {context}: {error}")


# Initialize automatically on import
LibraryLogger.setup()


__all__ = ['LibraryLogger', 'UIErrorHandler']
