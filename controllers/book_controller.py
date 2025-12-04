from services.book_service import BookService
from services.inventory_service import InventoryService
from services.report_service import ReportService
from models.Books import Book
from utils.logger import LibraryLogger

# Configurar logger
logger = LibraryLogger.get_logger(__name__)

class BookController:
    """Controller for book-related actions.

    This class coordinates requests from the UI or API layer and delegates
    operations to service classes such as BookService, InventoryService and
    ReportService. It handles creation, update, deletion, retrieval and
    higher-level operations like algorithmic searches and reporting triggers.

    Responsibilities:
        - Validate/prepare data when necessary before calling services.
        - Keep global reports in sync after catalog changes (best-effort).
        - Expose search and algorithmic features implemented in services.
    """
    def __init__(self):
        self.service = BookService()
        self.report_service = ReportService()

    def create_book(self, data):
        """Create a new book and update related systems.

        The `data` argument is expected to be a dictionary with at least the
        following keys: 'ISBNCode', 'title', 'author', 'weight', 'price'. The
        'id' key is optional; if missing or empty the controller will attempt
        to generate one via the service or fallback to a timestamp-based id.

        After creating the Book object and persisting it via BookService, the
        controller will attempt to add an inventory record (one physical copy)
        and generate an updated inventory value report (best-effort).

        Parameters:
            data (dict): book fields for creation.

        Returns:
            The identifier (id) of the created book.
        """
        # If caller did not provide an id (or provided an empty one), generate
        # the next chronological id from the service.
        if not data.get("id"):
            try:
                data["id"] = self.service.generate_next_id()
            except Exception:
                # If generation fails for any reason, fall back to a simple
                # timestamp-based id to avoid blocking creation.
                import time

                data["id"] = f"B{int(time.time())}"

        book = Book(
            data["id"],
            data["ISBNCode"],
            data["title"],
            data["author"],
            float(data["weight"]),
            int(data["price"]),
            # stock is managed by Inventory; do not pass it to Book
            bool(data.get("isBorrowed", False))
        )
        # Persist book in catalog
        self.service.add_book(book)

        # Ensure inventory is updated: always add a new inventory entry for the
        # created Book (each physical copy has its own inventory record). The
        # persistence layer will still write a single 'stock' key per ISBN.
        try:
            inv_svc = InventoryService()
            try:
                inv_svc.add_item(book, 1)
            except Exception:
                # If add_item fails (e.g., duplicate id), don't block book creation.
                pass
        except Exception:
            # Do not block book creation if inventory update fails; surface
            # errors elsewhere or log if desired.
            pass
        
        # Actualizar reporte global después de crear el libro
        try:
            self.report_service.generate_inventory_value_report()
            logger.info(f"Reporte global actualizado después de crear libro {book.get_id()}")
        except Exception as e:
            logger.warning(f"No se pudo actualizar el reporte global: {e}")
        
        return book.get_id()

    def update_book(self, book_id, data):
        """Update an existing book's data.

        Delegates to BookService to perform the update. After a successful
        update, the method attempts to regenerate the global inventory value
        report (best-effort). Exceptions from report generation are logged but
        do not propagate to the caller.

        Parameters:
            book_id: identifier of the book to update.
            data (dict): fields to update on the book.

        Returns:
            None
        """
        self.service.update_book(book_id, data)
        
        # Update global report after modifying the book (best-effort)
        try:
            self.report_service.generate_inventory_value_report()
            logger.info(f"Global report updated after modifying book {book_id}")
        except Exception as e:
            logger.warning(f"Failed to update global report: {e}")

    def delete_book(self, book_id):
        """Delete a book from the catalog.

        This method removes the book via BookService and attempts to regenerate
        the global inventory value report. Report generation failures are
        logged and not raised to callers.

        Parameters:
            book_id: identifier of the book to delete.

        Returns:
            None
        """
        self.service.delete_book(book_id)
        
        # Update global report after deleting the book (best-effort)
        try:
            self.report_service.generate_inventory_value_report()
            logger.info(f"Global report updated after deleting book {book_id}")
        except Exception as e:
            logger.warning(f"Failed to update global report: {e}")
    
    def get_book(self, book_id):
        """Retrieve a book by its identifier.

        Parameters:
            book_id: identifier of the book to retrieve.

        Returns:
            Book instance if found, otherwise implementation-specific (e.g., None or raises).
        """
        return self.service.find_by_id(book_id)

    def get_all_books(self):
        """Return list of all Book objects from the service."""
        return self.service.get_all_books()

    def calculate_total_value_by_author(self, author: str):
        """Calculate total monetary value of all books by a given author.
        
        Uses stack-style recursion to compute the sum.
        
        Parameters:
        - author: string with the author name
        
        Returns:
        - total value (float or int)
        """
        return self.service.calculate_total_value_by_author(author)
    
    def get_all_authors(self):
        """Get list of all unique authors in the catalog.
        
        Returns:
        - List[str] of author names, sorted alphabetically
        """
        return self.service.get_all_authors()

    def calculate_average_weight_by_author(self, author: str, debug: bool = False):
        """Calculate average weight of all books by a given author.
        
        Uses tail-style (queue) recursion to compute the average.
        
        Parameters:
        - author: string with the author name
        - debug: if True, prints recursion flow to console
        
        Returns:
        - average weight (float) in kg
        """
        return self.service.calculate_average_weight_by_author(author, debug)

    # -------------------- Brute Force Algorithm --------------------

    def find_risky_book_combinations(self, threshold: float = 8.0):
        """Find all combinations of 4 books that exceed weight threshold.

        This exposes the brute force algorithm through the controller layer.
        The algorithm exhaustively searches all possible combinations of 4 books
        from the catalog to identify risky shelf configurations.

        Args:
            threshold: Maximum weight threshold in Kg (default 8.0 - shelf capacity).

        Returns:
            List of dictionaries containing risky combinations.
        """
        return self.service.find_risky_book_combinations(threshold)

    def count_possible_combinations(self) -> int:
        """Get the total number of 4-book combinations that will be explored.

        Helper method to understand the scale of the brute force search.

        Returns:
            Total number of combinations the algorithm will check.
        """
        return self.service.count_possible_combinations()

    # -------------------- Search Methods (Linear Search Algorithm) --------------------

    def search_books_by_title(self, query: str):
        """Search books by title using linear search algorithm.
        
        This method delegates to InventoryService which implements recursive
        linear search to find books matching the given title query.
        
        Parameters:
        - query: string to search for in book titles (partial match, case-insensitive)
        
        Returns:
        - List of Inventory objects containing matching books
        """
        inv_service = InventoryService()
        return inv_service.find_by_title(query)

    def search_books_by_author(self, query: str):
        """Search books by author using linear search algorithm.
        
        This method delegates to InventoryService which implements recursive
        linear search to find books by the given author.
        
        Parameters:
        - query: string to search for in author names (partial match, case-insensitive)
        
        Returns:
        - List of Inventory objects containing matching books
        """
        inv_service = InventoryService()
        return inv_service.find_by_author(query)

    # -------------------- Backtracking Algorithm --------------------

    def find_optimal_shelf_selection(self, max_capacity: float = 8.0):
        """Find the optimal combination of books that maximizes value without exceeding weight capacity.

        This exposes the backtracking algorithm through the controller layer.
        The algorithm uses backtracking to solve the knapsack problem: finding
        the combination of books from the catalog that maximizes total value (COP)
        without exceeding the maximum shelf weight capacity.

        Args:
            max_capacity: Maximum weight capacity in Kg (default 8.0 - shelf capacity).

        Returns:
            Dictionary containing the optimal solution with max_value, total_weight,
            selected books, and their indices.
        """
        return self.service.find_optimal_shelf_selection(max_capacity)
