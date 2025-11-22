"""models.loan

Loan model for the library system.

This module defines a small `Loan` class with the data attributes required by
the project and two convenience methods: `mark_returned` and `to_dict`.

Only the `datetime` import is used by design.
"""

from datetime import datetime


class Loan:
	"""Represents a loan (book borrowing) record.

	Attributes
	----------
	loan_id : str
		Unique identifier for the loan record.
	user_id : str
		Identifier of the user who borrowed the book.
	isbn : str
		ISBN of the borrowed book.
	loan_date : date
		Date when the loan was created (a date object). If not provided, the
		current UTC date is used.
	returned : bool
		Flag indicating whether the book has been returned.
	"""

	def __init__(self, loan_id, user_id, isbn, loan_date=None, returned: bool = False):
		# Unique loan identifier (string)
		self.__loan_id = loan_id

		# User who borrowed the book
		self.__user_id = user_id

		# ISBN code of the borrowed book
		self.__isbn = isbn

		# Store a date object. If loan_date is not provided, use current UTC date.
		# We accept either a datetime.date or a datetime-like object; when a
		# datetime is provided we convert to date. Only datetime is imported.
		if loan_date is None:
			self.__loan_date = datetime.utcnow().date()
		else:
			# If user passed a datetime, convert to date; otherwise assume it
			# is already a date-like object with isoformat/supporting date()
			try:
				# If loan_date has a .date() method (datetime), use it
				self.__loan_date = loan_date.date()
			except Exception:
				# Fallback: store as given (expected to be a date)
				self.__loan_date = loan_date

		# Returned flag
		self.__returned = bool(returned)

	# --- Accessors ---
	def get_loan_id(self):
		return self.__loan_id

	def get_user_id(self):
		return self.__user_id

	def get_isbn(self):
		return self.__isbn

	def get_loan_date(self):
		return self.__loan_date

	def is_returned(self):
		return self.__returned

	# --- Mutators / helpers ---
	def set_loan_id(self, loan_id):
		self.__loan_id = loan_id

	def set_user_id(self, user_id):
		self.__user_id = user_id

	def set_isbn(self, isbn):
		self.__isbn = isbn

	def set_loan_date(self, loan_date):
		try:
			self.__loan_date = loan_date.date()
		except Exception:
			self.__loan_date = loan_date

	def set_returned(self, returned: bool):
		self.__returned = bool(returned)

	def mark_returned(self):
		"""Mark the loan as returned.

		This simply sets the returned flag to True. Business logic that needs a
		return date or additional side-effects should be implemented in the
		service layer.
		"""
		self.__returned = True

	def to_dict(self) -> dict:
		"""Serialize the loan to a plain dictionary.

		The date is converted to ISO 8601 (YYYY-MM-DD) string for JSON
		friendliness.
		"""
		loan_date = self.__loan_date
		# If loan_date is a datetime/date-like object, use isoformat when
		# available; otherwise store as-is.
		try:
			loan_date_serialized = loan_date.isoformat()
		except Exception:
			loan_date_serialized = loan_date

		return {
			"loan_id": self.__loan_id,
			"user_id": self.__user_id,
			"isbn": self.__isbn,
			"loan_date": loan_date_serialized,
			"returned": self.__returned,
		}

	def __str__(self):
		return (f"Loan[ID: {self.__loan_id}, User: {self.__user_id}, ISBN: {self.__isbn}, "
				f"Date: {self.__loan_date}, Returned: {self.__returned}]")


__all__ = ["Loan"]

