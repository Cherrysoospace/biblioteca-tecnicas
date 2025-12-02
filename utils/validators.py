"""validators.py

Framework centralizado de validación para el Sistema de Gestión de Bibliotecas.
Proporciona validadores reutilizables para todas las entidades del dominio.

Responsabilidades:
- Validar datos de entrada antes de persistir
- Lanzar excepciones específicas con mensajes claros
- Prevenir datos corruptos en JSON
- Centralizar reglas de negocio de validación

Autor: Sistema de Gestión de Bibliotecas
Fecha: 2025-12-02
"""

from typing import Any, Optional
import re
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)


# ==================== EXCEPCIONES PERSONALIZADAS ====================

class ValidationError(ValueError):
    """Excepción base para errores de validación.
    
    Se lanza cuando los datos de entrada no cumplen las reglas de negocio.
    """
    pass


class ISBNValidationError(ValidationError):
    """ISBN inválido o malformado."""
    pass


class PriceValidationError(ValidationError):
    """Precio inválido (negativo, cero, o no numérico)."""
    pass


class WeightValidationError(ValidationError):
    """Peso inválido (negativo o no numérico)."""
    pass


class NameValidationError(ValidationError):
    """Nombre inválido (vacío o solo espacios)."""
    pass


class IDValidationError(ValidationError):
    """ID inválido (vacío, formato incorrecto)."""
    pass


# ==================== VALIDADORES DE BOOK ====================

class BookValidator:
    """Validador para entidad Book.
    
    Reglas de negocio:
    - ISBN: máximo 13 dígitos (puede contener guiones)
    - Título: no vacío, no solo espacios
    - Autor: no vacío, no solo espacios
    - Peso: > 0 (kg)
    - Precio: > 0 (COP)
    """
    
    @staticmethod
    def validate_isbn(isbn: str) -> str:
        """Validar formato de ISBN.
        
        REGLAS:
        - No vacío
        - Máximo 13 dígitos (excluyendo guiones/espacios)
        - Puede contener guiones y espacios
        
        PARÁMETROS:
        ===========
        isbn : str
            ISBN a validar
            
        RETORNO:
        ========
        str
            ISBN validado y limpio
            
        EXCEPCIONES:
        ============
        ISBNValidationError
            Si el ISBN no cumple las reglas
            
        EJEMPLO:
        ========
        >>> BookValidator.validate_isbn("978-3-16-148410-0")  # ✓ Válido
        '978-3-16-148410-0'
        >>> BookValidator.validate_isbn("12345678901234")     # ✗ 14 dígitos
        ISBNValidationError: ISBN debe tener máximo 13 dígitos
        """
        if not isbn or not isinstance(isbn, str):
            raise ISBNValidationError("ISBN no puede estar vacío")
        
        isbn_clean = isbn.strip()
        if not isbn_clean:
            raise ISBNValidationError("ISBN no puede estar vacío")
        
        # Extraer solo dígitos (ignorar guiones y espacios)
        digits_only = re.sub(r'[^0-9]', '', isbn_clean)
        
        if not digits_only:
            raise ISBNValidationError("ISBN debe contener al menos un dígito")
        
        if len(digits_only) > 13:
            raise ISBNValidationError(
                f"ISBN debe tener máximo 13 dígitos (encontrados: {len(digits_only)})"
            )
        
        logger.debug(f"ISBN validado: {isbn_clean} ({len(digits_only)} dígitos)")
        return isbn_clean
    
    @staticmethod
    def validate_title(title: str) -> str:
        """Validar título de libro.
        
        REGLAS:
        - No vacío
        - No solo espacios
        - Longitud mínima: 1 carácter (sin espacios)
        
        PARÁMETROS:
        ===========
        title : str
            Título a validar
            
        RETORNO:
        ========
        str
            Título validado y con espacios normalizados
            
        EXCEPCIONES:
        ============
        NameValidationError
            Si el título es vacío o inválido
        """
        if not title or not isinstance(title, str):
            raise NameValidationError("Título no puede estar vacío")
        
        title_clean = title.strip()
        if not title_clean:
            raise NameValidationError("Título no puede estar vacío o ser solo espacios")
        
        logger.debug(f"Título validado: '{title_clean}'")
        return title_clean
    
    @staticmethod
    def validate_author(author: str) -> str:
        """Validar nombre de autor.
        
        REGLAS:
        - No vacío
        - No solo espacios
        
        PARÁMETROS:
        ===========
        author : str
            Nombre del autor a validar
            
        RETORNO:
        ========
        str
            Nombre validado y con espacios normalizados
            
        EXCEPCIONES:
        ============
        NameValidationError
            Si el nombre es vacío o inválido
        """
        if not author or not isinstance(author, str):
            raise NameValidationError("Nombre del autor no puede estar vacío")
        
        author_clean = author.strip()
        if not author_clean:
            raise NameValidationError("Nombre del autor no puede estar vacío o ser solo espacios")
        
        logger.debug(f"Autor validado: '{author_clean}'")
        return author_clean
    
    @staticmethod
    def validate_weight(weight: Any) -> float:
        """Validar peso del libro.
        
        REGLAS:
        - Debe ser convertible a float
        - Debe ser > 0 (peso en kg)
        
        PARÁMETROS:
        ===========
        weight : Any
            Peso a validar (puede ser int, float, str)
            
        RETORNO:
        ========
        float
            Peso validado
            
        EXCEPCIONES:
        ============
        WeightValidationError
            Si el peso es <= 0 o no convertible a número
        """
        try:
            weight_float = float(weight)
        except (ValueError, TypeError):
            raise WeightValidationError(
                f"Peso debe ser un número válido (recibido: {weight})"
            )
        
        if weight_float <= 0:
            raise WeightValidationError(
                f"Peso debe ser mayor a 0 kg (recibido: {weight_float})"
            )
        
        logger.debug(f"Peso validado: {weight_float} kg")
        return weight_float
    
    @staticmethod
    def validate_price(price: Any) -> int:
        """Validar precio del libro.
        
        REGLAS:
        - Debe ser convertible a int
        - Debe ser > 0 (precio en COP)
        
        PARÁMETROS:
        ===========
        price : Any
            Precio a validar (puede ser int, float, str)
            
        RETORNO:
        ========
        int
            Precio validado
            
        EXCEPCIONES:
        ============
        PriceValidationError
            Si el precio es <= 0 o no convertible a número
        """
        try:
            price_int = int(price)
        except (ValueError, TypeError):
            raise PriceValidationError(
                f"Precio debe ser un número entero válido (recibido: {price})"
            )
        
        if price_int <= 0:
            raise PriceValidationError(
                f"Precio debe ser mayor a 0 COP (recibido: {price_int})"
            )
        
        logger.debug(f"Precio validado: {price_int} COP")
        return price_int
    
    @staticmethod
    def validate_book_data(
        isbn: str,
        title: str,
        author: str,
        weight: Any,
        price: Any,
        book_id: Optional[str] = None
    ) -> dict:
        """Validar todos los campos de un libro.
        
        PARÁMETROS:
        ===========
        isbn : str
        title : str
        author : str
        weight : Any
        price : Any
        book_id : str, opcional
            ID del libro (solo para validar si se provee)
            
        RETORNO:
        ========
        dict
            Diccionario con datos validados:
            {
                'isbn': str,
                'title': str,
                'author': str,
                'weight': float,
                'price': int,
                'book_id': str (si se proveyó)
            }
            
        EXCEPCIONES:
        ============
        ValidationError
            Si algún campo es inválido
        """
        validated = {
            'isbn': BookValidator.validate_isbn(isbn),
            'title': BookValidator.validate_title(title),
            'author': BookValidator.validate_author(author),
            'weight': BookValidator.validate_weight(weight),
            'price': BookValidator.validate_price(price),
        }
        
        if book_id is not None:
            validated['book_id'] = BookValidator.validate_id(book_id)
        
        logger.info(f"Datos de libro validados: ISBN={validated['isbn']}, Título={validated['title']}")
        return validated
    
    @staticmethod
    def validate_id(book_id: str) -> str:
        """Validar ID de libro.
        
        REGLAS:
        - No vacío
        - No solo espacios
        
        PARÁMETROS:
        ===========
        book_id : str
            ID a validar
            
        RETORNO:
        ========
        str
            ID validado
            
        EXCEPCIONES:
        ============
        IDValidationError
            Si el ID es inválido
        """
        if not book_id or not isinstance(book_id, str):
            raise IDValidationError("ID de libro no puede estar vacío")
        
        id_clean = book_id.strip()
        if not id_clean:
            raise IDValidationError("ID de libro no puede estar vacío o ser solo espacios")
        
        return id_clean


# ==================== VALIDADORES DE USER ====================

class UserValidator:
    """Validador para entidad User.
    
    Reglas de negocio:
    - Nombre: no vacío, no solo espacios
    - ID: no vacío (si se provee)
    """
    
    @staticmethod
    def validate_name(name: str) -> str:
        """Validar nombre de usuario.
        
        REGLAS:
        - No vacío
        - No solo espacios
        - Longitud mínima: 1 carácter (sin espacios)
        
        PARÁMETROS:
        ===========
        name : str
            Nombre a validar
            
        RETORNO:
        ========
        str
            Nombre validado y con espacios normalizados
            
        EXCEPCIONES:
        ============
        NameValidationError
            Si el nombre es vacío o inválido
        """
        if not name or not isinstance(name, str):
            raise NameValidationError("Nombre de usuario no puede estar vacío")
        
        name_clean = name.strip()
        if not name_clean:
            raise NameValidationError("Nombre de usuario no puede estar vacío o ser solo espacios")
        
        logger.debug(f"Nombre de usuario validado: '{name_clean}'")
        return name_clean
    
    @staticmethod
    def validate_id(user_id: str) -> str:
        """Validar ID de usuario.
        
        REGLAS:
        - No vacío
        - No solo espacios
        
        PARÁMETROS:
        ===========
        user_id : str
            ID a validar
            
        RETORNO:
        ========
        str
            ID validado
            
        EXCEPCIONES:
        ============
        IDValidationError
            Si el ID es inválido
        """
        if not user_id or not isinstance(user_id, str):
            raise IDValidationError("ID de usuario no puede estar vacío")
        
        id_clean = user_id.strip()
        if not id_clean:
            raise IDValidationError("ID de usuario no puede estar vacío o ser solo espacios")
        
        return id_clean


# ==================== VALIDADORES DE LOAN ====================

class LoanValidator:
    """Validador para entidad Loan.
    
    Reglas de negocio:
    - user_id: no vacío
    - book_id: no vacío
    - isbn: formato válido
    """
    
    @staticmethod
    def validate_loan_data(user_id: str, book_id: str, isbn: str) -> dict:
        """Validar datos de un préstamo.
        
        PARÁMETROS:
        ===========
        user_id : str
        book_id : str
        isbn : str
            
        RETORNO:
        ========
        dict
            Diccionario con datos validados
            
        EXCEPCIONES:
        ============
        ValidationError
            Si algún campo es inválido
        """
        validated = {
            'user_id': UserValidator.validate_id(user_id),
            'book_id': BookValidator.validate_id(book_id),
            'isbn': BookValidator.validate_isbn(isbn),
        }
        
        logger.info(f"Datos de préstamo validados: user={validated['user_id']}, book={validated['book_id']}")
        return validated


# ==================== VALIDADORES DE RESERVATION ====================

class ReservationValidator:
    """Validador para entidad Reservation.
    
    Reglas de negocio:
    - user_id: no vacío
    - isbn: formato válido
    """
    
    @staticmethod
    def validate_reservation_data(user_id: str, isbn: str) -> dict:
        """Validar datos de una reservación.
        
        PARÁMETROS:
        ===========
        user_id : str
        isbn : str
            
        RETORNO:
        ========
        dict
            Diccionario con datos validados
            
        EXCEPCIONES:
        ============
        ValidationError
            Si algún campo es inválido
        """
        validated = {
            'user_id': UserValidator.validate_id(user_id),
            'isbn': BookValidator.validate_isbn(isbn),
        }
        
        logger.info(f"Datos de reserva validados: user={validated['user_id']}, isbn={validated['isbn']}")
        return validated


__all__ = [
    'ValidationError',
    'ISBNValidationError',
    'PriceValidationError',
    'WeightValidationError',
    'NameValidationError',
    'IDValidationError',
    'BookValidator',
    'UserValidator',
    'LoanValidator',
    'ReservationValidator',
]
