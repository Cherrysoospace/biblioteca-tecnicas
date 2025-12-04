from services.loan_service import LoanService


class LoanController:
	def __init__(self):
		"""Initialize the LoanController with a :class:`LoanService` instance.

		The controller is a thin layer that translates service results into
		simple dict responses for the UI or other callers.
		"""
		self.service = LoanService()

	def create_loan(self, user_id: str, isbn: str) -> dict:
		"""Create a loan and decrement inventory stock.

		The loan_id is now generated automatically by the service when not
		provided by the caller. Returns a dict with keys: success (bool),
		message (str), loan (Loan|None)
		"""
		try:
			loan = self.service.create_loan(None, user_id, isbn)
			return {"success": True, "message": "Loan created", "loan": loan}
		except Exception as e:
			return {"success": False, "message": str(e), "loan": None}

	def return_loan(self, loan_id: str) -> dict:
		"""Mark a loan returned and increment stock.

		Returns dict with keys: success, message
		"""
		try:
			self.service.mark_returned(loan_id)
			return {"success": True, "message": "Loan marked returned"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def list_loans(self):
		"""Return a list of all loans.

		Returns:
			List[Loan] - all loans currently persisted (copy of internal list).
		"""
		return self.service.get_all_loans()

	def get_loan(self, loan_id: str):
		"""Return a single loan by its ID.

		Args:
			loan_id: ID del préstamo

		Returns:
			Loan or None if no loan exists with the provided id.
		"""
		return self.service.find_by_id(loan_id)
	
	def find_by_id(self, loan_id: str):
		"""Find a loan by its ID.
		
		Args:
			loan_id: ID del préstamo
			
		Returns:
			Loan object or None if not found
		"""
		return self.service.find_by_id(loan_id)
	
	def find_by_user(self, user_id: str):
		"""Find all loans for a specific user.
		
		Args:
			user_id: ID del usuario
			
		Returns:
			List[Loan] - All loans for the user
		"""
		return self.service.find_by_user(user_id)
	
	def find_by_isbn(self, isbn: str):
		"""Find all loans for a specific ISBN.
		
		Args:
			isbn: ISBN del libro
			
		Returns:
			List[Loan] - All loans for this ISBN
		"""
		return self.service.find_by_isbn(isbn)
	
	def find_active_loans(self):
		"""Find all active loans (not returned).
		
		Returns:
			List[Loan] - All active loans
		"""
		return self.service.find_active_loans()

	def delete_loan(self, loan_id: str) -> dict:
		"""Delete a loan record. Returns dict with success/message."""
		try:
			self.service.delete_loan(loan_id)
			return {"success": True, "message": "Loan deleted"}
		except Exception as e:
			return {"success": False, "message": str(e)}

	def update_loan(self, loan_id: str, user_id: str = None, isbn: str = None, returned: bool = None, loan_date=None) -> dict:
		"""Update a loan record fields. Only provided fields are updated."""
		try:
			loan = self.service.update_loan(loan_id, user_id=user_id, isbn=isbn, returned=returned, loan_date=loan_date)
			return {"success": True, "message": "Loan updated", "loan": loan}
		except Exception as e:
			return {"success": False, "message": str(e), "loan": None}

	# -------------------- Loan History (Stack per User) --------------------
	
	def get_user_loan_history(self, user_id: str) -> dict:
		"""Get complete loan history for a user in LIFO order.
		
		Returns dict with keys: success, history (List[dict])
		"""
		try:
			history = self.service.get_user_loan_history(user_id)
			return {"success": True, "history": history}
		except Exception as e:
			return {"success": False, "history": [], "message": str(e)}
	
	def get_user_recent_loans(self, user_id: str, n: int = 5) -> dict:
		"""Get N most recent loans for a user.
		
		Returns dict with keys: success, recent_loans (List[dict])
		"""
		try:
			recent = self.service.get_user_recent_loans(user_id, n)
			return {"success": True, "recent_loans": recent}
		except Exception as e:
			return {"success": False, "recent_loans": [], "message": str(e)}
	
	def get_user_stack_size(self, user_id: str) -> dict:
		"""Get the size of a user's loan history stack.
		
		Returns dict with keys: success, size (int)
		"""
		try:
			size = self.service.get_user_stack_size(user_id)
			return {"success": True, "size": size}
		except Exception as e:
			return {"success": False, "size": 0, "message": str(e)}


