from services.loan_service import LoanService


class LoanController:
	def __init__(self):
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
		return self.service.get_all_loans()

	def get_loan(self, loan_id: str):
		return self.service.find_by_id(loan_id)

