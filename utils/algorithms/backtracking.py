"""Backtracking Algorithm Implementation - Knapsack Problem.

This module implements the backtracking algorithm to solve the knapsack problem:
finding the optimal combination of books that maximizes total value without
exceeding the maximum shelf weight capacity.

Project Requirement:
    Implement a backtracking algorithm that finds the combination of books
    that maximizes the total value (COP) without exceeding the maximum weight
    capacity (8 Kg) of a shelf. The algorithm must demonstrate the exploration
    and its execution.

Author: Library Management System Team
Date: 2025
"""


def knapsack_backtracking(index, current_weight, current_value, current_selection,
                         max_capacity, weights, values, best_solution):
    """Recursive auxiliary function that explores the decision tree.
    
    This function implements the backtracking pattern by exploring two branches
    at each decision point:
    1. Include the current book (if it fits)
    2. Exclude the current book
    
    The function updates the best_solution dictionary when it finds a better
    combination than previously recorded.
    
    Algorithm Logic (Pseudocode style):
    
        FUNCIÓN backtracking(índice, peso_actual, valor_actual, selección_actual):
            SI índice == total_libros ENTONCES
                SI valor_actual > mejor_valor ENTONCES
                    mejor_valor = valor_actual
                    mejor_selección = copiar(selección_actual)
                RETORNAR
            
            # Rama 1: INCLUIR el libro actual
            SI peso_actual + pesos[índice] <= capacidad ENTONCES
                selección_actual.agregar(índice)
                backtracking(índice+1, peso_actual+pesos[índice], 
                           valor_actual+valores[índice], selección_actual)
                selección_actual.quitar_último()  # BACKTRACKING
            
            # Rama 2: NO INCLUIR el libro actual
            backtracking(índice+1, peso_actual, valor_actual, selección_actual)
    
    Parameters:
    - index: Current index in the book list (0-based)
    - current_weight: Accumulated weight so far (in Kg)
    - current_value: Accumulated value so far (in COP)
    - current_selection: List of indices of books selected in this branch
    - max_capacity: Maximum weight capacity (8 Kg for shelf)
    - weights: List of book weights (parallel to values)
    - values: List of book prices (parallel to weights)
    - best_solution: Dictionary to store the best solution found (mutable state)
                     Keys: 'max_value', 'selection'
    
    Returns:
    - None (updates best_solution dict in place)
    
    """
    
    # --- BASE CASE ---
    # If we have reached the end of the books list
    if index == len(weights):
        # Compare if the current branch is better than the best recorded solution
        if current_value > best_solution["max_value"]:
            best_solution["max_value"] = current_value
            best_solution["selection"] = list(current_selection)  # Copy the list
        return

    # --- BRANCH 1: INCLUDE THE BOOK ---
    # Only enter if the weight does not exceed capacity
    if current_weight + weights[index] <= max_capacity:
        current_selection.append(index)  # Make decision
        
        knapsack_backtracking(
            index + 1,
            current_weight + weights[index],
            current_value + values[index],
            current_selection,
            max_capacity, weights, values, best_solution
        )
        
        current_selection.pop()  # Backtracking (Undo decision)

    # --- BRANCH 2: DO NOT INCLUDE THE BOOK ---
    # Move to next without adding weight or value
    knapsack_backtracking(
        index + 1,
        current_weight,
        current_value,
        current_selection,
        max_capacity, weights, values, best_solution
    )


def solve_optimal_shelf(books_data, max_capacity=8.0):
    """Main function that prepares data and initiates the backtracking recursion.
    
    This function solves the knapsack problem for books on a shelf:
    - Input: List of books with weights and prices
    - Constraint: Total weight cannot exceed max_capacity (8 Kg)
    - Objective: Maximize total value (COP)
    
    The function extracts weights and values from the books data, calls the
    backtracking algorithm, and returns the optimal solution in a readable format.
    
    OPTIMIZATION: For large datasets (>25 books), the algorithm prefilters books
    by selecting those with the best value-to-weight ratio to keep the problem
    tractable while still finding high-quality solutions.
    
    Parameters:
    - books_data: List of dictionaries containing book information.
                  Each dict must have: 'id', 'title', 'author', 'weight', 'price' keys.
    - max_capacity: Maximum weight capacity in Kg (default 8.0 - shelf capacity)
    
    Returns:
    - Dictionary containing:
        * 'max_value': Maximum total value achievable (in COP)
        * 'total_weight': Total weight of selected books (in Kg)
        * 'books': List of selected book dictionaries with full information
        * 'indices': List of indices of selected books (for reference)
    
    Example:
    >>> books = [
    ...     {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 2.0, 'price': 100},
    ...     {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 3.0, 'price': 150},
    ...     {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 4.0, 'price': 200},
    ... ]
    >>> result = solve_optimal_shelf(books, max_capacity=8.0)
    >>> result['max_value']
    350
    >>> len(result['books'])
    2
    
    """
    
    # Edge case: empty book list
    if not books_data:
        return {
            'max_value': 0,
            'total_weight': 0.0,
            'books': [],
            'indices': []
        }
    
    # OPTIMIZATION: For large datasets, prefilter books by value-to-weight ratio
    # This keeps the problem tractable while finding good solutions
    MAX_BOOKS_FOR_FULL_SEARCH = 25
    
    # Create indexed book data with value-to-weight ratio
    indexed_books = []
    for i, book in enumerate(books_data):
        try:
            weight = float(book.get('weight', 0))
            price = float(book.get('price', 0))
            # Calculate value per kg (higher is better)
            ratio = price / weight if weight > 0 else 0
            indexed_books.append({
                'original_index': i,
                'book': book,
                'weight': weight,
                'price': price,
                'ratio': ratio
            })
        except (ValueError, TypeError, ZeroDivisionError):
            # Skip books with invalid data
            continue
    
    # If we have too many books, select the best candidates by ratio
    if len(indexed_books) > MAX_BOOKS_FOR_FULL_SEARCH:
        # Sort by value-to-weight ratio (descending)
        indexed_books.sort(key=lambda x: x['ratio'], reverse=True)
        # Keep only the top candidates
        indexed_books = indexed_books[:MAX_BOOKS_FOR_FULL_SEARCH]
    
    # Extract weights and values for the selected books
    weights = [b['weight'] for b in indexed_books]
    values = [b['price'] for b in indexed_books]
    
    # Use a dictionary to store the global state of the best solution.
    # This is necessary because integers in Python are immutable when passed by function.
    best_solution = {
        "max_value": 0,
        "selection": []
    }
    
    # Initiate the backtracking recursion
    knapsack_backtracking(
        0,   # initial index
        0,   # initial weight
        0,   # initial value
        [],  # empty initial selection
        max_capacity,
        weights,
        values,
        best_solution
    )
    
    # Build detailed result with book information
    selected_books = []
    total_weight = 0.0
    
    for idx in best_solution["selection"]:
        # Map back to original book using indexed_books
        original_book = indexed_books[idx]['book']
        selected_books.append({
            'id': original_book.get('id', 'N/A'),
            'title': original_book.get('title', 'Unknown'),
            'author': original_book.get('author', 'Unknown'),
            'weight': weights[idx],
            'price': values[idx]
        })
        total_weight += weights[idx]
    
    return {
        'max_value': best_solution["max_value"],
        'total_weight': round(total_weight, 2),
        'books': selected_books,
        'indices': best_solution["selection"]
    }


# Example usage for testing:
if __name__ == "__main__":
    # Test data from professor's example
    print("=== Test 1: Professor's Example ===")
    test_weights = [12, 2, 1, 4, 1]
    test_values = [4, 2, 1, 10, 2]
    test_capacity = 15
    
    # Create fake books data for this test
    test_books = []
    for i in range(len(test_weights)):
        test_books.append({
            'id': f'B{i}',
            'title': f'Book {i}',
            'author': f'Author {i}',
            'weight': test_weights[i],
            'price': test_values[i]
        })
    
    result = solve_optimal_shelf(test_books, max_capacity=test_capacity)
    
    print(f"Maximum benefit possible: {result['max_value']}")
    print(f"Indices of selected books: {result['indices']}")
    print("\nSelection detail:")
    for book in result['books']:
        print(f"- {book['id']}: Weight {book['weight']} | Value {book['price']}")
    print(f"Total weight: {result['total_weight']}/{test_capacity}")
    print()
    
    # Test 2: Library shelf scenario (8 Kg capacity)
    print("=== Test 2: Library Shelf Scenario (8 Kg capacity) ===")
    library_books = [
        {'id': 'B001', 'title': 'Python Basics', 'author': 'Alice', 'weight': 2.5, 'price': 50000},
        {'id': 'B002', 'title': 'Data Structures', 'author': 'Bob', 'weight': 3.0, 'price': 75000},
        {'id': 'B003', 'title': 'Algorithms', 'author': 'Carol', 'weight': 2.8, 'price': 80000},
        {'id': 'B004', 'title': 'Web Development', 'author': 'Dave', 'weight': 1.5, 'price': 40000},
        {'id': 'B005', 'title': 'Machine Learning', 'author': 'Eve', 'weight': 3.5, 'price': 120000},
    ]
    
    result2 = solve_optimal_shelf(library_books, max_capacity=8.0)
    
    print(f"Maximum value possible: ${result2['max_value']:,} COP")
    print(f"Number of books selected: {len(result2['books'])}")
    print("\nOptimal selection:")
    for book in result2['books']:
        print(f"- {book['id']}: {book['title']} | {book['weight']} Kg | ${book['price']:,} COP")
    print(f"Total weight: {result2['total_weight']} Kg / 8.0 Kg")
    print(f"Weight capacity used: {(result2['total_weight']/8.0)*100:.1f}%")
