"""models.loan

Loan model for the library system.

This module defines a small :class:`Loan` class which encapsulates the data
for a single book loan (borrowing) record. The class provides simple accessors
and mutators for each field and a couple of small helpers for common
operations such as marking a loan returned and serializing the model to a
dictionary suitable for JSON storage.

Only the :class:`datetime` import is used by design.
"""

from datetime import datetime


class Loan:
	"""Represents a loan (book borrowing) record.

	This class stores a minimal set of fields required by the application and
	keeps them private. Use the provided accessors and mutators to work with the
	values. The class intentionally keeps business logic minimal — services and
	controllers should implement application rules (due dates, fines, audits,
	etc.).

	Attributes
	----------
	loan_id : str
		Unique identifier for the loan record.
	user_id : str
		Identifier of the user who borrowed the book.
	isbn : str
		ISBN of the borrowed book.
	loan_date : date
		Date when the loan was created (a :class:`datetime.date` object). If not
		provided the constructor sets the current UTC date.
	returned : bool
		Flag indicating whether the book has been returned.

	Notes
	-----
	The model's responsibility is purely structural: it stores data and offers
	small helpers to update fields. Any side effects (logging, persistence,
	notifications) belong in the service layer.
	"""

	def __init__(self, loan_id, user_id, isbn, loan_date=None, returned: bool = False):
		"""Create a new :class:`Loan` instance.

		Parameters
		----------
		loan_id : str
			Unique identifier for the loan.
		user_id : str
			Identifier of the user who borrows the book.
		isbn : str
			ISBN code of the borrowed book.
		loan_date : datetime.date or datetime.datetime, optional
			Date when the loan was created. If a :class:`datetime.datetime` is
			provided it will be converted to a date. If omitted the current UTC
			date is used.
		returned : bool, optional
			Initial returned state (defaults to False).

		The constructor stores values on private attributes and normalizes the
		loan date to a date object when possible.
		"""
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
		"""Return the loan's identifier (string)."""
		return self.__loan_id

	def get_user_id(self):
		"""Return the user id associated with this loan (string)."""
		return self.__user_id

	def get_isbn(self):
		"""Return the ISBN of the borrowed book (string)."""
		return self.__isbn

	def get_loan_date(self):
		"""Return the loan date as a :class:`datetime.date`-like object.

		The value is typically a :class:`datetime.date` instance or whatever was
		originally provided to the constructor if it couldn't be converted.
		"""
		return self.__loan_date

	def is_returned(self):
		"""Return True if the loan has been marked as returned, otherwise
		False.
		"""
		return self.__returned

	# --- Mutators / helpers ---
	def set_loan_id(self, loan_id):
		"""Set or replace the loan identifier.

		This method performs no validation beyond assigning the value. The
		caller is responsible for ensuring uniqueness if required by the
		application.
		"""
		self.__loan_id = loan_id

	def set_user_id(self, user_id):
		"""Set the user id for this loan."""
		self.__user_id = user_id

	def set_isbn(self, isbn):
		"""Set the ISBN for the borrowed book."""
		self.__isbn = isbn

	def set_loan_date(self, loan_date):
		"""Update the loan date.

		If a :class:`datetime.datetime` is provided this method will convert it
		into a date using :meth:`datetime.date()`. If conversion fails the value
		is stored as given (useful for already-serialized values).
		"""
		try:
			self.__loan_date = loan_date.date()
		except Exception:
			self.__loan_date = loan_date

	def set_returned(self, returned: bool):
		"""Set the returned flag.

		Parameters
		----------
		returned : bool
			If truthy the loan will be marked as returned; otherwise it will be
		marked not returned.
		"""
		self.__returned = bool(returned)

	def mark_returned(self):
		"""Mark the loan as returned.

		This simply sets the returned flag to True. Business logic that needs a
		return date or additional side-effects should be implemented in the
		service layer.
		"""
		# Mark the loan as returned. Services may want to call this helper and
		# then persist the change.
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
		"""Return a human-readable string representation for debugging."""
		return (f"Loan[ID: {self.__loan_id}, User: {self.__user_id}, ISBN: {self.__isbn}, "
				f"Date: {self.__loan_date}, Returned: {self.__returned}]")


__all__ = ["Loan"]

