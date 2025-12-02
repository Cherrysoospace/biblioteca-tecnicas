"""
Stack-style recursion examples for the course assignment.

This module implements a recursive (stack-style) function that computes the
total monetary value of all books by a given author. The recursion mimics the
classical factorial example where each call processes one element and pushes
the rest of the work onto the call stack.

Contract (inputs/outputs):
- inputs: books (list of dict), author (str), index (int, internal)
- output: total value as int or float
- error modes: returns 0 for empty lists or if author not found; expects book
  items to contain a numeric 'value' and a string 'author' key.

Edge cases considered:
- empty books list
- no book by the author
- books with missing or non-numeric value (handled by treating as 0)

Usage example (demonstrated in the module demo):
>>> books = [
...   {"isbn": "1", "title": "A", "author": "Alice", "value": 100},
...   {"isbn": "2", "title": "B", "author": "Bob", "value": 150},
... ]
>>> total_value_by_author(books, "Alice")
100

This file contains simple asserts as a minimal test harness.
"""

def total_value_by_author(books, author, index=0):
    """Return the total value of books by `author` using stack recursion.

    This function processes one book per call and delegates the remainder to
    a recursive call with an incremented index. It uses the call stack to
    accumulate the sum (like a classic factorial recursion shape).

    Parameters
    - books: list of dict-like objects. Each book should have at least the
      keys 'author' (str) and 'value' (int/float). If a book lacks 'value' or
      it is not numeric, the book contributes 0 to the total.
    - author: string with the author name to match (case-sensitive).
    - index: internal recursion index (start at 0). Not intended for external
      callers.

    Returns
    - total value (int or float)

    Complexity: O(n) time and O(n) call-stack depth where n is len(books).
    """

    # Base case: we've processed all books
    if index >= len(books):
        return 0

    # Safe extraction of fields with defensive checks
    book = books[index]
    try:
        book_author = book.get('author') if isinstance(book, dict) else None
    except Exception:
        book_author = None

    # Determine contribution of current book
    contribution = 0
    if book_author == author:
        # read numeric value defensively
        try:
            val = book.get('value', 0)
            # support int-like or float-like strings gracefully
            if isinstance(val, (int, float)):
                contribution = val
            else:
                contribution = float(val)
        except Exception:
            contribution = 0

    # Recursive step: add current contribution to total of the rest
    return contribution + total_value_by_author(books, author, index + 1)


def _demo():
    """Simple demo and self-checks for the function."""
    sample_books = [
        {"isbn": "111", "title": "Python 101", "author": "Alice", "value": 120},
        {"isbn": "112", "title": "Advanced Python", "author": "Bob", "value": 200},
        {"isbn": "113", "title": "Data Structures", "author": "Alice", "value": 80},
        {"isbn": "114", "title": "Cooking", "author": "Carol", "value": "50"},
        {"isbn": "115", "title": "Mystery", "author": "Alice", "value": None},
    ]

    # Expected: Alice -> 120 + 80 + 0 = 200
    total_alice = total_value_by_author(sample_books, "Alice")
    print(f"Total value for Alice: {total_alice}")

    # Expected: Bob -> 200
    total_bob = total_value_by_author(sample_books, "Bob")
    print(f"Total value for Bob: {total_bob}")

    # Expected: Carol -> 50 (string converted to float)
    total_carol = total_value_by_author(sample_books, "Carol")
    print(f"Total value for Carol: {total_carol}")

    # Basic assertions as minimal tests
    assert total_alice == 200, "Alice total should be 200"
    assert total_bob == 200, "Bob total should be 200"
    assert total_carol == 50.0, "Carol total should be 50.0"

    print("All demo checks passed.")


if __name__ == '__main__':
    _demo()
