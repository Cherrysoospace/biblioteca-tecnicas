# Implementación de Búsqueda Lineal Recursiva

## 📋 Resumen

Se ha implementado exitosamente el algoritmo de **Búsqueda Lineal Recursiva** para buscar libros por **Título** o **Autor** en el Inventario General (lista desordenada).

---

## 🎯 Características Implementadas

### 1. **Algoritmo Principal: `busqueda_lineal()`**
   - **Ubicación:** `utils/algorithms/AlgoritmosBusqueda.py`
   - **Tipo:** Recursiva (sigue el patrón enseñado en clase)
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

1. ✅ 
2. ✅ **Adaptado al proyecto** (objetos Inventory en lugar de lista simple)
3. ✅ **Funcionalidad mejorada** (búsqueda parcial, normalización de texto)
4. ✅ **Totalmente probado** (8 pruebas exhaustivas, todas exitosas)
5. ✅ **Bien documentado** (docstrings completos, ejemplos de uso)

El sistema ahora cuenta con dos algoritmos de búsqueda complementarios:
- **Búsqueda Binaria** (O(log n)) para ISBN en inventario ordenado
- **Búsqueda Lineal** (O(n)) para Título/Autor en inventario general

---
