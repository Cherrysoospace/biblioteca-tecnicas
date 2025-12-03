"""
Script de demostración de la funcionalidad de búsqueda de préstamos.
Muestra las capacidades del nuevo botón "Buscar" en el listado de préstamos.
"""

from controllers.loan_controller import LoanController


def demo_loan_search():
    """Demonstración de todas las capacidades de búsqueda de préstamos."""
    
    print("=" * 80)
    print("DEMOSTRACIÓN: FUNCIONALIDAD DE BÚSQUEDA DE PRÉSTAMOS")
    print("=" * 80)
    print()
    
    controller = LoanController()
    
    print("📋 BOTÓN 'BUSCAR' AGREGADO AL LISTADO DE PRÉSTAMOS")
    print("-" * 80)
    print()
    print("El botón 'Buscar' en el listado de préstamos abre una ventana con:")
    print()
    print("  ✓ 4 OPCIONES DE BÚSQUEDA:")
    print("    1. Por ID del Préstamo")
    print("    2. Por Usuario (ID)")
    print("    3. Por ISBN")
    print("    4. Solo Préstamos Activos")
    print()
    print("  ✓ CARACTERÍSTICAS:")
    print("    - Campo de entrada para buscar")
    print("    - Botón 'Buscar' para ejecutar la búsqueda")
    print("    - Botón 'Limpiar' para resetear la búsqueda")
    print("    - Tabla de resultados con los préstamos encontrados")
    print("    - Contador de resultados encontrados")
    print("    - Soporte para Enter (tecla) para buscar")
    print()
    
    # Obtener datos para demostración
    all_loans = controller.list_loans()
    active_loans = controller.find_active_loans()
    
    print("=" * 80)
    print("EJEMPLOS DE BÚSQUEDA CON DATOS ACTUALES")
    print("=" * 80)
    print()
    
    if not all_loans:
        print("⚠ No hay préstamos en el sistema para demostrar.")
        return
    
    # Ejemplo 1: Búsqueda por ID
    print("1️⃣ EJEMPLO: BÚSQUEDA POR ID")
    print("-" * 80)
    test_loan = all_loans[0]
    test_id = test_loan.get_loan_id()
    print(f"Buscar préstamo con ID: {test_id}")
    result = controller.find_by_id(test_id)
    if result:
        print(f"✓ Encontrado:")
        print(f"  - ID: {result.get_loan_id()}")
        print(f"  - Usuario: {result.get_user_id()}")
        print(f"  - ISBN: {result.get_isbn()}")
        print(f"  - Fecha: {result.get_loan_date()}")
        print(f"  - Devuelto: {'Sí' if result.is_returned() else 'No'}")
    print()
    
    # Ejemplo 2: Búsqueda por Usuario
    print("2️⃣ EJEMPLO: BÚSQUEDA POR USUARIO")
    print("-" * 80)
    test_user = test_loan.get_user_id()
    print(f"Buscar préstamos del usuario: {test_user}")
    results = controller.find_by_user(test_user)
    print(f"✓ Encontrados: {len(results)} préstamo(s)")
    for i, loan in enumerate(results[:3], 1):
        print(f"  {i}. ID: {loan.get_loan_id()}, ISBN: {loan.get_isbn()}, "
              f"Devuelto: {'Sí' if loan.is_returned() else 'No'}")
    if len(results) > 3:
        print(f"  ... y {len(results) - 3} más")
    print()
    
    # Ejemplo 3: Búsqueda por ISBN
    print("3️⃣ EJEMPLO: BÚSQUEDA POR ISBN")
    print("-" * 80)
    test_isbn = test_loan.get_isbn()
    print(f"Buscar préstamos del ISBN: {test_isbn}")
    results = controller.find_by_isbn(test_isbn)
    print(f"✓ Encontrados: {len(results)} préstamo(s)")
    for i, loan in enumerate(results[:3], 1):
        print(f"  {i}. ID: {loan.get_loan_id()}, Usuario: {loan.get_user_id()}, "
              f"Devuelto: {'Sí' if loan.is_returned() else 'No'}")
    if len(results) > 3:
        print(f"  ... y {len(results) - 3} más")
    print()
    
    # Ejemplo 4: Búsqueda de activos
    print("4️⃣ EJEMPLO: PRÉSTAMOS ACTIVOS")
    print("-" * 80)
    print(f"Buscar todos los préstamos activos (no devueltos)")
    print(f"✓ Encontrados: {len(active_loans)} préstamo(s) activo(s)")
    for i, loan in enumerate(active_loans[:5], 1):
        print(f"  {i}. ID: {loan.get_loan_id()}, Usuario: {loan.get_user_id()}, "
              f"ISBN: {loan.get_isbn()}")
    if len(active_loans) > 5:
        print(f"  ... y {len(active_loans) - 5} más")
    print()
    
    # Resumen
    print("=" * 80)
    print("RESUMEN DE FUNCIONALIDAD")
    print("=" * 80)
    print(f"📊 Total de préstamos: {len(all_loans)}")
    print(f"📗 Préstamos activos: {len(active_loans)}")
    print(f"📘 Préstamos devueltos: {len(all_loans) - len(active_loans)}")
    print()
    print("✅ IMPLEMENTACIÓN COMPLETA:")
    print("  ✓ Ventana de búsqueda (loan_search.py)")
    print("  ✓ Botón 'Buscar' en el listado")
    print("  ✓ 4 métodos de búsqueda implementados")
    print("  ✓ Interfaz gráfica con CustomTkinter")
    print("  ✓ Validación y manejo de errores")
    print("  ✓ Contador de resultados")
    print("  ✓ Tabla de resultados con formato")
    print()
    print("🎯 CÓMO USAR:")
    print("  1. Abrir el listado de préstamos desde el menú principal")
    print("  2. Hacer clic en el botón 'Buscar'")
    print("  3. Seleccionar el tipo de búsqueda")
    print("  4. Ingresar el valor (excepto para 'Solo Activos')")
    print("  5. Hacer clic en 'Buscar' o presionar Enter")
    print("  6. Ver los resultados en la tabla")
    print()
    print("=" * 80)


if __name__ == "__main__":
    demo_loan_search()
