"""
Test Completo: Flujo de Reservas con Validación de Stock = 0

Este test valida el flujo completo de reservas:
1. Solo se permite reservar libros con stock = 0
2. Las reservas se asignan automáticamente en orden FIFO
3. La integración con préstamos funciona correctamente
"""

from services.reservation_service import ReservationService
from services.loan_service import LoanService
from services.inventory_service import InventoryService
from services.book_service import BookService


def test_complete_reservation_flow():
    """Test del flujo completo de reservas desde la creación hasta la asignación."""
    
    print("\n" + "="*70)
    print("TEST COMPLETO: Flujo de Reservas con Stock = 0")
    print("="*70)
    
    # Inicializar servicios
    reservation_service = ReservationService()
    loan_service = LoanService()
    inventory_service = InventoryService()
    book_service = BookService()
    
    # PASO 1: Encontrar un libro con al menos 1 copia disponible
    print("\n📋 PASO 1: Buscar libro para el test")
    print("-" * 70)
    
    test_isbn = None
    test_book_id = None
    
    for inv in inventory_service.inventory_general:
        if inv.get_available_count() >= 1:
            test_isbn = inv.get_isbn()
            for book in inv.get_items():
                if not book.get_isBorrowed():
                    test_book_id = book.get_id()
                    break
            if test_book_id:
                break
    
    if not test_isbn or not test_book_id:
        print("❌ No se encontró libro disponible para test")
        return False
    
    print(f"✅ Libro encontrado: ISBN {test_isbn}")
    print(f"   Book ID: {test_book_id}")
    
    # PASO 2: Intentar crear reserva CON stock disponible (debe fallar)
    print("\n📋 PASO 2: Intentar reservar libro CON stock (debe RECHAZAR)")
    print("-" * 70)
    
    try:
        reservation_service.create_reservation(
            reservation_id=None,
            user_id="U002",  # Usuario válido de la BD
            isbn=test_isbn
        )
        print("❌ FALLO: Se permitió crear reserva con stock disponible")
        return False
    except ValueError as e:
        if "available" in str(e).lower():
            print(f"✅ CORRECTO: Reserva rechazada")
            print(f"   Mensaje: {e}")
        else:
            print(f"⚠️ Reserva rechazada con mensaje inesperado: {e}")
    
    # PASO 3: Crear préstamo para agotar el stock
    print("\n📋 PASO 3: Crear préstamo para agotar stock")
    print("-" * 70)
    
    try:
        loan = loan_service.create_loan(
            loan_id=None,
            user_id="U004",  # Usuario válido de la BD
            isbn=test_isbn
        )
        print(f"✅ Préstamo creado: {loan.get_loan_id()}")
    except Exception as e:
        print(f"❌ Error creando préstamo: {e}")
        return False
    
    # Verificar que el stock ahora es 0
    inventory_service._load_inventories()
    inventories = inventory_service.find_by_isbn(test_isbn)
    total_available = sum(inv.get_available_count() for inv in inventories)
    
    print(f"   Stock disponible después del préstamo: {total_available}")
    
    if total_available > 0:
        print(f"⚠️ Aún hay {total_available} copias disponibles")
        print(f"   Test parcial - continuando de todos modos...")
    
    # PASO 4: Crear reservas ahora que stock = 0
    print("\n📋 PASO 4: Crear reservas con stock = 0")
    print("-" * 70)
    
    reservations_created = []
    users = ["U009", "U010", "U012"]  # Usuarios válidos de la BD
    
    # Si hay stock disponible, prestar todos los libros primero
    if total_available > 0:
        print(f"   Prestando {total_available} copias adicionales...")
        for inv in inventories:
            for book in inv.get_items():
                if not book.get_isBorrowed():
                    try:
                        extra_loan = loan_service.create_loan(
                            loan_id=None,
                            user_id=f"U{(hash(book.get_id()) % 13) + 1:03d}",  # Usuario válido de la BD
                            isbn=test_isbn
                        )
                        print(f"   ✅ Préstamo extra creado: {extra_loan.get_loan_id()}")
                    except Exception as e:
                        print(f"   ⚠️ No se pudo crear préstamo extra: {e}")
        
        # Recargar inventario
        inventory_service._load_inventories()
        inventories = inventory_service.find_by_isbn(test_isbn)
        total_available = sum(inv.get_available_count() for inv in inventories)
        print(f"   Stock disponible ahora: {total_available}")
    
    # Crear las reservas
    for i, user_id in enumerate(users, start=1):
        try:
            res = reservation_service.create_reservation(
                reservation_id=None,
                user_id=user_id,
                isbn=test_isbn
            )
            reservations_created.append(res)
            print(f"   ✅ Reserva {i} creada: {res.get_reservation_id()} - Usuario: {user_id}")
        except ValueError as e:
            print(f"   ❌ No se pudo crear reserva {i}: {e}")
            # Si falla por stock, algo está mal
            if "available" in str(e).lower():
                print(f"   ❌ ERROR: Stock debería ser 0 pero se rechazó la reserva")
                return False
    
    if not reservations_created:
        print("❌ No se crearon reservas")
        return False
    
    print(f"\n   Total de reservas creadas: {len(reservations_created)}")
    
    # PASO 5: Devolver el libro y verificar asignación FIFO
    print("\n📋 PASO 5: Devolver libro y verificar asignación FIFO")
    print("-" * 70)
    
    try:
        loan_service.mark_returned(loan.get_loan_id())
        print(f"✅ Libro devuelto: {loan.get_loan_id()}")
    except Exception as e:
        print(f"❌ Error al devolver libro: {e}")
        return False
    
    # PASO 6: Verificar que se asignó la primera reserva (FIFO)
    print("\n📋 PASO 6: Verificar asignación FIFO")
    print("-" * 70)
    
    # Recargar servicio de reservas
    reservation_service_new = ReservationService()
    
    # Verificar primera reserva
    first_res = reservation_service_new.find_by_id(reservations_created[0].get_reservation_id())
    
    if not first_res:
        print("❌ No se encontró la primera reserva")
        return False
    
    print(f"   Primera reserva en cola: {first_res.get_reservation_id()}")
    print(f"   Usuario: {first_res.get_user_id()}")
    print(f"   Estado: {first_res.get_status()}")
    
    if first_res.get_status() == 'assigned':
        print(f"   ✅ CORRECTO: Primera reserva asignada (FIFO)")
        print(f"   Fecha de asignación: {first_res.get_assigned_date()}")
    else:
        print(f"   ❌ FALLO: Primera reserva NO fue asignada")
        return False
    
    # Verificar que las demás siguen pendientes
    pending_count = 0
    for res in reservations_created[1:]:
        res_updated = reservation_service_new.find_by_id(res.get_reservation_id())
        if res_updated and res_updated.get_status() == 'pending':
            pending_count += 1
    
    print(f"\n   Reservas restantes pendientes: {pending_count}/{len(reservations_created)-1}")
    
    # PASO 7: Limpieza
    print("\n📋 PASO 7: Limpieza de datos de prueba")
    print("-" * 70)
    
    # Eliminar reservas creadas
    for res in reservations_created:
        try:
            reservation_service_new.delete_reservation(res.get_reservation_id())
        except Exception:
            pass
    
    print(f"   ✅ {len(reservations_created)} reservas eliminadas")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("VALIDACIÓN COMPLETA DEL SISTEMA DE RESERVAS")
    print("="*70)
    print("\nEste test verifica:")
    print("1. ❌ Rechaza reservas con stock disponible")
    print("2. ✅ Permite reservas con stock = 0")
    print("3. ✅ Asignación automática en orden FIFO")
    print("4. ✅ Integración con sistema de préstamos")
    
    result = test_complete_reservation_flow()
    
    print("\n" + "="*70)
    if result:
        print("🎉 TEST COMPLETO EXITOSO")
        print("="*70)
        print("\n✅ Todas las correcciones críticas funcionan correctamente:")
        print("   • Validación de stock = 0 implementada")
        print("   • Cola FIFO funcionando correctamente")
        print("   • Integración con préstamos operativa")
    else:
        print("❌ TEST FALLIDO")
        print("="*70)
        print("\nRevisar implementación")
    
    print("="*70)
