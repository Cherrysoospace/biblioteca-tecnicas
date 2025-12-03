"""
Queue-style (tail) recursion examples for the course assignment.

This module implements a tail-recursive function to compute the average
weight of all books by a given author. The implementation uses accumulator
parameters (index, count, total_weight) to maintain state across recursive
calls, demonstrating the tail recursion pattern.

Contract (inputs/outputs):
- inputs: books (list of dict), author (str)
- output: average weight as float
- error modes: returns 0.0 for empty lists or if no books by the author are found

Edge cases considered:
- empty books list
- no book by the author
- books with missing weight (handled by treating as 0.0)

Usage example:
>>> books = [
...   {"author": "Alice", "weight": 1.2, "price": 10000},
...   {"author": "Bob", "weight": 2.5, "price": 15000},
...   {"author": "Alice", "weight": 0.8, "price": 8000},
... ]
>>> avg_weight_by_author(books, "Alice")
1.0

Note: Python does not perform tail call optimization; this is an educational
implementation demonstrating the accumulator pattern.
"""


def avg_weight_by_author(books, author, index=0, count=0, total_weight=0.0, debug=False):
	"""Compute the average weight of books by `author` using tail recursion.

	This function uses accumulator parameters (index, count, total_weight) to
	maintain state across recursive calls. Each call processes one book and
	passes updated accumulators to the next call, demonstrating the queue-style
	(tail) recursion pattern.

	Parameters
	----------
	books : list of dict
		A list of book dictionaries. Each book should have at least the keys
		'author' (str) and 'weight' (int/float). If a book lacks 'weight',
		it contributes 0.0 to the total.
	author : str
		The author name to filter by (case-sensitive exact match).
	index : int, optional
		Internal recursion index (default: 0). Not intended for external callers.
	count : int, optional
		Accumulator for the number of books by the author found so far (default: 0).
	total_weight : float, optional
		Accumulator for the total weight of books by the author (default: 0.0).
	debug : bool, optional
		If True, prints the recursion index and accumulator state at each
		recursive call to demonstrate tail recursion flow.

	Returns
	-------
	float
		The average weight (in kg) of all books by the specified author.
		Returns 0.0 if no books match the author.

	Complexity
	----------
	O(n) time and O(n) call-stack depth where n is len(books).
	(Note: Python does not optimize tail calls, so stack depth is still O(n))
	"""
	# Base case: we've processed all books
	if index >= len(books):
		if debug:
			print(f"Base case reached: count={count}, total_weight={total_weight}")
		return (total_weight / count) if count > 0 else 0.0

	# Get current book
	book = books[index]
	book_author = book.get('author', '')
	book_weight = book.get('weight', 0.0)

	# Recursive step: update accumulators if author matches
	if book_author == author:
		if debug:
			print(f"Include index={index}: weight={book_weight} -> count={count + 1}, total={total_weight + book_weight}")
		return avg_weight_by_author(books, author, index + 1, count + 1, total_weight + book_weight, debug)
	else:
		if debug:
			print(f"Skip index={index}: author={book_author}")
		return avg_weight_by_author(books, author, index + 1, count, total_weight, debug)


def _demo():
	"""Simple demo and self-checks for the function."""
	# Sample books matching the structure used in books.json
	sample_books = [
		{"id": "B001", "ISBNCode": "111", "title": "Alpha", "author": "Alice", "weight": 1.2, "price": 10000},
		{"id": "B002", "ISBNCode": "222", "title": "Beta", "author": "Bob", "weight": 2.5, "price": 15000},
		{"id": "B003", "ISBNCode": "333", "title": "Gamma", "author": "Alice", "weight": 0.8, "price": 8000},
		{"id": "B004", "ISBNCode": "444", "title": "Delta", "author": "Carol", "weight": 1.5, "price": 12000},
		{"id": "B005", "ISBNCode": "555", "title": "Epsilon", "author": "Alice"},  # Missing weight
	]

	print("Demo: tail-recursive average weight by author (debug on)\n")
	
	# Expected: Alice -> (1.2 + 0.8 + 0.0) / 3 = 0.6667
	author_to_check = 'Alice'
	avg = avg_weight_by_author(sample_books, author_to_check, debug=True)
	print(f"\nAverage weight for author '{author_to_check}': {avg:.3f}")
	
	# Additional tests without debug output
	print("\n--- Additional Tests (no debug) ---")
	avg_bob = avg_weight_by_author(sample_books, "Bob")
	print(f"Average weight for Bob: {avg_bob:.3f}")
	assert avg_bob == 2.5, "Bob should have average weight 2.5"
	
	avg_carol = avg_weight_by_author(sample_books, "Carol")
	print(f"Average weight for Carol: {avg_carol:.3f}")
	assert avg_carol == 1.5, "Carol should have average weight 1.5"
	
	avg_none = avg_weight_by_author(sample_books, "NonExistent")
	print(f"Average weight for NonExistent author: {avg_none:.3f}")
	assert avg_none == 0.0, "Non-existent author should return 0.0"
	
	print("\nAll demo checks passed.")


if __name__ == '__main__':
	_demo()

