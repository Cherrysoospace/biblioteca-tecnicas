# IMPLEMENTACIÓN BÚSQUEDA BINARIA - BÚSQUEDA POR ISBN

## ✅ ESTADO: COMPLETADO

---

## 📋 RESUMEN DE IMPLEMENTACIÓN

Se implementó el algoritmo **Búsqueda Binaria Recursiva** para buscar libros por ISBN en el Inventario Ordenado, cumpliendo con el requisito crítico del proyecto:

> "Búsqueda Binaria (Crítica): Implementar la búsqueda por ISBN sobre el Inventario Ordenado. Esta función es crítica; su resultado (posición o no encontrado) debe ser utilizado obligatoriamente para verificar si un libro devuelto tiene reservas pendientes en la Cola de Espera. Si esto es así debe asignarse a la persona que ha solicitado la reserva según la prioridad."

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### 1. **Algoritmo de Búsqueda Binaria** (`utils/algorithms/AlgoritmosBusqueda.py`)

#### Función principal:
- ✅ `busqueda_binaria(inventario_ordenado, isbn_buscado, inicio=0, fin=None)` - Búsqueda recursiva por ISBN

#### Características:
- ✅ **Implementación recursiva** siguiendo el paradigma divide y conquista
- ✅ **Precondición CRÍTICA**: Requiere inventario ordenado por ISBN
- ✅ **Recursión con parámetros opcionales** - inicio y fin para control interno
- ✅ **Documentación completa** con ejemplos y advertencias

### 2. **Integración Crítica con Sistema de Reservas** (`services/loan_service.py`)

#### Uso en devolución de libros:
```python
def return_loan(self, loan_id: str) -> Loan:
    """
    Devolver un libro y verificar reservas pendientes usando búsqueda binaria.
    """
    # ... marcar libro como devuelto ...
    
    # CRÍTICO: Usar búsqueda binaria para verificar reservas
    inventario_ordenado = self.inventory_service.inventory_sorted
    isbn_returned = loan.get_isbn()
    
    # Búsqueda binaria del libro en el inventario ordenado
    index = busqueda_binaria(inventario_ordenado, isbn_returned)
    
    if index != -1:
        # Libro encontrado - verificar reservas pendientes
        pending_reservations = reservation_service.find_by_isbn(
            isbn_returned, 
            only_pending=True
        )
        
        if pending_reservations:
            # Asignar automáticamente al siguiente en la cola (FIFO)
            assigned_reservation = reservation_service.assign_next_for_isbn(isbn_returned)
            
            # Crear préstamo automático para el usuario con reserva
            new_loan = self.create_loan(
                user_id=assigned_reservation.get_user_id(),
                isbn=isbn_returned
            )
```

---

## 🔄 FLUJO CRÍTICO: DEVOLUCIÓN Y ASIGNACIÓN DE RESERVAS

```
┌─────────────────────────────────────────────────────┐
│  Usuario devuelve libro (return_loan)               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  1. Marcar préstamo como devuelto                   │
│  2. Actualizar libro como no prestado               │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  CRÍTICO: Cargar Inventario Ordenado                │
│  (ordenado por ISBN con insercion_ordenada)         │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  BÚSQUEDA BINARIA por ISBN                          │
│  index = busqueda_binaria(inventario, isbn)         │
└────────────────┬────────────────────────────────────┘
                 │
                 ├─── index == -1 (NO encontrado)
                 │    └─→ Fin del proceso
                 │
                 └─── index != -1 (SÍ encontrado)
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Verificar reservas pendientes para este ISBN       │
│  pending_reservations = find_by_isbn(isbn)          │
└────────────────┬────────────────────────────────────┘
                 │
                 ├─── Sin reservas pendientes
                 │    └─→ Libro queda disponible
                 │
                 └─── CON reservas pendientes
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Asignar libro al PRIMERO en la cola (FIFO)         │
│  assigned = assign_next_for_isbn(isbn)              │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  Crear préstamo AUTOMÁTICO para usuario reservante  │
│  new_loan = create_loan(user_id, isbn)              │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
        ✅ Libro asignado según prioridad
```

---

## 🧮 ALGORITMO PASO A PASO

### **Funcionamiento de Binary Search:**

```python
def busqueda_binaria(inventario_ordenado, isbn_buscado, inicio=0, fin=None):
    """
    Búsqueda binaria recursiva por ISBN.
    
    PRECONDICIÓN: inventario DEBE estar ordenado por ISBN.
    """
    # Primera llamada: establecer fin
    if fin is None:
        fin = len(inventario_ordenado) - 1
    
    # Caso base 1: lista vacía
    if not inventario_ordenado:
        return -1
    
    # Caso base 2: sublista sin elementos (no encontrado)
    if inicio > fin:
        return -1
    
    # Calcular punto medio
    medio = (inicio + fin) // 2
    isbn_medio = inventario_ordenado[medio].get_isbn()
    
    # Caso base 3: elemento encontrado
    if isbn_medio == isbn_buscado:
        return medio
    
    # Caso recursivo 1: buscar en mitad izquierda
    elif isbn_medio > isbn_buscado:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, inicio, medio - 1)
    
    # Caso recursivo 2: buscar en mitad derecha
    else:
        return busqueda_binaria(inventario_ordenado, isbn_buscado, medio + 1, fin)
```

### **Ejemplo Visual:**

```
Inventario Ordenado: [45, 123, 456, 789, 978, 9780, 9781, 9782]
                      0   1    2    3    4    5     6     7
Buscar ISBN: 978

ITERACIÓN 1:
  inicio=0, fin=7, medio=3
  inventario[3] = 789
  789 < 978 → Buscar mitad DERECHA [medio+1...fin]

ITERACIÓN 2:
  inicio=4, fin=7, medio=5
  inventario[5] = 9780
  9780 > 978 → Buscar mitad IZQUIERDA [inicio...medio-1]

ITERACIÓN 3:
  inicio=4, fin=4, medio=4
  inventario[4] = 978
  978 == 978 → ✅ ENCONTRADO en índice 4

Resultado: 4
```

### **Caso No Encontrado:**

```
Inventario Ordenado: [45, 123, 456, 789, 978, 9780, 9781, 9782]
Buscar ISBN: 500

ITERACIÓN 1:
  inicio=0, fin=7, medio=3
  inventario[3] = 789
  789 > 500 → Buscar mitad IZQUIERDA

ITERACIÓN 2:
  inicio=0, fin=2, medio=1
  inventario[1] = 123
  123 < 500 → Buscar mitad DERECHA

ITERACIÓN 3:
  inicio=2, fin=2, medio=2
  inventario[2] = 456
  456 < 500 → Buscar mitad DERECHA

ITERACIÓN 4:
  inicio=3, fin=2
  inicio > fin → ❌ NO ENCONTRADO

Resultado: -1
```

---

## 🔗 DEPENDENCIAS CRÍTICAS

### **1. Inventario Ordenado (PRECONDICIÓN)**

⚠️ **ADVERTENCIA CRÍTICA**: Búsqueda binaria **SOLO funciona** si el inventario está ordenado por ISBN.

```python
# ❌ INCORRECTO - Inventario no ordenado
inventario = inventory_service.inventory_general  # NO ordenado
index = busqueda_binaria(inventario, isbn)  # ❌ Resultado INCORRECTO

# ✅ CORRECTO - Inventario ordenado
inventario = inventory_service.inventory_sorted  # Ordenado con insercion_ordenada()
index = busqueda_binaria(inventario, isbn)  # ✅ Resultado CORRECTO
```

### **2. Algoritmo de Ordenamiento por Inserción**

La búsqueda binaria depende completamente de que el inventario esté ordenado:

```python
# 1. Ordenar inventario usando insercion_ordenada (REQUERIMIENTO)
from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
inventario_ordenado = insercion_ordenada(inventario.copy())

# 2. Guardar inventario ordenado
inventory_repo.save_sorted(inventario_ordenado)

# 3. Ahora búsqueda binaria es confiable
from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria
index = busqueda_binaria(inventario_ordenado, isbn_buscado)
```

### **3. Sistema de Reservas (Cola FIFO)**

La búsqueda binaria es el **punto de entrada** para el flujo de asignación de reservas:

```
busqueda_binaria() → Verifica libro en inventario
    ↓
find_by_isbn() → Busca reservas pendientes para ese ISBN
    ↓
assign_next_for_isbn() → Asigna libro al primero en cola (FIFO)
    ↓
create_loan() → Crea préstamo automático
```

---

## 📁 ARCHIVOS MODIFICADOS/CREADOS

### **Archivos Creados:**

1. **`utils/algorithms/AlgoritmosBusqueda.py`**
   - ✅ Función `busqueda_binaria(inventario_ordenado, isbn_buscado, inicio, fin)`
   - ✅ Implementación recursiva completa
   - ✅ Documentación detallada con ejemplos
   - ✅ Advertencias sobre precondición de ordenamiento
   - ✅ Exportada en `__all__`

### **Archivos Modificados:**

2. **`services/loan_service.py`**
   - ✅ Import de `busqueda_binaria`
   - ✅ Integración en `return_loan()` método
   - ✅ Verificación de reservas usando resultado de búsqueda binaria
   - ✅ Asignación automática según prioridad (FIFO)
   - ✅ Creación de préstamo automático para usuario reservante

3. **`repositories/inventory_repository.py`**
   - ✅ Método `load_sorted()` para cargar inventario ordenado
   - ✅ Garantiza disponibilidad del inventario ordenado

4. **`services/inventory_service.py`**
   - ✅ Propiedad `inventory_sorted` disponible públicamente
   - ✅ Sincronización automática tras operaciones CRUD

---

## 💡 CASOS DE USO EN EL SISTEMA

### **1. Verificación de Libro en Devolución (USO CRÍTICO):**
```python
# Usuario devuelve libro
loan_service.return_loan("L001")

# Internamente:
# 1. Cargar inventario ordenado
inventario = inventory_service.inventory_sorted

# 2. BÚSQUEDA BINARIA para verificar libro
index = busqueda_binaria(inventario, "978-...")

# 3. Si encontrado (index != -1), verificar reservas
if index != -1:
    reservas = find_by_isbn("978-...")
    if reservas:
        # Asignar automáticamente al primero en cola
        assign_next_for_isbn("978-...")
```

### **2. Búsqueda Rápida de Libro por ISBN:**
```python
# Cargar inventario ordenado
inventario_ordenado = inventory_service.inventory_sorted

# Buscar libro específico
index = busqueda_binaria(inventario_ordenado, "9780451524935")

if index != -1:
    libro_encontrado = inventario_ordenado[index]
    print(f"Libro: {libro_encontrado.get_book().get_title()}")
else:
    print("Libro no existe en inventario")
```

### **3. Verificación de Disponibilidad:**
```python
# Verificar si libro existe antes de crear préstamo
inventario_ordenado = inventory_service.inventory_sorted
index = busqueda_binaria(inventario_ordenado, isbn_solicitado)

if index == -1:
    raise ValueError("Libro no existe en el catálogo")

# Libro existe, proceder con préstamo
loan_service.create_loan(user_id, isbn_solicitado)
```

### **4. Reportes y Estadísticas:**
```python
# Verificar múltiples libros rápidamente
isbns_a_verificar = ["978...", "979...", "123..."]
inventario_ordenado = inventory_service.inventory_sorted

for isbn in isbns_a_verificar:
    index = busqueda_binaria(inventario_ordenado, isbn)
    if index != -1:
        print(f"✓ ISBN {isbn} encontrado")
    else:
        print(f"✗ ISBN {isbn} no encontrado")
```

---

## ✅ VALIDACIÓN Y TESTING

### **Test 1: Búsqueda Exitosa**
```python
# Setup
inventario = [
    Inventory(isbn="45"),
    Inventory(isbn="123"),
    Inventory(isbn="456"),
    Inventory(isbn="789")
]

# Búsqueda
index = busqueda_binaria(inventario, "456")

# Verificación
assert index == 2, "Debe encontrar ISBN '456' en posición 2"
assert inventario[index].get_isbn() == "456", "ISBN debe coincidir"
```

### **Test 2: Búsqueda Fallida**
```python
# Buscar ISBN que no existe
index = busqueda_binaria(inventario, "999")

# Verificación
assert index == -1, "Debe retornar -1 para ISBN no encontrado"
```

### **Test 3: Lista Vacía**
```python
# Inventario vacío
inventario_vacio = []
index = busqueda_binaria(inventario_vacio, "123")

# Verificación
assert index == -1, "Lista vacía debe retornar -1"
```

### **Test 4: Un Solo Elemento**
```python
# Inventario con un elemento
inventario_unitario = [Inventory(isbn="123")]

# Búsqueda exitosa
index = busqueda_binaria(inventario_unitario, "123")
assert index == 0, "Debe encontrar el único elemento"

# Búsqueda fallida
index = busqueda_binaria(inventario_unitario, "456")
assert index == -1, "Debe retornar -1 si no coincide"
```

### **Test 5: Flujo Completo de Reserva**
```python
# 1. Usuario solicita libro prestado (stock = 0)
reservation_service.create_reservation(user_id="U001", isbn="978...")

# 2. Otro usuario devuelve ese libro
loan_service.return_loan("L005")  # ISBN = "978..."

# 3. Verificar que búsqueda binaria encontró el libro
# (internamente ejecutada en return_loan)

# 4. Verificar que se asignó automáticamente
reservations = reservation_service.find_by_user("U001")
assert reservations[0].get_status() == "assigned"

# 5. Verificar que se creó préstamo automático
loans = loan_service.find_by_user("U001")
assert len(loans) > 0
assert loans[-1].get_isbn() == "978..."
```

---

## 🎯 IMPORTANCIA CRÍTICA EN EL PROYECTO

### **Requisito Explícito:**
> "Esta función es crítica; su resultado (posición o no encontrado) debe ser utilizado obligatoriamente para verificar si un libro devuelto tiene reservas pendientes en la Cola de Espera."

### **Cumplimiento:**
✅ **Implementación completa** - Algoritmo recursivo funcional
✅ **Uso obligatorio** - Integrada en flujo de devolución de libros
✅ **Verificación de reservas** - Utiliza resultado para buscar en cola de espera
✅ **Asignación por prioridad** - Respeta orden FIFO de la cola
✅ **Préstamo automático** - Crea préstamo para usuario reservante
✅ **Eficiencia garantizada** - O(log n) para inventarios grandes

### **Flujo Crítico Validado:**
```
Libro Devuelto
    ↓
Búsqueda Binaria (CRÍTICA) ← Encuentra libro en inventario ordenado
    ↓
¿Tiene reservas? ← Consulta cola de espera (FIFO)
    ↓
SÍ → Asignar al primero en cola
    ↓
Crear préstamo automático
    ↓
✅ Usuario con reserva recibe el libro automáticamente
```

---

## 🔐 GARANTÍAS DE CORRECTITUD

### **Invariantes del Algoritmo:**

1. **Precondición**: Inventario DEBE estar ordenado por ISBN
   - ✅ Garantizado por `insercion_ordenada()` ejecutada automáticamente

2. **Correctitud**: Si el elemento existe, se encuentra
   - ✅ Garantizado por divide-and-conquer recursivo

3. **Terminación**: El algoritmo siempre termina
   - ✅ Garantizado por reducción del espacio de búsqueda en cada paso

### **Manejo de Casos Edge:**
✅ **Lista vacía** → Retorna -1
✅ **Un elemento** → Encuentra o retorna -1
✅ **Elemento al inicio** → O(log n) operaciones
✅ **Elemento al final** → O(log n) operaciones
✅ **Elemento en el medio** → O(log n) operaciones
✅ **Elemento no existe** → O(log n) operaciones, retorna -1

---

## 📝 CONCLUSIONES

### **Cumplimiento de Requisitos:**
✅ **Algoritmo implementado** - Búsqueda binaria recursiva funcional
✅ **Uso crítico** - Integrada en flujo de devolución/reservas
✅ **Verificación de reservas** - Utiliza resultado obligatoriamente
✅ **Asignación por prioridad** - Respeta cola FIFO
✅ **Documentación completa** - Código completamente comentado
✅ **Testing validado** - Casos de prueba cubiertos

### **Ventajas de la Implementación:**
✅ **Escalabilidad** - Funciona perfectamente con inventarios grandes
✅ **Recursividad clara** - Implementación elegante y fácil de entender
✅ **Integración crítica** - Corazón del sistema de reservas
✅ **Confiabilidad** - Precondiciones garantizadas por el sistema

### **Impacto en el Sistema:**
✅ **Performance** - Búsquedas instantáneas en inventarios grandes
✅ **User Experience** - Asignación automática de reservas
✅ **Integridad** - Garantiza orden correcto de asignación (FIFO)
✅ **Escalabilidad** - Sistema funcional con miles de libros

---
