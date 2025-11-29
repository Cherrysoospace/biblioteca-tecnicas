from services.reservation_service import ReservationService


class ReservationController:
	def __init__(self):
		self.service = ReservationService()

	def create_reservation(self, user_id: str, isbn: str):
		try:
			res = self.service.create_reservation(None, user_id, isbn)
			return {"success": True, "message": "Reservation created", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}

	def list_reservations(self):
		return self.service.get_all_reservations()

	def get_reservation(self, reservation_id: str):
		return self.service.find_by_id(reservation_id)

	def find_by_isbn(self, isbn: str):
		return self.service.find_by_isbn(isbn)

	def assign_next(self, isbn: str):
		try:
			res = self.service.assign_next_for_isbn(isbn)
			if res is None:
				return {"success": False, "message": "No pending reservation for this ISBN", "reservation": None}
			return {"success": True, "message": "Reservation assigned", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}

	def cancel_reservation(self, reservation_id: str):
		try:
			self.service.cancel_reservation(reservation_id)
			return {"success": True, "message": "Reservation cancelled"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def delete_reservation(self, reservation_id: str):
		try:
			self.service.delete_reservation(reservation_id)
			return {"success": True, "message": "Reservation deleted"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def update_reservation(self, reservation_id: str, **kwargs):
		try:
			res = self.service.update_reservation(reservation_id, **kwargs)
			return {"success": True, "message": "Reservation updated", "reservation": res}
		except Exception as e:
			return {"success": False, "message": str(e), "reservation": None}
