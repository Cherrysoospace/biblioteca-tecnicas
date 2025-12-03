"""Demonstration of Brute Force Algorithm for Risky Book Combinations.

This script demonstrates the brute force algorithm that finds all combinations
of 4 books that exceed the maximum shelf capacity of 8 Kg.

Project Requirement:
    Implement a brute force algorithm that finds and lists all possible
    combinations of four books that, when adding their weight in Kg,
    exceed a risk threshold of 8 Kg (maximum shelf capacity).

Usage:
    python demo_brute_force.py
"""

from controllers.book_controller import BookController


def display_risky_combinations(combinations, threshold=8.0):
    """Display risky combinations in a formatted way."""
    if not combinations:
        print("\n✓ No risky combinations found! All 4-book combinations are within safe limits.")
        return
    
    print(f"\n⚠ Found {len(combinations)} risky combinations that exceed {threshold} Kg:\n")
    print("=" * 100)
    
    for idx, combo in enumerate(combinations, 1):
        print(f"\nRisky Combination #{idx}:")
        print(f"  Total Weight: {combo['total_weight']} Kg")
        print(f"  Exceeds threshold by: {combo['excess']} Kg")
        print(f"  Books in combination:")
        
        for i, book in enumerate(combo['books'], 1):
            print(f"    {i}. [{book['id']}] {book['title']} by {book['author']} - {book['weight']} Kg")
        
        print("-" * 100)


def main():
    """Main demonstration of the brute force algorithm."""
    print("=" * 100)
    print("BRUTE FORCE ALGORITHM DEMONSTRATION")
    print("Finding Risky 4-Book Combinations (Weight > 8 Kg)")
    print("=" * 100)
    
    # Initialize controller
    controller = BookController()
    
    # Get inventory statistics
    all_books = controller.get_all_books()
    total_books = len(all_books)
    
    print(f"\nInventory Statistics:")
    print(f"  Total books in catalog: {total_books}")
    
    if total_books < 4:
        print("\n❌ Error: Need at least 4 books to form combinations.")
        print("   Please add more books to the inventory first.")
        return
    
    # Calculate total combinations to explore
    total_combinations = controller.count_possible_combinations()
    print(f"  Total 4-book combinations to explore: {total_combinations:,}")
    
    # Show weight distribution
    weights = [book.get_weight() for book in all_books]
    avg_weight = sum(weights) / len(weights) if weights else 0
    min_weight = min(weights) if weights else 0
    max_weight = max(weights) if weights else 0
    
    print(f"\nWeight Distribution:")
    print(f"  Average book weight: {avg_weight:.2f} Kg")
    print(f"  Lightest book: {min_weight:.2f} Kg")
    print(f"  Heaviest book: {max_weight:.2f} Kg")
    
    # Run brute force algorithm
    threshold = 8.0
    print(f"\n{'='*100}")
    print(f"Running Brute Force Algorithm (threshold = {threshold} Kg)...")
    print(f"{'='*100}")
    
    risky_combinations = controller.find_risky_book_combinations(threshold)
    
    # Display results
    display_risky_combinations(risky_combinations, threshold)
    
    # Summary statistics
    print(f"\n{'='*100}")
    print("SUMMARY")
    print(f"{'='*100}")
    print(f"  Total combinations explored: {total_combinations:,}")
    print(f"  Risky combinations found: {len(risky_combinations)}")
    
    if risky_combinations:
        percentage = (len(risky_combinations) / total_combinations) * 100
        print(f"  Percentage of risky combinations: {percentage:.2f}%")
        
        # Find the most risky combination
        most_risky = max(risky_combinations, key=lambda x: x['excess'])
        print(f"\n  Most risky combination:")
        print(f"    Total weight: {most_risky['total_weight']} Kg")
        print(f"    Exceeds by: {most_risky['excess']} Kg")
    
    print(f"\n{'='*100}")
    print("Algorithm demonstration completed successfully!")
    print(f"{'='*100}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
