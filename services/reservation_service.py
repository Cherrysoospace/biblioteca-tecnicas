"""services.reservation_service

Reservation service layer: business logic for creating, managing and assigning
reservations. Persistence is delegated to a repository implementation.

This module implements FIFO (queue) semantics for pending reservations and
exposes CRUD-like operations used by controllers or higher-level services.
"""

import os
import json
from datetime import datetime
from typing import List, Optional

from models.reservation import Reservation
from repositories.reservation_repository import ReservationRepository
from utils.structures.queue import Queue


class ReservationService:
	"""Service to manage reservations.

	Responsibilities:
	- BUSINESS LOGIC ONLY: reservation queue management, status updates
	- Persistence delegated to ReservationRepository (SRP compliance)
	- Create, list, find, update, cancel, assign reservations
	- Uses Queue structure (FIFO) for pending reservations management
	
	CRITICAL: Only allows reservations when book stock = 0 (business rule validation)
	"""

	def __init__(self, repository: ReservationRepository = None):
		self.repository = repository or ReservationRepository()
		self.reservations: List[Reservation] = []
		self._load_reservations()

	def _load_reservations(self) -> None:
		"""Load reservations from repository.

		This populates the in-memory reservation list from the configured
		repository. If loading fails the service falls back to an empty list.
		"""
		try:
			self.reservations = self.repository.load_all()
		except Exception:
			# Start with empty list if load fails
			self.reservations = []

	def _save_reservations(self) -> None:
		"""Persist reservations using repository."""
		self.repository.save_all(self.reservations)

	# -------------------- CRUD / Actions --------------------
	def _generate_next_id(self) -> str:
		"""Generate the next reservation identifier.

		The repository uses string identifiers with an 'R' prefix (e.g. R001).
		This helper inspects existing IDs and returns a new unique ID in the
		format 'Rnnn' where nnn is a zero-padded integer.

		Returns
		-------
		str
			New unique reservation id (e.g. 'R005').
		"""
		existing = {r.get_reservation_id() for r in self.reservations if r.get_reservation_id()}
		max_n = 0
		for rid in existing:
			if isinstance(rid, str) and rid.startswith('R'):
				num = rid[1:]
				if '-' in num:
					num = num.split('-', 1)[0]
				if num.isdigit():
					try:
						v = int(num)
						if v > max_n:
							max_n = v
					except Exception:
						pass
		next_n = max_n + 1
		return f"R{next_n:03d}"

	def create_reservation(self, reservation_id: Optional[str], user_id: str, isbn: str) -> Reservation:
		"""Create a reservation. If reservation_id None, generate one.
		
		CRITICAL VALIDATIONS:
		1. Only allows reservation if book stock = 0 (business rule)
		2. User cannot reserve a book they already have on active loan
		
		Args:
			reservation_id: Unique ID (auto-generated if None)
			user_id: User requesting the reservation
			isbn: ISBN of the book to reserve
			
		Returns:
			Reservation: Created reservation object
			
		Raises:
			ValueError: If book has available stock (stock > 0) or user already has the book on loan
		"""
		# CRITICAL VALIDATION #1: Validate stock = 0 before creating reservation
		from services.inventory_service import InventoryService
		inv_service = InventoryService()
		
		# Calculate total available stock for this ISBN
		inventories = inv_service.find_by_isbn(isbn)
		if not inventories:
			raise ValueError(f"Cannot create reservation: ISBN '{isbn}' does not exist in inventory")
		
		total_available = sum(inv.get_available_count() for inv in inventories)
		
		if total_available > 0:
			raise ValueError(
				f"Cannot create reservation: ISBN '{isbn}' has {total_available} "
				f"{'copy' if total_available == 1 else 'copies'} available. "
				f"Reservations are only allowed for books with zero stock."
			)
		
		# CRITICAL VALIDATION #2: User cannot reserve a book they already have on active loan
		try:
			from services.loan_service import LoanService
			loan_service = LoanService()
			
			# Check if user has any active loans for this ISBN
			user_loans = loan_service.find_by_user(user_id)
			active_loan_for_isbn = None
			for loan in user_loans:
				if loan.get_isbn() == isbn and not loan.is_returned():
					active_loan_for_isbn = loan
					break
			
			if active_loan_for_isbn:
				raise ValueError(
					f"Cannot create reservation: User '{user_id}' already has an active loan "
					f"(Loan ID: {active_loan_for_isbn.get_loan_id()}) for ISBN '{isbn}'. "
					f"Users cannot reserve books they currently have borrowed."
				)
		except ValueError:
			# Re-raise validation errors
			raise
		except ImportError:
			# If LoanService is not available, skip validation
			pass
		except Exception as e:
			# Log error but allow validation to continue
			import logging
			logger = logging.getLogger(__name__)
			logger.error(f"Error checking loans for user {user_id} during reservation: {e}")
		
		# Generate ID if needed
		if not reservation_id:
			reservation_id = self._generate_next_id()
		
		# Ensure uniqueness
		existing = {r.get_reservation_id() for r in self.reservations}
		if reservation_id in existing:
			# append suffix to disambiguate
			counter = 1
			base = reservation_id
			while reservation_id in existing:
				reservation_id = f"{base}-{counter}"
				counter += 1

		# Create reservation and add to list (maintains FIFO order)
		res = Reservation(reservation_id, user_id, isbn)
		self.reservations.append(res)
		self._save_reservations()
		return res

	def get_all_reservations(self) -> List[Reservation]:
		"""Return a shallow copy list of all reservations.

		Returns
		-------
		List[Reservation]
			All Reservation objects currently loaded in memory.
		"""
		return list(self.reservations)

	def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
		"""Find a reservation by its unique identifier.

		Parameters
		----------
		reservation_id : str
			Reservation identifier to search for.

		Returns
		-------
		Optional[Reservation]
			The Reservation if found, otherwise None.
		"""
		return next((r for r in self.reservations if r.get_reservation_id() == reservation_id), None)

	def find_by_isbn(self, isbn: str, only_pending: bool = True) -> List[Reservation]:
		"""Find reservations for a specific ISBN.
		
		Args:
			isbn: ISBN to search for
			only_pending: If True, return only pending reservations (default)
			
		Returns:
			List[Reservation]: Reservations in FIFO order (insertion order preserved)
		"""
		res = [r for r in self.reservations if r.get_isbn() == isbn]
		if only_pending:
			res = [r for r in res if r.get_status() == 'pending']
		# preserve insertion order (queue semantics)
		return res

	def assign_next_for_isbn(self, isbn: str) -> Optional[Reservation]:
		"""Assign the earliest pending reservation for the ISBN using FIFO queue logic.
		
		This method implements the Queue (FIFO) structure requirement:
		- Gets all pending reservations for the ISBN
		- Assigns the FIRST one (First In, First Out)
		- Updates status to 'assigned' and sets assigned_date
		
		Args:
			isbn: ISBN of the book being assigned
			
		Returns:
			Optional[Reservation]: Assigned reservation or None if no pending reservations
		"""
		# Get pending reservations in FIFO order
		pending = self.find_by_isbn(isbn, only_pending=True)
		if not pending:
			return None
		
		# FIFO: Assign the first (earliest) reservation in the queue
		next_res = pending[0]
		next_res.set_status('assigned')
		next_res.set_assigned_date(datetime.utcnow())
		self._save_reservations()
		return next_res
	
	def get_queue_position(self, user_id: str, isbn: str) -> Optional[int]:
		"""Get the position of a user in the reservation queue for a specific ISBN.
		
		Args:
			user_id: User ID to check
			isbn: ISBN of the book
			
		Returns:
			Optional[int]: Position in queue (1-based) or None if not in queue
		"""
		pending = self.find_by_isbn(isbn, only_pending=True)
		for i, res in enumerate(pending, start=1):
			if res.get_user_id() == user_id:
				return i
		return None

	def cancel_reservation(self, reservation_id: str) -> None:
		"""Mark a reservation as cancelled and persist the change.

		Parameters
		----------
		reservation_id : str
			Identifier of the reservation to cancel.

		Raises
		------
		ValueError
			If no reservation exists with the provided id.
		"""
		res = self.find_by_id(reservation_id)
		if res is None:
			raise ValueError(f"No reservation found with id '{reservation_id}'")
		res.set_status('cancelled')
		self._save_reservations()

	def delete_reservation(self, reservation_id: str) -> None:
		"""Permanently remove a reservation from storage.

		Parameters
		----------
		reservation_id : str
			Identifier of the reservation to delete.

		Raises
		------
		ValueError
			If the reservation cannot be found.
		"""
		res = self.find_by_id(reservation_id)
		if res is None:
			raise ValueError(f"No reservation found with id '{reservation_id}'")
		self.reservations = [r for r in self.reservations if r.get_reservation_id() != reservation_id]
		self._save_reservations()

	def update_reservation(self, reservation_id: str, **kwargs) -> Reservation:
		"""Update reservation fields: user_id, isbn, status. Returns updated Reservation."""
		res = self.find_by_id(reservation_id)
		if res is None:
			raise ValueError(f"No reservation found with id '{reservation_id}'")
		if 'user_id' in kwargs:
			res.set_user_id(kwargs.get('user_id'))
		if 'isbn' in kwargs:
			res.set_isbn(kwargs.get('isbn'))
		if 'status' in kwargs:
			res.set_status(kwargs.get('status'))
		if 'assigned_date' in kwargs:
			assigned_val = kwargs.get('assigned_date')
			# Convert ISO string to datetime object if needed
			if assigned_val and isinstance(assigned_val, str):
				try:
					from datetime import datetime as _dt
					assigned_val = _dt.fromisoformat(assigned_val)
				except Exception:
					pass
			res.set_assigned_date(assigned_val)
		self._save_reservations()
		return res


__all__ = ["ReservationService"]
