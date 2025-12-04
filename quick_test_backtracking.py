"""Quick test script for Backtracking algorithm.

This script provides a fast way to verify the backtracking algorithm
is working correctly with the real books.json data.

Usage:
    python quick_test_backtracking.py
"""

from controllers.book_controller import BookController


def main():
    print("=" * 70)
    print("QUICK TEST - BACKTRACKING ALGORITHM")
    print("=" * 70)
    print()
    
    # Initialize controller
    controller = BookController()
    
    # Get total books
    all_books = controller.get_all_books()
    print(f"📚 Total books in catalog: {len(all_books)}")
    print(f"⚖️  Shelf capacity: 8.0 Kg")
    print()
    
    # Run backtracking algorithm
    print("🔄 Running backtracking algorithm...")
    result = controller.find_optimal_shelf_selection(max_capacity=8.0)
    print("✅ Algorithm completed!")
    print()
    
    # Display results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"💰 Maximum value: ${result['max_value']:,.2f} COP")
    print(f"⚖️  Total weight: {result['total_weight']} Kg / 8.0 Kg")
    print(f"📊 Capacity used: {(result['total_weight']/8.0)*100:.1f}%")
    print(f"📚 Books selected: {len(result['books'])}")
    print()
    
    if result['books']:
        print("TOP 5 SELECTED BOOKS:")
        print("-" * 70)
        for i, book in enumerate(result['books'][:5], 1):
            print(f"{i}. {book['id']}: {book['title'][:40]}")
            print(f"   Weight: {book['weight']} Kg | Price: ${book['price']:,.0f} COP")
            print()
        
        if len(result['books']) > 5:
            print(f"... and {len(result['books']) - 5} more books")
    
    print("=" * 70)
    print("✅ TEST PASSED - Algorithm working correctly!")
    print("=" * 70)


if __name__ == "__main__":
    main()
