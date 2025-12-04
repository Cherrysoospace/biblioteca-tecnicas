"""Demonstration of the Backtracking Algorithm - Optimal Shelf Selection.

This script demonstrates the backtracking algorithm implementation that solves
the knapsack problem for books on a shelf. It finds the combination of books
that maximizes total value (COP) without exceeding the maximum shelf weight
capacity (8 Kg).

The algorithm explores all possible combinations using backtracking, which
efficiently prunes branches that exceed the weight constraint.

Usage:
    python demo_backtracking.py

Author: Library Management System Team
Date: 2025
"""

from controllers.book_controller import BookController


def main():
    """Main demonstration function."""
    
    print("=" * 80)
    print("BACKTRACKING ALGORITHM DEMONSTRATION")
    print("Optimal Shelf Selection - Knapsack Problem")
    print("=" * 80)
    print()
    
    # Initialize controller
    controller = BookController()
    
    # Get all books from the catalog
    all_books = controller.get_all_books()
    
    print(f"Total books in catalog: {len(all_books)}")
    print(f"Shelf weight capacity: 8.0 Kg")
    print()
    
    # Show a sample of the books available
    print("Sample of books in catalog:")
    print("-" * 80)
    for i, book in enumerate(all_books[:10], 1):  # Show first 10 books
        print(f"{i}. {book.get_id()} - {book.get_title()}")
        print(f"   Author: {book.get_author()}")
        print(f"   Weight: {book.get_weight()} Kg | Price: ${book.get_price():,} COP")
        print()
    
    if len(all_books) > 10:
        print(f"... and {len(all_books) - 10} more books")
        print()
    
    # Execute the backtracking algorithm
    print("=" * 80)
    print("EXECUTING BACKTRACKING ALGORITHM...")
    print("=" * 80)
    print()
    print("The algorithm will explore all possible combinations of books,")
    print("pruning branches that exceed the 8 Kg weight capacity.")
    print()
    
    # Find optimal shelf selection
    result = controller.find_optimal_shelf_selection(max_capacity=8.0)
    
    # Display results
    print("=" * 80)
    print("OPTIMAL SOLUTION FOUND")
    print("=" * 80)
    print()
    
    print(f"Maximum value achievable: ${result['max_value']:,} COP")
    print(f"Total weight: {result['total_weight']} Kg / 8.0 Kg")
    print(f"Weight capacity used: {(result['total_weight']/8.0)*100:.1f}%")
    print(f"Number of books selected: {len(result['books'])}")
    print()
    
    # Display selected books
    print("SELECTED BOOKS (Optimal Combination):")
    print("-" * 80)
    
    if result['books']:
        for i, book in enumerate(result['books'], 1):
            print(f"{i}. {book['id']} - {book['title']}")
            print(f"   Author: {book['author']}")
            print(f"   Weight: {book['weight']} Kg")
            print(f"   Price: ${book['price']:,} COP")
            print()
        
        # Summary statistics
        print("-" * 80)
        print("SUMMARY:")
        print(f"  Total Value: ${result['max_value']:,} COP")
        print(f"  Total Weight: {result['total_weight']} Kg")
        print(f"  Average price per book: ${result['max_value'] / len(result['books']):,.2f} COP")
        print(f"  Average weight per book: {result['total_weight'] / len(result['books']):.2f} Kg")
        print(f"  Value per Kg: ${result['max_value'] / result['total_weight']:,.2f} COP/Kg")
    else:
        print("No books could be selected within the weight constraint.")
    
    print()
    print("=" * 80)
    print("Algorithm Characteristics:")
    print("-" * 80)
    print("- Algorithm Type: Backtracking (Decision Tree Exploration)")
    print("- Problem Type: 0/1 Knapsack Problem")
    print("- Time Complexity: O(2^n) worst case")
    print("- Space Complexity: O(n) recursion depth")
    print("- Optimization: Pruning branches that exceed weight capacity")
    print("=" * 80)


if __name__ == "__main__":
    main()
