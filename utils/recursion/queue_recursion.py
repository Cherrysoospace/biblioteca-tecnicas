"""Recursion examples for queue-style (tail) recursion.

This module implements a tail-recursive function to compute the average
weight of all books by a given author. The implementation accepts a list
of book-like objects (either instances of the project's `Book` class or
plain dicts with `author` / `weight` keys) and demonstrates the
accumulator-style recursion pattern shown in the class example.

The helpers are defined at module level (no nested functions), and the
implementation intentionally mirrors the accumulator (tail recursion)
pattern used in class examples. Note: Python does not perform tail
call optimization; this is an educational implementation.
"""


def _get_author(b):
	"""Return the author string for a book-like object or dict.

	Supports objects with `get_author()` and dicts with keys 'author' or
	'autor'. If author cannot be determined returns empty string.
	"""
	if hasattr(b, 'get_author') and callable(getattr(b, 'get_author')):
		return b.get_author()
	try:
		return b.get('author') or b.get('autor') or ""
	except Exception:
		return ""


def _get_weight(b):
	"""Return the weight (float) for a book-like object or dict.

	Supports objects with `get_weight()` and dicts with keys 'weight' or
	'peso'. If weight cannot be determined returns 0.0.
	"""
	if hasattr(b, 'get_weight') and callable(getattr(b, 'get_weight')):
		try:
			return float(b.get_weight())
		except Exception:
			return 0.0
	try:
		w = b.get('weight') if isinstance(b, dict) else None
		if w is None:
			w = b.get('peso') if isinstance(b, dict) else None
		return float(w) if w is not None else 0.0
	except Exception:
		return 0.0


def _helper_avg_weight(books, author, index, count, total_weight, debug):
	"""Tail-recursive helper to compute average weight.

	Parameters mirror the accumulators used in the assignment: index,
	count and total_weight. Defined at module level to avoid nested
	function definitions.
	"""
	if index >= len(books):
		if debug:
			print(f"Base case reached: count={count}, total_weight={total_weight}")
		return (total_weight / count) if count > 0 else 0.0

	b = books[index]
	b_author = _get_author(b)
	b_weight = _get_weight(b)

	if b_author == author:
		if debug:
			print(f"Include index={index}: weight={b_weight} -> count={count + 1}, total={total_weight + b_weight}")
		return _helper_avg_weight(books, author, index + 1, count + 1, total_weight + b_weight, debug)
	else:
		if debug:
			print(f"Skip index={index}: author={b_author}")
		return _helper_avg_weight(books, author, index + 1, count, total_weight, debug)


def avg_weight_by_author(books, author, debug=False):
	"""Compute the average weight of books by `author` using tail recursion.

	Parameters
	----------
	books:
		A list of book-like objects. Each item may be either:
		  - an object with `.get_author()` and `.get_weight()` methods (the
			project's `Book` class), or
		  - a dict with keys 'author' and 'weight' (or 'peso').
	author:
		The author name to filter by (case-sensitive exact match).
	debug:
		If True, prints the recursion index and accumulator state at
		each recursive call to demonstrate tail recursion flow.

	Returns
	-------
	float
		The average weight (in the same units as book.weight). If no books
		match the author, returns 0.0.
	"""

	return _helper_avg_weight(books, author, 0, 0, 0.0, debug)


if __name__ == '__main__':
	# Demo: construct a few Book instances if the project's Book class is
	# available; otherwise use plain dicts. This demonstrates the tail
	# recursion flow on the console.
	try:
		from models.Books import Book

		sample_books = [
			Book(1, '111', 'Alpha', 'Alice', 1.2, 10000),
			Book(2, '222', 'Beta', 'Bob', 2.5, 15000),
			Book(3, '333', 'Gamma', 'Alice', 0.8, 8000),
			Book(4, '444', 'Delta', 'Carol', 1.5, 12000),
		]
	except Exception:
		sample_books = [
			{'id': 1, 'ISBN': '111', 'title': 'Alpha', 'author': 'Alice', 'weight': 1.2},
			{'id': 2, 'ISBN': '222', 'title': 'Beta', 'author': 'Bob', 'weight': 2.5},
			{'id': 3, 'ISBN': '333', 'title': 'Gamma', 'author': 'Alice', 'weight': 0.8},
			{'id': 4, 'ISBN': '444', 'title': 'Delta', 'author': 'Carol', 'weight': 1.5},
		]

	print("Demo: tail-recursive average weight by author (debug on)\\n")
	author_to_check = 'Alice'
	avg = avg_weight_by_author(sample_books, author_to_check, debug=True)
	print(f"\\nAverage weight for author '{author_to_check}': {avg:.3f}")

