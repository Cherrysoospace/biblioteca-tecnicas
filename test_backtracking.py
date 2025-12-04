"""Unit tests for the Backtracking Algorithm - Knapsack Problem.

This module tests the backtracking algorithm implementation that finds
the optimal combination of books that maximizes value without exceeding
the maximum shelf weight capacity.

Test Coverage:
- Basic functionality with simple cases
- Edge cases (empty list, single book, all books too heavy)
- Optimal selection verification
- Weight constraint enforcement
- Value maximization
- Integration with BookController

Author: Library Management System Team
Date: 2025
"""

import unittest
from utils.algorithms.backtracking import solve_optimal_shelf, knapsack_backtracking
from controllers.book_controller import BookController


class TestBacktrackingAlgorithm(unittest.TestCase):
    """Test cases for the backtracking algorithm."""

    def test_empty_books_list(self):
        """Test with an empty books list."""
        books_data = []
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertEqual(result['max_value'], 0)
        self.assertEqual(result['total_weight'], 0.0)
        self.assertEqual(len(result['books']), 0)
        self.assertEqual(len(result['indices']), 0)

    def test_single_book_fits(self):
        """Test with a single book that fits within capacity."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.0, 'price': 100}
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertEqual(result['max_value'], 100)
        self.assertEqual(result['total_weight'], 2.0)
        self.assertEqual(len(result['books']), 1)
        self.assertEqual(result['books'][0]['id'], 'B001')

    def test_single_book_too_heavy(self):
        """Test with a single book that exceeds capacity."""
        books_data = [
            {'id': 'B001', 'title': 'Heavy Book', 'author': 'Author A', 'weight': 10.0, 'price': 100}
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertEqual(result['max_value'], 0)
        self.assertEqual(result['total_weight'], 0.0)
        self.assertEqual(len(result['books']), 0)

    def test_all_books_too_heavy(self):
        """Test when all books individually exceed capacity."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 9.0, 'price': 100},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 10.0, 'price': 150},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 12.0, 'price': 200},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertEqual(result['max_value'], 0)
        self.assertEqual(result['total_weight'], 0.0)
        self.assertEqual(len(result['books']), 0)

    def test_professor_example(self):
        """Test with the professor's example from class."""
        books_data = [
            {'id': 'B0', 'title': 'Book 0', 'author': 'A', 'weight': 12, 'price': 4},
            {'id': 'B1', 'title': 'Book 1', 'author': 'B', 'weight': 2, 'price': 2},
            {'id': 'B2', 'title': 'Book 2', 'author': 'C', 'weight': 1, 'price': 1},
            {'id': 'B3', 'title': 'Book 3', 'author': 'D', 'weight': 4, 'price': 10},
            {'id': 'B4', 'title': 'Book 4', 'author': 'E', 'weight': 1, 'price': 2},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=15)
        
        # Expected: books at indices 1, 2, 3, 4 (skip book 0 which is too heavy)
        # Total weight: 2 + 1 + 4 + 1 = 8
        # Total value: 2 + 1 + 10 + 2 = 15
        self.assertEqual(result['max_value'], 15)
        self.assertLessEqual(result['total_weight'], 15)

    def test_optimal_value_selection(self):
        """Test that the algorithm selects the combination with maximum value."""
        books_data = [
            {'id': 'B001', 'title': 'Light Cheap', 'author': 'A', 'weight': 1.0, 'price': 10},
            {'id': 'B002', 'title': 'Light Expensive', 'author': 'B', 'weight': 1.0, 'price': 100},
            {'id': 'B003', 'title': 'Heavy Expensive', 'author': 'C', 'weight': 7.0, 'price': 200},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        # Should select B002 and B003 (weight: 8.0, value: 300)
        # instead of B001 and B002 (weight: 2.0, value: 110)
        self.assertEqual(result['max_value'], 300)
        self.assertEqual(result['total_weight'], 8.0)
        self.assertEqual(len(result['books']), 2)

    def test_weight_constraint_respected(self):
        """Test that the algorithm never exceeds the weight capacity."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 2.5, 'price': 50},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 3.0, 'price': 75},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 2.8, 'price': 80},
            {'id': 'B004', 'title': 'Book 4', 'author': 'D', 'weight': 1.5, 'price': 40},
            {'id': 'B005', 'title': 'Book 5', 'author': 'E', 'weight': 3.5, 'price': 120},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertLessEqual(result['total_weight'], 8.0)
        self.assertGreater(result['max_value'], 0)

    def test_multiple_optimal_solutions(self):
        """Test case where multiple combinations have the same optimal value."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 2.0, 'price': 100},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 2.0, 'price': 100},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 4.0, 'price': 200},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=4.0)
        
        # Either B001 + B002 or B003 should be selected (both give value 200)
        self.assertEqual(result['max_value'], 200)
        self.assertLessEqual(result['total_weight'], 4.0)

    def test_fractional_weights(self):
        """Test with fractional weights (realistic book weights)."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 1.2, 'price': 30000},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 2.3, 'price': 50000},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 1.8, 'price': 40000},
            {'id': 'B004', 'title': 'Book 4', 'author': 'D', 'weight': 2.7, 'price': 60000},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        self.assertLessEqual(result['total_weight'], 8.0)
        self.assertGreater(result['max_value'], 0)
        # Should select all 4 books (total weight: 8.0, total value: 180000)
        self.assertEqual(result['max_value'], 180000)
        self.assertEqual(len(result['books']), 4)

    def test_invalid_book_data(self):
        """Test handling of books with invalid weight or price data."""
        books_data = [
            {'id': 'B001', 'title': 'Valid Book', 'author': 'A', 'weight': 2.0, 'price': 100},
            {'id': 'B002', 'title': 'Invalid Weight', 'author': 'B', 'weight': 'invalid', 'price': 100},
            {'id': 'B003', 'title': 'Missing Weight', 'author': 'C', 'price': 100},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        # Should handle invalid data gracefully
        self.assertGreaterEqual(result['max_value'], 100)  # At least the valid book

    def test_large_capacity(self):
        """Test with capacity larger than total weight of all books."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 1.0, 'price': 50},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 1.5, 'price': 75},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 2.0, 'price': 100},
        ]
        result = solve_optimal_shelf(books_data, max_capacity=100.0)
        
        # Should select all books
        self.assertEqual(result['max_value'], 225)
        self.assertEqual(result['total_weight'], 4.5)
        self.assertEqual(len(result['books']), 3)

    def test_integration_with_book_controller(self):
        """Test integration with BookController using real books.json data."""
        controller = BookController()
        result = controller.find_optimal_shelf_selection(max_capacity=8.0)
        
        # Verify result structure
        self.assertIn('max_value', result)
        self.assertIn('total_weight', result)
        self.assertIn('books', result)
        self.assertIn('indices', result)
        
        # Verify constraints
        self.assertGreaterEqual(result['max_value'], 0)
        self.assertLessEqual(result['total_weight'], 8.0)
        self.assertIsInstance(result['books'], list)
        
        # If books were selected, verify their data
        if result['books']:
            for book in result['books']:
                self.assertIn('id', book)
                self.assertIn('title', book)
                self.assertIn('author', book)
                self.assertIn('weight', book)
                self.assertIn('price', book)

    def test_result_consistency(self):
        """Test that the algorithm produces consistent results."""
        books_data = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'A', 'weight': 2.0, 'price': 100},
            {'id': 'B002', 'title': 'Book 2', 'author': 'B', 'weight': 3.0, 'price': 150},
            {'id': 'B003', 'title': 'Book 3', 'author': 'C', 'weight': 4.0, 'price': 200},
        ]
        
        # Run algorithm multiple times
        result1 = solve_optimal_shelf(books_data, max_capacity=8.0)
        result2 = solve_optimal_shelf(books_data, max_capacity=8.0)
        result3 = solve_optimal_shelf(books_data, max_capacity=8.0)
        
        # Results should be identical
        self.assertEqual(result1['max_value'], result2['max_value'])
        self.assertEqual(result2['max_value'], result3['max_value'])
        self.assertEqual(result1['total_weight'], result2['total_weight'])
        self.assertEqual(result2['total_weight'], result3['total_weight'])


class TestBacktrackingInternals(unittest.TestCase):
    """Test internal mechanisms of the backtracking algorithm."""

    def test_best_solution_update(self):
        """Test that best_solution is updated correctly during recursion."""
        weights = [2, 3, 4]
        values = [100, 150, 200]
        best_solution = {"max_value": 0, "selection": []}
        
        knapsack_backtracking(0, 0, 0, [], 8.0, weights, values, best_solution)
        
        # Should have found an optimal solution
        self.assertGreater(best_solution["max_value"], 0)
        self.assertGreater(len(best_solution["selection"]), 0)

    def test_backtracking_exploration(self):
        """Test that backtracking explores different branches."""
        # This test verifies that the algorithm explores multiple combinations
        weights = [1, 1, 1, 1]
        values = [10, 20, 30, 40]
        best_solution = {"max_value": 0, "selection": []}
        
        knapsack_backtracking(0, 0, 0, [], 3.0, weights, values, best_solution)
        
        # Should select the 3 most valuable books (indices 1, 2, 3)
        self.assertEqual(best_solution["max_value"], 90)
        self.assertEqual(len(best_solution["selection"]), 3)


def run_tests():
    """Run all tests and display results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBacktrackingAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktrackingInternals))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
