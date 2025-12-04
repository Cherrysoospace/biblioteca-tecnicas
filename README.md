# 🏮 Sistema de Gestión de Biblioteca - Mitrauma

Sistema completo de gestión de biblioteca desarrollado en Python con interfaz gráfica moderna, implementando algoritmos fundamentales de ciencias de la computación.

---

## 👥 Autores

<!-- TODO: Reemplazar con los nombres reales de los autores -->

- **Luz Alejandra López Cuayal** - 55242 - GitHub: Cherrysoospace
- **Cristhian Andrey Zambrano Cerón** - 55009 - GitHub: CristhianZambranoC
---

## 📋 Descripción del Proyecto

Sistema de gestión de biblioteca que implementa:

- ✅ **Gestión de Libros:** CRUD completo con validaciones
- ✅ **Gestión de Usuarios:** Control de usuarios y permisos
- ✅ **Préstamos y Devoluciones:** Sistema completo de préstamos
- ✅ **Reservas:** Cola de espera para libros prestados
- ✅ **Inventario:** Control de stock y disponibilidad
- ✅ **Estanterías:** Organización física de libros
- ✅ **Reportes:** Generación de reportes con ordenamiento

### 🧮 Algoritmos Implementados

El proyecto incluye implementaciones manuales (sin librerías) de:

1. **Búsqueda Binaria** - O(log n)
2. **Búsqueda Lineal Recursiva** - O(n)
3. **Merge Sort** - O(n log n)
4. **Insertion Sort** - O(n²)
5. **Backtracking** - Problema de la mochila (knapsack)
6. **Fuerza Bruta** - Combinaciones de 4 libros
7. **Recursión de Pila** - Cálculo de valor por autor
8. **Recursión de Cola** - Cálculo de peso promedio

### 🏗️ Arquitectura

Arquitectura en capas siguiendo principios SOLID:

```
UI (CustomTkinter)
    ↓
Controllers
    ↓
Services (Lógica de Negocio)
    ↓
Repositories (Persistencia)
    ↓
Models (Entidades)
```

---

## 🚀 Instalación

### Prerrequisitos

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Cherrysoospace/biblioteca-tecnicas.git
cd biblioteca-tecnicas/library
```

O descargar el ZIP desde GitHub y extraer.

### Paso 2: Crear Entorno Virtual (Recomendado)

#### Windows:
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate
```

#### Linux/Mac:
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate
```

### Paso 3: Instalar Dependencias

Una vez activado el entorno virtual:

```bash
pip install -r requirements.txt
```

**Dependencias instaladas:**
- `customtkinter==5.2.2` - Framework de interfaz gráfica moderna
- `darkdetect==0.8.0` - Detección de tema oscuro/claro del sistema
- `packaging==25.0` - Gestión de versiones
- `pillow==12.0.0` - Procesamiento de imágenes

### Paso 4: Verificar Instalación

```bash
# Verificar que Python está correctamente configurado
python --version

# Verificar que las dependencias se instalaron
pip list
```

### Paso 5: Ejecutar el Programa

```bash
python main.py
```

---

## 📂 Estructura del Proyecto

```
library/
├── main.py                 # Punto de entrada del programa
├── requirements.txt        # Dependencias del proyecto
│
├── models/                 # Entidades del dominio
│   ├── Books.py
│   ├── user.py
│   ├── loan.py
│   ├── reservation.py
│   ├── shelf.py
│   └── inventory.py
│
├── repositories/           # Capa de persistencia (JSON)
│   ├── base_repository.py
│   ├── book_repository.py
│   ├── user_repository.py
│   └── ...
│
├── services/              # Lógica de negocio
│   ├── book_service.py
│   ├── loan_service.py
│   ├── inventory_service.py
│   ├── report_service.py
│   └── ...
│
├── controllers/           # Coordinación UI-Services
│   ├── book_controller.py
│   ├── loan_controller.py
│   └── ...
│
├── ui/                    # Interfaz gráfica
│   ├── main_menu.py
│   ├── book/
│   ├── loan/
│   ├── user/
│   └── ...
│
├── utils/                 # Utilidades y algoritmos
│   ├── algorithms/        # Algoritmos implementados
│   │   ├── AlgoritmosBusqueda.py
│   │   ├── AlgoritmosOrdenamiento.py
│   │   ├── backtracking.py
│   │   └── brute_force.py
│   ├── structures/        # Estructuras de datos
│   │   ├── stack.py
│   │   ├── queue.py
│   │   └── ordered_list.py
│   ├── recursion/         # Recursión
│   │   ├── stack_recursion.py
│   │   └── queue_recursion.py
│   ├── validators.py      # Validaciones centralizadas
│   ├── logger.py          # Sistema de logging
│   └── file_handler.py    # Manejo de archivos JSON
│
└── data/                  # Archivos de persistencia (JSON)
    ├── books.json
    ├── users.json
    ├── loans.json
    ├── inventory_general.json
    └── ...
```

---

## 🎮 Uso del Sistema

### Menú Principal

Al ejecutar `python main.py`, aparece el menú principal con opciones:

- **📚 Libros:** Gestionar catálogo (agregar, editar, eliminar, buscar)
- **👥 Usuarios:** Gestionar usuarios del sistema
- **📖 Préstamos:** Registrar préstamos y devoluciones
- **🔖 Reservas:** Gestionar cola de espera
- **📊 Reportes:** Ver reportes ordenados y estadísticas
- **🗄️ Estanterías:** Organizar libros por ubicación física

### Funcionalidades Destacadas

#### 🔍 Búsqueda de Libros
- **Búsqueda Lineal:** Por título o autor (búsqueda parcial)
- **Búsqueda Binaria:** Por ISBN en inventario ordenado

#### 📊 Reportes Automáticos
- **Reporte de Inventario:** Lista de todos los libros ordenados por precio (Merge Sort)
- **Backtracking Report:** Combinación óptima de libros para una estantería
- **Brute Force Report:** Todas las combinaciones riesgosas de 4 libros

#### ♻️ Recursión
- **Valor Total por Autor:** Suma recursiva usando pila
- **Peso Promedio por Autor:** Cálculo recursivo usando cola

---

## 🧪 Testing

El proyecto incluye tests exhaustivos en archivos `test_*.py`:

```bash
# Ejecutar tests individuales
python test_backtracking.py
python test_brute_force.py
python test_busqueda_lineal.py
python test_merge_sort_report.py

# Ver todos los tests
ls test_*.py
```

---

## 🛠️ Troubleshooting

### Problema: "No module named 'customtkinter'"

**Solución:**
```bash
pip install customtkinter
```

### Problema: Error al ejecutar en Linux/Mac

**Solución:** Usar `python3` en lugar de `python`:
```bash
python3 main.py
```

### Problema: Interfaz muy pequeña o muy grande

**Solución:** El sistema detecta automáticamente la resolución de pantalla y ajusta el escalado. Si necesitas ajustarlo manualmente, edita `ui/main_menu.py`:

```python
# Línea ~45
ctk.set_widget_scaling(1.0)  # Cambiar a 0.8 o 1.2 según necesites
```

### Problema: Archivos JSON corruptos

**Solución:** Eliminar la carpeta `data/` y reiniciar el programa (se regenerarán):
```bash
rm -r data/  # Linux/Mac
rmdir /s data  # Windows
python main.py
```

---

## 📝 Notas Técnicas

### Persistencia
- Los datos se almacenan en archivos JSON en la carpeta `data/`
- No requiere base de datos externa
- Formato legible y fácil de depurar

### Logging
- Los logs se guardan en `logs/library.log`
- Útil para debugging y auditoría

### Validaciones
- Todas las entradas son validadas antes de persistir
- Mensajes de error claros y descriptivos

---

## 📚 Documentación Adicional

El proyecto incluye documentación detallada en archivos Markdown:

- `IMPLEMENTACION_BACKTRACKING.md` - Detalles del algoritmo backtracking
- `IMPLEMENTACION_FUERZA_BRUTA.md` - Detalles del algoritmo de fuerza bruta
- `IMPLEMENTACION_BUSQUEDA_LINEAL.md` - Detalles de búsqueda lineal
- `IMPLEMENTACION_MERGE_SORT.md` - Detalles de Merge Sort
- `REPOSITORY_PATTERN_IMPLEMENTATION.md` - Patrón Repository
- `IMPLEMENTATION_SUMMARY.md` - Resumen general

---

## 📄 Licencia

<!-- TODO: Especificar la licencia del proyecto -->

Este proyecto fue desarrollado con fines académicos para la materia de Técnicas de Programación.

---

## 🤝 Contribuciones

Este es un proyecto académico. Para sugerencias o mejoras, contactar a los autores.

---

## 📧 Contacto

<!-- TODO: Agregar información de contacto si es necesario -->

- **Universidad:** Universidad de Caldas
- **Materia:** Técnicas de Programación
- **Semestre:** 2025-2
- **Profesor:** Johnny Alexander Salazar Cardona

---

**Desarrollado con ❤️ usando Python y CustomTkinter**
