import os
import json
from datetime import datetime
from typing import List, Optional

from models.reservation import Reservation


class ReservationService:
	"""Service to manage reservations.

	Responsibilities:
	- Persist reservations to `data/reservations.json` as a list of dicts
	- Create, list, find, update, cancel, assign reservations
	- Treat the stored list order as the FIFO queue for pending reservations
	"""

	def __init__(self, json_path: Optional[str] = None):
		base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
		if json_path:
			self.json_path = os.path.abspath(json_path)
		else:
			self.json_path = os.path.join(base, 'data', 'reservations.json')

		self.reservations: List[Reservation] = []

		self._ensure_file()
		self._load_from_file()

	def _ensure_file(self) -> None:
		directory = os.path.dirname(self.json_path)
		if not os.path.isdir(directory):
			os.makedirs(directory, exist_ok=True)
		if not os.path.exists(self.json_path):
			try:
				with open(self.json_path, 'w', encoding='utf-8') as f:
					json.dump([], f, ensure_ascii=False, indent=2)
			except Exception as e:
				raise Exception(f"Unable to create reservations JSON file: {e}")

	def _load_from_file(self) -> None:
		try:
			with open(self.json_path, 'r', encoding='utf-8') as f:
				data = json.load(f)
		except json.JSONDecodeError:
			data = []
		except Exception as e:
			raise Exception(f"Unable to read reservations JSON file: {e}")

		loaded: List[Reservation] = []
		if isinstance(data, list):
			for item in data:
				if not isinstance(item, dict):
					continue
				try:
					# prefer using from_dict if available
					try:
						r = Reservation.from_dict(item)
					except Exception:
						# fallback: construct with raw fields
						r = Reservation(item.get('reservation_id'), item.get('user_id'), item.get('isbn'), item.get('reserved_date'), item.get('status', 'pending'))
					# restore assigned_date/position if present
					if 'assigned_date' in item and item.get('assigned_date'):
						try:
							from datetime import datetime as _dt
							r.set_assigned_date(_dt.fromisoformat(item.get('assigned_date')))
						except Exception:
							r.set_assigned_date(item.get('assigned_date'))
					if 'position' in item:
						r.set_position(item.get('position'))
					loaded.append(r)
				except Exception:
					continue

		self.reservations = loaded

	def _save_to_file(self) -> None:
		data = [r.to_dict() for r in self.reservations]
		try:
			with open(self.json_path, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
		except Exception as e:
			raise Exception(f"Unable to write reservations JSON file: {e}")

	# -------------------- CRUD / Actions --------------------
	def _generate_next_id(self) -> str:
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
		"""Create a reservation. If reservation_id None, generate one."""
		if not reservation_id:
			reservation_id = self._generate_next_id()
		# ensure uniqueness
		existing = {r.get_reservation_id() for r in self.reservations}
		if reservation_id in existing:
			# append suffix to disambiguate
			counter = 1
			base = reservation_id
			while reservation_id in existing:
				reservation_id = f"{base}-{counter}"
				counter += 1

		res = Reservation(reservation_id, user_id, isbn)
		self.reservations.append(res)
		self._save_to_file()
		return res

	def get_all_reservations(self) -> List[Reservation]:
		return list(self.reservations)

	def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
		return next((r for r in self.reservations if r.get_reservation_id() == reservation_id), None)

	def find_by_isbn(self, isbn: str, only_pending: bool = True) -> List[Reservation]:
		res = [r for r in self.reservations if r.get_isbn() == isbn]
		if only_pending:
			res = [r for r in res if r.get_status() == 'pending']
		# preserve insertion order (queue semantics)
		return res

	def assign_next_for_isbn(self, isbn: str) -> Optional[Reservation]:
		"""Assign the earliest pending reservation for the ISBN.

		Sets status='assigned' and assigned_date. Returns the Reservation or None.
		"""
		pending = self.find_by_isbn(isbn, only_pending=True)
		if not pending:
			return None
		next_res = pending[0]
		next_res.set_status('assigned')
		next_res.set_assigned_date(datetime.utcnow())
		# update positions for queue convenience
		self._recompute_positions_for_isbn(isbn)
		self._save_to_file()
		return next_res

	def _recompute_positions_for_isbn(self, isbn: str) -> None:
		# set position as 1-based index among pending reservations for the isbn
		pending = [r for r in self.reservations if r.get_isbn() == isbn and r.get_status() == 'pending']
		for idx, r in enumerate(pending, start=1):
			r.set_position(idx)

	def cancel_reservation(self, reservation_id: str) -> None:
		res = self.find_by_id(reservation_id)
		if res is None:
			raise ValueError(f"No reservation found with id '{reservation_id}'")
		res.set_status('cancelled')
		self._recompute_positions_for_isbn(res.get_isbn())
		self._save_to_file()

	def delete_reservation(self, reservation_id: str) -> None:
		res = self.find_by_id(reservation_id)
		if res is None:
			raise ValueError(f"No reservation found with id '{reservation_id}'")
		self.reservations = [r for r in self.reservations if r.get_reservation_id() != reservation_id]
		self._recompute_positions_for_isbn(res.get_isbn())
		self._save_to_file()

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
			res.set_assigned_date(kwargs.get('assigned_date'))
		self._recompute_positions_for_isbn(res.get_isbn())
		self._save_to_file()
		return res


__all__ = ["ReservationService"]
