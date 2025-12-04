"""controllers.reservation_controller

Controller layer for reservation-related operations. This module adapts the
ReservationService to a simple procedural interface suitable for CLI or UI
integration. Each method returns plain Python types (dict or lists) so callers
can consume results without depending on service internals.
"""

from services.reservation_service import ReservationService


class ReservationController:
	"""Controller exposing reservation actions to UI or higher layers.

	This class wraps the ReservationService and returns simple result shapes
	(such as dicts with 'success'/'message') to simplify integration with
	command-line or GUI components.
	"""

	def __init__(self):
		"""Initialize the controller with a ReservationService instance.

		No parameters. The service is instantiated lazily here so callers don't
		need to construct it themselves.
		"""
		self.service = ReservationService()

	def create_reservation(self, user_id: str, isbn: str):
		"""Create a reservation for a user and ISBN.

		Parameters
		----------
		user_id : str
			Identifier of the user requesting the reservation.
		isbn : str
			ISBN of the book to reserve.

		Returns
		-------
		dict
			Result dictionary with keys: 'success', 'message', 'reservation'.
		"""
		try:
			res = self.service.create_reservation(None, user_id, isbn)
			return {"success": True, "message": "Reservation created", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}

	def list_reservations(self):
		"""Return all reservations managed by the service.

		Returns
		-------
		List[Reservation]
			List of Reservation objects.
		"""
		return self.service.get_all_reservations()

	def get_reservation(self, reservation_id: str):
		"""Retrieve a reservation by id.

		Parameters
		----------
		reservation_id : str
			Identifier of the reservation to retrieve.

		Returns
		-------
		Optional[Reservation]
			Reservation instance or None if not found.
		"""
		return self.service.find_by_id(reservation_id)

	def find_by_isbn(self, isbn: str):
		"""Find pending reservations for a given ISBN.

		Parameters
		----------
		isbn : str
			ISBN to search reservations for.

		Returns
		-------
		List[Reservation]
			Reservations in FIFO order.
		"""
		return self.service.find_by_isbn(isbn)

	def assign_next(self, isbn: str):
		"""Assign the next pending reservation for an ISBN.

		Parameters
		----------
		isbn : str
			ISBN for which the next reservation should be assigned.

		Returns
		-------
		dict
			Result shape with 'success', 'message', and 'reservation' keys.
		"""
		try:
			res = self.service.assign_next_for_isbn(isbn)
			if res is None:
				return {"success": False, "message": "No pending reservation for this ISBN", "reservation": None}
			return {"success": True, "message": "Reservation assigned", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}

	def cancel_reservation(self, reservation_id: str):
		"""Cancel a reservation by id.

		Returns a dict indicating success or failure and a human message.
		"""
		try:
			self.service.cancel_reservation(reservation_id)
			return {"success": True, "message": "Reservation cancelled"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def delete_reservation(self, reservation_id: str):
		"""Delete a reservation by id and persist the change.

		Returns
		-------
		dict
			Result with 'success' and 'message'.
		"""
		try:
			self.service.delete_reservation(reservation_id)
			return {"success": True, "message": "Reservation deleted"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def update_reservation(self, reservation_id: str, **kwargs):
		"""Update fields of a reservation.

		Accepts keyword arguments supported by the service (user_id, isbn, status,
		assigned_date). Returns the updated reservation inside the result dict.
		"""
		try:
			res = self.service.update_reservation(reservation_id, **kwargs)
			return {"success": True, "message": "Reservation updated", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}
