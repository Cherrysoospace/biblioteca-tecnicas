"""Unit tests for brute force algorithm.

This module tests the brute force algorithm that finds all combinations
of 4 books that exceed the weight threshold of 8 Kg.
"""

import pytest
from utils.algorithms.brute_force import find_risky_combinations, count_total_combinations


class TestBruteForceAlgorithm:
    """Test suite for brute force algorithm."""

    def test_find_risky_combinations_basic(self):
        """Test finding risky combinations with basic data."""
        # 4 heavy books that when combined exceed 8 Kg
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.5},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 2.8},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 2.3},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 2.0},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        # Should find exactly 1 combination (the only possible one)
        assert len(risky) == 1
        
        # Verify the combination details
        combo = risky[0]
        assert combo['total_weight'] == 9.6
        assert combo['excess'] == 1.6
        assert len(combo['books']) == 4

    def test_find_risky_combinations_no_risky(self):
        """Test when no combinations exceed threshold."""
        # Light books that won't exceed 8 Kg
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 1.0},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 1.2},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 1.3},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 1.5},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        # Should find no risky combinations
        assert len(risky) == 0

    def test_find_risky_combinations_multiple(self):
        """Test finding multiple risky combinations."""
        # 5 books where multiple combinations exceed 8 Kg
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.5},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 2.8},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 2.3},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 2.0},
            {'id': 'B005', 'title': 'Book 5', 'author': 'Author E', 'weight': 3.0},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        # Should find multiple risky combinations
        assert len(risky) > 1
        
        # All combinations should exceed threshold
        for combo in risky:
            assert combo['total_weight'] > 8.0
            assert combo['excess'] > 0

    def test_find_risky_combinations_insufficient_books(self):
        """Test with fewer than 4 books."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 3.0},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 3.0},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 3.0},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        # Should return empty list (need 4 books)
        assert len(risky) == 0

    def test_find_risky_combinations_custom_threshold(self):
        """Test with custom threshold."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 1.5},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 1.5},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 1.5},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 1.5},
        ]
        
        # Total weight = 6.0, which is below 8.0 but above 5.0
        risky_8 = find_risky_combinations(books, threshold=8.0)
        risky_5 = find_risky_combinations(books, threshold=5.0)
        
        assert len(risky_8) == 0  # Below 8.0
        assert len(risky_5) == 1  # Above 5.0

    def test_combination_structure(self):
        """Test that combination structure is correct."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.5},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 2.8},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 2.3},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 2.0},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        assert len(risky) > 0
        combo = risky[0]
        
        # Check required keys
        assert 'books' in combo
        assert 'total_weight' in combo
        assert 'excess' in combo
        
        # Check books structure
        assert len(combo['books']) == 4
        for book in combo['books']:
            assert 'id' in book
            assert 'title' in book
            assert 'author' in book
            assert 'weight' in book

    def test_count_total_combinations(self):
        """Test counting total combinations."""
        # C(4, 4) = 1
        assert count_total_combinations(4) == 1
        
        # C(5, 4) = 5
        assert count_total_combinations(5) == 5
        
        # C(10, 4) = 210
        assert count_total_combinations(10) == 210
        
        # C(20, 4) = 4845
        assert count_total_combinations(20) == 4845
        
        # Less than 4 books
        assert count_total_combinations(3) == 0
        assert count_total_combinations(0) == 0

    def test_exhaustive_search(self):
        """Test that algorithm explores ALL combinations."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 1.0},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 1.0},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 1.0},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 1.0},
            {'id': 'B005', 'title': 'Book 5', 'author': 'Author E', 'weight': 10.0},  # Very heavy
        ]
        
        # With threshold 8.0, any combination with B005 should be risky
        risky = find_risky_combinations(books, threshold=8.0)
        
        # C(5, 4) = 5 total combinations
        # 4 combinations include B005 (risky): B1+B2+B3+B5, B1+B2+B4+B5, B1+B3+B4+B5, B2+B3+B4+B5
        # 1 combination without B005 (safe): B1+B2+B3+B4 = 4.0 Kg
        # So 4 should exceed 8.0 (1+1+1+10=13, etc.)
        assert len(risky) == 4

    def test_weight_precision(self):
        """Test that weight calculations maintain precision."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.123},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 2.456},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 2.789},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 2.012},
        ]
        
        risky = find_risky_combinations(books, threshold=8.0)
        
        if len(risky) > 0:
            combo = risky[0]
            # Check that total_weight is rounded to 2 decimals
            assert isinstance(combo['total_weight'], float)
            assert isinstance(combo['excess'], float)
            
            # Verify the sum is correct (within floating point tolerance)
            expected = sum(b['weight'] for b in combo['books'])
            assert abs(combo['total_weight'] - expected) < 0.01

    def test_invalid_weight_handling(self):
        """Test handling of invalid weight data."""
        books = [
            {'id': 'B001', 'title': 'Book 1', 'author': 'Author A', 'weight': 2.0},
            {'id': 'B002', 'title': 'Book 2', 'author': 'Author B', 'weight': 'invalid'},
            {'id': 'B003', 'title': 'Book 3', 'author': 'Author C', 'weight': 2.0},
            {'id': 'B004', 'title': 'Book 4', 'author': 'Author D', 'weight': 2.0},
        ]
        
        # Should skip combinations with invalid weights
        risky = find_risky_combinations(books, threshold=8.0)
        
        # Should not crash, may return empty or partial results
        assert isinstance(risky, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
