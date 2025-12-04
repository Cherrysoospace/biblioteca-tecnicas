# Project Structure - Library Management System

```
biblioteca-tecnicas/
│
├── main.py
├── requirements.txt
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── install.txt
│
├── models/
│   ├── Books.py
│   ├── user.py
│   ├── loan.py
│   ├── reservation.py
│   ├── shelf.py
│   └── inventory.py
│
├── repositories/
│   ├── base_repository.py
│   ├── book_repository.py
│   ├── user_repository.py
│   ├── loan_repository.py
│   ├── loan_history_repository.py
│   ├── reservation_repository.py
│   ├── shelf_repository.py
│   └── inventory_repository.py
│
├── services/
│   ├── book_service.py
│   ├── user_service.py
│   ├── loan_service.py
│   ├── reservation_service.py
│   ├── shelf_service.py
│   ├── inventory_service.py
│   └── report_service.py
│
├── controllers/
│   ├── book_controller.py
│   ├── user_controller.py
│   ├── loan_controller.py
│   ├── reservation_controller.py
│   └── shelf_controller.py
│
├── ui/
│   ├── main_menu.py
│   ├── theme.py
│   ├── widget_factory.py
│   │
│   ├── assets/
│   │   ├── backgrounds/
│   │   └── twemoji/
│   │
│   ├── book/
│   │   ├── book_list.py
│   │   ├── book_form.py
│   │   ├── book_search.py
│   │   ├── author_value_report.py
│   │   ├── author_weight_report.py
│   │   ├── backtracking_report.py
│   │   └── brute_force_report.py
│   │
│   ├── user/
│   │   ├── user_list.py
│   │   └── user_form.py
│   │
│   ├── loan/
│   │   ├── loan_list.py
│   │   ├── loan_form.py
│   │   ├── loan_edit.py
│   │   ├── loan_search.py
│   │   └── loan_history.py
│   │
│   ├── reservation/
│   │   ├── reservation_list.py
│   │   ├── reservation_form.py
│   │   └── reservation_edit.py
│   │
│   └── shelf/
│       ├── shelf_list.py
│       ├── shelf_form.py
│       ├── shelf_edit.py
│       └── assign_book_form.py
│
├── utils/
│   ├── config.py
│   ├── file_handler.py
│   ├── logger.py
│   ├── validators.py
│   ├── search_helpers.py
│   ├── report_helpers.py
│   │
│   ├── algorithms/
│   │   ├── AlgoritmosOrdenamiento.py
│   │   ├── AlgoritmosBusqueda.py
│   │   ├── AlgoritmosSinComentarios.py
│   │   ├── backtracking.py
│   │   └── brute_force.py
│   │
│   ├── recursion/
│   │   ├── stack_recursion.py
│   │   └── queue_recursion.py
│   │
│   ├── structures/
│   │   ├── stack.py
│   │   └── queue.py
│   │
│   └── validators/
│       ├── __init__.py
│       ├── exceptions.py
│       ├── book_validator.py
│       ├── user_validator.py
│       ├── loan_validator.py
│       ├── reservation_validator.py
│       └── shelf_validator.py
│
├── data/
│   ├── books.json
│   ├── users.json
│   ├── shelves.json
│   ├── loan.json
│   ├── loan_history.json
│   ├── reservations.json
│   ├── inventory_general.json
│   ├── inventory_sorted.json
│   └── inventory_value.json
│
└── logs/
```
