# 🔍 Guía: Cómo Probar la Búsqueda Lineal en el Programa

## 📋 Opciones para Probar la Búsqueda Lineal

---

## ✅ **OPCIÓN 1: Usar el Script de Prueba (Recomendado para Pruebas Rápidas)**

### Paso 1: Ejecutar el script de prueba
```powershell
py test_busqueda_lineal.py
```

**Qué hace:**
- Prueba el algoritmo con datos de ejemplo
- Muestra 8 pruebas diferentes
- Verifica búsqueda por título, autor, mayúsculas, acentos, etc.

**Resultado esperado:**
```
✓ TEST 1: Búsqueda por título exacto - ÉXITO
✓ TEST 2: Búsqueda por título parcial - ÉXITO
✓ TEST 3: Búsqueda por autor - ÉXITO
... (todas las pruebas pasan)
```

---

## ✅ **OPCIÓN 2: Probar con Datos Reales del Sistema**

### Paso 1: Ejecutar el script de integración
```powershell
py test_integration_busqueda_lineal.py
```

**Qué hace:**
- Usa los datos reales de `data/books.json`
- Prueba `find_by_title()` y `find_by_author()` del sistema
- Busca libros reales en tu inventario

**Ejemplo de búsqueda:**
```
Búsqueda: 'the'
Total de resultados: 12
  1. The Odyssey
  2. The Great Gatsby
  3. The Road
  4. The Institute
  5. The Alchemist
  ...
```

---

## ✅ **OPCIÓN 3: Usar Python Interactivo (Consola)**

### Paso 1: Abrir Python en el directorio del proyecto
```powershell
py
```

### Paso 2: Importar y usar el algoritmo
```python
# Importar servicios necesarios
from services.inventory_service import InventoryService

# Crear instancia del servicio
service = InventoryService()

# BÚSQUEDA POR TÍTULO
resultados = service.find_by_title("quijote")
print(f"Encontrados: {len(resultados)} libros")
for inv in resultados:
    libro = inv.get_book()
    print(f"- {libro.get_title()} ({libro.get_author()})")

# BÚSQUEDA POR AUTOR
resultados = service.find_by_author("garcía")
print(f"Encontrados: {len(resultados)} libros")
for inv in resultados:
    libro = inv.get_book()
    print(f"- {libro.get_title()} ({libro.get_author()})")

# BÚSQUEDA INSENSIBLE A MAYÚSCULAS
resultados = service.find_by_title("THE ODYSSEY")  # en mayúsculas
print(f"Encontrados: {len(resultados)} libros")

# BÚSQUEDA SIN ACENTOS
resultados = service.find_by_author("garcia marquez")  # sin acentos
print(f"Encontrados: {len(resultados)} libros")

# Salir
exit()
```

---

## ✅ **OPCIÓN 4: Crear un Programa de Demostración Simple**

### Archivo: `demo_busqueda_lineal.py`

Crea este archivo en la raíz del proyecto:

```python
"""
Demo interactiva de búsqueda lineal
"""
from services.inventory_service import InventoryService

def main():
    print("\n" + "="*60)
    print("🔍 DEMOSTRACIÓN DE BÚSQUEDA LINEAL")
    print("="*60)
    
    service = InventoryService()
    
    while True:
        print("\n" + "-"*60)
        print("Opciones:")
        print("1. Buscar por título")
        print("2. Buscar por autor")
        print("3. Salir")
        print("-"*60)
        
        opcion = input("\nElige una opción (1-3): ").strip()
        
        if opcion == "1":
            titulo = input("Introduce el título (puede ser parcial): ").strip()
            resultados = service.find_by_title(titulo)
            
            print(f"\n📚 Resultados: {len(resultados)} libro(s) encontrado(s)")
            for i, inv in enumerate(resultados, 1):
                libro = inv.get_book()
                print(f"{i}. {libro.get_title()}")
                print(f"   Autor: {libro.get_author()}")
                print(f"   ISBN: {libro.get_ISBNCode()}")
                print(f"   Stock: {inv.get_stock()}")
                print()
        
        elif opcion == "2":
            autor = input("Introduce el autor (puede ser parcial): ").strip()
            resultados = service.find_by_author(autor)
            
            print(f"\n📚 Resultados: {len(resultados)} libro(s) encontrado(s)")
            for i, inv in enumerate(resultados, 1):
                libro = inv.get_book()
                print(f"{i}. {libro.get_title()}")
                print(f"   Autor: {libro.get_author()}")
                print(f"   ISBN: {libro.get_ISBNCode()}")
                print(f"   Stock: {inv.get_stock()}")
                print()
        
        elif opcion == "3":
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción inválida. Por favor elige 1, 2 o 3.")

if __name__ == "__main__":
    main()
```

### Ejecutar la demo:
```powershell
py demo_busqueda_lineal.py
```

### Ejemplo de uso interactivo:
```
🔍 DEMOSTRACIÓN DE BÚSQUEDA LINEAL
============================================================

Opciones:
1. Buscar por título
2. Buscar por autor
3. Salir
------------------------------------------------------------

Elige una opción (1-3): 1
Introduce el título (puede ser parcial): odyssey

📚 Resultados: 1 libro(s) encontrado(s)
1. The Odyssey
   Autor: Homer
   ISBN: 9780140268867
   Stock: 2

------------------------------------------------------------
Opciones:
1. Buscar por título
2. Buscar por autor
3. Salir
------------------------------------------------------------

Elige una opción (1-3): 2
Introduce el autor (puede ser parcial): homer

📚 Resultados: 1 libro(s) encontrado(s)
1. The Odyssey
   Autor: Homer
   ISBN: 9780140268867
   Stock: 2
```

---

## 🎯 **OPCIÓN 5: Probar en la Interfaz Gráfica (Tkinter)**

### Para agregar búsqueda a la interfaz del programa:

1. **Ejecutar el programa principal:**
   ```powershell
   py main.py
   ```

2. **Ir a "Libros" → "Ver Listado de Libros"**

3. **Usar el campo de búsqueda** (si existe en `book_list.py`)

Si NO existe campo de búsqueda en la UI, puedes agregarlo fácilmente.

---

## 📊 **PRUEBAS QUE PUEDES HACER**

### 1. **Búsqueda Parcial**
```python
service.find_by_title("odyss")  # Encuentra "The Odyssey"
service.find_by_title("great")  # Encuentra "The Great Gatsby"
```

### 2. **Búsqueda Insensible a Mayúsculas**
```python
service.find_by_title("ODYSSEY")  # Funciona igual
service.find_by_title("odyssey")  # Funciona igual
service.find_by_title("OdYsSeY")  # Funciona igual
```

### 3. **Búsqueda Sin Acentos**
```python
service.find_by_author("garcia")  # Encuentra "García Márquez"
service.find_by_title("anos")     # Encuentra "Cien Años de Soledad"
```

### 4. **Búsqueda por Apellido**
```python
service.find_by_author("márquez")  # Encuentra García Márquez
service.find_by_author("orwell")   # Encuentra George Orwell
```

### 5. **Múltiples Resultados**
```python
service.find_by_title("the")  # Encuentra TODOS los libros con "the"
```

---

## 🔬 **Verificar que es Búsqueda Lineal Recursiva**

### Código del algoritmo en `utils/algorithms/AlgoritmosBusqueda.py`:

```python
def busqueda_lineal(inventario, criterio_busqueda, indice=0):
    # Caso base: llegamos al final
    if indice >= len(inventario):
        return -1
    
    # Obtener libro actual
    libro_actual = inventario[indice].get_book()
    
    # Si no hay libro, continuar
    if libro_actual is None:
        return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
    
    # Normalizar y comparar
    from utils.search_helpers import normalizar_texto
    criterio_norm = normalizar_texto(criterio_busqueda)
    titulo_norm = normalizar_texto(libro_actual.get_title())
    autor_norm = normalizar_texto(libro_actual.get_author())
    
    # Caso base: encontrado
    if criterio_norm in titulo_norm or criterio_norm in autor_norm:
        return indice
    
    # Caso recursivo: seguir buscando
    return busqueda_lineal(inventario, criterio_busqueda, indice + 1)
```

**Características:**
- ✅ **Recursiva** (se llama a sí misma)
- ✅ **O(n)** complejidad lineal
- ✅ **NO usa bucles** (for/while)
- ✅ **Sigue el patrón de clase** exactamente

---

## 📝 **Ejemplos de Búsquedas Reales**

Con los datos del sistema (40 libros en `data/books.json`):

| Búsqueda | Tipo | Resultados Esperados |
|----------|------|---------------------|
| `"odyssey"` | Título | "The Odyssey" |
| `"the"` | Título | 12 libros |
| `"garcía"` | Autor | Libros de García Márquez |
| `"orwell"` | Autor | "1984", "Animal Farm" |
| `"alchemist"` | Título | "The Alchemist" |
| `"programacion"` | Título | Libros de programación |

---

## ⚡ **Comando Rápido para Probar AHORA MISMO**

```powershell
py -c "from services.inventory_service import InventoryService; s = InventoryService(); r = s.find_by_title('the'); print(f'Encontrados: {len(r)} libros'); [print(f'- {inv.get_book().get_title()}') for inv in r[:5]]"
```

Esto busca todos los libros con "the" en el título y muestra los primeros 5.

---

## 🎓 **Para Demostrar en Clase**

1. **Mostrar el código recursivo** en `AlgoritmosBusqueda.py`
2. **Ejecutar** `py test_busqueda_lineal.py` para mostrar todas las pruebas
3. **Demostrar en consola** con búsquedas interactivas
4. **Mostrar** que funciona con mayúsculas, acentos, búsqueda parcial
5. **Comparar** con búsqueda binaria (solo ISBN exacto, requiere orden)

---

## ✅ **Resumen de Comandos**

```powershell
# Prueba del algoritmo puro
py test_busqueda_lineal.py

# Prueba con datos reales
py test_integration_busqueda_lineal.py

# Demo interactiva (crear archivo primero)
py demo_busqueda_lineal.py

# Verificar no hay conflictos
py test_no_conflicts_algorithms.py

# Consola Python interactiva
py
>>> from services.inventory_service import InventoryService
>>> service = InventoryService()
>>> resultados = service.find_by_title("odyssey")
>>> print(len(resultados))
```

---

**¡La búsqueda lineal está lista para probarse! 🎉**
