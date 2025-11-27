import os
import json
from typing import List, Optional, Dict, Any

from models.user import User

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
	"""Service for managing simple User catalog and persistence.

	- Uses a single JSON file: `./data/users.json` storing a list of flattened users: {'id','name'}.
	- Keeps two in-memory lists:
		`users_general`: insertion-order list loaded from JSON.
		`users_sorted`: list ordered by `name` (built using external insertion_sort_users).

	Algorithms are imported from `utils/algoritmos` but not implemented here.
	"""

	def __init__(self, json_path: Optional[str] = None):
		"""Initialize UserService and load users from JSON.

		Parameters:
		- json_path: optional path to `users.json`. If None, defaults to `./data/users.json`.

		Raises:
		- ValueError: if JSON exists but is malformed.
		- Exception: for IO errors.
		"""
		if json_path:
			self.json_path = os.path.abspath(json_path)
		else:
			base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
			self.json_path = os.path.join(base, 'data', 'users.json')

		self.users_general: List[User] = []
		self.users_sorted: List[User] = []

		self._ensure_file()
		self._load_from_file()

	# -------------------- File handling --------------------
	def _ensure_file(self) -> None:
		"""Ensure `users.json` exists; create it with an empty list if missing.

		Raises:
		- Exception: if directory or file cannot be created.
		"""
		directory = os.path.dirname(self.json_path)
		if not os.path.isdir(directory):
			os.makedirs(directory, exist_ok=True)
		if not os.path.exists(self.json_path):
			try:
				with open(self.json_path, 'w', encoding='utf-8') as f:
					json.dump([], f, ensure_ascii=False, indent=2)
			except Exception as e:
				raise Exception(f"Unable to create users JSON file: {e}")

	def _load_from_file(self) -> None:
		"""Load users from `users.json` into `self.users_general` and build `users_sorted`.

		Expected format: JSON list of objects with keys ['id','name'].

		Raises:
		- ValueError: if JSON is malformed or entries missing required fields.
		- Exception: for IO errors.
		"""
		try:
			with open(self.json_path, 'r', encoding='utf-8') as f:
				data = json.load(f)
		except json.JSONDecodeError as e:
			raise ValueError(f"users.json contains invalid JSON: {e}")
		except Exception as e:
			raise Exception(f"Unable to read users JSON file: {e}")

		if not isinstance(data, list):
			raise ValueError("users.json must contain a JSON list of user objects")

		loaded: List[User] = []
		for idx, item in enumerate(data):
			if not isinstance(item, dict):
				raise ValueError(f"Invalid user entry at index {idx}: expected object/dict")
			for key in ('id', 'name'):
				if key not in item:
					raise ValueError(f"Missing '{key}' in user entry at index {idx}")
			try:
				user = User(item['id'], item['name'])
			except Exception as e:
				raise ValueError(f"Invalid data types in user entry at index {idx}: {e}")
			loaded.append(user)

		self.users_general = loaded

		# Build sorted list using external insertion sort when available
		# Keep a sorted view by name using builtin sort
		self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())

	def _save_to_file(self) -> None:
		"""Persist `self.users_general` to `users.json` in flattened format.

		Raises:
		- Exception: for IO errors while writing.
		"""
		data = []
		for u in self.users_general:
			data.append({'id': u.get_id(), 'name': u.get_name()})

		try:
			with open(self.json_path, 'w', encoding='utf-8') as f:
				json.dump(data, f, ensure_ascii=False, indent=2)
		except Exception as e:
			raise Exception(f"Unable to write users JSON file: {e}")

	# -------------------- CRUD --------------------
	def add_user(self, user: User) -> None:
		"""Add a new User to the catalog and persist.

		Parameters:
		- user: User instance to add.

		Returns: None

		Raises:
		- ValueError: if a user with the same `id` already exists.
		- ImportError: if `insertion_sort_users` is not available when attempting to order.
		- Exception: for IO errors.
		"""
		if any(u.get_id() == user.get_id() for u in self.users_general):
			raise ValueError(f"A user with id '{user.get_id()}' already exists")

		self.users_general.append(user)

		# Update sorted list view using builtin sort
		self.users_sorted = sorted(self.users_general, key=lambda u: u.get_name())


		self._save_to_file()

	def create_user(self, name: str) -> User:
		"""Create a new user with an auto-generated unique ID and persist it.

		ID generation strategy:
		- Prefer IDs of the form 'U###' where ### is a zero-padded integer.
		- Find existing IDs that match 'U' followed by digits, take the max numeric
		  suffix and increment. If none found, start at 1 (U001).
		- Ensure the generated ID does not collide with any existing id; if it does
		  (unlikely), append a suffix '-1', '-2', ... until unique.
		"""
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
		user = UserModel(new_id, name)
		self.add_user(user)
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

		self._save_to_file()

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

		self._save_to_file()


# Example:
# svc = UserService()
# svc.add_user(User('u1','Alice'))
# print([u.get_name() for u in svc.get_all_users()])

