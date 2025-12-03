"""
Script de prueba para la funcionalidad de Recursión de Pila
Calcula el valor total de libros por autor
"""

from controllers.book_controller import BookController

def test_author_value_calculation():
    """Prueba la funcionalidad de cálculo de valor por autor."""
    print("=" * 70)
    print("PRUEBA DE RECURSIÓN DE PILA - Valor Total por Autor")
    print("=" * 70)
    print()
    
    # Crear controlador
    controller = BookController()
    
    # Obtener todos los autores
    authors = controller.get_all_authors()
    print(f"📚 Total de autores en el sistema: {len(authors)}")
    print()
    
    # Probar con varios autores
    test_authors = [
        "Homer",
        "Jane Austen",
        "Suzanne Collins",
        "Stephen King",
        "hi",
    ]
    
    print("-" * 70)
    print("RESULTADOS DE CÁLCULO POR AUTOR:")
    print("-" * 70)
    
    for author in test_authors:
        if author in authors:
            # Calcular valor total usando recursión de pila
            total_value = controller.calculate_total_value_by_author(author)
            
            # Contar libros de este autor
            all_books = controller.get_all_books()
            author_books = [b for b in all_books if b.get_author() == author]
            
            print(f"\n👤 Autor: {author}")
            print(f"   📖 Libros: {len(author_books)}")
            print(f"   💰 Valor Total: ${total_value:,.0f} COP")
            
            # Mostrar detalles de libros
            for book in author_books:
                print(f"      - {book.get_title()} (${book.get_price():,.0f})")
        else:
            print(f"\n👤 Autor: {author}")
            print(f"   ❌ No encontrado en el sistema")
    
    print()
    print("=" * 70)
    print("✅ PRUEBA COMPLETADA")
    print("=" * 70)
    print()
    print("💡 Para usar la interfaz gráfica:")
    print("   1. Ejecuta: python main.py")
    print("   2. Haz clic en '📚 Valor por Autor'")
    print("   3. Selecciona un autor y calcula")
    print()


if __name__ == "__main__":
    test_author_value_calculation()
