import os
import json
from typing import List, Optional, Dict, Any

from models.user import User
from repositories.user_repository import UserRepository
from utils.validators import UserValidator, ValidationError
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)

# Attempt to import algorithms. If not available, set to None and raise ImportError when used.
# The project should not rely on a custom insertion sort here; use Python's built-in sorted().
insertion_sort_users = None

try:
	from utils.algoritmos.busqueda_lineal import buscar_lineal
except Exception:
	buscar_lineal = None

try:
	from utils.algoritmos.busqueda_binaria import buscar_binario
except Exception:
	buscar_binario = None


class UserService:
	"""Service for managing simple User catalog.

	Responsibilities:
	- BUSINESS LOGIC ONLY: ID generation, validation, sorting
	- Persistence delegated to UserRepository (SRP compliance)

	- Keeps two in-memory lists:
		`users_general`: insertion-order list loaded from JSON.
		`users_sorted`: list ordered by `name` (built using external insertion_sort_users).

	Algorithms are imported from `utils/algoritmos` but not implemented here.
	"""

	def __init__(self, repository: UserRepository = None):
		"""Initialize UserService with a repository.

		Parameters:
		- repository: optional UserRepository instance. If None, creates a new one.

		Raises:
		- ValueError: if JSON exists but is malformed.
		- Exception: for IO errors.
		"""
		self.repository = repository or UserRepository()

		self.users_general: List[User] = []
		self.users_sorted: List[User] = []

		self._load_users()

	# -------------------- Persistence (delegated to repository) --------------------
	def _load_users(self) -> None:
		"""Load users from repository and build sorted view.

		Raises:
		- ValueError: if data is malformed
		- Exception: for IO errors.
		"""
		self.users_general = self.repository.load_all()

		# Build sorted list using builtin sort
		self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

	def _save_users(self) -> None:
		"""Persist users using repository.

		Raises:
		- Exception: for IO errors while writing.
		"""
		self.repository.save_all(self.users_general)

	# -------------------- CRUD --------------------
	def add_user(self, user: User) -> None:
		"""Add a new User to the catalog and persist.

		Parameters:
		- user: User instance to add.

		Returns: None

		Raises:
		- ValidationError: if user data is invalid (name empty)
		- ValueError: if a user with the same `id` already exists.
		- ImportError: if `insertion_sort_users` is not available when attempting to order.
		- Exception: for IO errors.
		"""
		# Validar datos del usuario ANTES de agregar
		try:
			UserValidator.validate_name(user.get_name())
			UserValidator.validate_id(user.get_id())
		except ValidationError as e:
			logger.error(f"Validación fallida al agregar usuario: {e}")
			raise
		
		if any(u.get_id() == user.get_id() for u in self.users_general):
			raise ValueError(f"A user with id '{user.get_id()}' already exists")

		self.users_general.append(user)

		# Update sorted list view using builtin sort
		self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

		self._save_users()
		logger.info(f"Usuario agregado: id={user.get_id()}, nombre={user.get_name()}")

	def create_user(self, name: str) -> User:
		"""Create a new user with an auto-generated unique ID and persist it.

		ID generation strategy:
		- Prefer IDs of the form 'U###' where ### is a zero-padded integer.
		- Find existing IDs that match 'U' followed by digits, take the max numeric
		  suffix and increment. If none found, start at 1 (U001).
		- Ensure the generated ID does not collide with any existing id; if it does
		  (unlikely), append a suffix '-1', '-2', ... until unique.
		  
		Raises:
		- ValidationError: if name is empty or invalid
		"""
		# VALIDAR nombre ANTES de crear usuario
		try:
			name_clean = UserValidator.validate_name(name)
		except ValidationError as e:
			logger.error(f"Validación fallida al crear usuario: {e}")
			raise
		
		# collect existing ids
		existing_ids = {u.get_id() for u in self.users_general}
		# find numeric suffixes for IDs like U123
		max_n = 0
		for uid in existing_ids:
			if isinstance(uid, str) and uid.startswith('U'):
				num_part = uid[1:]
				if num_part.isdigit():
					try:
						val = int(num_part)
						if val > max_n:
							max_n = val
					except Exception:
						pass

		base_num = max_n + 1
		new_id = f"U{base_num:03d}"
		# ensure uniqueness
		counter = 1
		while new_id in existing_ids:
			new_id = f"U{base_num:03d}-{counter}"
			counter += 1

		from models.user import User as UserModel
		user = UserModel(new_id, name_clean)  # Usar nombre validado
		self.add_user(user)
		logger.info(f"Usuario creado: id={new_id}, nombre={name_clean}")
		return user

	def get_all_users(self) -> List[User]:
		"""Return all users in insertion order.

		Returns:
		- List[User]
		"""
		return list(self.users_general)

	def find_by_id(self, id: str) -> Optional[User]:
		"""Find a user by unique id using linear scan.

		Parameters:
		- id: str

		Returns:
		- User if found, else None
		"""
		for u in self.users_general:
			if u.get_id() == id:
				return u
		return None

	def find_by_name(self, name: str) -> List[User]:
		"""Find users matching `name` using external search algorithms.

		Prefers `buscar_lineal` on the general list. If `buscar_lineal` is None
		and `buscar_binario` exists, uses binary search on `users_sorted`.

		Parameters:
		- name: str

		Returns:
		- List[User] matching the name (may be empty)

		Raises:
		- ImportError: if neither `buscar_lineal` nor `buscar_binario` are available.
		"""
		if buscar_lineal is not None:
			try:
				result = buscar_lineal(self.users_general, name, lambda u: u.get_name())
			except TypeError:
				result = buscar_lineal(self.users_general, name)
		elif buscar_binario is not None:
			try:
				result = buscar_binario(self.users_sorted, name, lambda u: u.get_name())
			except TypeError:
				result = buscar_binario(self.users_sorted, name)
		else:
			raise ImportError('Required search algorithms (buscar_lineal or buscar_binario) not available')

		if result is None:
			return []
		if isinstance(result, list):
			return result
		return [result]

	def update_user(self, id: str, new_data: Dict[str, Any]) -> None:
		"""Update an existing user's fields and keep lists consistent.

		Only keys present in `new_data` are updated. Allowed keys: 'id','name'.

		Parameters:
		- id: str
		- new_data: dict

		Returns: None

		Raises:
		- ValueError: if user not found or updating id would create a duplicate.
		- ImportError: if `insertion_sort_users` is not available for reordering.
		- Exception: for IO errors while persisting.
		"""
		user = self.find_by_id(id)
		if user is None:
			raise ValueError(f"No user found with id '{id}'")

		if 'id' in new_data:
			new_id = new_data['id']
			if new_id != id and any(u.get_id() == new_id for u in self.users_general):
				raise ValueError(f"Cannot update id: another user with id '{new_id}' already exists")

		if 'id' in new_data:
			user.set_id(new_data['id'])
		if 'name' in new_data:
			user.set_name(new_data['name'])

		# Rebuild the sorted view after update using builtin sort
		self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

		self._save_users()

	def delete_user(self, id: str) -> None:
		"""Delete a user by id from both lists and persist.

		Parameters:
		- id: str

		Returns: None

		Raises:
		- ValueError: if user not found.
		- Exception: for IO errors while persisting.
		"""
		user = self.find_by_id(id)
		if user is None:
			raise ValueError(f"No user found with id '{id}'")

		self.users_general = [u for u in self.users_general if u.get_id() != id]
		self.users_sorted = [u for u in self.users_sorted if u.get_id() != id]

		self._save_users()


# Example:
# svc = UserService()
# svc.add_user(User('u1','Alice'))
# print([u.get_name() for u in svc.get_all_users()])

