# Implementación de Recursión de Pila - Valor Total por Autor

## 📚 Resumen de Implementación

Se ha implementado completamente la funcionalidad de **Recursión de Pila** para calcular el valor total de todos los libros de un autor específico, cumpliendo con el requerimiento del proyecto:

> "Recursión de Pila: Implementar una función recursiva que calcule el Valor Total de todos los libros de un autor específico."

---

## 🎯 Componentes Implementados

### 1. **Función de Recursión de Pila** (`utils/recursion/stack_recursion.py`)
- ✅ Algoritmo recursivo puro que procesa un libro a la vez
- ✅ Usa la pila de llamadas para acumular valores
- ✅ Caso base cuando se procesan todos los libros
- ✅ Complejidad: O(n) tiempo, O(n) espacio en pila
- ✅ Simplificado para usar `price` (no `value`)
- ✅ Eliminadas validaciones innecesarias (siempre son diccionarios con números)

### 2. **Capa de Servicio** (`services/book_service.py`)
- ✅ Método `calculate_total_value_by_author(author: str) -> float`
- ✅ Convierte objetos Book al formato esperado por la recursión
- ✅ Método auxiliar `get_all_authors() -> List[str]` para listar autores únicos

### 3. **Capa de Control** (`controllers/book_controller.py`)
- ✅ Método `calculate_total_value_by_author(author: str)`
- ✅ Método `get_all_authors()` 
- ✅ Expone la funcionalidad a la capa de presentación

### 4. **Interfaz Gráfica** (`ui/book/author_value_report.py`)
- ✅ Ventana dedicada con diseño consistente con el sistema
- ✅ Selector dropdown con todos los autores disponibles
- ✅ Botón de cálculo con ícono
- ✅ Área de resultados con formato profesional
- ✅ Muestra explicación del algoritmo de recursión
- ✅ Lista detallada de libros del autor
- ✅ Manejo robusto de errores

### 5. **Menú Principal** (`ui/main_menu.py`)
- ✅ Botón "📚 Valor por Autor" agregado al menú
- ✅ Importación del módulo `AuthorValueReport`
- ✅ Método `open_author_value_report()` para abrir la ventana

---

## 🚀 Cómo Usar

### Opción 1: Interfaz Gráfica
1. Ejecutar el sistema: `python main.py`
2. En el menú principal, hacer clic en **"📚 Valor por Autor"**
3. Seleccionar un autor del menú desplegable
4. Presionar **"🧮 Calcular Valor Total"**
5. Ver los resultados detallados con explicación del algoritmo

### Opción 2: Script de Prueba
```bash
python test_author_value_recursion.py
```

### Opción 3: Programática
```python
from controllers.book_controller import BookController

controller = BookController()
total = controller.calculate_total_value_by_author("Homer")
print(f"Valor total: ${total:,.0f} COP")
```

---

## 📊 Ejemplo de Salida

```
╔════════════════════════════════════════════════════════════╗
║              RESULTADO DEL CÁLCULO (Recursión)             ║
╚════════════════════════════════════════════════════════════╝

👤 Autor: Suzanne Collins

📚 Libros encontrados: 2

💰 VALOR TOTAL: $71,000 COP

───────────────────────────────────────────────────────────────

📋 Detalle de libros:

   1. Mockingjay
      • ISBN: 9780446310789
      • Precio: $26,000 COP
      • Estado: Disponible

   2. The Hunger Games
      • ISBN: 9780439023528
      • Precio: $45,000 COP
      • Estado: Disponible

───────────────────────────────────────────────────────────────

🔄 Explicación del Algoritmo (Recursión de Pila):

   La función procesa cada libro recursivamente:
   
   total_value_by_author(books, "Suzanne Collins", index=0)
   ├─ Si index >= len(books): return 0  (caso base)
   ├─ book = books[index]
   ├─ Si book.author == "Suzanne Collins":
   │     contribution = book.price
   │  Sino:
   │     contribution = 0
   └─ return contribution + total_value_by_author(..., index+1)
   
   📊 Llamadas recursivas realizadas: 32
   💾 Profundidad máxima de pila: 32
   ⏱️  Complejidad: O(n) tiempo, O(n) espacio
```

---

## ✅ Verificación

Todos los componentes fueron probados y funcionan correctamente:

- ✅ La función de recursión calcula correctamente los totales
- ✅ El servicio convierte los datos apropiadamente
- ✅ El controlador expone la funcionalidad
- ✅ La UI muestra resultados formateados
- ✅ El menú principal tiene el botón activo
- ✅ Manejo de errores robusto en todos los niveles

---

## 🔄 Algoritmo de Recursión de Pila

### Características:
- **Tipo:** Recursión de Pila (Stack Recursion)
- **Forma:** Similar a factorial clásico
- **Acumulación:** En la vuelta de las llamadas
- **Caso base:** `index >= len(books)` retorna 0
- **Caso recursivo:** `contribution + recursion(index+1)`

### Por qué es Recursión de PILA:
1. Hay una operación **después** de la llamada recursiva (suma)
2. Cada llamada debe **esperar** el resultado de la siguiente
3. Acumula en el **camino de vuelta**
4. Usa la **pila de llamadas** para guardar estado

---

## 📁 Archivos Modificados/Creados

1. ✅ `utils/recursion/stack_recursion.py` - Simplificado y optimizado
2. ✅ `services/book_service.py` - Agregados métodos de recursión
3. ✅ `controllers/book_controller.py` - Expuesta funcionalidad
4. ✅ `ui/book/author_value_report.py` - **NUEVO** - Ventana UI
5. ✅ `ui/main_menu.py` - Agregado botón y método
6. ✅ `test_author_value_recursion.py` - **NUEVO** - Script de prueba

---

## 🎓 Cumplimiento del Proyecto

Esta implementación cumple completamente con el requisito:

> **Recursión (Pila y Cola)**
> 
> 1. Recursión de Pila: Implementar una función recursiva que calcule el Valor Total
>    de todos los libros de un autor específico.

✅ **Implementado y funcional**

---
