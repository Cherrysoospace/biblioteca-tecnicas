"""Brute Force Algorithm Implementation.

This module implements the brute force algorithm to find all combinations
of 4 books that exceed a weight threshold of 8 Kg (risky shelf capacity).

Project Requirement:
    Implement a brute force algorithm that finds and lists all possible
    combinations of four books that, when adding their weight in Kg,
    exceed a risk threshold of 8 Kg (maximum shelf capacity).
    The algorithm must exhaustively explore all combinations.

Author: Library Management System Team
Date: 2025
"""

from typing import List, Dict, Any


def find_risky_combinations(books_data: List[Dict[str, Any]], threshold: float = 8.0) -> List[Dict[str, Any]]:
    """Find all combinations of 4 books that exceed the weight threshold using brute force.
    
    This algorithm exhaustively explores ALL possible combinations of 4 books
    from the provided list and identifies those whose combined weight exceeds
    the specified threshold (default 8 Kg - maximum shelf capacity).
    
    Algorithm Logic (Pseudocode style):
    
        PARA i DESDE 0 HASTA libros.tamaño - 4 HACER
            PARA j DESDE i+1 HASTA libros.tamaño - 3 HACER
                PARA k DESDE j+1 HASTA libros.tamaño - 2 HACER
                    PARA m DESDE k+1 HASTA libros.tamaño - 1 HACER
                        peso_total = libros[i].peso + libros[j].peso + libros[k].peso + libros[m].peso
                        SI peso_total > umbral ENTONCES
                            AGREGAR (libros[i], libros[j], libros[k], libros[m]) A resultado
        RETORNAR resultado
    
    Parameters:
    - books_data: List of dictionaries containing book information.
                  Each dict must have: 'id', 'title', 'weight' keys.
    - threshold: Maximum weight threshold in Kg (default 8.0).
    
    Returns:
    - List of dictionaries, each containing:
        * 'books': List of 4 book dictionaries (id, title, weight)
        * 'total_weight': Combined weight of the 4 books
        * 'excess': How much the combination exceeds the threshold
    
    Example:
    >>> books = [
    ...     {'id': 'B001', 'title': 'Book 1', 'weight': 2.5},
    ...     {'id': 'B002', 'title': 'Book 2', 'weight': 2.8},
    ...     {'id': 'B003', 'title': 'Book 3', 'weight': 2.3},
    ...     {'id': 'B004', 'title': 'Book 4', 'weight': 2.0},
    ... ]
    >>> risky = find_risky_combinations(books, threshold=8.0)
    >>> len(risky)
    1
    >>> risky[0]['total_weight']
    9.6
    
    Complexity:
    - Time: O(n^4) where n is the number of books (exhaustive search)
    - Space: O(k) where k is the number of risky combinations found
    
    Notes:
    - This is an intentionally BRUTE FORCE approach - it explores ALL combinations
    - For large datasets (n > 50), this will be slow
    - The algorithm demonstrates the exhaustive search pattern
    """
    risky_combinations = []
    
    # Get the total number of books
    n = len(books_data)
    
    # Need at least 4 books to form a combination
    if n < 4:
        return risky_combinations
    
    # PARA i DESDE 0 HASTA libros.tamaño - 4 HACER
    # Range goes from 0 to n-3 (to leave room for 3 more books)
    for i in range(n - 3):
        
        # PARA j DESDE i+1 HASTA libros.tamaño - 3 HACER
        # Range goes from i+1 to n-2 (to leave room for 2 more books)
        for j in range(i + 1, n - 2):
            
            # PARA k DESDE j+1 HASTA libros.tamaño - 2 HACER
            # Range goes from j+1 to n-1 (to leave room for 1 more book)
            for k in range(j + 1, n - 1):
                
                # PARA m DESDE k+1 HASTA libros.tamaño - 1 HACER
                # Range goes from k+1 to n (last book)
                for m in range(k + 1, n):
                    
                    # Get the 4 books from the indices
                    book1 = books_data[i]
                    book2 = books_data[j]
                    book3 = books_data[k]
                    book4 = books_data[m]
                    
                    # Calculate total weight of this combination
                    # peso_total = libros[i].peso + libros[j].peso + libros[k].peso + libros[m].peso
                    try:
                        weight1 = float(book1.get('weight', 0))
                        weight2 = float(book2.get('weight', 0))
                        weight3 = float(book3.get('weight', 0))
                        weight4 = float(book4.get('weight', 0))
                        
                        total_weight = weight1 + weight2 + weight3 + weight4
                        
                    except (ValueError, TypeError):
                        # Skip combinations with invalid weight data
                        continue
                    
                    # SI peso_total > umbral ENTONCES
                    if total_weight > threshold:
                        # AGREGAR (libros[i], libros[j], libros[k], libros[m]) A resultado
                        # Create a clean representation of this risky combination
                        combination = {
                            'books': [
                                {
                                    'id': book1.get('id', 'N/A'),
                                    'title': book1.get('title', 'Unknown'),
                                    'author': book1.get('author', 'Unknown'),
                                    'weight': weight1
                                },
                                {
                                    'id': book2.get('id', 'N/A'),
                                    'title': book2.get('title', 'Unknown'),
                                    'author': book2.get('author', 'Unknown'),
                                    'weight': weight2
                                },
                                {
                                    'id': book3.get('id', 'N/A'),
                                    'title': book3.get('title', 'Unknown'),
                                    'author': book3.get('author', 'Unknown'),
                                    'weight': weight3
                                },
                                {
                                    'id': book4.get('id', 'N/A'),
                                    'title': book4.get('title', 'Unknown'),
                                    'author': book4.get('author', 'Unknown'),
                                    'weight': weight4
                                }
                            ],
                            'total_weight': round(total_weight, 2),
                            'excess': round(total_weight - threshold, 2)
                        }
                        
                        risky_combinations.append(combination)
    
    # RETORNAR resultado
    return risky_combinations


def count_total_combinations(num_books: int) -> int:
    """Calculate the total number of 4-book combinations possible.
    
    This is a helper function to show how many combinations the brute force
    algorithm will explore. Uses the combination formula: C(n, 4) = n! / (4! * (n-4)!)
    
    Parameters:
    - num_books: Total number of books available
    
    Returns:
    - Total number of 4-book combinations to explore
    
    Example:
    >>> count_total_combinations(20)
    4845
    >>> count_total_combinations(10)
    210
    """
    if num_books < 4:
        return 0
    
    # Combination formula: C(n, 4) = n! / (4! * (n-4)!)
    # Simplified: (n * (n-1) * (n-2) * (n-3)) / (4 * 3 * 2 * 1)
    result = (num_books * (num_books - 1) * (num_books - 2) * (num_books - 3)) // 24
    return result


# Example usage for testing:
if __name__ == "__main__":
    # Test data: 5 books with varying weights
    test_books = [
        {'id': 'B001', 'title': 'Heavy Book 1', 'author': 'Author A', 'weight': 2.5},
        {'id': 'B002', 'title': 'Heavy Book 2', 'author': 'Author B', 'weight': 2.8},
        {'id': 'B003', 'title': 'Medium Book', 'author': 'Author C', 'weight': 2.3},
        {'id': 'B004', 'title': 'Light Book', 'author': 'Author D', 'weight': 2.0},
        {'id': 'B005', 'title': 'Very Heavy Book', 'author': 'Author E', 'weight': 3.0},
    ]
    
    print("=== Brute Force Algorithm Test ===")
    print(f"Total books: {len(test_books)}")
    print(f"Total combinations to explore: {count_total_combinations(len(test_books))}")
    print()
    
    # Find risky combinations (threshold = 8.0 Kg)
    risky = find_risky_combinations(test_books, threshold=8.0)
    
    print(f"Risky combinations found: {len(risky)}")
    print()
    
    # Display each risky combination
    for idx, combo in enumerate(risky, 1):
        print(f"Combination {idx}:")
        print(f"  Total Weight: {combo['total_weight']} Kg (Exceeds by {combo['excess']} Kg)")
        print("  Books:")
        for book in combo['books']:
            print(f"    - {book['id']}: {book['title']} ({book['weight']} Kg)")
        print()
