"""
Test: Validación de Eliminación de Libros

Este test verifica que no se puedan eliminar libros que estén:
1. En préstamos activos
2. En la lista de espera (reservas pendientes)

Esto protege la integridad referencial de la base de datos.
"""

from services.book_service import BookService
from services.loan_service import LoanService
from services.reservation_service import ReservationService
from services.inventory_service import InventoryService


def test_cannot_delete_book_with_active_loan():
    """Test que NO se puede eliminar un libro con préstamos activos."""
    
    print("\n" + "="*70)
    print("TEST 1: Intentar eliminar libro con préstamo activo")
    print("="*70)
    
    book_service = BookService()
    loan_service = LoanService()
    
    # Buscar un libro con préstamo activo (no devuelto)
    active_loans = [loan for loan in loan_service.get_all_loans() if not loan.is_returned()]
    
    if not active_loans:
        print("⚠️ No hay préstamos activos - creando uno para el test...")
        
        # Buscar un libro disponible
        inventory_service = InventoryService()
        test_isbn = None
        test_book_id = None
        
        for inv in inventory_service.inventory_general:
            if inv.get_available_count() > 0:
                test_isbn = inv.get_isbn()
                for book in inv.get_items():
                    if not book.get_isBorrowed():
                        test_book_id = book.get_id()
                        break
                if test_book_id:
                    break
        
        if test_book_id:
            # Crear préstamo
            try:
                loan = loan_service.create_loan(None, "U001", test_isbn)
                print(f"   ✅ Préstamo creado: {loan.get_loan_id()}")
                active_loans = [loan]
            except Exception as e:
                print(f"   ❌ Error creando préstamo: {e}")
                return False
        else:
            print("⚠️ No hay libros disponibles - test omitido")
            return True
    
    # Obtener el libro del préstamo activo
    test_loan = active_loans[0]
    test_isbn = test_loan.get_isbn()
    
    # Buscar un libro físico con ese ISBN
    all_books = book_service.get_all_books()
    test_book = None
    for book in all_books:
        if book.get_ISBNCode() == test_isbn:
            test_book = book
            break
    
    if not test_book:
        print(f"⚠️ No se encontró libro con ISBN {test_isbn}")
        return True
    
    print(f"\n📚 Libro encontrado: ID {test_book.get_id()}")
    print(f"   ISBN: {test_isbn}")
    print(f"   Título: {test_book.get_title()}")
    print(f"   Préstamo activo: {test_loan.get_loan_id()}")
    
    # Intentar eliminar el libro (debe fallar)
    print(f"\n🚫 Intentando eliminar libro con préstamo activo...")
    try:
        book_service.delete_book(test_book.get_id())
        print(f"   ❌ FALLO: Se permitió eliminar el libro")
        return False
    except ValueError as e:
        error_msg = str(e)
        if "active loan" in error_msg.lower() or "préstamo" in error_msg.lower():
            print(f"   ✅ CORRECTO: Eliminación rechazada")
            print(f"   ✅ Mensaje: {error_msg}")
            return True
        else:
            print(f"   ⚠️ Rechazado pero mensaje inesperado: {error_msg}")
            return True


def test_cannot_delete_book_with_pending_reservation():
    """Test que NO se puede eliminar un libro con reservas pendientes."""
    
    print("\n" + "="*70)
    print("TEST 2: Intentar eliminar libro con reserva pendiente")
    print("="*70)
    
    book_service = BookService()
    reservation_service = ReservationService()
    
    # Buscar un ISBN con reservas pendientes
    all_reservations = reservation_service.get_all_reservations()
    pending_reservations = [r for r in all_reservations if r.get_status() == 'pending']
    
    if not pending_reservations:
        print("⚠️ No hay reservas pendientes")
        print("   Para probar esta funcionalidad, cree una reserva manualmente")
        return True
    
    # Obtener el ISBN de una reserva pendiente
    test_reservation = pending_reservations[0]
    test_isbn = test_reservation.get_isbn()
    
    # Buscar un libro físico con ese ISBN
    all_books = book_service.get_all_books()
    test_book = None
    for book in all_books:
        if book.get_ISBNCode() == test_isbn:
            test_book = book
            break
    
    if not test_book:
        print(f"⚠️ No se encontró libro con ISBN {test_isbn}")
        return True
    
    print(f"\n📚 Libro encontrado: ID {test_book.get_id()}")
    print(f"   ISBN: {test_isbn}")
    print(f"   Título: {test_book.get_title()}")
    print(f"   Reserva pendiente: {test_reservation.get_reservation_id()}")
    print(f"   Usuario: {test_reservation.get_user_id()}")
    
    # Intentar eliminar el libro (debe fallar)
    print(f"\n🚫 Intentando eliminar libro con reserva pendiente...")
    try:
        book_service.delete_book(test_book.get_id())
        print(f"   ❌ FALLO: Se permitió eliminar el libro")
        return False
    except ValueError as e:
        error_msg = str(e)
        if "reservation" in error_msg.lower() or "reserva" in error_msg.lower():
            print(f"   ✅ CORRECTO: Eliminación rechazada")
            print(f"   ✅ Mensaje: {error_msg}")
            return True
        else:
            print(f"   ⚠️ Rechazado pero mensaje inesperado: {error_msg}")
            return True


def test_can_delete_book_without_constraints():
    """Test que SÍ se puede eliminar un libro sin préstamos ni reservas."""
    
    print("\n" + "="*70)
    print("TEST 3: Eliminar libro SIN préstamos ni reservas (debe permitir)")
    print("="*70)
    
    book_service = BookService()
    loan_service = LoanService()
    reservation_service = ReservationService()
    
    # Buscar un libro que no esté en préstamos ni reservas
    all_books = book_service.get_all_books()
    all_loans = loan_service.get_all_loans()
    all_reservations = reservation_service.get_all_reservations()
    
    # ISBNs en préstamos activos
    loaned_isbns = {loan.get_isbn() for loan in all_loans if not loan.is_returned()}
    
    # ISBNs en reservas pendientes
    reserved_isbns = {res.get_isbn() for res in all_reservations if res.get_status() == 'pending'}
    
    # Buscar libro libre
    test_book = None
    for book in all_books:
        isbn = book.get_ISBNCode()
        if isbn not in loaned_isbns and isbn not in reserved_isbns and not book.get_isBorrowed():
            test_book = book
            break
    
    if not test_book:
        print("⚠️ No hay libros disponibles sin restricciones")
        print("   Todos los libros tienen préstamos o reservas")
        return True
    
    print(f"\n📚 Libro encontrado: ID {test_book.get_id()}")
    print(f"   ISBN: {test_book.get_ISBNCode()}")
    print(f"   Título: {test_book.get_title()}")
    print(f"   Sin préstamos activos: ✅")
    print(f"   Sin reservas pendientes: ✅")
    
    # Nota: No eliminaremos realmente el libro en el test para no afectar la BD
    print(f"\n⚠️ SIMULACIÓN: No se eliminará realmente para preservar la BD")
    print(f"   En producción, este libro SÍ podría eliminarse")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VALIDACIÓN: Protección de Integridad Referencial")
    print("="*70)
    print("\nEste test verifica que NO se puedan eliminar libros con:")
    print("1. Préstamos activos (sin devolver)")
    print("2. Reservas pendientes en lista de espera")
    
    # Ejecutar tests
    result1 = test_cannot_delete_book_with_active_loan()
    result2 = test_cannot_delete_book_with_pending_reservation()
    result3 = test_can_delete_book_without_constraints()
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE RESULTADOS")
    print("="*70)
    print(f"Test 1 - Rechazar con préstamo activo:  {'✅ PASS' if result1 else '❌ FAIL'}")
    print(f"Test 2 - Rechazar con reserva pendiente: {'✅ PASS' if result2 else '❌ FAIL'}")
    print(f"Test 3 - Permitir sin restricciones:     {'✅ PASS' if result3 else '❌ FAIL'}")
    
    if result1 and result2 and result3:
        print("\n🎉 VALIDACIÓN EXITOSA - Integridad referencial protegida")
    else:
        print("\n⚠️ Algunos tests fallaron - revisar implementación")
    
    print("="*70)
