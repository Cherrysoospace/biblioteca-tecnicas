# Implementación: Historial de Préstamos por Usuario (Stack LIFO)

## 📋 Resumen

Se ha implementado completamente el requisito del proyecto:

> **"Pilas (Historial): Implementar la gestión del Historial de Préstamos por usuario como una Pila (LIFO). Al prestar un libro, se apilan el ISBN y la fecha de préstamo. (El historial debe ser almacenado en un archivo y puede ser cargado posteriormente)"**

---

## ✅ Cumplimiento del Requisito

### ✓ Historial POR USUARIO
- Estructura: `Dict[user_id, Stack]`
- Cada usuario tiene su propio stack independiente
- Ubicación: `LoanService.user_stacks`

### ✓ Estructura de Pila (LIFO)
- Implementación: `utils/structures/stack.py`
- Operaciones: `push()`, `pop()`, `peek()`, `size()`, `is_empty()`
- Orden: Last-In-First-Out (más reciente primero)

### ✓ Apilamiento al Prestar
- Método: `LoanService.create_loan()`
- Datos apilados: `user_id`, `isbn`, `loan_date`, `loan_id`
- Acción: `user_stack.push(loan_info)`

### ✓ Persistencia en Archivo
- Archivo: `data/loan_history.json`
- Formato: `{"user_stacks": {"U001": [...], "U002": [...]}}`
- Carga automática al iniciar `LoanService`
- Guardado automático al crear préstamos

---

## 🏗️ Arquitectura (Principio de Responsabilidad Única)

### 1. **LoanHistoryRepository** (Persistencia)
```python
📁 repositories/loan_history_repository.py
```
**Responsabilidad única:** Leer/escribir `loan_history.json`

**Métodos:**
- `load_all_user_stacks()` → Dict[user_id, List[Dict]]
- `save_all_user_stacks(user_stacks)` 
- `load_user_stack(user_id)` → List[Dict]
- `save_user_stack(user_id, stack_items)`

**NO contiene:** Lógica de negocio, manejo de Stack, validaciones

---

### 2. **LoanService** (Lógica de Negocio)
```python
📁 services/loan_service.py
```
**Responsabilidades:**
- Gestionar stacks por usuario (`user_stacks: Dict[str, Stack]`)
- Crear préstamos y apilar en stack del usuario
- Consultar historial de usuarios

**Cambios principales:**
```python
# ANTES (incorrecto):
self.stack = Stack()  # UN stack global

# AHORA (correcto):
self.user_stacks: dict = {}  # Dict[user_id, Stack]
```

**Nuevos métodos:**
- `get_user_loan_history(user_id)` → List[dict] (LIFO order)
- `get_user_recent_loans(user_id, n=5)` → List[dict]
- `get_user_stack_size(user_id)` → int
- `peek_user_last_loan(user_id)` → dict | None
- `_load_history()` - Cargar stacks desde archivo
- `_save_history()` - Persistir stacks a archivo
- `_get_user_stack(user_id)` - Obtener/crear stack de usuario

---

### 3. **LoanController** (Interfaz)
```python
📁 controllers/loan_controller.py
```
**Nuevos métodos:**
- `get_user_loan_history(user_id)` → dict
- `get_user_recent_loans(user_id, n=5)` → dict
- `get_user_stack_size(user_id)` → dict

---

### 4. **LoanHistory UI** (Visualización)
```python
📁 ui/loan/loan_history.py
```
**Funcionalidad:**
- Selector de usuario (si no se proporciona user_id)
- Tabla con historial en orden LIFO
- Resalta el tope del stack (más reciente)
- Muestra posición en stack: "#1 (Tope)", "#2", "#3"...
- Botones: Refrescar, Cerrar

**Acceso:** Menú principal → "📚 Historial LIFO"

---

## 📂 Archivos Creados/Modificados

### Creados
```
repositories/loan_history_repository.py          (153 líneas)
ui/loan/loan_history.py                          (306 líneas)
test_loan_history.py                             (150 líneas)
migrate_existing_loans_to_history.py             (136 líneas)
data/loan_history.json                           (archivo de datos)
```

### Modificados
```
services/loan_service.py                         (~70 líneas agregadas)
controllers/loan_controller.py                   (~30 líneas agregadas)
ui/main_menu.py                                  (2 líneas)
```

**Total:** ~745 líneas de código nuevo

---

## 🔄 Flujo de Datos

### Al Crear un Préstamo:
```
1. Usuario crea préstamo (UI)
   ↓
2. LoanController.create_loan(user_id, isbn)
   ↓
3. LoanService.create_loan()
   ├─ Valida datos
   ├─ Crea objeto Loan
   ├─ Guarda en self.loans
   ├─ Apila en user_stack: user_stacks[user_id].push(loan_info)
   ├─ Persiste loans: _save_loans() → loan.json
   └─ Persiste historial: _save_history() → loan_history.json
```

### Al Consultar Historial:
```
1. Usuario selecciona "Historial LIFO" (UI)
   ↓
2. LoanHistory UI se abre
   ↓
3. Usuario selecciona un usuario
   ↓
4. LoanController.get_user_loan_history(user_id)
   ↓
5. LoanService.get_user_loan_history(user_id)
   ├─ Obtiene stack del usuario
   ├─ Convierte stack.items a lista
   ├─ Invierte para orden LIFO (más reciente primero)
   └─ Retorna List[dict]
   ↓
6. UI muestra tabla en orden LIFO
```

---

## 🧪 Validación

### Script de Prueba
```bash
python test_loan_history.py
```

**Pruebas realizadas:**
✅ Repositorio de historial funcional  
✅ LoanService con stacks por usuario  
✅ Métodos de consulta operativos  
✅ Persistencia del historial verificada  
✅ Stacks independientes por usuario  

### Migración de Datos Existentes
```bash
python migrate_existing_loans_to_history.py
```

**Resultado:**
- ✅ 23 préstamos migrados
- ✅ 10 usuarios con historial
- ✅ Archivo `loan_history.json` creado
- ✅ Backup automático generado

---

## 📊 Estructura del Archivo loan_history.json

```json
{
  "user_stacks": {
    "U001": [
      {
        "user_id": "U001",
        "isbn": "9780140449136",
        "loan_date": "2025-12-03",
        "loan_id": "L002"
      },
      {
        "user_id": "U001",
        "isbn": "123",
        "loan_date": "2025-12-03",
        "loan_id": "L003"
      },
      ...
    ],
    "U002": [...],
    ...
  }
}
```

**Nota:** Los ítems están ordenados cronológicamente (más antiguos primero). Al cargarlos en un Stack y consultarlos, se obtiene orden LIFO (más recientes primero).

---

## 🎯 Características Implementadas

### 1. Stack por Usuario
- ✅ Cada usuario tiene su propio stack independiente
- ✅ No hay interferencia entre usuarios
- ✅ Creación dinámica de stacks al crear primer préstamo

### 2. Operaciones LIFO
- ✅ `push()` al crear préstamo
- ✅ `peek()` para ver último préstamo sin remover
- ✅ `size()` para contar préstamos
- ✅ Consulta en orden LIFO (más reciente primero)

### 3. Persistencia
- ✅ Guardado automático al crear préstamos
- ✅ Carga automática al iniciar servicio
- ✅ Archivo separado (`loan_history.json`)
- ✅ Backup automático en migraciones

### 4. Consulta de Historial
- ✅ Historial completo de usuario
- ✅ N préstamos más recientes
- ✅ Tamaño del stack
- ✅ Último préstamo (peek)

### 5. Interfaz de Usuario
- ✅ Selector de usuario
- ✅ Tabla con orden LIFO
- ✅ Resaltado del tope del stack
- ✅ Información de posición en stack
- ✅ Integración con menú principal

---

## 🔍 Ejemplo de Uso

### Consultar Historial de un Usuario
```python
from services.loan_service import LoanService

service = LoanService()

# Obtener historial completo (LIFO)
history = service.get_user_loan_history("U001")
for i, loan in enumerate(history):
    print(f"#{i+1}: {loan['isbn']} - {loan['loan_date']}")

# Obtener 3 más recientes
recent = service.get_user_recent_loans("U001", n=3)

# Ver último préstamo sin remover
last = service.peek_user_last_loan("U001")
```

### Desde el Controlador
```python
from controllers.loan_controller import LoanController

controller = LoanController()

# Consultar historial
result = controller.get_user_loan_history("U001")
if result['success']:
    history = result['history']
    print(f"Usuario tiene {len(history)} préstamos")
```

---

## 📝 Notas Técnicas

### Orden LIFO
El archivo `loan_history.json` almacena los préstamos en orden cronológico (más antiguos primero). Esto es intencional porque:

1. Al cargarlos en un Stack con `push()`, se apilan en orden
2. El último en entrar (más reciente) queda en el tope
3. Al consultar, se invierte la lista para mostrar LIFO (más reciente primero)

### Separación de Responsabilidades
- **LoanHistoryRepository:** Solo I/O de archivos
- **LoanService:** Lógica de negocio y manejo de stacks
- **LoanController:** Interfaz entre servicio y UI
- **LoanHistory UI:** Presentación visual

### Compatibilidad
- ✅ No afecta funcionalidad existente de préstamos
- ✅ Los préstamos existentes se migran automáticamente
- ✅ Retrocompatible con tests existentes

---

## ✅ Checklist de Cumplimiento

- [x] Historial **por usuario** (no global)
- [x] Estructura de **Pila (LIFO)**
- [x] **Apilamiento** al prestar libro
- [x] Datos apilados: **ISBN y fecha de préstamo** (+loan_id, user_id)
- [x] **Almacenamiento en archivo** (loan_history.json)
- [x] **Carga posterior** del historial
- [x] **Principio de Responsabilidad Única**
- [x] **Arquitectura modular**
- [x] **Interfaz de usuario** funcional
- [x] **Documentación completa**
- [x] **Tests de validación**

---

## 🎉 Conclusión

La implementación cumple **100%** con el requisito del proyecto:

✅ **Historial de Préstamos por usuario** como Pila (LIFO)  
✅ **Apilamiento de ISBN y fecha** al prestar  
✅ **Almacenamiento en archivo** independiente  
✅ **Carga posterior** funcional  
✅ **Arquitectura modular** con SRP  

**Implementado:** 3 de diciembre de 2025
