"""
Test de validación: No se puede crear reserva si el usuario ya tiene prestado ese libro.

Este test verifica que:
1. Un usuario NO puede reservar un libro que actualmente tiene prestado (activo)
2. Un usuario SÍ puede reservar un libro que devolvió previamente
3. La validación funciona correctamente en el flujo completo
"""

from services.loan_service import LoanService
from services.reservation_service import ReservationService
from services.inventory_service import InventoryService
from services.book_service import BookService


def test_cannot_reserve_book_with_active_loan():
    """Test que NO se puede reservar un libro que el usuario tiene prestado."""
    print("\n" + "="*80)
    print("TEST: Usuario NO puede reservar libro que ya tiene prestado")
    print("="*80)
    
    loan_service = LoanService()
    reservation_service = ReservationService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # Paso 1: Encontrar un libro con stock > 0 para crear un préstamo
    print("\n📋 Paso 1: Buscando libro con stock disponible...")
    test_isbn = None
    test_user_id = "U001"  # Usuario válido
    
    for inv in inventory_service.inventory_general:
        if inv.get_available_count() >= 1:
            test_isbn = inv.get_isbn()
            break
    
    if not test_isbn:
        print("⚠️  No hay libros con stock disponible. Test omitido.")
        return False
    
    print(f"   ✅ Libro encontrado: ISBN {test_isbn}")
    
    # Paso 2: Crear un préstamo para este usuario
    print("\n📋 Paso 2: Creando préstamo para usuario U001...")
    try:
        loan = loan_service.create_loan(
            loan_id=None,
            user_id=test_user_id,
            isbn=test_isbn
        )
        print(f"   ✅ Préstamo creado: {loan.get_loan_id()}")
        print(f"      Usuario: {loan.get_user_id()}")
        print(f"      ISBN: {loan.get_isbn()}")
        print(f"      Devuelto: {loan.is_returned()}")
    except Exception as e:
        print(f"   ❌ Error creando préstamo: {e}")
        return False
    
    # Paso 3: Marcar todos los demás libros del mismo ISBN como prestados
    # para que el stock llegue a 0 y se pueda intentar crear reserva
    print("\n📋 Paso 3: Reduciendo stock a 0 (prestando otros ejemplares)...")
    other_loans = []
    try:
        books = book_service.find_by_isbn(test_isbn)
        available_books = [b for b in books if not b.get_isBorrowed()]
        
        print(f"   📚 Ejemplares disponibles: {len(available_books)}")
        
        # Crear préstamos para otros usuarios hasta agotar stock
        other_users = ["U002", "U003", "U004", "U005"]
        for i, book in enumerate(available_books):
            if i < len(other_users):
                try:
                    other_loan = loan_service.create_loan(
                        loan_id=None,
                        user_id=other_users[i],
                        isbn=test_isbn
                    )
                    other_loans.append(other_loan)
                    print(f"   ✅ Préstamo adicional creado para {other_users[i]}")
                except Exception as e:
                    print(f"   ⚠️  No se pudo crear préstamo adicional: {e}")
                    break
    except Exception as e:
        print(f"   ⚠️  Error reduciendo stock: {e}")
    
    # Verificar que el stock es 0
    inventory_service = InventoryService()  # Recargar para obtener datos actualizados
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    print(f"   📊 Stock actual: {total_available}")
    
    if total_available > 0:
        print(f"   ⚠️  Stock aún mayor a 0. No se puede probar la validación de reserva.")
        # Limpiar préstamos creados
        cleanup_test_loans(loan_service, loan, other_loans)
        return False
    
    # Paso 4: Intentar crear reserva para el mismo usuario que ya tiene el libro prestado
    print("\n📋 Paso 4: Intentando crear reserva (DEBE FALLAR)...")
    print(f"   Usuario: {test_user_id}")
    print(f"   ISBN: {test_isbn}")
    print(f"   Estado préstamo: Activo (no devuelto)")
    
    try:
        reservation = reservation_service.create_reservation(
            reservation_id=None,
            user_id=test_user_id,
            isbn=test_isbn
        )
        print(f"\n   ❌ ERROR: Se creó la reserva cuando NO debería permitirse!")
        print(f"   ❌ Reserva ID: {reservation.get_reservation_id()}")
        
        # Limpiar reserva y préstamos
        try:
            reservation_service.delete_reservation(reservation.get_reservation_id())
        except Exception:
            pass
        cleanup_test_loans(loan_service, loan, other_loans)
        
        return False
        
    except ValueError as e:
        error_msg = str(e)
        if "already has an active loan" in error_msg or "already has an active loan" in error_msg.lower():
            print(f"\n   ✅ CORRECTO: Validación funcionó")
            print(f"   ✅ Mensaje: {error_msg}")
            
            # Limpiar préstamos
            cleanup_test_loans(loan_service, loan, other_loans)
            
            return True
        else:
            print(f"\n   ⚠️  Error inesperado: {error_msg}")
            cleanup_test_loans(loan_service, loan, other_loans)
            return False
    
    except Exception as e:
        print(f"\n   ❌ Error inesperado: {e}")
        cleanup_test_loans(loan_service, loan, other_loans)
        return False


def test_can_reserve_after_return():
    """Test que SÍ se puede reservar un libro después de devolverlo."""
    print("\n" + "="*80)
    print("TEST: Usuario SÍ puede reservar libro después de devolverlo")
    print("="*80)
    
    loan_service = LoanService()
    reservation_service = ReservationService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # Paso 1: Encontrar un libro con stock > 0
    print("\n📋 Paso 1: Buscando libro con stock disponible...")
    test_isbn = None
    test_user_id = "U001"
    
    for inv in inventory_service.inventory_general:
        if inv.get_available_count() >= 1:
            test_isbn = inv.get_isbn()
            break
    
    if not test_isbn:
        print("⚠️  No hay libros con stock disponible. Test omitido.")
        return False
    
    print(f"   ✅ Libro encontrado: ISBN {test_isbn}")
    
    # Paso 2: Crear préstamo
    print("\n📋 Paso 2: Creando préstamo...")
    try:
        loan = loan_service.create_loan(
            loan_id=None,
            user_id=test_user_id,
            isbn=test_isbn
        )
        print(f"   ✅ Préstamo creado: {loan.get_loan_id()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Paso 3: Devolver el libro
    print("\n📋 Paso 3: Devolviendo el libro...")
    try:
        loan_service.mark_returned(loan.get_loan_id())
        print(f"   ✅ Libro devuelto")
        
        # Verificar que está devuelto
        loan_service = LoanService()  # Recargar para obtener datos actualizados
        updated_loan = loan_service.find_by_id(loan.get_loan_id())
        if updated_loan:
            print(f"      Estado devuelto: {updated_loan.is_returned()}")
    except Exception as e:
        print(f"   ❌ Error devolviendo: {e}")
        cleanup_test_loans(loan_service, loan, [])
        return False
    
    # Paso 4: Reducir stock a 0 prestando otros ejemplares
    print("\n📋 Paso 4: Reduciendo stock a 0...")
    other_loans = []
    try:
        books = book_service.find_by_isbn(test_isbn)
        available_books = [b for b in books if not b.get_isBorrowed()]
        
        print(f"   📚 Ejemplares disponibles: {len(available_books)}")
        
        other_users = ["U002", "U003", "U004", "U005"]
        for i, book in enumerate(available_books):
            if i < len(other_users):
                try:
                    other_loan = loan_service.create_loan(
                        loan_id=None,
                        user_id=other_users[i],
                        isbn=test_isbn
                    )
                    other_loans.append(other_loan)
                    print(f"   ✅ Préstamo adicional creado para {other_users[i]}")
                except Exception as e:
                    break
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
    
    # Verificar stock
    inventory_service = InventoryService()
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    print(f"   📊 Stock actual: {total_available}")
    
    if total_available > 0:
        print(f"   ⚠️  Stock aún mayor a 0. Test omitido.")
        cleanup_test_loans(loan_service, loan, other_loans)
        return False
    
    # Paso 5: Intentar crear reserva (DEBE PERMITIRSE porque el libro fue devuelto)
    print("\n📋 Paso 5: Intentando crear reserva (DEBE PERMITIRSE)...")
    print(f"   Usuario: {test_user_id}")
    print(f"   ISBN: {test_isbn}")
    print(f"   Estado préstamo anterior: Devuelto")
    
    try:
        reservation = reservation_service.create_reservation(
            reservation_id=None,
            user_id=test_user_id,
            isbn=test_isbn
        )
        print(f"\n   ✅ CORRECTO: Reserva creada exitosamente")
        print(f"   ✅ Reserva ID: {reservation.get_reservation_id()}")
        print(f"      Usuario: {reservation.get_user_id()}")
        print(f"      ISBN: {reservation.get_isbn()}")
        
        # Limpiar
        try:
            reservation_service.delete_reservation(reservation.get_reservation_id())
            print(f"   🧹 Reserva eliminada")
        except Exception:
            pass
        cleanup_test_loans(loan_service, loan, other_loans)
        
        return True
        
    except ValueError as e:
        print(f"\n   ❌ ERROR: No se pudo crear la reserva cuando SÍ debería permitirse")
        print(f"   ❌ Mensaje: {e}")
        cleanup_test_loans(loan_service, loan, other_loans)
        return False
    
    except Exception as e:
        print(f"\n   ❌ Error inesperado: {e}")
        cleanup_test_loans(loan_service, loan, other_loans)
        return False


def cleanup_test_loans(loan_service, main_loan, other_loans):
    """Limpiar préstamos de prueba devolviendo y eliminando."""
    print("\n🧹 Limpiando préstamos de prueba...")
    
    # Devolver y eliminar préstamo principal
    try:
        if main_loan and not main_loan.is_returned():
            loan_service.mark_returned(main_loan.get_loan_id())
        if main_loan:
            loan_service.delete_loan(main_loan.get_loan_id())
        print(f"   ✅ Préstamo principal eliminado")
    except Exception as e:
        print(f"   ⚠️  Error limpiando préstamo principal: {e}")
    
    # Devolver y eliminar otros préstamos
    for other_loan in other_loans:
        try:
            if not other_loan.is_returned():
                loan_service.mark_returned(other_loan.get_loan_id())
            loan_service.delete_loan(other_loan.get_loan_id())
        except Exception as e:
            print(f"   ⚠️  Error limpiando préstamo {other_loan.get_loan_id()}: {e}")
    
    if other_loans:
        print(f"   ✅ {len(other_loans)} préstamos adicionales eliminados")


def run_all_tests():
    """Ejecutar todos los tests de validación."""
    print("\n" + "="*80)
    print("SUITE DE TESTS: Validación de Reserva vs Préstamo Activo")
    print("="*80)
    
    results = []
    
    # Test 1: No se puede reservar con préstamo activo
    result1 = test_cannot_reserve_book_with_active_loan()
    results.append(("Usuario NO puede reservar libro prestado", result1))
    
    # Test 2: Sí se puede reservar después de devolver
    result2 = test_can_reserve_after_return()
    results.append(("Usuario SÍ puede reservar después de devolver", result2))
    
    # Resumen
    print("\n" + "="*80)
    print("RESUMEN DE RESULTADOS")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    print(f"\nTotal: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡Todos los tests pasaron exitosamente!")
    else:
        print(f"\n⚠️  {total - passed} test(s) fallaron")


if __name__ == "__main__":
    run_all_tests()
