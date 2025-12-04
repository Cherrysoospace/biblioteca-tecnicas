# IMPLEMENTACIÓN MANEJO DE LISTAS - INVENTARIO GENERAL E INVENTARIO ORDENADO

## ✅ ESTADO: COMPLETADO

---

## 📋 RESUMEN DE IMPLEMENTACIÓN

Se implementó el sistema de **Manejo de Listas** con dos listas maestras sincronizadas, cumpliendo con el requisito del proyecto:

> "Manejo de Listas: Se deben mantener dos listas maestras de objetos Libro: el Inventario General (una lista desordenada, reflejando el orden de carga) y el Inventario Ordenado (una lista siempre mantenida en orden ascendente por ISBN)."

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### 1. **Servicio de Inventario** (`services/inventory_service.py`)

#### Clase InventoryService:
```python
class InventoryService:
    """Service for managing inventory groups and stock levels.
    
    In-Memory State:
        Two synchronized lists are maintained:
        
        - inventory_general (List[Inventory]): 
          Unsorted list reflecting load order.
          This is the PRIMARY working list for mutations.
          
        - inventory_sorted (List[Inventory]): 
          Sorted copy ordered by ISBN (ascending).
          Maintained using insertion sort algorithm.
          Used for efficient binary search operations.
    
    Synchronization:
        Both lists remain synchronized after every mutation:
        1. Operations apply to inventory_general
        2. synchronize_inventories() creates sorted copy
        3. Both lists persisted to JSON files
    """
    
    def __init__(self, repository: InventoryRepository = None):
        self.repository = repository or InventoryRepository()
        
        # TWO MASTER LISTS (required by project)
        self.inventory_general: List[Inventory] = []  # Unsorted
        self.inventory_sorted: List[Inventory] = []   # Sorted by ISBN
        
        self._load_inventories()
        self.synchronize_inventories()
```

### 2. **Dos Listas Maestras**

#### **Lista 1: Inventario General (Desordenado)**
```python
# Características:
# - Lista NO ordenada
# - Refleja orden de carga desde archivo
# - Lista primaria para operaciones CRUD
# - Persistida en: data/inventory_general.json

self.inventory_general: List[Inventory] = []

# Ejemplo:
# [
#   Inventory(isbn="9780451524935"),  # Cargado primero
#   Inventory(isbn="123"),             # Cargado segundo
#   Inventory(isbn="9780345339683"),  # Cargado tercero
#   Inventory(isbn="45")               # Cargado cuarto
# ]
# Orden: según aparecen en el archivo (sin ordenar)
```

#### **Lista 2: Inventario Ordenado (Por ISBN)**
```python
# Características:
# - Lista ORDENADA por ISBN ascendente
# - Copia sincronizada del Inventario General
# - Ordenado con algoritmo insercion_ordenada()
# - Usado para búsqueda binaria eficiente
# - Persistida en: data/inventory_sorted.json

self.inventory_sorted: List[Inventory] = []

# Ejemplo (mismo contenido, ordenado):
# [
#   Inventory(isbn="45"),              # ISBN más pequeño
#   Inventory(isbn="123"),             
#   Inventory(isbn="9780345339683"),  
#   Inventory(isbn="9780451524935")   # ISBN más grande
# ]
# Orden: ascendente por ISBN (ordenado)
```

### 3. **Modelo Inventory** (`models/inventory.py`)

#### Concepto de Grupo de Inventario:
```python
class Inventory:
    """Represents a group of books with the same ISBN.
    
    One Inventory object = One ISBN code
    Multiple physical copies = Multiple Book objects in items list
    
    Attributes:
        stock: Number of available (not borrowed) copies
        items: List of Book objects (all physical copies)
    """
    
    def __init__(self, stock: int, items: List[Book]):
        self.__stock = stock
        self.__items = items
    
    def get_isbn(self) -> str:
        """Get ISBN from first book in group."""
        if self.__items:
            return self.__items[0].get_ISBNCode()
        return ""
    
    def get_available_count(self) -> int:
        """Count non-borrowed books."""
        return sum(1 for book in self.__items if not book.get_isBorrowed())
```

**Ejemplo de Agrupación:**
```python
# Biblioteca tiene 3 copias de "Don Quijote" (ISBN 978-123):
# - Copia 1: B001 (disponible)
# - Copia 2: B002 (prestada)
# - Copia 3: B003 (disponible)

inventory = Inventory(
    stock=2,  # 2 disponibles
    items=[
        Book(id="B001", isbn="978-123", borrowed=False),
        Book(id="B002", isbn="978-123", borrowed=True),
        Book(id="B003", isbn="978-123", borrowed=False)
    ]
)

# Un solo Inventory agrupa todos los libros con mismo ISBN
```

---

## 🔄 FLUJO DE SINCRONIZACIÓN DE LISTAS

```
┌─────────────────────────────────────────────────────┐
│  OPERACIÓN DE MUTACIÓN                              │
│  (add_item / update / delete)                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  1. MODIFICAR inventory_general (lista primaria)    │
│     - Agregar libro a grupo existente o nuevo       │
│     - Actualizar datos de libro                     │
│     - Eliminar libro de grupo                       │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  2. LLAMAR synchronize_inventories()                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  3. CREAR COPIA PROFUNDA (Deep Copy)                │
│     inventory_sorted = []                           │
│                                                     │
│     Para cada Inventory en inventory_general:       │
│       - Copiar cada Book (evitar referencias)       │
│       - Crear nuevo Inventory con libros copiados   │
│       - Agregar a inventory_sorted                  │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  4. ORDENAR inventory_sorted                        │
│     insercion_ordenada(inventory_sorted)            │
│                                                     │
│     Algoritmo de Inserción:                         │
│     - Ordena por ISBN ascendente                    │
│     - O(n²) pero eficiente para listas pequeñas     │
│     - Mantiene estabilidad del ordenamiento         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  5. PERSISTIR AMBAS LISTAS                          │
│     repository.save_both(general, sorted)           │
│                                                     │
│     Guarda en:                                      │
│     - data/inventory_general.json (sin ordenar)     │
│     - data/inventory_sorted.json (ordenado)         │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
        ✅ AMBAS LISTAS SINCRONIZADAS
```

---

## 💡 OPERACIONES CRUD Y SINCRONIZACIÓN

### **1. Agregar Libro (add_item)**

```python
def add_item(self, book: Book, stock: int = 1) -> None:
    """Add new book to inventory system.
    
    Logic:
    1. Validate book ID is unique
    2. Search for existing group with same ISBN
    3. If found: Add to existing group
    4. If not: Create new group
    5. Synchronize both lists
    """
    # Check for duplicate ID
    for inventory in self.inventory_general:
        for existing_book in inventory.get_items():
            if existing_book.get_id() == book.get_id():
                raise ValueError(f"Book id '{book.get_id()}' already exists")
    
    # Find or create group
    target_inventory = None
    for inventory in self.inventory_general:
        if inventory.get_isbn() == book.get_ISBNCode():
            target_inventory = inventory
            break
    
    if target_inventory:
        # Add to existing group
        target_inventory.add_item(book)
    else:
        # Create new group
        new_inventory = Inventory(stock=1, items=[book])
        self.inventory_general.append(new_inventory)
    
    # Synchronize
    self.synchronize_inventories()
```

**Ejemplo:**
```python
# Estado inicial (2 grupos):
inventory_general = [
    Inventory(isbn="123", items=[Book("B001")]),
    Inventory(isbn="456", items=[Book("B002")])
]

# Agregar libro con ISBN existente (123):
book_new = Book(id="B003", isbn="123", ...)
service.add_item(book_new)

# Resultado (aún 2 grupos, B003 agregado al primero):
inventory_general = [
    Inventory(isbn="123", items=[Book("B001"), Book("B003")]),  ← agregado aquí
    Inventory(isbn="456", items=[Book("B002")])
]

# Agregar libro con ISBN nuevo (789):
book_new2 = Book(id="B004", isbn="789", ...)
service.add_item(book_new2)

# Resultado (3 grupos):
inventory_general = [
    Inventory(isbn="123", items=[Book("B001"), Book("B003")]),
    Inventory(isbn="456", items=[Book("B002")]),
    Inventory(isbn="789", items=[Book("B004")])  ← nuevo grupo
]

# inventory_sorted se sincroniza automáticamente y queda ordenado:
inventory_sorted = [
    Inventory(isbn="123", ...),  # ISBN más pequeño primero
    Inventory(isbn="456", ...),
    Inventory(isbn="789", ...)   # ISBN más grande último
]
```

### **2. Actualizar Libro (update_book_in_inventory)**

```python
def update_book_in_inventory(self, book_id: str, updated_book: Book) -> None:
    """Update book information in inventory.
    
    ISBN Change Handling:
    - If ISBN changes: Move book to different group
    - Old group: Remove book, delete if empty
    - New group: Add book (or create new group)
    """
    found = False
    old_isbn = None
    old_inventory = None
    
    # Find and update book
    for inventory in self.inventory_general:
        for i, book in enumerate(inventory.get_items()):
            if book.get_id() == book_id:
                old_isbn = book.get_ISBNCode()
                old_inventory = inventory
                
                # Update book in place
                inventory.get_items()[i] = updated_book
                found = True
                break
        if found:
            break
    
    if not found:
        raise ValueError(f"Book '{book_id}' not found")
    
    # Handle ISBN change
    if old_isbn != updated_book.get_ISBNCode():
        # Remove from old group
        old_inventory.remove_item(book_id)
        
        # Remove empty groups
        self.inventory_general = [
            inv for inv in self.inventory_general 
            if len(inv.get_items()) > 0
        ]
        
        # Add to new group
        target_inventory = None
        for inventory in self.inventory_general:
            if inventory.get_isbn() == updated_book.get_ISBNCode():
                target_inventory = inventory
                break
        
        if target_inventory:
            target_inventory.add_item(updated_book)
        else:
            new_inventory = Inventory(stock=1, items=[updated_book])
            self.inventory_general.append(new_inventory)
    
    self.synchronize_inventories()
```

**Ejemplo:**
```python
# Cambiar ISBN de libro B002:
# Antes:
inventory_general = [
    Inventory(isbn="123", items=[Book("B001")]),
    Inventory(isbn="456", items=[Book("B002"), Book("B003")])
]

# Actualizar B002: isbn="456" → isbn="789"
updated = Book(id="B002", isbn="789", ...)
service.update_book_in_inventory("B002", updated)

# Después:
inventory_general = [
    Inventory(isbn="123", items=[Book("B001")]),
    Inventory(isbn="456", items=[Book("B003")]),     # B002 removido
    Inventory(isbn="789", items=[Book("B002")])      # B002 en nuevo grupo
]
```

### **3. Eliminar Libro (delete_book_from_inventory)**

```python
def delete_book_from_inventory(self, book_id: str) -> None:
    """Delete book from inventory.
    
    Logic:
    1. Find and remove book from its group
    2. Delete empty groups
    3. Synchronize both lists
    """
    found = False
    
    for inventory in self.inventory_general:
        if inventory.remove_item(book_id):
            found = True
            break
    
    if not found:
        raise ValueError(f"Book '{book_id}' not found")
    
    # Remove empty groups
    self.inventory_general = [
        inv for inv in self.inventory_general 
        if len(inv.get_items()) > 0
    ]
    
    self.synchronize_inventories()
```

**Ejemplo:**
```python
# Antes:
inventory_general = [
    Inventory(isbn="123", items=[Book("B001")]),       # grupo de 1 libro
    Inventory(isbn="456", items=[Book("B002"), Book("B003")])  # grupo de 2
]

# Eliminar B001 (único en su grupo):
service.delete_book_from_inventory("B001")

# Después:
inventory_general = [
    # Grupo isbn="123" eliminado (quedó vacío)
    Inventory(isbn="456", items=[Book("B002"), Book("B003")])
]

# Eliminar B002 (uno de dos en grupo):
service.delete_book_from_inventory("B002")

# Después:
inventory_general = [
    Inventory(isbn="456", items=[Book("B003")])  # Grupo mantiene 1 libro
]
```

### **4. Sincronizar Listas (synchronize_inventories)**

```python
def synchronize_inventories(self) -> None:
    """Synchronize sorted list with general list.
    
    Process:
    1. Create deep copy of inventory_general
    2. Apply insertion sort by ISBN
    3. Persist both lists to JSON files
    """
    # Deep copy
    self.inventory_sorted = []
    for inv in self.inventory_general:
        books_copy = []
        for book in inv.get_items():
            book_copy = Book(
                book.get_id(),
                book.get_ISBNCode(),
                book.get_title(),
                book.get_author(),
                book.get_weight(),
                book.get_price(),
                book.get_isBorrowed()
            )
            books_copy.append(book_copy)
        
        inv_copy = Inventory(stock=inv.get_stock(), items=books_copy)
        self.inventory_sorted.append(inv_copy)
    
    # Sort using insertion sort algorithm
    insercion_ordenada(self.inventory_sorted)
    
    # Save both
    self._save_inventories()
```

---

## 📊 EJEMPLO COMPLETO DE MANEJO DE LISTAS

### **Escenario: Biblioteca con 5 libros**

#### Estado Inicial (carga desde books.json):
```json
// books.json (orden de carga):
[
  {"id": "B001", "ISBNCode": "9780451524935", ...},  // Cargado 1º
  {"id": "B002", "ISBNCode": "123", ...},             // Cargado 2º
  {"id": "B003", "ISBNCode": "9780451524935", ...},  // Cargado 3º (mismo ISBN que B001)
  {"id": "B004", "ISBNCode": "456", ...},             // Cargado 4º
  {"id": "B005", "ISBNCode": "123", ...}              // Cargado 5º (mismo ISBN que B002)
]
```

#### inventory_general (sin ordenar, refleja orden de carga):
```python
[
  Inventory(
    isbn="9780451524935",
    items=[Book("B001"), Book("B003")]  # Agrupados por ISBN
  ),
  Inventory(
    isbn="123",
    items=[Book("B002"), Book("B005")]  # Agrupados por ISBN
  ),
  Inventory(
    isbn="456",
    items=[Book("B004")]
  )
]

# Orden: según fueron procesados al cargar
# - Grupo "9780451524935" primero (B001 cargado primero)
# - Grupo "123" segundo (B002 cargado segundo)
# - Grupo "456" tercero (B004 cargado cuarto)
```

#### inventory_sorted (ordenado por ISBN ascendente):
```python
[
  Inventory(
    isbn="123",                         # ISBN más pequeño
    items=[Book("B002"), Book("B005")]
  ),
  Inventory(
    isbn="456",
    items=[Book("B004")]
  ),
  Inventory(
    isbn="9780451524935",              # ISBN más grande
    items=[Book("B001"), Book("B003")]
  )
]

# Orden: alfabético/numérico por ISBN
# - "123" < "456" < "9780451524935"
```

---

## 🔍 USO DE CADA LISTA

### **Inventario General (Unsorted) - Usos:**

✅ **Operaciones CRUD** - Lista primaria para modificaciones
```python
# Agregar, actualizar, eliminar libros
service.add_item(new_book)
service.update_book_in_inventory(book_id, updated_data)
service.delete_book_from_inventory(book_id)
```

✅ **Búsqueda Lineal** - Por título o autor (no requiere orden)
```python
# Búsqueda por título/autor en lista desordenada
from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal
index = busqueda_lineal(inventory_general, "Don Quijote")
```

✅ **Listados Simples** - Mostrar en orden de carga
```python
# Mostrar todos los libros en orden original
for inventory in service.inventory_general:
    print(f"ISBN: {inventory.get_isbn()}, Stock: {inventory.get_stock()}")
```

✅ **Reportes Sin Orden** - Inventario general sin clasificar
```python
# Generar reporte de inventario completo
report = {
    "total_groups": len(service.inventory_general),
    "total_books": sum(len(inv.get_items()) for inv in service.inventory_general)
}
```

### **Inventario Ordenado (Sorted) - Usos:**

✅ **Búsqueda Binaria (CRÍTICA)** - Por ISBN (requiere orden)
```python
# Búsqueda binaria en lista ordenada (O(log n))
from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria
index = busqueda_binaria(inventory_sorted, "9780451524935")

# CRÍTICO: Usado en devolución de libros para verificar reservas
if index != -1:
    # Libro encontrado, verificar reservas pendientes
    pending_reservations = reservation_service.find_by_isbn(isbn)
```

✅ **Listados Ordenados** - Mostrar por ISBN alfabético
```python
# Mostrar inventario ordenado por ISBN
for inventory in service.inventory_sorted:
    print(f"ISBN: {inventory.get_isbn()}")
# Output:
# ISBN: 123
# ISBN: 456
# ISBN: 9780451524935
```

✅ **Reportes Clasificados** - Inventario ordenado para análisis
```python
# Generar reporte con ISBNs en orden
sorted_report = []
for inv in service.inventory_sorted:
    sorted_report.append({
        "isbn": inv.get_isbn(),
        "stock": inv.get_stock(),
        "total_copies": len(inv.get_items())
    })
```

---

## 📁 PERSISTENCIA DE AMBAS LISTAS

### **Archivos JSON:**

#### **1. inventory_general.json (Sin Ordenar)**
```json
[
  {
    "stock": 2,
    "items": [
      {"id": "B001", "ISBNCode": "9780451524935", ...},
      {"id": "B003", "ISBNCode": "9780451524935", ...}
    ]
  },
  {
    "stock": 2,
    "items": [
      {"id": "B002", "ISBNCode": "123", ...},
      {"id": "B005", "ISBNCode": "123", ...}
    ]
  },
  {
    "stock": 1,
    "items": [
      {"id": "B004", "ISBNCode": "456", ...}
    ]
  }
]
```

#### **2. inventory_sorted.json (Ordenado por ISBN)**
```json
[
  {
    "stock": 2,
    "items": [
      {"id": "B002", "ISBNCode": "123", ...},
      {"id": "B005", "ISBNCode": "123", ...}
    ]
  },
  {
    "stock": 1,
    "items": [
      {"id": "B004", "ISBNCode": "456", ...}
    ]
  },
  {
    "stock": 2,
    "items": [
      {"id": "B001", "ISBNCode": "9780451524935", ...},
      {"id": "B003", "ISBNCode": "9780451524935", ...}
    ]
  }
]
```

**Diferencia:** Mismo contenido, diferente orden.

---

## ✅ CUMPLIMIENTO DE REQUISITOS

### **Requisito del Proyecto:**
> "Manejo de Listas: Se deben mantener dos listas maestras de objetos Libro: el Inventario General (una lista desordenada, reflejando el orden de carga) y el Inventario Ordenado (una lista siempre mantenida en orden ascendente por ISBN)."

### **Cumplimiento:**
✅ **Dos listas maestras** - `inventory_general` e `inventory_sorted`
✅ **Inventario General desordenado** - Refleja orden de carga del archivo
✅ **Inventario Ordenado** - Mantenido en orden ascendente por ISBN
✅ **Sincronización automática** - Tras cada operación CRUD
✅ **Algoritmo de Inserción** - Usado para mantener orden (insercion_ordenada)
✅ **Persistencia** - Ambas listas guardadas en archivos JSON
✅ **Objetos Libro** - Ambas listas contienen objetos Book (dentro de Inventory)
✅ **Búsqueda Binaria lista** - inventory_sorted siempre disponible y ordenada

---

## 🎯 VENTAJAS DE LA ARQUITECTURA DE DOS LISTAS

### **Separación de Responsabilidades:**
✅ **inventory_general** - Operaciones de mutación (add/update/delete)
✅ **inventory_sorted** - Operaciones de búsqueda eficiente (binary search)
✅ **Especialización** - Cada lista optimizada para su propósito

### **Performance:**
✅ **Mutaciones rápidas** - En lista desordenada (sin costo de ordenamiento)
✅ **Búsquedas rápidas** - En lista ordenada (O(log n) vs O(n))
✅ **Sincronización bajo demanda** - Solo después de mutaciones

### **Integridad:**
✅ **Deep copy** - Evita referencias compartidas entre listas
✅ **Sincronización garantizada** - Ambas listas siempre consistentes
✅ **Persistencia dual** - No se pierde ninguna versión

### **Mantenibilidad:**
✅ **Código claro** - Cada lista con propósito bien definido
✅ **Fácil debugging** - Ambas listas inspeccionables en archivos JSON
✅ **Testeable** - Fácil validar sincronización

---

## 📝 CONCLUSIONES

### **Implementación Completa:**
✅ **Dos listas maestras** - inventory_general e inventory_sorted
✅ **Sincronización automática** - synchronize_inventories() tras cada mutación
✅ **Algoritmo de ordenamiento** - insercion_ordenada() para mantener orden
✅ **Persistencia dual** - Ambas listas guardadas en JSON
✅ **Deep copy** - Previene efectos secundarios entre listas
✅ **Operaciones CRUD** - Completas en inventory_general

### **Cumplimiento Total:**
✅ **Inventario General** - Lista desordenada, orden de carga
✅ **Inventario Ordenado** - Lista ordenada por ISBN ascendente
✅ **Mantenimiento automático** - Orden preservado tras operaciones
✅ **Objetos Libro** - Contenidos en Inventory (agrupados por ISBN)
✅ **Búsqueda Binaria** - Lista ordenada siempre disponible

### **Arquitectura Profesional:**
✅ **Patrón Service Layer** - Lógica de negocio centralizada
✅ **Patrón Repository** - Persistencia separada
✅ **Single Responsibility** - Cada lista con propósito único
✅ **Sincronización confiable** - Estado consistente garantizado