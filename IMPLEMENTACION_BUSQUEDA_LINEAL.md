# Implementación de Búsqueda Lineal Recursiva

## 📋 Resumen

Se ha implementado exitosamente el algoritmo de **Búsqueda Lineal Recursiva** para buscar libros por **Título** o **Autor** en el Inventario General (lista desordenada).

---

## 🎯 Características Implementadas

### 1. **Algoritmo Principal: `busqueda_lineal()`**
   - **Ubicación:** `utils/algorithms/AlgoritmosBusqueda.py`
   - **Tipo:** Recursiva (sigue el patrón enseñado en clase)
   - **Complejidad:** O(n) tiempo, O(n) espacio
   - **Entrada:** Inventario (no requiere ordenamiento) + criterio de búsqueda
   - **Salida:** Índice del primer libro encontrado o -1 si no existe

### 2. **Función Auxiliar: `normalizar_texto()`**
   - **Ubicación:** `utils/search_helpers.py`
   - **Propósito:** Normalización para búsquedas insensibles a mayúsculas y acentos
   - **Transformaciones:**
     - Convierte a minúsculas
     - Elimina acentos (á→a, é→e, í→i, ó→o, ú→u, ñ→n)
     - Elimina espacios extra

---

## 🔍 Comparación con el Ejemplo de Clase

### **Patrón Original (Clase):**
```python
def busqueda_lineal(lista, elemento, indice=0):
    # Caso base: llegamos al final sin encontrar
    if indice >= len(lista):
        return -1
    
    # Caso base: encontramos el elemento
    if lista[indice] == elemento:
        return indice
    
    # Caso recursivo: seguir buscando
    return busqueda_lineal(lista, elemento, indice + 1)
```

### **Implementación del Proyecto:**
```python
def busqueda_lineal(inventario, criterio_busqueda, indice=0):
    # Caso base: llegamos al final sin encontrar
    if indice >= len(inventario):
        return -1
    
    # Obtener libro actual
    libro_actual = inventario[indice].get_book()
    
    # Si no hay libro, continuar
    if libro_actual is None:
        return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
    
    # Obtener título y autor
    titulo = libro_actual.get_title() or ""
    autor = libro_actual.get_author() or ""
    
    # Normalizar texto
    from utils.search_helpers import normalizar_texto
    criterio_norm = normalizar_texto(criterio_busqueda)
    titulo_norm = normalizar_texto(titulo)
    autor_norm = normalizar_texto(autor)
    
    # Caso base: encontramos coincidencia parcial
    if criterio_norm in titulo_norm or criterio_norm in autor_norm:
        return indice
    
    # Caso recursivo: seguir buscando
    return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
```

### **Diferencias Clave:**
| Aspecto | Ejemplo Clase | Implementación Proyecto |
|---------|--------------|------------------------|
| **Comparación** | Exacta (`==`) | Parcial (`in`) |
| **Datos** | Lista simple | Objetos `Inventory` |
| **Búsqueda** | Un campo | Título + Autor |
| **Normalización** | No | Sí (mayúsculas/acentos) |
| **Manejo nulos** | No aplica | Verifica `None` |

---

## ✅ Funcionalidades

### **Búsqueda Flexible:**
- ✓ Búsqueda por **título exacto**: `"1984"` → Encuentra "1984"
- ✓ Búsqueda por **título parcial**: `"quijote"` → Encuentra "Don Quijote de la Mancha"
- ✓ Búsqueda por **autor**: `"garcía márquez"` → Encuentra libros de Gabriel García Márquez
- ✓ **Insensible a mayúsculas**: `"ORWELL"` = `"orwell"` = `"OrWeLl"`
- ✓ **Insensible a acentos**: `"anos"` encuentra "Años", `"garcia"` encuentra "García"

### **NO Requiere Ordenamiento:**
- ✓ Funciona sobre el **Inventario General** (lista desordenada)
- ✓ Útil cuando el criterio de búsqueda no es el mismo que el criterio de ordenamiento

---

## 📊 Resultados de Pruebas

Se creó `test_busqueda_lineal.py` con 8 pruebas exhaustivas:

```
✓ TEST 1: Búsqueda por título exacto - ÉXITO
✓ TEST 2: Búsqueda por título parcial - ÉXITO
✓ TEST 3: Búsqueda por autor - ÉXITO
✓ TEST 4: Búsqueda insensible a mayúsculas (4 casos) - ÉXITO
✓ TEST 5: Búsqueda sin acentos (3 casos) - ÉXITO
✓ TEST 6: Búsqueda de elemento inexistente - ÉXITO
✓ TEST 7: Función auxiliar normalizar_texto (5 casos) - ÉXITO
✓ TEST 8: Verificación de recursividad - ÉXITO
```

**Todas las pruebas pasaron exitosamente.**

---

## 📁 Archivos Modificados/Creados

### **Modificados:**
1. **`utils/algorithms/AlgoritmosBusqueda.py`**
   - Agregada función `busqueda_lineal()`
   - Actualizada documentación del módulo
   - Exportada en `__all__`

2. **`utils/search_helpers.py`**
   - Agregada función `normalizar_texto()`
   - Documentación completa con ejemplos
   - Exportada en `__all__`

### **Creados:**
3. **`test_busqueda_lineal.py`**
   - Suite de 8 pruebas completas
   - Inventario de prueba con 5 libros
   - Validación de recursividad

---

## 💡 Casos de Uso en el Sistema

### **1. Búsqueda de Libros en UI:**
```python
from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal

# Usuario busca "quijote" en la interfaz
indice = busqueda_lineal(inventario_general, "quijote")

if indice != -1:
    libro = inventario_general[indice].get_book()
    mostrar_resultado(libro)
else:
    mostrar_mensaje("No se encontró ningún libro")
```

### **2. Búsqueda por Autor:**
```python
# Usuario busca todos los libros de "García Márquez"
indice = busqueda_lineal(inventario_general, "garcía márquez")

# Encontrar más coincidencias continuando la búsqueda
while indice != -1:
    libro = inventario_general[indice].get_book()
    resultados.append(libro)
    indice = busqueda_lineal(inventario_general, "garcía márquez", indice + 1)
```

---

## 🔬 Análisis de Complejidad

### **Búsqueda Lineal:**
- **Complejidad Temporal:**
  - Mejor caso: O(1) - elemento en primera posición
  - Caso promedio: O(n/2) ≈ O(n)
  - Peor caso: O(n) - elemento en última posición o no existe

- **Complejidad Espacial:**
  - O(n) por la pila de recursión
  - Cada llamada recursiva agrega un frame a la pila

### **Comparación con Búsqueda Binaria:**
| Aspecto | Búsqueda Lineal | Búsqueda Binaria |
|---------|-----------------|------------------|
| **Ordenamiento** | NO requiere | SÍ requiere |
| **Tiempo** | O(n) | O(log n) |
| **Espacio** | O(n) | O(log n) |
| **Búsqueda** | Título/Autor | Solo ISBN |
| **Coincidencia** | Parcial | Exacta |

---

## 📝 Documentación Técnica

### **Función `busqueda_lineal()`:**

**Parámetros:**
- `inventario` (list): Lista de objetos `Inventory` (NO necesita estar ordenada)
- `criterio_busqueda` (str): Texto a buscar en título o autor
- `indice` (int): Índice actual (uso interno, default: 0)

**Retorno:**
- `int`: Índice del primer libro encontrado, o -1 si no existe

**Ejemplo:**
```python
>>> from utils.algorithms.AlgoritmosBusqueda import busqueda_lineal
>>> indice = busqueda_lineal(inventario_general, "garcía márquez")
>>> if indice != -1:
...     libro = inventario_general[indice].get_book()
...     print(libro.get_title())
```

---

## ✨ Conclusión

La implementación de Búsqueda Lineal Recursiva cumple con los requisitos educativos:

1. ✅ **Sigue el patrón enseñado en clase** (estructura recursiva idéntica)
2. ✅ **Adaptado al proyecto** (objetos Inventory en lugar de lista simple)
3. ✅ **Funcionalidad mejorada** (búsqueda parcial, normalización de texto)
4. ✅ **Totalmente probado** (8 pruebas exhaustivas, todas exitosas)
5. ✅ **Bien documentado** (docstrings completos, ejemplos de uso)

El sistema ahora cuenta con dos algoritmos de búsqueda complementarios:
- **Búsqueda Binaria** (O(log n)) para ISBN en inventario ordenado
- **Búsqueda Lineal** (O(n)) para Título/Autor en inventario general

---

**Autor:** Sistema de Gestión de Bibliotecas  
**Fecha:** 2025-12-03  
**Versión:** 1.0
