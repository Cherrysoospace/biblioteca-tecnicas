"""models.reservation

Reservation model used by the reservation service and data storage.

This module defines a simple `Reservation` class containing only data
attributes. Business logic and persistence belong to the service layer.
"""

from datetime import datetime


class Reservation:
	"""Model for a book reservation.

	Attributes
	----------
	reservation_id
		Unique identifier for the reservation (string or int).
	user_id
		Identifier of the user who made the reservation.
	isbn
		ISBN code of the reserved book.
	reserved_date
		Datetime when the reservation was created. If not provided, it will be
		set to the current UTC time.
	status
		Reservation status (e.g. 'pending', 'assigned', 'cancelled').
	"""

	def __init__(self, reservation_id, user_id, isbn,
				 reserved_date: datetime = None, status: str = "pending"):
		# Unique identifier for the reservation (str or int).
		# Examples: numeric DB id or UUID string.
		self.__reservation_id = reservation_id

		# Identifier of the user who placed the reservation.
		# Type: str or int depending on project conventions.
		self.__user_id = user_id

		# ISBN code of the reserved book (string).
		self.__isbn = isbn

		# Datetime when the reservation was created. If not provided,
		# the current UTC time will be used.
		self.__reserved_date = reserved_date or datetime.utcnow()

		# Reservation status string. Common values: 'pending', 'assigned', 'cancelled'.
		self.__status = status

		# Assigned date (when the reservation was given a book)
		self.__assigned_date = None

	def get_reservation_id(self):
		"""Return the reservation's unique identifier.

		Returns
		-------
		str|int
			The reservation id (type depends on storage conventions).
		"""
		return self.__reservation_id

	def get_user_id(self):
		"""Return the identifier of the user who placed the reservation."""
		return self.__user_id

	def get_isbn(self):
		"""Return the ISBN code of the reserved book."""
		return self.__isbn

	def get_reserved_date(self):
		"""Return the reservation creation datetime (UTC)."""
		return self.__reserved_date

	def get_status(self):
		"""Return the current reservation status string."""
		return self.__status

	def get_assigned_date(self):
		"""Return the datetime when the reservation was assigned (or None)."""
		return self.__assigned_date

	def get_position(self):
		"""Return the reservation position in a queue (if set)."""
		return self.__position


	def set_reservation_id(self, reservation_id):
		"""Set the reservation's unique identifier.

		Parameters
		----------
		reservation_id : str|int
			New reservation identifier.
		"""
		self.__reservation_id = reservation_id

	def set_user_id(self, user_id):
		"""Set the identifier of the user who made the reservation."""
		self.__user_id = user_id

	def set_isbn(self, isbn):
		"""Set the ISBN code for this reservation."""
		self.__isbn = isbn

	def set_reserved_date(self, reserved_date: datetime):
		"""Set the reservation creation datetime.

		Parameters
		----------
		reserved_date : datetime
			Datetime object (preferably UTC) representing when reservation was made.
		"""
		self.__reserved_date = reserved_date

	def set_status(self, status: str):
		"""Update the reservation status string (e.g. 'pending', 'assigned')."""
		self.__status = status

	def set_assigned_date(self, assigned_date: datetime):
		"""Set the datetime when the reservation was assigned."""
		self.__assigned_date = assigned_date

	def set_position(self, position: int):
		"""Set the reservation position in queue."""
		self.__position = position

	def to_dict(self) -> dict:
		"""Serialize reservation to a plain dictionary for JSON storage.

		Dates are converted to ISO 8601 strings when possible.
		"""
		from datetime import datetime
		
		# Handle reserved_date - convert to ISO string if it's a datetime object
		if isinstance(self.__reserved_date, datetime):
			reserved = self.__reserved_date.isoformat()
		elif isinstance(self.__reserved_date, str):
			reserved = self.__reserved_date
		else:
			try:
				reserved = self.__reserved_date.isoformat()
			except Exception:
				reserved = str(self.__reserved_date)

		# Handle assigned_date - convert to ISO string if it's a datetime object
		if self.__assigned_date is None:
			assigned = None
		elif isinstance(self.__assigned_date, datetime):
			assigned = self.__assigned_date.isoformat()
		elif isinstance(self.__assigned_date, str):
			assigned = self.__assigned_date
		else:
			try:
				assigned = self.__assigned_date.isoformat()
			except Exception:
				assigned = str(self.__assigned_date)

		return {
			"reservation_id": self.__reservation_id,
			"user_id": self.__user_id,
			"isbn": self.__isbn,
			"reserved_date": reserved,
			"status": self.__status,
			"assigned_date": assigned,
			"position": self.__position,
		}

	@classmethod
	def from_dict(cls, data: dict):
		"""Construct a Reservation from a dict (as stored in JSON)."""
		from datetime import datetime as _dt
		
		res_date = data.get('reserved_date')
		assigned_date = data.get('assigned_date')
		
		# Convert reserved_date string to datetime object
		if res_date and isinstance(res_date, str):
			try:
				res_date = _dt.fromisoformat(res_date)
			except Exception:
				pass
		
		r = cls(data.get('reservation_id'), data.get('user_id'), data.get('isbn'), res_date, data.get('status', 'pending'))
		
		# Convert assigned_date string to datetime object
		if assigned_date:
			if isinstance(assigned_date, str):
				try:
					assigned_date = _dt.fromisoformat(assigned_date)
					r.set_assigned_date(assigned_date)
				except Exception:
					r.set_assigned_date(assigned_date)
			else:
				r.set_assigned_date(assigned_date)
		
		r.set_position(data.get('position'))
		return r


	def __str__(self):
		"""Return a readable string representation of the reservation."""
		return (f"Reservation[ID: {self.__reservation_id}, User: {self.__user_id}, "
			f"ISBN: {self.__isbn}, Date: {self.__reserved_date}, Status: {self.__status}, "
			f"Position: {self.__position}, Assigned: {self.__assigned_date}]")


__all__ = ["Reservation"]

