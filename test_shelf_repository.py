import json
from pathlib import Path
from repositories.shelf_repository import ShelfRepository
from models.shelf import Shelf
from models.Books import Book
from utils.file_handler import JSONFileHandler


def test_shelf_repository_roundtrip(tmp_path):
    """Save a shelf via the repository and load it back."""
    file_path = tmp_path / "shelves.json"
    repo = ShelfRepository(str(file_path))

    # initially empty
    loaded = repo.load_all()
    assert isinstance(loaded, list)
    assert len(loaded) == 0

    # create shelf with one book
    book = Book('B001', '978-1', 'Title', 'Author', 0.5, 100, False)
    shelf = Shelf('S1', books=[book], capacity=5.0)

    repo.save_all([shelf])

    # load back
    items = repo.load_all()
    assert len(items) == 1
    s = items[0]
    assert getattr(s, '_Shelf__id', None) == 'S1'
    assert s.capacity == 5.0
    books = getattr(s, '_Shelf__books')
    assert len(books) == 1
    assert books[0].get_id() == 'B001'
    assert books[0].get_title() == 'Title'


def test_shelf_repository_handles_malformed_books(tmp_path):
    """Repository should tolerate malformed book entries inside shelf JSON."""
    file_path = tmp_path / "shelves.json"

    # craft a JSON payload with a shelf that contains valid and invalid book entries
    payload = [
        {
            'id': 'S2',
            'capacity': 8.0,
            'books': [
                {
                    'id': 'B10',
                    'ISBNCode': '978-2',
                    'title': 'Good Book',
                    'author': 'Author X',
                    'weight': 0.7,
                    'price': 50,
                    'isBorrowed': False
                },
                'not-a-dict',
                123,
                {'bad': 'entry'}
            ]
        }
    ]

    # write raw JSON
    JSONFileHandler.ensure_file(str(file_path), default_content=[])
    JSONFileHandler.save_json(str(file_path), payload)

    repo = ShelfRepository(str(file_path))
    items = repo.load_all()

    # should load one shelf and only include the valid book
    assert len(items) == 1
    s = items[0]
    books = getattr(s, '_Shelf__books')
    assert len(books) == 1
    assert books[0].get_id() == 'B10'
    assert books[0].get_title() == 'Good Book'
