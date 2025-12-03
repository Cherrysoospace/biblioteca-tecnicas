# Implementación del Algoritmo de Fuerza Bruta

## Descripción General

Este documento explica la implementación del algoritmo de **Fuerza Bruta** para encontrar combinaciones de 4 libros que excedan la capacidad máxima de una estantería (8 Kg).

---

## Requerimiento del Proyecto

**Del documento del proyecto:**
> Fuerza Bruta (Estantería Deficiente): Implementar un algoritmo que encuentre y liste todas las combinaciones posibles de cuatro libros que, al sumar su peso en Kg, superen un umbral de "riesgo" de 8 Kg (Que es lo máximo que soporta un estante de libros). El algoritmo debe explorar exhaustivamente todas las combinaciones.

---

## Implementación

### Ubicación de Archivos

```
biblioteca-tecnicas/
├── utils/
│   └── algorithms/
│       └── brute_force.py         # Algoritmo de fuerza bruta
├── services/
│   └── shelf_service.py           # Lógica de negocio
├── controllers/
│   └── shelf_controller.py        # Capa de controlador
├── demo_brute_force.py            # Demostración del algoritmo
└── test_brute_force.py            # Pruebas unitarias
```

---

## Algoritmo Principal

### Función: `find_risky_combinations()`

**Ubicación:** `utils/algorithms/brute_force.py`

**Pseudocódigo:**
```
PARA i DESDE 0 HASTA libros.tamaño - 4 HACER
    PARA j DESDE i+1 HASTA libros.tamaño - 3 HACER
        PARA k DESDE j+1 HASTA libros.tamaño - 2 HACER
            PARA m DESDE k+1 HASTA libros.tamaño - 1 HACER
                peso_total = libros[i].peso + libros[j].peso + libros[k].peso + libros[m].peso
                SI peso_total > umbral ENTONCES
                    AGREGAR (libros[i], libros[j], libros[k], libros[m]) A resultado
RETORNAR resultado
```

**Implementación en Python:**
```python
def find_risky_combinations(books_data: List[Dict[str, Any]], threshold: float = 8.0):
    risky_combinations = []
    n = len(books_data)
    
    if n < 4:
        return risky_combinations
    
    # PARA i DESDE 0 HASTA libros.tamaño - 4 HACER
    for i in range(n - 3):
        
        # PARA j DESDE i+1 HASTA libros.tamaño - 3 HACER
        for j in range(i + 1, n - 2):
            
            # PARA k DESDE j+1 HASTA libros.tamaño - 2 HACER
            for k in range(j + 1, n - 1):
                
                # PARA m DESDE k+1 HASTA libros.tamaño - 1 HACER
                for m in range(k + 1, n):
                    
                    # Obtener los 4 libros
                    book1 = books_data[i]
                    book2 = books_data[j]
                    book3 = books_data[k]
                    book4 = books_data[m]
                    
                    # peso_total = suma de pesos
                    total_weight = (book1['weight'] + book2['weight'] + 
                                  book3['weight'] + book4['weight'])
                    
                    # SI peso_total > umbral ENTONCES
                    if total_weight > threshold:
                        # AGREGAR combinación A resultado
                        risky_combinations.append({
                            'books': [book1, book2, book3, book4],
                            'total_weight': total_weight,
                            'excess': total_weight - threshold
                        })
    
    # RETORNAR resultado
    return risky_combinations
```

---

## Características del Algoritmo

### 1. Búsqueda Exhaustiva
- **Explora TODAS** las combinaciones posibles de 4 libros
- No omite ninguna combinación potencial
- Garantiza encontrar todas las combinaciones riesgosas

### 2. Complejidad
- **Tiempo:** O(n⁴) donde n es el número de libros
- **Espacio:** O(k) donde k es el número de combinaciones riesgosas encontradas

### 3. Número de Combinaciones
Para n libros, el algoritmo explora **C(n, 4) = n! / (4! × (n-4)!)** combinaciones:

| Libros (n) | Combinaciones |
|-----------|---------------|
| 4         | 1             |
| 5         | 5             |
| 10        | 210           |
| 20        | 4,845         |
| 30        | 27,405        |
| 40        | 91,390        |
| 50        | 230,300       |

---

## Integración con el Sistema

### Capa de Servicio

**Archivo:** `services/shelf_service.py`

```python
def find_risky_book_combinations(self, threshold: float = 8.0) -> List[dict]:
    """Find all combinations of 4 books that exceed weight threshold using brute force."""
    from utils.algorithms.brute_force import find_risky_combinations
    from services.book_service import BookService
    
    # Obtener todos los libros del inventario
    book_service = BookService()
    all_books = book_service.get_all_books()
    
    # Convertir objetos Book a diccionarios
    books_data = []
    for book in all_books:
        books_data.append({
            'id': book.get_id(),
            'title': book.get_title(),
            'author': book.get_author(),
            'weight': book.get_weight(),
            'price': book.get_price()
        })
    
    # Aplicar algoritmo de fuerza bruta
    return find_risky_combinations(books_data, threshold)
```

### Capa de Controlador

**Archivo:** `controllers/shelf_controller.py`

```python
def find_risky_book_combinations(self, threshold: float = 8.0):
    """Find all combinations of 4 books that exceed weight threshold."""
    return self.service.find_risky_book_combinations(threshold)

def count_possible_combinations(self) -> int:
    """Get the total number of 4-book combinations that will be explored."""
    return self.service.count_possible_combinations()
```

---

## Uso del Algoritmo

### Desde la UI o Script Principal

```python
from controllers.shelf_controller import ShelfController

# Inicializar controlador
controller = ShelfController()

# Encontrar combinaciones riesgosas
risky = controller.find_risky_book_combinations(threshold=8.0)

# Mostrar resultados
print(f"Combinaciones riesgosas encontradas: {len(risky)}")

for combo in risky:
    print(f"\nPeso total: {combo['total_weight']} Kg")
    print(f"Excede por: {combo['excess']} Kg")
    print("Libros:")
    for book in combo['books']:
        print(f"  - {book['id']}: {book['title']} ({book['weight']} Kg)")
```

### Demo Script

**Ejecutar:** `python demo_brute_force.py`

Este script muestra:
- Estadísticas del inventario
- Número total de combinaciones a explorar
- Todas las combinaciones riesgosas encontradas
- Resumen y análisis

---

## Resultados de Ejemplo

### Ejemplo 1: Inventario con 33 libros

```
====================================================================================================
BRUTE FORCE ALGORITHM DEMONSTRATION
Finding Risky 4-Book Combinations (Weight > 8 Kg)
====================================================================================================

Inventory Statistics:
  Total books in catalog: 33
  Total 4-book combinations to explore: 40,920

Weight Distribution:
  Average book weight: 0.74 Kg
  Lightest book: 0.10 Kg
  Heaviest book: 3.00 Kg

====================================================================================================
Running Brute Force Algorithm (threshold = 8.0 Kg)...
====================================================================================================

✓ No risky combinations found! All 4-book combinations are within safe limits.

====================================================================================================
SUMMARY
====================================================================================================
  Total combinations explored: 40,920
  Risky combinations found: 0
```

### Ejemplo 2: Con libros pesados

```
⚠ Found 4 risky combinations that exceed 8.0 Kg:

==================================================================================================

Risky Combination #1:
  Total Weight: 13.0 Kg
  Exceeds threshold by: 5.0 Kg
  Books in combination:
    1. [B001] Heavy Book 1 by Author A - 1.0 Kg
    2. [B002] Heavy Book 2 by Author B - 1.0 Kg
    3. [B003] Heavy Book 3 by Author C - 1.0 Kg
    4. [B005] Very Heavy Book by Author E - 10.0 Kg
```

---

## Pruebas Unitarias

**Archivo:** `test_brute_force.py`

### Tests implementados:
1. ✅ `test_find_risky_combinations_basic` - Prueba básica con 4 libros
2. ✅ `test_find_risky_combinations_no_risky` - Sin combinaciones riesgosas
3. ✅ `test_find_risky_combinations_multiple` - Múltiples combinaciones
4. ✅ `test_find_risky_combinations_insufficient_books` - Menos de 4 libros
5. ✅ `test_find_risky_combinations_custom_threshold` - Umbral personalizado
6. ✅ `test_combination_structure` - Estructura de los resultados
7. ✅ `test_count_total_combinations` - Conteo de combinaciones
8. ✅ `test_exhaustive_search` - Búsqueda exhaustiva
9. ✅ `test_weight_precision` - Precisión de pesos
10. ✅ `test_invalid_weight_handling` - Manejo de datos inválidos

**Ejecutar pruebas:**
```bash
python -m pytest test_brute_force.py -v
```

**Resultado:** ✅ 10 pruebas pasadas

---

## Ventajas y Desventajas

### ✅ Ventajas
1. **Exhaustivo:** Encuentra TODAS las combinaciones riesgosas
2. **Preciso:** No omite ninguna combinación
3. **Simple:** Fácil de entender e implementar
4. **Verificable:** Resultados completamente predecibles

### ⚠️ Desventajas
1. **Lento:** O(n⁴) es costoso para grandes inventarios
2. **No escalable:** Con 50 libros explora 230,300 combinaciones
3. **Uso de memoria:** Puede generar muchos resultados

---

## Optimizaciones Posibles

Si el rendimiento fuera un problema (no es el caso en este proyecto educativo):

1. **Poda temprana:** Si 3 libros ya superan 8 Kg, no probar el 4to
2. **Ordenamiento:** Ordenar por peso y detener búsqueda anticipadamente
3. **Memoización:** Cachear sumas parciales
4. **Paralelización:** Dividir el trabajo entre procesadores

**Nota:** Estas optimizaciones NO son necesarias para cumplir el requerimiento del proyecto, que específicamente pide "explorar exhaustivamente todas las combinaciones".

---

## Cumplimiento del Requerimiento

✅ **Implementado correctamente:**
- ✅ Encuentra todas las combinaciones de 4 libros
- ✅ Identifica las que superan 8 Kg
- ✅ Explora exhaustivamente (no omite combinaciones)
- ✅ Lista todos los resultados encontrados
- ✅ Integrado con el sistema de estanterías
- ✅ Completamente documentado
- ✅ Probado exhaustivamente

---

## Próximos Pasos

El siguiente algoritmo a implementar es **Backtracking** para la Estantería Óptima:
> "Implementar un algoritmo que encuentre la combinación de libros que maximice el valor total (COP) sin exceder la capacidad máxima de peso (8 Kg) de un estante."

Este problema es conocido como el **Problema de la Mochila (Knapsack Problem)** y será resuelto usando backtracking.

---

## Referencias

- Código fuente: `utils/algorithms/brute_force.py`
- Servicio: `services/shelf_service.py`
- Controlador: `controllers/shelf_controller.py`
- Demo: `demo_brute_force.py`
- Tests: `test_brute_force.py`
