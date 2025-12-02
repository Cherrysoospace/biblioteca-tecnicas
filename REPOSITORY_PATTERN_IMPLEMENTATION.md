# Implementación del Patrón Repository

## 📋 Resumen de Cambios

Se implementó el **Patrón Repository** para corregir la violación del **Principio de Responsabilidad Única (SRP)** en los servicios.

### ❌ Problema Identificado
Los servicios mezclaban dos responsabilidades:
1. **Lógica de negocio** (validaciones, generación de IDs, sincronización)
2. **Persistencia de datos** (leer/escribir JSON)

### ✅ Solución Implementada
Se separó la persistencia en una **capa de repositorios**:

```
┌─────────────────────────────────────┐
│      CAPA DE SERVICIOS              │
│  (Solo lógica de negocio)           │
│                                     │
│  • BookService                      │
│  • UserService                      │
│  • LoanService                      │
│  • ReservationService               │
│  • InventoryService                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│    CAPA DE REPOSITORIOS             │
│  (Solo persistencia)                │
│                                     │
│  • BookRepository                   │
│  • UserRepository                   │
│  • LoanRepository                   │
│  • ReservationRepository            │
│  • InventoryRepository              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         ARCHIVOS JSON               │
│                                     │
│  • books.json                       │
│  • users.json (data/)               │
│  • loan.json                        │
│  • reservations.json                │
│  • inventory_value.json (reports/)  │
│  • inventory_sorted.json            │
└─────────────────────────────────────┘
```

## 📁 Archivos Creados

### 1. **repositories/base_repository.py** (240 líneas)
Repositorio genérico base con tipos parametrizados:

```python
class BaseRepository(Generic[T]):
    """Repositorio genérico para cualquier modelo T"""
    
    def load_all(self) -> List[T]
    def save_all(self, items: List[T]) -> None
    def clear(self) -> None
```

**Características:**
- Usa `Generic[T]` para tipos parametrizados
- Funciones de conversión `from_dict` y `to_dict` como parámetros
- Delegación completa a `JSONFileHandler` para I/O

### 2. **repositories/book_repository.py** (~50 líneas)
Repositorio para persistencia de libros.

**Responsabilidades:**
- ✅ Convertir `Book` ↔ `dict`
- ✅ Leer/escribir `books.json`
- ❌ NO contiene lógica de negocio

### 3. **repositories/user_repository.py** (~40 líneas)
Repositorio para persistencia de usuarios.

**Responsabilidades:**
- ✅ Convertir `User` ↔ `dict`
- ✅ Leer/escribir `users.json`
- ❌ NO contiene lógica de negocio

### 4. **repositories/loan_repository.py** (~60 líneas)
Repositorio para persistencia de préstamos.

**Responsabilidades:**
- ✅ Convertir `Loan` ↔ `dict`
- ✅ Serializar fechas con `datetime.isoformat()`
- ✅ Leer/escribir `loan.json`
- ❌ NO maneja inventario ni validaciones

### 5. **repositories/reservation_repository.py** (~55 líneas)
Repositorio para persistencia de reservaciones.

**Responsabilidades:**
- ✅ Convertir `Reservation` ↔ `dict`
- ✅ Serializar fechas y estado
- ✅ Leer/escribir `reservations.json`
- ❌ NO maneja cola de prioridad

### 6. **repositories/inventory_repository.py** (~150 líneas)
Repositorio para persistencia de inventario (dual-file).

**Responsabilidades:**
- ✅ Manejar lista de `Inventory` (no DualFileRepository)
- ✅ Convertir `List[Inventory]` ↔ JSON con estructura anidada
- ✅ Leer/escribir `inventory_value.json` e `inventory_sorted.json`
- ❌ NO ordena ni sincroniza inventarios

**Estructura JSON:**
```json
[
  {
    "stock": 2,
    "items": [
      {"id": "B001", "ISBNCode": "978...", "title": "...", ...},
      {"id": "B002", "ISBNCode": "978...", "title": "...", ...}
    ]
  }
]
```

## 🔧 Archivos Modificados

### 1. **services/book_service.py**
**Cambios:**
- ❌ Eliminado: `_ensure_file()`, `_load_from_file()`, `_save_to_file()`
- ✅ Agregado: `BookRepository` como dependencia inyectada
- ✅ Agregado: `_load_books()`, `_save_books()` (delegan al repositorio)
- ✅ Conservado: `generate_next_id()`, validaciones, sincronización con inventario

**Reducción de código:** ~80 líneas de I/O eliminadas

### 2. **services/user_service.py**
**Cambios:**
- ❌ Eliminado: `_ensure_file()`, `_load_from_file()`, `_save_to_file()`
- ✅ Agregado: `UserRepository` como dependencia inyectada
- ✅ Agregado: `_load_users()`, `_save_users()` (delegan al repositorio)
- ✅ Conservado: `create_user()`, ID auto-generado, ordenamiento

**Reducción de código:** ~60 líneas de I/O eliminadas

### 3. **services/loan_service.py**
**Cambios:**
- ❌ Eliminado: `_ensure_file()`, `_load_from_file()`, `_save_to_file()`
- ✅ Agregado: `LoanRepository` como dependencia inyectada
- ✅ Agregado: `_load_loans()`, `_save_loans()` (delegan al repositorio)
- ✅ Agregado: Lazy loading para `book_service` e `inventory_service` (evita importaciones circulares)
- ✅ Conservado: Lógica de préstamos, manejo de stock, stack de préstamos

**Reducción de código:** ~50 líneas de I/O eliminadas

### 4. **services/reservation_service.py**
**Cambios:**
- ❌ Eliminado: `_ensure_file()`, `_load_from_file()`, `_save_to_file()`
- ✅ Agregado: `ReservationRepository` como dependencia inyectada
- ✅ Agregado: `_load_reservations()`, `_save_reservations()` (delegan al repositorio)
- ✅ Conservado: Cola FIFO, asignación de reservas, cálculo de posiciones

**Reducción de código:** ~70 líneas de I/O eliminadas

### 5. **services/inventory_service.py**
**Cambios:**
- ❌ Eliminado: `_ensure_files_exist()`, `_load_general()`, `_load_sorted()`, `_save_general()`, `_save_sorted()`
- ✅ Agregado: `InventoryRepository` como dependencia inyectada
- ✅ Agregado: `_load_inventories()`, `_save_inventories()` (delegan al repositorio)
- ✅ Conservado: `synchronize_inventories()`, ordenamiento con `insercion_ordenada()`, regeneración desde books.json

**Reducción de código:** ~180 líneas de I/O eliminadas

## 📊 Métricas de Impacto

### Eliminación de Código Duplicado
| Servicio | Líneas I/O Eliminadas | Métodos Eliminados |
|----------|----------------------|-------------------|
| BookService | ~80 | 3 |
| UserService | ~60 | 3 |
| LoanService | ~50 | 3 |
| ReservationService | ~70 | 3 |
| InventoryService | ~180 | 5 |
| **TOTAL** | **~440 líneas** | **17 métodos** |

### Código Agregado
| Archivo | Líneas | Responsabilidad |
|---------|--------|----------------|
| base_repository.py | 240 | Infraestructura genérica |
| book_repository.py | 50 | Persistencia de libros |
| user_repository.py | 40 | Persistencia de usuarios |
| loan_repository.py | 60 | Persistencia de préstamos |
| reservation_repository.py | 55 | Persistencia de reservas |
| inventory_repository.py | 150 | Persistencia de inventario |
| **TOTAL** | **595 líneas** | **Capa de repositorios** |

### Balance Neto
- **Líneas eliminadas:** 440
- **Líneas agregadas:** 595
- **Diferencia:** +155 líneas

**Análisis:**
- ✅ Mejor organización (separación de responsabilidades)
- ✅ Código más testeable (se pueden mockear repositorios)
- ✅ Menos acoplamiento (servicios no conocen detalles de persistencia)
- ✅ Reutilización (BaseRepository genérico)

## 🧪 Validación

Se creó `test_repositories.py` para validar la implementación:

```
=== TEST: Repositorios ===

1. BookRepository:
   ✓ Cargados 29 libros
   ✓ Primer libro: The Odyssey

2. UserRepository:
   ✓ Cargados 11 usuarios
   ✓ Primer usuario: Alejandra López

3. LoanRepository:
   ✓ Cargados 3 préstamos
   ✓ Primer préstamo: L001

4. ReservationRepository:
   ✓ Cargadas 2 reservaciones
   ✓ Primera reservación: R001

5. InventoryRepository:
   ✓ Inventario cargado
   ✓ Grupos de inventario: 27
   ✓ Stock total: 29

✅ PATRÓN REPOSITORY IMPLEMENTADO CORRECTAMENTE
```

## 🎯 Principios SOLID Aplicados

### 1. **SRP (Single Responsibility Principle)** ✅
- **Antes:** Servicios con 2 responsabilidades (negocio + persistencia)
- **Ahora:** 
  - Servicios: SOLO lógica de negocio
  - Repositorios: SOLO persistencia

### 2. **DIP (Dependency Inversion Principle)** ✅
- Servicios dependen de **abstracciones** (repositorios inyectados)
- No dependen de **detalles** (archivos JSON concretos)

### 3. **OCP (Open/Closed Principle)** ✅
- `BaseRepository<T>` permite crear nuevos repositorios sin modificar código existente

## 🔄 Arquitectura Limpia (Clean Architecture)

```
┌─────────────────────────────────────┐
│   DOMAIN LAYER (Modelos)            │
│   Book, User, Loan, Reservation     │
└─────────────────────────────────────┘
                ▲
                │
┌─────────────────────────────────────┐
│   APPLICATION LAYER (Servicios)     │
│   - Reglas de negocio                │
│   - Validaciones                     │
│   - Coordinación                     │
└─────────────────────────────────────┘
                ▲
                │
┌─────────────────────────────────────┐
│   INFRASTRUCTURE LAYER (Repos)      │
│   - Persistencia JSON                │
│   - Conversión dict ↔ modelo        │
└─────────────────────────────────────┘
```

## 🚀 Beneficios

1. **Testabilidad:** Se pueden crear mocks de repositorios para tests unitarios
2. **Mantenibilidad:** Cambios en persistencia no afectan lógica de negocio
3. **Extensibilidad:** Fácil cambiar de JSON a DB sin tocar servicios
4. **Legibilidad:** Código más limpio y fácil de entender
5. **Reutilización:** `BaseRepository<T>` evita duplicación

## 📝 Notas Técnicas

### Importaciones Circulares
En `LoanService` se usó lazy loading para evitar importaciones circulares:

```python
@property
def inventory_service(self):
    if self._inventory_service is None:
        from services.inventory_service import InventoryService
        self._inventory_service = InventoryService()
    return self._inventory_service
```

### Conversión de Fechas
Los repositorios usan `datetime.isoformat()` para serializar fechas:

```python
'loan_date': loan.get_loan_date().isoformat() if loan.get_loan_date() else None
```

### Genéricos de Python
`BaseRepository` usa `TypeVar` para tipos genéricos:

```python
from typing import Generic, TypeVar, List, Callable

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(
        self,
        file_path: str,
        from_dict: Callable[[dict], T],
        to_dict: Callable[[T], dict]
    ):
        ...
```

## ✅ Estado Final

- ✅ 5 repositorios creados
- ✅ 5 servicios refactorizados
- ✅ SRP cumplido (separación persistencia/negocio)
- ✅ ~440 líneas de código I/O eliminadas
- ✅ Tests pasando correctamente
- ✅ Aplicación funcionando sin errores

---

**Autor:** GitHub Copilot  
**Fecha:** 2025-12-02  
**Patrón:** Repository Pattern  
**Principio:** Single Responsibility Principle (SRP)
