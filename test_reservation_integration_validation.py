"""
Test de integración: Validación de reserva en el flujo completo
desde Controller hasta UI.

Verifica que la validación funciona en todos los niveles:
1. Service Layer
2. Controller Layer
3. Error messages apropiados
"""

from controllers.reservation_controller import ReservationController
from services.loan_service import LoanService
from services.inventory_service import InventoryService
from services.book_service import BookService


def test_controller_validation():
    """Test de validación a nivel de Controller."""
    print("\n" + "="*80)
    print("TEST DE INTEGRACIÓN: Controller + Service")
    print("="*80)
    
    controller = ReservationController()
    loan_service = LoanService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # Preparar datos de prueba
    print("\n📋 Preparando datos de prueba...")
    
    # Encontrar libro con stock
    test_isbn = None
    for inv in inventory_service.inventory_general:
        if inv.get_available_count() >= 1:
            test_isbn = inv.get_isbn()
            break
    
    if not test_isbn:
        print("⚠️  No hay libros disponibles. Test omitido.")
        return False
    
    test_user_id = "U001"
    
    # Crear préstamo
    print(f"\n1️⃣ Creando préstamo para {test_user_id}...")
    try:
        loan = loan_service.create_loan(None, test_user_id, test_isbn)
        print(f"   ✅ Préstamo creado: {loan.get_loan_id()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Reducir stock a 0
    print("\n2️⃣ Reduciendo stock a 0...")
    other_loans = []
    try:
        books = book_service.find_by_isbn(test_isbn)
        available_books = [b for b in books if not b.get_isBorrowed()]
        
        other_users = ["U002", "U003", "U004", "U005"]
        for i, book in enumerate(available_books):
            if i < len(other_users):
                try:
                    other_loan = loan_service.create_loan(None, other_users[i], test_isbn)
                    other_loans.append(other_loan)
                except Exception:
                    break
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Verificar stock
    inventory_service = InventoryService()
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    print(f"   📊 Stock actual: {total_available}")
    
    if total_available > 0:
        print("   ⚠️  No se pudo reducir stock a 0. Test omitido.")
        cleanup(loan_service, loan, other_loans)
        return False
    
    # Test del Controller
    print("\n3️⃣ Probando Controller.create_reservation()...")
    print(f"   Usuario: {test_user_id}")
    print(f"   ISBN: {test_isbn}")
    
    result = controller.create_reservation(test_user_id, test_isbn)
    
    # Verificar resultado
    if result.get('success'):
        print("\n   ❌ ERROR: Controller permitió la reserva cuando NO debería")
        print(f"   ❌ Resultado: {result}")
        cleanup(loan_service, loan, other_loans)
        return False
    else:
        error_message = result.get('message', '')
        if "already has an active loan" in error_message:
            print("\n   ✅ CORRECTO: Controller rechazó la reserva")
            print(f"   ✅ Mensaje: {error_message}")
            cleanup(loan_service, loan, other_loans)
            return True
        else:
            print(f"\n   ⚠️  Error inesperado: {error_message}")
            cleanup(loan_service, loan, other_loans)
            return False


def test_error_messages():
    """Test de mensajes de error descriptivos."""
    print("\n" + "="*80)
    print("TEST: Calidad de Mensajes de Error")
    print("="*80)
    
    controller = ReservationController()
    loan_service = LoanService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # Preparar datos
    print("\n📋 Preparando escenario...")
    
    test_isbn = None
    for inv in inventory_service.inventory_general:
        if inv.get_available_count() >= 1:
            test_isbn = inv.get_isbn()
            break
    
    if not test_isbn:
        print("⚠️  No hay libros disponibles.")
        return False
    
    test_user_id = "U001"
    
    # Crear préstamo y reducir stock
    loan = loan_service.create_loan(None, test_user_id, test_isbn)
    print(f"   ✅ Préstamo: {loan.get_loan_id()}")
    
    other_loans = []
    books = book_service.find_by_isbn(test_isbn)
    available_books = [b for b in books if not b.get_isBorrowed()]
    
    other_users = ["U002", "U003", "U004", "U005"]
    for i, book in enumerate(available_books):
        if i < len(other_users):
            try:
                other_loans.append(loan_service.create_loan(None, other_users[i], test_isbn))
            except Exception:
                break
    
    # Verificar stock
    inventory_service = InventoryService()
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    
    if total_available > 0:
        cleanup(loan_service, loan, other_loans)
        return False
    
    # Verificar mensaje de error
    print("\n📋 Verificando mensaje de error...")
    result = controller.create_reservation(test_user_id, test_isbn)
    error_msg = result.get('message', '')
    
    print(f"\n📝 Mensaje de error:")
    print(f"   {error_msg}")
    
    # Verificar componentes del mensaje
    checks = [
        ("Menciona user_id", test_user_id in error_msg),
        ("Menciona ISBN", test_isbn in error_msg),
        ("Menciona loan_id", loan.get_loan_id() in error_msg),
        ("Menciona 'active loan'", "active loan" in error_msg.lower()),
        ("Es descriptivo", len(error_msg) > 50)
    ]
    
    print("\n✅ Verificaciones del mensaje:")
    all_passed = True
    for check_name, passed in checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    cleanup(loan_service, loan, other_loans)
    return all_passed


def test_multiple_users_scenario():
    """Test de escenario con múltiples usuarios."""
    print("\n" + "="*80)
    print("TEST: Escenario Multi-Usuario")
    print("="*80)
    
    controller = ReservationController()
    loan_service = LoanService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # Encontrar libro con suficiente stock
    print("\n📋 Buscando libro con múltiples copias...")
    test_isbn = None
    for inv in inventory_service.inventory_general:
        books = book_service.find_by_isbn(inv.get_isbn())
        available = [b for b in books if not b.get_isBorrowed()]
        if len(available) >= 3:
            test_isbn = inv.get_isbn()
            break
    
    if not test_isbn:
        print("⚠️  No hay libros con suficientes copias. Test omitido.")
        return False
    
    print(f"   ✅ ISBN: {test_isbn}")
    
    # Escenario:
    # - Usuario U001 tiene préstamo activo
    # - Usuario U002 no tiene préstamo
    # - Usuario U003 devolvió su préstamo
    
    users = {
        "U001": {"has_loan": True, "returned": False},
        "U002": {"has_loan": False, "returned": False},
        "U003": {"has_loan": True, "returned": True}
    }
    
    loans = {}
    
    print("\n1️⃣ Creando préstamos...")
    
    # U001: préstamo activo
    loan1 = loan_service.create_loan(None, "U001", test_isbn)
    loans["U001"] = loan1
    print(f"   ✅ U001: Préstamo {loan1.get_loan_id()} (activo)")
    
    # U003: préstamo y devolución
    loan3 = loan_service.create_loan(None, "U003", test_isbn)
    loans["U003"] = loan3
    loan_service.mark_returned(loan3.get_loan_id())
    print(f"   ✅ U003: Préstamo {loan3.get_loan_id()} (devuelto)")
    
    # Reducir stock a 0
    print("\n2️⃣ Reduciendo stock a 0...")
    other_loans = []
    books = book_service.find_by_isbn(test_isbn)
    available_books = [b for b in books if not b.get_isBorrowed()]
    
    temp_users = ["U004", "U005", "U006"]
    for i, book in enumerate(available_books):
        if i < len(temp_users):
            try:
                other_loans.append(loan_service.create_loan(None, temp_users[i], test_isbn))
            except Exception:
                break
    
    # Verificar stock
    inventory_service = InventoryService()
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    print(f"   📊 Stock: {total_available}")
    
    if total_available > 0:
        cleanup(loan_service, loan1, other_loans + [loan3])
        return False
    
    # Probar reservas para cada usuario
    print("\n3️⃣ Probando creación de reservas...")
    
    results = {}
    
    # U001: Debe FALLAR (tiene préstamo activo)
    print("\n   Usuario U001 (préstamo activo):")
    result1 = controller.create_reservation("U001", test_isbn)
    results["U001"] = not result1.get('success')
    status = "✅" if not result1.get('success') else "❌"
    print(f"   {status} Resultado: {'Rechazado' if not result1.get('success') else 'Permitido'}")
    
    # U002: Debe PERMITIRSE (sin préstamo)
    print("\n   Usuario U002 (sin préstamo):")
    result2 = controller.create_reservation("U002", test_isbn)
    results["U002"] = result2.get('success')
    status = "✅" if result2.get('success') else "❌"
    print(f"   {status} Resultado: {'Permitido' if result2.get('success') else 'Rechazado'}")
    if result2.get('success'):
        # Limpiar reserva
        try:
            res_id = result2.get('reservation').get_reservation_id()
            controller.delete_reservation(res_id)
        except Exception:
            pass
    
    # U003: Debe PERMITIRSE (préstamo devuelto)
    print("\n   Usuario U003 (préstamo devuelto):")
    result3 = controller.create_reservation("U003", test_isbn)
    results["U003"] = result3.get('success')
    status = "✅" if result3.get('success') else "❌"
    print(f"   {status} Resultado: {'Permitido' if result3.get('success') else 'Rechazado'}")
    if result3.get('success'):
        try:
            res_id = result3.get('reservation').get_reservation_id()
            controller.delete_reservation(res_id)
        except Exception:
            pass
    
    # Limpiar
    cleanup(loan_service, loan1, other_loans + [loan3])
    
    # Verificar que todos los resultados fueron correctos
    all_correct = all(results.values())
    
    print("\n📊 Resumen:")
    print(f"   U001 (activo):   {'✅ Rechazado correctamente' if results['U001'] else '❌ Error'}")
    print(f"   U002 (sin):      {'✅ Permitido correctamente' if results['U002'] else '❌ Error'}")
    print(f"   U003 (devuelto): {'✅ Permitido correctamente' if results['U003'] else '❌ Error'}")
    
    return all_correct


def cleanup(loan_service, main_loan, other_loans):
    """Limpiar datos de prueba."""
    try:
        if main_loan and not main_loan.is_returned():
            loan_service.mark_returned(main_loan.get_loan_id())
        if main_loan:
            loan_service.delete_loan(main_loan.get_loan_id())
    except Exception:
        pass
    
    for loan in other_loans:
        try:
            if not loan.is_returned():
                loan_service.mark_returned(loan.get_loan_id())
            loan_service.delete_loan(loan.get_loan_id())
        except Exception:
            pass


def run_integration_tests():
    """Ejecutar suite completa de tests de integración."""
    print("\n" + "="*80)
    print("SUITE DE TESTS DE INTEGRACIÓN")
    print("Validación: Usuario con Préstamo Activo")
    print("="*80)
    
    results = []
    
    # Test 1: Controller validation
    result1 = test_controller_validation()
    results.append(("Controller validation", result1))
    
    # Test 2: Error messages
    result2 = test_error_messages()
    results.append(("Error messages quality", result2))
    
    # Test 3: Multiple users scenario
    result3 = test_multiple_users_scenario()
    results.append(("Multi-user scenario", result3))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests de integración pasaron!")
        print("✅ La validación funciona correctamente en todos los niveles")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")


if __name__ == "__main__":
    run_integration_tests()
