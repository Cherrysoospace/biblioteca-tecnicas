# Guía de Prueba: Algoritmo de Fuerza Bruta

Esta guía te ayudará a probar el algoritmo de fuerza bruta implementado en el proyecto.

---

## 🚀 Pruebas Rápidas

### 1. Ejecutar Demostración Completa

```bash
python demo_brute_force.py
```

**Qué hace:**
- Carga todos los libros del inventario
- Calcula cuántas combinaciones explorará
- Encuentra todas las combinaciones de 4 libros que excedan 8 Kg
- Muestra estadísticas detalladas

**Resultado esperado:**
```
====================================================================================================
BRUTE FORCE ALGORITHM DEMONSTRATION
Finding Risky 4-Book Combinations (Weight > 8 Kg)
====================================================================================================

Inventory Statistics:
  Total books in catalog: 33
  Total 4-book combinations to explore: 40,920

Running Brute Force Algorithm (threshold = 8.0 Kg)...
...
```

---

### 2. Ejecutar Pruebas Unitarias

```bash
python -m pytest test_brute_force.py -v
```

**Qué hace:**
- Ejecuta 10 pruebas automáticas
- Verifica todos los casos del algoritmo
- Valida la correctitud de los resultados

**Resultado esperado:**
```
test_brute_force.py::TestBruteForceAlgorithm::test_find_risky_combinations_basic PASSED
test_brute_force.py::TestBruteForceAlgorithm::test_find_risky_combinations_no_risky PASSED
...
========================================== 10 passed in 0.07s ===========================================
```

---

### 3. Probar el Algoritmo Directamente

Crea un archivo `test_manual_brute_force.py`:

```python
from utils.algorithms.brute_force import find_risky_combinations, count_total_combinations

# Crear libros de prueba
books = [
    {'id': 'B001', 'title': 'Libro Pesado 1', 'author': 'Autor A', 'weight': 2.5},
    {'id': 'B002', 'title': 'Libro Pesado 2', 'author': 'Autor B', 'weight': 2.8},
    {'id': 'B003', 'title': 'Libro Pesado 3', 'author': 'Autor C', 'weight': 2.3},
    {'id': 'B004', 'title': 'Libro Pesado 4', 'author': 'Autor D', 'weight': 2.0},
]

print(f"Total de libros: {len(books)}")
print(f"Combinaciones a explorar: {count_total_combinations(len(books))}")

# Buscar combinaciones riesgosas
risky = find_risky_combinations(books, threshold=8.0)

print(f"\nCombinaciones riesgosas encontradas: {len(risky)}")
for combo in risky:
    print(f"  Peso total: {combo['total_weight']} Kg (Excede por {combo['excess']} Kg)")
```

**Ejecutar:**
```bash
python test_manual_brute_force.py
```

---

## 🧪 Casos de Prueba

### Caso 1: Sin combinaciones riesgosas (libros ligeros)

```python
books = [
    {'id': 'B001', 'title': 'Ligero 1', 'author': 'A', 'weight': 1.0},
    {'id': 'B002', 'title': 'Ligero 2', 'author': 'B', 'weight': 1.0},
    {'id': 'B003', 'title': 'Ligero 3', 'author': 'C', 'weight': 1.0},
    {'id': 'B004', 'title': 'Ligero 4', 'author': 'D', 'weight': 1.0},
]

risky = find_risky_combinations(books, threshold=8.0)
# Resultado: [] (lista vacía, 1+1+1+1 = 4 Kg < 8 Kg)
```

### Caso 2: Una combinación riesgosa

```python
books = [
    {'id': 'B001', 'title': 'Pesado 1', 'author': 'A', 'weight': 2.5},
    {'id': 'B002', 'title': 'Pesado 2', 'author': 'B', 'weight': 2.8},
    {'id': 'B003', 'title': 'Pesado 3', 'author': 'C', 'weight': 2.3},
    {'id': 'B004', 'title': 'Pesado 4', 'author': 'D', 'weight': 2.0},
]

risky = find_risky_combinations(books, threshold=8.0)
# Resultado: 1 combinación (2.5+2.8+2.3+2.0 = 9.6 Kg > 8 Kg)
```

### Caso 3: Múltiples combinaciones riesgosas

```python
books = [
    {'id': 'B001', 'title': 'Pesado 1', 'author': 'A', 'weight': 2.5},
    {'id': 'B002', 'title': 'Pesado 2', 'author': 'B', 'weight': 2.8},
    {'id': 'B003', 'title': 'Pesado 3', 'author': 'C', 'weight': 2.3},
    {'id': 'B004', 'title': 'Pesado 4', 'author': 'D', 'weight': 2.0},
    {'id': 'B005', 'title': 'Muy Pesado', 'author': 'E', 'weight': 3.0},
]

risky = find_risky_combinations(books, threshold=8.0)
# Resultado: Varias combinaciones (las que incluyen libros pesados)
```

### Caso 4: Umbral personalizado

```python
books = [
    {'id': 'B001', 'title': 'Libro 1', 'author': 'A', 'weight': 1.5},
    {'id': 'B002', 'title': 'Libro 2', 'author': 'B', 'weight': 1.5},
    {'id': 'B003', 'title': 'Libro 3', 'author': 'C', 'weight': 1.5},
    {'id': 'B004', 'title': 'Libro 4', 'author': 'D', 'weight': 1.5},
]

risky_8 = find_risky_combinations(books, threshold=8.0)  # []
risky_5 = find_risky_combinations(books, threshold=5.0)  # [1 combinación]
# Total: 1.5+1.5+1.5+1.5 = 6.0 Kg
```

---

## 📊 Desde el Sistema Principal

Si quieres probar el algoritmo desde la UI del sistema:

1. **Agregar funcionalidad en la UI** (opcional):
   - Opción en el menú de estanterías
   - "Analizar combinaciones riesgosas"

2. **O usar desde Python REPL:**

```python
from controllers.shelf_controller import ShelfController

controller = ShelfController()

# Obtener número de combinaciones
total = controller.count_possible_combinations()
print(f"Total de combinaciones: {total}")

# Encontrar combinaciones riesgosas
risky = controller.find_risky_book_combinations(threshold=8.0)
print(f"Combinaciones riesgosas: {len(risky)}")

# Ver detalles de una combinación
if risky:
    first = risky[0]
    print(f"Peso: {first['total_weight']} Kg")
    print(f"Excede por: {first['excess']} Kg")
    for book in first['books']:
        print(f"  - {book['title']}: {book['weight']} Kg")
```

---

## 🔍 Verificación de Resultados

### Fórmula de Combinaciones

Para verificar que el algoritmo explora todas las combinaciones:

**C(n, 4) = n! / (4! × (n-4)!)**

Ejemplos:
- C(4, 4) = 1
- C(5, 4) = 5
- C(10, 4) = 210
- C(20, 4) = 4,845

### Verificación Manual

Si tienes 5 libros: A, B, C, D, E

**Todas las combinaciones posibles:**
1. A + B + C + D
2. A + B + C + E
3. A + B + D + E
4. A + C + D + E
5. B + C + D + E

**Total: 5 combinaciones** ✅

---

## ❗ Solución de Problemas

### Problema: "No risky combinations found"

**Posibles causas:**
1. Los libros en el inventario son demasiado ligeros
2. El inventario tiene menos de 4 libros
3. Ninguna combinación de 4 libros excede 8 Kg

**Solución:**
```python
# Agregar libros más pesados para pruebas
from models.Books import Book
from services.book_service import BookService

service = BookService()

# Crear libros pesados
heavy1 = Book('TEST1', '978-TEST-001', 'Heavy Book 1', 'Test Author', 2.5, 50000, False)
heavy2 = Book('TEST2', '978-TEST-002', 'Heavy Book 2', 'Test Author', 2.8, 60000, False)
heavy3 = Book('TEST3', '978-TEST-003', 'Heavy Book 3', 'Test Author', 2.3, 55000, False)
heavy4 = Book('TEST4', '978-TEST-004', 'Heavy Book 4', 'Test Author', 2.0, 45000, False)

# Agregar al inventario
service.add_book(heavy1)
service.add_book(heavy2)
service.add_book(heavy3)
service.add_book(heavy4)

# Ahora probar el algoritmo de nuevo
```

### Problema: "Takes too long"

**Causa:** Demasiados libros en el inventario

**Solución:**
- Con 50+ libros, el algoritmo puede tardar varios segundos
- Esto es ESPERADO en fuerza bruta (O(n⁴))
- No es un error, es la naturaleza del algoritmo

---

## ✅ Checklist de Pruebas

- [ ] ✅ Ejecutar `demo_brute_force.py`
- [ ] ✅ Ejecutar `pytest test_brute_force.py`
- [ ] ✅ Probar con 4 libros (1 combinación)
- [ ] ✅ Probar con 5 libros (5 combinaciones)
- [ ] ✅ Probar con umbral personalizado
- [ ] ✅ Verificar que encuentra todas las combinaciones
- [ ] ✅ Verificar que los pesos se suman correctamente
- [ ] ✅ Verificar que el exceso se calcula bien

---

## 📝 Notas Finales

1. **Rendimiento esperado:**
   - 20 libros: ~0.01 segundos
   - 33 libros: ~0.05 segundos
   - 50 libros: ~0.5 segundos

2. **El algoritmo es correcto si:**
   - Explora C(n, 4) combinaciones
   - Encuentra TODAS las que exceden el umbral
   - No reporta falsos positivos

3. **Documentación completa:**
   - Ver: `IMPLEMENTACION_FUERZA_BRUTA.md`
   - Código: `utils/algorithms/brute_force.py`

---

**¡Algoritmo funcionando correctamente! ✅**
