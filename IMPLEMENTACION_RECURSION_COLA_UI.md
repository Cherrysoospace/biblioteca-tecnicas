# Interfaz de Recursión de Cola - Author Weight Report

## Resumen

Se ha creado una interfaz gráfica completa para demostrar la **Recursión de Cola** (Queue/Tail Recursion) calculando el **peso promedio** de libros por autor.

## Archivo Creado

**`ui/book/author_weight_report.py`** - Ventana de interfaz gráfica para calcular peso promedio por autor usando recursión de cola.

## Características Principales

### 1. **Interfaz Intuitiva**
- ✅ Selección de autor mediante dropdown (todos los autores de la base de datos)
- ✅ Checkbox para activar **modo debug** (muestra el flujo de recursión)
- ✅ Área de resultados scrollable con formato claro
- ✅ Botones para calcular, limpiar y cerrar

### 2. **Visualización Completa**
La interfaz muestra:
- 👤 **Autor seleccionado**
- 📚 **Número de libros** encontrados del autor
- ⚖️ **Peso promedio** calculado (en kg)
- 🔍 **Flujo de recursión** (si modo debug está activado)
- 📋 **Detalle de cada libro** (título, ISBN, peso, estado)
- 📐 **Cálculo manual** verificable (suma total ÷ cantidad)
- 🔄 **Explicación del algoritmo** con pseudocódigo

### 3. **Modo Debug Especial**
Cuando se activa el modo debug:
- Captura la salida de consola del algoritmo recursivo
- Muestra cada paso de la recursión:
  - `Skip index=X: author=Y` (cuando no coincide el autor)
  - `Include index=X: weight=W -> count=C, total=T` (cuando coincide)
  - `Base case reached: count=C, total_weight=T` (caso base)

### 4. **Integración con el Sistema**
- ✅ Importado en `ui/main_menu.py`
- ✅ Nuevo botón "⚖️ Peso por Autor" en el menú principal
- ✅ Usa `BookController.calculate_average_weight_by_author()`
- ✅ Logging completo de operaciones
- ✅ Manejo de errores robusto con `UIErrorHandler`

## Ejemplo de Uso

### Caso de Prueba: Autor "hi"

Autor "hi" tiene 2 libros en la base de datos:
- Libro 1: peso = 0.25 kg
- Libro 2: peso = 0.20 kg

**Resultado esperado**: (0.25 + 0.20) / 2 = **0.225 kg**

### Flujo de Recursión (Debug)
```
Skip index=0: author=Homer
Skip index=1: author=Jane Austen
...
Skip index=27: author=DU DU DU
Include index=28: weight=0.25 -> count=1, total=0.25
Include index=29: weight=0.2 -> count=2, total=0.45
Skip index=30: author=0001
...
Base case reached: count=2, total_weight=0.45
```

**✅ Resultado**: 0.45 / 2 = 0.225 kg

## Implementación Técnica

### Estructura del Algoritmo
```python
def avg_weight_by_author(books, author, index=0, count=0, total_weight=0.0, debug=False):
    # Caso base
    if index >= len(books):
        return (total_weight / count) if count > 0 else 0.0
    
    # Obtener libro actual
    book = books[index]
    book_author = book.get('author', '')
    book_weight = book.get('weight', 0.0)
    
    # Paso recursivo con acumuladores
    if book_author == author:
        return avg_weight_by_author(books, author, index + 1, 
                                     count + 1, total_weight + book_weight, debug)
    else:
        return avg_weight_by_author(books, author, index + 1, 
                                     count, total_weight, debug)
```

### Captura de Output en Modo Debug
```python
import io
import sys

# Redirigir stdout
old_stdout = sys.stdout
sys.stdout = captured_output = io.StringIO()

# Ejecutar con debug
avg_weight = controller.calculate_average_weight_by_author(author, debug=True)

# Restaurar stdout y obtener la salida capturada
sys.stdout = old_stdout
debug_output = captured_output.getvalue()
```

## Validaciones y Manejo de Errores

1. **Validación de selección**: No permite calcular sin seleccionar un autor válido
2. **Libros sin peso**: Trata valores faltantes como 0.0
3. **Autor sin libros**: Retorna 0.0 (evita división por cero)
4. **Errores de cálculo**: Capturados y mostrados con `UIErrorHandler`
5. **Logging**: Todas las operaciones quedan registradas

## Cumplimiento del Proyecto

Esta implementación cumple con el requisito del proyecto:

> **"Recursión de Cola: Implementar una función recursiva que calcule el Peso Promedio de la colección de un autor, demostrando la lógica de la recursión de cola por consola."**

✅ **Función recursiva implementada** (`avg_weight_by_author`)  
✅ **Calcula peso promedio** por autor  
✅ **Usa patrón de cola** (acumuladores, última operación es llamada recursiva)  
✅ **Demuestra la lógica por consola** (modo debug)  
✅ **Interfaz gráfica completa** para facilitar las pruebas

## Archivos Modificados/Creados

1. **Creado**: `ui/book/author_weight_report.py` (interfaz completa)
2. **Modificado**: `ui/main_menu.py` (import y botón)
3. **Creado**: `test_queue_recursion.py` (pruebas CLI)
4. **Modificado**: `utils/recursion/queue_recursion.py` (simplificado)
5. **Modificado**: `services/book_service.py` (método agregado)
6. **Modificado**: `controllers/book_controller.py` (método agregado)
