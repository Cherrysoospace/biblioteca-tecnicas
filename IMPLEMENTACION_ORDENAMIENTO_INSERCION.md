# IMPLEMENTACIÓN ORDENAMIENTO POR INSERCIÓN - INVENTARIO ORDENADO

## ✅ ESTADO: COMPLETADO

---

## 📋 RESUMEN DE IMPLEMENTACIÓN

Se implementó el algoritmo **Ordenamiento por Inserción** para mantener el Inventario Ordenado por ISBN, cumpliendo con el requisito del proyecto:

> "Ordenamiento por Inserción: Este algoritmo debe usarse para mantener el Inventario Ordenado cada vez que se agrega un nuevo libro al sistema. Esto asegura que la lista para la Búsqueda Binaria esté siempre lista."

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### 1. **Algoritmo de Ordenamiento por Inserción** (`utils/algorithms/AlgoritmosOrdenamiento.py`)

#### Funciones principales:
- ✅ `insercion_ordenada(lista_libros)` - Ordena inventario por ISBN usando Insertion Sort
- ✅ `_comparar_isbn_mayor(isbn1, isbn2)` - Compara ISBNs (numérico cuando es posible)

#### Características:
- ✅ **Implementación manual** del algoritmo clásico de inserción
- ✅ **Ordenamiento in-place** - modifica la lista original sin crear copias
- ✅ **Complejidad O(n²)** en el peor caso, pero eficiente para listas pequeñas o casi ordenadas
- ✅ **Algoritmo estable** - preserva orden relativo de elementos con igual ISBN
- ✅ **Comparación inteligente de ISBN** - preferencia por comparación numérica
- ✅ **Documentación completa** con explicaciones detalladas

### 2. **Comparación Inteligente de ISBNs**

```python
def _comparar_isbn_mayor(isbn1, isbn2):
    """
    Compare two ISBNs preferring numeric comparison when possible.
    
    - Si ambos ISBNs son numéricos: compara como enteros
    - Si alguno contiene caracteres no numéricos: compara lexicográficamente
    """
    try:
        return int(isbn1) > int(isbn2)
    except (ValueError, TypeError):
        return isbn1 > isbn2
```

#### Ventajas:
✅ **Evita problemas de ordenamiento** como "2" > "123" (lexicográfico)
✅ **Compatible con ISBNs con guiones** como "978-..."
✅ **Flexible** para diferentes formatos de ISBN

### 3. **Integración con InventoryRepository** (`repositories/inventory_repository.py`)

#### Método implementado:
```python
def save_sorted(self, inventories: List['Inventory']) -> bool:
    """
    Guardar inventario ordenado por ISBN usando inserción ordenada.
    """
    from utils.algorithms.AlgoritmosOrdenamiento import insercion_ordenada
    
    # Ordenar usando algoritmo de inserción
    inventarios_ordenados = insercion_ordenada(inventories.copy())
    
    # Guardar en archivo JSON
    self.file_handler.save_json(
        self.sorted_inventory_file,
        [inv.to_dict() for inv in inventarios_ordenados]
    )
```

#### Ubicación del inventario ordenado:
📁 `data/inventory_sorted.json`

---

## 🔄 FLUJO DE MANTENIMIENTO DEL INVENTARIO ORDENADO

```
┌─────────────────────────────────────────────────────┐
│  Usuario agrega/modifica libro en el sistema        │
├─────────────────────────────────────────────────────┤
│  • BookService.add_book()                           │
│  • BookService.update_book()                        │
│  • BookService.delete_book()                        │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  InventoryService actualiza inventarios             │
├─────────────────────────────────────────────────────┤
│  • Inventory General (sin ordenar)                  │
│  • Inventory Sorted (ordenado por ISBN)             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  InventoryRepository.save_sorted()                  │
├─────────────────────────────────────────────────────┤
│  1. Copia lista de inventarios                      │
│  2. Aplica insercion_ordenada()                     │
│  3. Guarda en inventory_sorted.json                 │
└─────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│  inventory_sorted.json LISTO para Búsqueda Binaria  │
└─────────────────────────────────────────────────────┘
```

---

## 📊 EJEMPLO DE INVENTARIO ORDENADO

### Antes del ordenamiento (Inventario General):
```json
[
  {"isbn": "9780451524935", "titulo": "1984", "autor": "George Orwell"},
  {"isbn": "123", "titulo": "El Principito", "autor": "Antoine de Saint-Exupéry"},
  {"isbn": "9780345339683", "titulo": "El Hobbit", "autor": "J.R.R. Tolkien"},
  {"isbn": "45", "titulo": "Cien Años de Soledad", "autor": "Gabriel García Márquez"}
]
```

### Después del ordenamiento (Inventario Ordenado):
```json
[
  {"isbn": "45", "titulo": "Cien Años de Soledad", "autor": "Gabriel García Márquez"},
  {"isbn": "123", "titulo": "El Principito", "autor": "Antoine de Saint-Exupéry"},
  {"isbn": "9780345339683", "titulo": "El Hobbit", "autor": "J.R.R. Tolkien"},
  {"isbn": "9780451524935", "titulo": "1984", "autor": "George Orwell"}
]
```

**Nota:** Los ISBNs numéricos (45, 123) se ordenan correctamente antes que los alfanuméricos (978...).

---

## 🧮 ALGORITMO PASO A PASO

### **Funcionamiento del Insertion Sort:**

```python
def insercion_ordenada(lista_libros):
    # Caso base: lista vacía o de un elemento
    if not lista_libros or len(lista_libros) <= 1:
        return lista_libros
    
    # Recorrer desde el segundo elemento
    for i in range(1, len(lista_libros)):
        # Elemento a insertar en la parte ordenada
        inventario_actual = lista_libros[i]
        isbn_actual = inventario_actual.get_isbn()
        
        # Buscar posición de inserción
        j = i - 1
        
        # Desplazar elementos mayores hacia la derecha
        while j >= 0 and _comparar_isbn_mayor(lista_libros[j].get_isbn(), isbn_actual):
            lista_libros[j + 1] = lista_libros[j]
            j -= 1
        
        # Insertar en la posición correcta
        lista_libros[j + 1] = inventario_actual
    
    return lista_libros
```

### **Ejemplo Visual:**

```
INICIAL: [978, 123, 45, 9780]

Iteración 1 (i=1, elemento=123):
  [978, 123, 45, 9780]
   ↓
  [123, 978, 45, 9780]  ← 123 < 978, se inserta antes

Iteración 2 (i=2, elemento=45):
  [123, 978, 45, 9780]
        ↓
  [45, 123, 978, 9780]  ← 45 < 123 < 978, se inserta al inicio

Iteración 3 (i=3, elemento=9780):
  [45, 123, 978, 9780]
             ↓
  [45, 123, 978, 9780]  ← 9780 > 978, ya está en posición

RESULTADO: [45, 123, 978, 9780] ✓
```

## 🔗 INTEGRACIÓN CON BÚSQUEDA BINARIA

El Inventario Ordenado generado por este algoritmo es **CRÍTICO** para la Búsqueda Binaria:

```python
from utils.algorithms.AlgoritmosBusqueda import busqueda_binaria

# Cargar inventario ordenado
inventario_ordenado = inventory_repo.load_sorted()

# Búsqueda binaria de libro por ISBN
isbn_buscado = "9780451524935"
posicion = busqueda_binaria(inventario_ordenado, isbn_buscado)

if posicion != -1:
    print(f"Libro encontrado en posición {posicion}")
else:
    print("Libro no encontrado")
```

### **Requisitos para Búsqueda Binaria:**
✅ Lista **DEBE estar ordenada** por el criterio de búsqueda (ISBN)
✅ El Insertion Sort **garantiza** este requisito tras cada operación
✅ Sin ordenamiento, la búsqueda binaria **NO funcionaría correctamente**

---

## 📁 ARCHIVOS MODIFICADOS/CREADOS

### **Archivos Modificados:**

1. **`utils/algorithms/AlgoritmosOrdenamiento.py`**
   - ✅ Agregada función `insercion_ordenada(lista_libros)`
   - ✅ Agregada función auxiliar `_comparar_isbn_mayor(isbn1, isbn2)`
   - ✅ Documentación completa con explicaciones de complejidad
   - ✅ Exportadas en `__all__`

2. **`repositories/inventory_repository.py`**
   - ✅ Método `save_sorted()` utiliza `insercion_ordenada()`
   - ✅ Garantiza que `inventory_sorted.json` siempre esté ordenado

3. **`services/inventory_service.py`**
   - ✅ Llama automáticamente a `save_sorted()` tras modificaciones
   - ✅ Mantiene sincronizados Inventario General e Inventario Ordenado

---

## 💡 CASOS DE USO EN EL SISTEMA

### **1. Agregar Nuevo Libro:**
```python
# Usuario agrega libro con ISBN "456"
book_service.add_book(nuevo_libro)

# Automáticamente:
# 1. Se agrega al Inventario General (sin orden)
# 2. Se ejecuta insercion_ordenada() en el Inventario Ordenado
# 3. Se guarda inventory_sorted.json con el nuevo libro en su posición correcta
```

### **2. Actualizar Libro:**
```python
# Usuario actualiza el ISBN de un libro
book_service.update_book("B001", {"isbn": "999"})

# Automáticamente:
# 1. Se actualiza en ambos inventarios
# 2. Se reordena el Inventario Ordenado con insercion_ordenada()
# 3. inventory_sorted.json se actualiza con el nuevo orden
```

### **3. Eliminar Libro:**
```python
# Usuario elimina un libro
book_service.delete_book("B001")

# Automáticamente:
# 1. Se elimina de ambos inventarios
# 2. El Inventario Ordenado se mantiene ordenado (sin necesidad de reordenar)
# 3. inventory_sorted.json se actualiza
```

### **4. Preparación para Búsqueda Binaria:**
```python
# El sistema siempre tiene listo el inventario ordenado
inventario_ordenado = inventory_repo.load_sorted()

# Búsqueda binaria funciona correctamente porque el inventario
# está GARANTIZADO ordenado por ISBN gracias a insercion_ordenada()
resultado = busqueda_binaria(inventario_ordenado, isbn_buscado)
```

---

## ✅ VALIDACIÓN DE ORDENAMIENTO

### **Verificación Manual:**
```python
# Cargar inventario ordenado
inventario_ordenado = inventory_repo.load_sorted()

# Verificar que cada elemento está en orden
for i in range(len(inventario_ordenado) - 1):
    isbn_actual = inventario_ordenado[i].get_isbn()
    isbn_siguiente = inventario_ordenado[i + 1].get_isbn()
    
    # Verificar que isbn_actual <= isbn_siguiente
    assert not _comparar_isbn_mayor(isbn_actual, isbn_siguiente), \
        f"Error: {isbn_actual} > {isbn_siguiente}"

print("✓ Inventario correctamente ordenado por ISBN")
```

---

## 📝 CONCLUSIONES

### **Cumplimiento de Requisitos:**
✅ **Algoritmo implementado** - Insertion Sort funcional y documentado
✅ **Mantiene Inventario Ordenado** - Se ejecuta automáticamente tras cada cambio
✅ **Preparado para Búsqueda Binaria** - Inventario siempre ordenado por ISBN
✅ **Implementación manual** - No usa `sorted()` ni `.sort()`
✅ **Documentación completa** - Código completamente comentado

### **Ventajas de la Implementación:**
✅ **Automático** - No requiere intervención manual
✅ **Confiable** - Garantiza invariante de ordenamiento
✅ **Estable** - Preserva orden de elementos iguales
✅ **Simple** - Fácil de mantener y entender

### **Integración con el Sistema:**
✅ **BookService** - Trigger automático al agregar/actualizar/eliminar
✅ **InventoryService** - Coordina actualización de ambos inventarios
✅ **InventoryRepository** - Persiste inventario ordenado en JSON
✅ **AlgoritmosBusqueda** - Búsqueda binaria usa inventario ordenado
