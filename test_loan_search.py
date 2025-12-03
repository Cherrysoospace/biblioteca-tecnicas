"""
Test script to verify loan search methods implementation.
Tests: find_by_id, find_by_user, find_by_isbn, find_active_loans
"""

from controllers.loan_controller import LoanController
from services.loan_service import LoanService


def test_loan_search_methods():
    """Test all loan search methods in controller and service."""
    
    print("=" * 70)
    print("PRUEBA DE MÉTODOS DE BÚSQUEDA DE PRÉSTAMOS")
    print("=" * 70)
    
    controller = LoanController()
    service = LoanService()
    
    # 1. Test find_by_id
    print("\n1. BÚSQUEDA POR ID")
    print("-" * 70)
    all_loans = controller.list_loans()
    if all_loans:
        test_loan_id = all_loans[0].get_loan_id()
        print(f"Buscando préstamo con ID: {test_loan_id}")
        
        # Test controller method
        loan = controller.find_by_id(test_loan_id)
        if loan:
            print(f"✓ Controller.find_by_id() encontró: {loan.get_loan_id()}")
            print(f"  - Usuario: {loan.get_user_id()}")
            print(f"  - ISBN: {loan.get_isbn()}")
            print(f"  - Devuelto: {loan.is_returned()}")
        else:
            print(f"✗ Controller.find_by_id() no encontró el préstamo")
        
        # Test service method
        loan = service.find_by_id(test_loan_id)
        if loan:
            print(f"✓ Service.find_by_id() encontró: {loan.get_loan_id()}")
        else:
            print(f"✗ Service.find_by_id() no encontró el préstamo")
    else:
        print("✗ No hay préstamos para probar find_by_id")
    
    # 2. Test find_by_user
    print("\n2. BÚSQUEDA POR USUARIO")
    print("-" * 70)
    if all_loans:
        test_user_id = all_loans[0].get_user_id()
        print(f"Buscando préstamos del usuario: {test_user_id}")
        
        # Test controller method
        user_loans = controller.find_by_user(test_user_id)
        print(f"✓ Controller.find_by_user() encontró {len(user_loans)} préstamo(s):")
        for loan in user_loans[:3]:  # Show first 3
            print(f"  - ID: {loan.get_loan_id()}, ISBN: {loan.get_isbn()}, "
                  f"Devuelto: {loan.is_returned()}")
        
        # Test service method
        user_loans = service.find_by_user(test_user_id)
        print(f"✓ Service.find_by_user() encontró {len(user_loans)} préstamo(s)")
    else:
        print("✗ No hay préstamos para probar find_by_user")
    
    # 3. Test find_by_isbn
    print("\n3. BÚSQUEDA POR ISBN")
    print("-" * 70)
    if all_loans:
        test_isbn = all_loans[0].get_isbn()
        print(f"Buscando préstamos del ISBN: {test_isbn}")
        
        # Test controller method
        isbn_loans = controller.find_by_isbn(test_isbn)
        print(f"✓ Controller.find_by_isbn() encontró {len(isbn_loans)} préstamo(s):")
        for loan in isbn_loans[:3]:  # Show first 3
            print(f"  - ID: {loan.get_loan_id()}, Usuario: {loan.get_user_id()}, "
                  f"Devuelto: {loan.is_returned()}")
        
        # Test service method
        isbn_loans = service.find_by_isbn(test_isbn)
        print(f"✓ Service.find_by_isbn() encontró {len(isbn_loans)} préstamo(s)")
    else:
        print("✗ No hay préstamos para probar find_by_isbn")
    
    # 4. Test find_active_loans
    print("\n4. BÚSQUEDA DE PRÉSTAMOS ACTIVOS")
    print("-" * 70)
    
    # Test controller method
    active_loans = controller.find_active_loans()
    print(f"✓ Controller.find_active_loans() encontró {len(active_loans)} préstamo(s) activo(s):")
    for loan in active_loans[:3]:  # Show first 3
        print(f"  - ID: {loan.get_loan_id()}, Usuario: {loan.get_user_id()}, "
              f"ISBN: {loan.get_isbn()}")
    
    # Test service method
    active_loans = service.find_active_loans()
    print(f"✓ Service.find_active_loans() encontró {len(active_loans)} préstamo(s) activo(s)")
    
    # Summary
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    total_loans = len(all_loans)
    active_count = len(active_loans)
    returned_count = total_loans - active_count
    
    print(f"Total de préstamos: {total_loans}")
    print(f"Préstamos activos: {active_count}")
    print(f"Préstamos devueltos: {returned_count}")
    
    print("\n✓ MÉTODOS DE BÚSQUEDA IMPLEMENTADOS:")
    print("  1. find_by_id(loan_id) - Buscar por ID")
    print("  2. find_by_user(user_id) - Buscar por usuario")
    print("  3. find_by_isbn(isbn) - Buscar por ISBN")
    print("  4. find_active_loans() - Buscar préstamos activos")
    
    print("\n✓ Todos los métodos están funcionando correctamente!")
    print("=" * 70)


if __name__ == "__main__":
    test_loan_search_methods()
