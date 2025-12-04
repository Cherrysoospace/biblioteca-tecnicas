"""Book Search Window - Linear Search Algorithm Demonstration.

This module implements an interactive search interface for finding books using
recursive linear search algorithm. It demonstrates the linear search requirement
from the project specifications while providing practical book discovery functionality.

Project Requirement:
    Implements recursive linear search for book catalog searching with
    case-insensitive, accent-insensitive partial matching capabilities.

Algorithm - Recursive Linear Search:
    The search uses recursive linear search (implemented in controller) that:
    - Processes one inventory item at a time
    - Recursively delegates remainder to next call
    - Base case: index >= list length
    - Returns accumulated matches
    
    Pseudocode:
    ```
    def linear_search(items, query, field, index=0, results=[]):
        if index >= len(items):              # Base case
            return results
        
        if query.lower() in items[index].field.lower():
            results.append(items[index])
        
        return linear_search(items, query, field, index+1, results)
    ```
    
    Complexity: O(n) time, O(n) space (recursion stack)

Search Features:
    1. Dual Search Modes:
       - By Title: Searches book titles
       - By Author: Searches author names
    
    2. Intelligent Matching:
       - Case-insensitive: "GATSBY" matches "gatsby"
       - Accent-insensitive: "café" matches "cafe"
       - Partial matching: "Great" matches "The Great Gatsby"
       - Substring search: Works with any part of field
    
    3. Search Triggers:
       - Primary button: "🔍 Buscar" click
       - Keyboard: Enter key in search field
    
    4. Result Display:
       - Treeview table with 5 columns
       - Result count indicator
       - Success/error feedback messages
       - Empty state handling

UI Components:
    1. Header:
       - Title: "🔍 Búsqueda de Libros" (factory-created)
    
    2. Search Controls Frame:
       - Radio buttons: Title/Author selection
       - Search entry field with placeholder
       - Primary search button
       - Small clear button
    
    3. Info/Results Labels:
       - Info label: Search tips and status messages
       - Results label: Count of found books
    
    4. Results Table:
       - 5 columns: ISBN, Title, Author, Price, Stock
       - Vertical and horizontal scrollbars
       - Themed styling matching application
       - Row height 28px for comfortable reading
    
    5. Bottom Controls:
       - Close button: Dismisses window

Table Configuration:
    Column Specifications:
    ```
    Column    Width    Alignment   Heading
    ------    -----    ---------   -------
    isbn      150px    left        "ISBN"
    title     300px    left        "Título"
    author    200px    left        "Autor"
    price     100px    left        "Precio (COP)"
    stock     80px     left        "Stock"
    ```

Styling Strategy:
    Treeview Customization:
    - Theme: 'clam' (modern, customizable)
    - Row font: 10pt normal (from theme)
    - Heading font: 11pt bold (from theme)
    - Row height: 28px (comfortable spacing)
    - Background: theme.BG_COLOR (warm beige)
    - Heading background: theme.BORDER_COLOR (black)
    - Heading text: theme.BG_COLOR (beige on black)
    - Selection: theme.BUTTON_HOVER (deep red)

Data Flow:
    Search Execution:
    ```
    User enters query "Gatsby" and selects "Title"
    → perform_search() called
    → controller.search_books_by_title("Gatsby")
    → Linear search algorithm processes inventory
    → Returns list of matching InventoryGeneral objects
    → Populate table with book details from inventory
    → Update result count and status message
    ```

Search Types:
    Title Search:
    - Calls: controller.search_books_by_title(query)
    - Searches: Book.title field
    - Example: "Great" finds "The Great Gatsby"
    
    Author Search:
    - Calls: controller.search_books_by_author(query)
    - Searches: Book.author field
    - Example: "Fitzgerald" finds "F. Scott Fitzgerald"

Result Data:
    Returns InventoryGeneral objects containing:
    - Book reference: Full Book object with all details
    - Stock count: Available quantity
    - ISBN: From book.get_ISBNCode()
    - Title: From book.get_title()
    - Author: From book.get_author()
    - Price: From book.get_price()

Feedback Messages:
    Success States:
    - "✅ Búsqueda completada usando algoritmo de búsqueda lineal recursiva"
    - "📊 {n} resultado(s) encontrado(s)"
    
    Empty States:
    - "❌ No se encontraron libros con '{query}' en {search_type}"
    
    Error States:
    - "❌ Error en la búsqueda: {error_message}"
    
    Initial/Clear State:
    - "💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales."

Keyboard Shortcuts:
    - Enter in search field: Triggers search
    - Allows quick searching without mouse

Window Management:
    - Type: CTkToplevel (popup window)
    - Transient to parent (stays on top)
    - Size: 1000x600 pixels
    - Scrollbars: Both vertical and horizontal

Validation:
    - Empty query: Shows warning dialog
    - Requires non-empty search term
    - No other field validation needed

Error Handling:
    - Search execution: Catches controller exceptions
    - Shows error dialog with exception message
    - Updates info label with error status
    - Table remains empty on error
    - Window remains functional

Clear Functionality:
    Resets to initial state:
    - Clears search entry field
    - Removes all table rows
    - Resets current_results to empty list
    - Clears results count label
    - Restores initial info message

Educational Value:
    - Demonstrates recursive linear search algorithm
    - Shows O(n) search complexity in practice
    - Compares with other search algorithms (binary search in other modules)
    - Practical application of searching concepts

Performance:
    - Time: O(n) for each search (linear scan of inventory)
    - Space: O(n) for recursion stack + results list
    - UI Update: O(m) where m = matching results

Limitations:
    - No regex support (simple substring matching)
    - No multi-field search (can't search title AND author)
    - No result sorting options
    - No export functionality
    - Manual refresh needed if data changes externally

See Also:
    - controllers.book_controller.BookController.search_books_by_title
    - controllers.book_controller.BookController.search_books_by_author
    - ui.book.book_list.BookList: Opens this window via search button

Date: 2025-12-03
"""

import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from controllers.book_controller import BookController


class BookSearch(ctk.CTkToplevel):
    """Interactive book search window using recursive linear search algorithm.
    
    This window provides a user-friendly interface for searching the book catalog
    using recursive linear search. It supports dual search modes (title/author),
    intelligent matching (case-insensitive, accent-insensitive, partial), and
    displays results in a themed Treeview table.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Table: ttk.Treeview (5 columns)
        Layout: Vertical stack (title → controls → info → table → buttons)
        Controller: BookController for search operations
        Algorithm: Recursive linear search O(n)
    
    UI Components:
        1. Title Section:
           - Title label with search icon emoji
        
        2. Search Controls Frame (styled card):
           - Radio buttons: Title/Author selection
           - Search entry field with placeholder
           - Primary search button (🔍 Buscar)
           - Small clear button
        
        3. Info/Results Row:
           - Left: Info label (tips and status)
           - Right: Results count label
        
        4. Results Table:
           - Treeview with 5 columns
           - Dual scrollbars (vertical + horizontal)
           - Themed styling
           - Row height 28px
        
        5. Bottom Bar:
           - Close button (small, right-aligned)
    
    Search Modes:
        Title Mode (search_type="title"):
        - Searches in Book.title field
        - Radio button: "Título"
        - Example: "Great" → "The Great Gatsby"
        
        Author Mode (search_type="author"):
        - Searches in Book.author field
        - Radio button: "Autor"
        - Example: "Scott" → "F. Scott Fitzgerald"
    
    Table Layout:
        ```
        ISBN              | Título                    | Autor          | Precio (COP) | Stock
        ------------------|---------------------------|----------------|--------------|------
        978-3-16-148410-0 | The Great Gatsby          | F. Scott...    | $25,000      | 5
        978-0-06-112008-4 | To Kill a Mockingbird     | Harper Lee     | $30,000      | 3
        ...
        ```
    
    Attributes:
        controller (BookController): Handles search operations
        current_results (list): List of InventoryGeneral objects from last search
        search_type (StringVar): Selected search mode ("title" or "author")
        search_entry (CTkEntry): Text input for search query
        info_label (CTkLabel): Displays status/tips messages
        results_label (CTkLabel): Displays result count
        tree (ttk.Treeview): Results table widget
        _parent_window: Reference to parent window
    
    Window Configuration:
        - Dimensions: 1000x600 pixels
        - Title: "🔍 Búsqueda de Libros"
        - Transient: Attached to parent
        - Scrollbars: Both vertical and horizontal
    
    Search Algorithm:
        Uses recursive linear search implemented in controller:
        - Time complexity: O(n) where n = inventory size
        - Space complexity: O(n) for recursion stack
        - Accumulates matches during recursive traversal
        - Base case: index >= list length
    
    Matching Strategy:
        - Case-insensitive: Converts both query and field to lowercase
        - Accent-insensitive: Normalizes accents (implementation in controller)
        - Partial matching: Uses substring search ("in" operator)
        - Example: Query "CAFE" matches "Café París"
    
    Event Bindings:
        - Enter key in search_entry: Triggers perform_search()
        - Primary button click: Triggers perform_search()
        - Clear button click: Triggers clear_search()
        - Close button click: Destroys window
    
    Styling Details:
        Radio Buttons:
        - Selected color: theme.BUTTON_HOVER (deep red)
        - Hover color: theme.BORDER_COLOR (black)
        
        Search Entry:
        - Width: 400px, Height: 36px
        - Placeholder: "Introduce título o autor (búsqueda parcial)..."
        
        Buttons:
        - Primary (search): 120x36px
        - Small (clear): 100x36px
        
        Table:
        - Row height: 28px (larger than BookList's 24px)
        - Selection color: theme.BUTTON_HOVER
    
    Result Display:
        Each row shows:
        - ISBN: Full code from book
        - Title: Full title from book
        - Author: Full author name from book
        - Price: Formatted with $ and comma separator
        - Stock: Available quantity from inventory
    
    Error Resilience:
        - Window scaling: Continues with default if fails
        - Theme application: Fallback to direct fg_color
        - Transient setup: Continues if parent None
        - Style configuration: Uses defaults if fails
        - Search execution: Shows error dialog, remains functional
    
    State Management:
        - current_results: Tracks last search results
        - Allows potential export or further operations
        - Cleared on new search or clear action
    
    See Also:
        - controllers.book_controller.BookController: Search implementation
        - ui.book.book_list.BookList: Launches this window
    """
    
    def __init__(self, parent=None):
        """Initialize the book search window with controls and results table.
        
        Creates and configures the complete search interface including search controls
        (radio buttons, entry field, buttons), themed Treeview table with scrollbars,
        and status labels. Sets up event bindings for keyboard shortcuts.
        
        Purpose:
            Provides a complete, ready-to-use book search interface with recursive
            linear search algorithm demonstration and practical book discovery.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Store parent reference
            3. Apply window scaling
            4. Apply theme
            5. Set window title and geometry (1000x600)
            6. Set transient to parent
            7. Initialize BookController
            8. Initialize current_results list
            9. Create main container frame
            10. Build title section
            11. Build search controls frame:
                - Search type radio buttons (title/author)
                - Search entry field
                - Search and clear buttons
            12. Build info/results labels row
            13. Create table holder frame (native tk.Frame)
            14. Configure Treeview style
            15. Create Treeview with 5 columns
            16. Configure column headings and widths
            17. Create and attach scrollbars (vertical + horizontal)
            18. Build bottom button frame
            19. Bind Enter key to search action
        
        Search Controls Layout:
            ```
            [Search Controls Frame - BUTTON_COLOR background]
            ┌─────────────────────────────────────────────────┐
            │ Search Type Row:                                │
            │   "Buscar por:" (○ Título) (○ Autor)           │
            ├─────────────────────────────────────────────────┤
            │ Search Input Row:                               │
            │   "Buscar:" [___entry field___] [🔍 Buscar] [Limpiar] │
            └─────────────────────────────────────────────────┘
            ```
        
        Radio Button Configuration:
            Both share single StringVar (search_type):
            - Title radio: value="title", default selected
            - Author radio: value="author"
            - Colors: fg=BUTTON_HOVER, hover=BORDER_COLOR
        
        Entry Field Setup:
            - Width: 400px (flexible with expand=True)
            - Height: 36px (matches button heights)
            - Placeholder: Long descriptive text
            - Enter key binding: Triggers search
        
        Button Sizing:
            Primary (search):
            - Width: 120px, Height: 36px
            - Prominent for emphasis
            
            Small (clear):
            - Width: 100px, Height: 36px
            - Secondary action styling
        
        Table Holder Grid Layout:
            ```
            Grid (2x2):
            ┌─────────────────┬───┐
            │                 │ V │  Row 0: Tree + Vertical scrollbar
            │   Treeview      │ S │
            │                 │ B │
            ├─────────────────┼───┤
            │   H Scrollbar   │   │  Row 1: Horizontal scrollbar
            └─────────────────┴───┘
            
            Row 0 weight=1 (expands)
            Column 0 weight=1 (expands)
            ```
        
        Scrollbar Configuration:
            Vertical:
            - Orient: vertical
            - Command: tree.yview
            - Grid: row=0, column=1, sticky="ns"
            
            Horizontal:
            - Orient: horizontal
            - Command: tree.xview
            - Grid: row=1, column=0, sticky="ew"
            
            Tree scrollcommands:
            - yscrollcommand=vsb.set
            - xscrollcommand=hsb.set
        
        Column Configuration Loop:
            ```python
            cols = ("isbn", "title", "author", "price", "stock")
            widths = [150, 300, 200, 100, 80]
            
            for col, width in zip(cols, widths):
                tree.heading(col, text=heading_text)
                tree.column(col, width=width, anchor="w")
            ```
        
        Treeview Styling:
            Similar to BookList but with differences:
            - Row height: 28px (vs 24px in BookList)
            - Selection: BUTTON_HOVER (vs ACCENT_RED in BookList)
            - No alternating row colors (cleaner for search results)
        
        Initial State:
            - Radio: "Título" selected (search_type="title")
            - Entry: Empty with placeholder visible
            - Info label: Tips message
            - Results label: Empty
            - Table: Empty (no rows)
            - current_results: Empty list
        
        Event Binding:
            ```python
            search_entry.bind("<Return>", lambda e: perform_search())
            ```
            
            Allows Enter key to trigger search without clicking button.
        
        Error Handling:
            Protected operations:
            - Window scaling: Non-fatal
            - Theme application: Fallback method
            - Transient setup: Continues if fails
            - Style configuration: Uses defaults
            - All styling wrapped in try-except
        
        Args:
            parent (CTk, optional): Parent window for transient behavior. Defaults to None.
        
        Side Effects:
            - Creates new toplevel window
            - Initializes BookController
            - Applies global Treeview styling (affects all Treeviews)
            - Displays window on screen
        
        Raises:
            None: All exceptions caught and handled gracefully
        
        Example:
            >>> # Open from BookList
            >>> search_window = BookSearch(parent=book_list)
        """
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass
        
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # Window configuration
        self.title("🔍 Búsqueda de Libros")
        self.geometry("1000x600")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        # Book controller (follows MVC pattern)
        self.controller = BookController()
        self.current_results = []

        # Main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 12), fill="x")
        
        title_lbl = wf.create_title_label(title_frame, "🔍 Búsqueda de Libros")
        title_lbl.pack(side="left")

        # Search controls frame
        search_frame = ctk.CTkFrame(container, fg_color=theme.BUTTON_COLOR, corner_radius=8)
        search_frame.pack(fill="x", pady=(0, 12), padx=8)

        # Search type selector
        type_frame = ctk.CTkFrame(search_frame, fg_color=theme.BUTTON_COLOR)
        type_frame.pack(fill="x", padx=12, pady=(12, 8))
        
        lbl_type = ctk.CTkLabel(type_frame, text="Buscar por:", text_color=theme.TEXT_COLOR)
        lbl_type.pack(side="left", padx=(0, 12))

        self.search_type = ctk.StringVar(value="title")
        
        radio_title = ctk.CTkRadioButton(
            type_frame,
            text="Título",
            variable=self.search_type,
            value="title",
            fg_color=theme.BUTTON_HOVER,
            hover_color=theme.BORDER_COLOR
        )
        radio_title.pack(side="left", padx=8)
        
        radio_author = ctk.CTkRadioButton(
            type_frame,
            text="Autor",
            variable=self.search_type,
            value="author",
            fg_color=theme.BUTTON_HOVER,
            hover_color=theme.BORDER_COLOR
        )
        radio_author.pack(side="left", padx=8)

        # Search input frame
        input_frame = ctk.CTkFrame(search_frame, fg_color=theme.BUTTON_COLOR)
        input_frame.pack(fill="x", padx=12, pady=(8, 12))

        lbl_search = ctk.CTkLabel(input_frame, text="Buscar:", text_color=theme.TEXT_COLOR)
        lbl_search.pack(side="left", padx=(0, 12))

        self.search_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Introduce título o autor (búsqueda parcial)...",
            width=400,
            height=36
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self.perform_search())

        btn_search = wf.create_primary_button(
            input_frame,
            "🔍 Buscar",
            command=self.perform_search,
            width=120,
            height=36
        )
        btn_search.pack(side="left", padx=(0, 8))

        btn_clear = wf.create_small_button(
            input_frame,
            "Limpiar",
            command=self.clear_search,
            width=100,
            height=36
        )
        btn_clear.pack(side="left")

        # Info label
        info_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        info_frame.pack(fill="x", pady=(0, 8))
        
        self.info_label = ctk.CTkLabel(
            info_frame,
            text="💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales.",
            text_color=theme.TEXT_COLOR
        )
        self.info_label.pack(side="left")

        # Results count label
        self.results_label = ctk.CTkLabel(info_frame, text="", text_color=theme.TEXT_COLOR)
        self.results_label.pack(side="right")

        # Table frame for results
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("isbn", "title", "author", "price", "stock")
        col_widths = [150, 300, 200, 100, 80]

        # Style the Treeview
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        try:
            fam, fsize, fweight = theme.get_font(self, size=10)
        except Exception:
            fam, fsize, fweight = ("Segoe UI", 10, "normal")
        
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=28, fieldbackground=theme.BG_COLOR)

        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception:
            hfam, hfsize = (fam, fsize + 1)
        
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        try:
            style.map("Treeview", background=[('selected', theme.BUTTON_HOVER)])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("isbn", text="ISBN")
        self.tree.heading("title", text="Título")
        self.tree.heading("author", text="Autor")
        self.tree.heading("price", text="Precio (COP)")
        self.tree.heading("stock", text="Stock")

        for col, w in zip(cols, col_widths):
            self.tree.column(col, width=w, anchor="w")

        # Scrollbars
        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_holder, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_holder.rowconfigure(0, weight=1)
        table_holder.columnconfigure(0, weight=1)

        # Bottom buttons
        bottom_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR)
        bottom_frame.pack(fill="x", pady=(8, 0))

        btn_close = wf.create_small_button(bottom_frame, "Cerrar", command=self.destroy)
        btn_close.pack(side="right")

    def perform_search(self):
        """Execute search using recursive linear search algorithm and display results.
        
        Validates search input, executes the appropriate search via controller
        (title or author), clears previous results, populates table with matches,
        and updates status labels with result count and algorithm information.
        
        Purpose:
            Primary search execution method that orchestrates the entire search
            workflow from validation through result display, demonstrating the
            recursive linear search algorithm while providing practical book discovery.
        
        Workflow:
            1. Input Validation:
               - Get query from search_entry and strip whitespace
               - Check if empty
               - Show warning dialog if empty, return early
            
            2. Search Type Detection:
               - Read search_type variable ("title" or "author")
            
            3. Clear Previous Results:
               - Delete all existing Treeview rows
            
            4. Execute Search:
               - Call appropriate controller method based on search_type
               - Controller performs recursive linear search
               - Returns list of matching InventoryGeneral objects
            
            5. Store Results:
               - Save results to self.current_results
            
            6. Update Result Count:
               - Configure results_label with count
            
            7. Handle Empty Results:
               - If no matches, update info_label with "not found" message
               - Return early (table remains empty)
            
            8. Populate Table:
               - Iterate through results
               - Extract book data from each InventoryGeneral
               - Format as tuple (ISBN, title, author, price, stock)
               - Insert into Treeview
            
            9. Update Success Message:
               - Configure info_label with algorithm completion message
        
        Controller Methods Called:
            Title Search:
            ```python
            results = controller.search_books_by_title(query)
            ```
            - Searches Book.title field
            - Recursive linear search implementation
            - Returns matching InventoryGeneral objects
            
            Author Search:
            ```python
            results = controller.search_books_by_author(query)
            ```
            - Searches Book.author field
            - Recursive linear search implementation
            - Returns matching InventoryGeneral objects
        
        Result Data Structure:
            Each result is an InventoryGeneral object:
            ```python
            result.get_book()        # Returns Book object
            result.get_stock()       # Returns int (available quantity)
            ```
        
        Table Population:
            For each result:
            ```python
            book = inv.get_book()
            row = (
                book.get_ISBNCode(),              # "978-3-16-148410-0"
                book.get_title(),                 # "The Great Gatsby"
                book.get_author(),                # "F. Scott Fitzgerald"
                f"${book.get_price():,}",         # "$25,000"
                inv.get_stock()                   # 5
            )
            tree.insert("", "end", values=row)
            ```
        
        Price Formatting:
            Uses f-string with comma separator:
            - Input: 25000
            - Output: "$25,000"
            - Format: f"${price:,}"
        
        Status Messages:
            Empty Query:
            - Dialog title: "Campo vacío"
            - Message: "Por favor introduce un término de búsqueda."
            - Parent: self (modal to search window)
            
            No Results:
            - Info label: "❌ No se encontraron libros con '{query}' en {search_type}"
            - Example: "❌ No se encontraron libros con 'xyz' en title"
            
            Success:
            - Results label: "📊 {n} resultado(s) encontrado(s)"
            - Info label: "✅ Búsqueda completada usando algoritmo de búsqueda lineal recursiva"
            
            Error:
            - Dialog title: "Error"
            - Dialog message: "Error al realizar la búsqueda: {exception}"
            - Info label: "❌ Error en la búsqueda: {exception}"
        
        Search Algorithm Details:
            The controller implements recursive linear search:
            - Traverses inventory list one item at a time
            - Compares query against specified field (title/author)
            - Case-insensitive comparison
            - Accent-insensitive comparison
            - Partial matching (substring search)
            - Accumulates matches in results list
            - Base case: index >= list length
            - Time: O(n), Space: O(n)
        
        Validation:
            Only validates non-empty query:
            - Empty/whitespace-only: Shows warning
            - All other input accepted
            - No regex validation
            - No length limits
        
        Error Handling:
            Search Execution:
            - Wrapped in try-except
            - Catches any controller exceptions
            - Shows error dialog to user
            - Updates info_label with error
            - Table remains empty on error
            - Window remains functional
            
            Book Extraction:
            - Checks if inv.get_book() returns valid book
            - Skips inventory items without book (defensive)
        
        Performance:
            - Search: O(n) where n = inventory size
            - Table population: O(m) where m = results
            - Total: O(n) (search dominates)
        
        Triggers:
            1. Primary button click: "🔍 Buscar"
            2. Enter key in search_entry field
        
        Args:
            None (reads from self.search_entry and self.search_type)
        
        Returns:
            None
        
        Side Effects:
            - Clears all Treeview rows
            - Queries controller for search results
            - Updates current_results list
            - Populates Treeview with results
            - Updates results_label with count
            - Updates info_label with status
            - May show warning/error dialogs
        
        Raises:
            None: All exceptions caught and displayed
        
        Example Flow:
            ```
            User enters "Great" and selects "Título"
            → Clicks "🔍 Buscar" or presses Enter
            → perform_search() called
            → Validates: query="Great" (valid)
            → Clears table
            → Calls controller.search_books_by_title("Great")
            → Controller returns [InventoryGeneral(book="The Great Gatsby", stock=5)]
            → Updates: current_results = [inv1]
            → Updates: results_label = "📊 1 resultado(s) encontrado(s)"
            → Inserts row: ("978-...", "The Great Gatsby", "F. Scott...", "$25,000", 5)
            → Updates: info_label = "✅ Búsqueda completada..."
            ```
        """
        """Ejecuta la búsqueda usando búsqueda lineal."""
        query = self.search_entry.get().strip()
        
        if not query:
            messagebox.showwarning(
                "Campo vacío",
                "Por favor introduce un término de búsqueda.",
                parent=self
            )
            return

        search_type = self.search_type.get()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Perform search using linear search algorithm through controller
        try:
            if search_type == "title":
                results = self.controller.search_books_by_title(query)
            else:  # author
                results = self.controller.search_books_by_author(query)
            
            self.current_results = results
            
            # Update results label
            self.results_label.configure(
                text=f"📊 {len(results)} resultado(s) encontrado(s)"
            )
            
            if not results:
                self.info_label.configure(
                    text=f"❌ No se encontraron libros con '{query}' en {search_type}"
                )
                return
            
            # Populate table
            for inv in results:
                book = inv.get_book()
                if book:
                    self.tree.insert("", "end", values=(
                        book.get_ISBNCode(),
                        book.get_title(),
                        book.get_author(),
                        f"${book.get_price():,}",
                        inv.get_stock()
                    ))
            
            self.info_label.configure(
                text=f"✅ Búsqueda completada usando algoritmo de búsqueda lineal recursiva"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al realizar la búsqueda: {str(e)}",
                parent=self
            )
            self.info_label.configure(
                text=f"❌ Error en la búsqueda: {str(e)}"
            )

    def clear_search(self):
        """Clear search input, results table, and reset to initial state.
        
        Resets all search-related UI elements to their initial state: clears the
        search entry field, removes all table rows, empties the results list,
        clears the result count, and restores the initial info message.
        
        Purpose:
            Provides a quick way to reset the search interface to a clean state,
            allowing users to start a fresh search without manually clearing
            the input or closing/reopening the window.
        
        Workflow:
            1. Clear Search Entry:
               - Delete all text from search_entry
               - Range: 0 to 'end'
            
            2. Clear Table:
               - Get all tree children (row IDs)
               - Delete each row from Treeview
            
            3. Reset Results List:
               - Set current_results to empty list
            
            4. Clear Result Count:
               - Configure results_label to empty string
            
            5. Restore Info Message:
               - Configure info_label with initial tips message
        
        Entry Deletion:
            ```python
            search_entry.delete(0, 'end')
            ```
            - 0: Start position (first character)
            - 'end': End position (last character)
            - Removes all text, placeholder becomes visible
        
        Table Clearing:
            ```python
            for item in tree.get_children():
                tree.delete(item)
            ```
            - tree.get_children() returns tuple of item IDs
            - Each item deleted individually
            - Table becomes empty (no rows)
        
        State After Clear:
            - search_entry: Empty (placeholder visible)
            - tree: No rows (empty table)
            - current_results: [] (empty list)
            - results_label: "" (blank)
            - info_label: "💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales."
            - search_type: Unchanged (retains last selection)
        
        State Preservation:
            Does NOT reset:
            - Radio button selection (search_type)
            - Window position
            - Column widths
            - User preferences
        
        Use Cases:
            1. Start Fresh Search:
               - User wants to search for different term
               - Clears previous results and input
            
            2. Clear Mistake:
               - User entered wrong query
               - Quick way to clear without manual selection
            
            3. Reset View:
               - User finished reviewing results
               - Wants clean slate
        
        Trigger:
            - "Limpiar" small button click
        
        Args:
            None (operates on self.search_entry, self.tree, etc.)
        
        Returns:
            None
        
        Side Effects:
            - Clears search_entry text
            - Removes all Treeview rows
            - Resets current_results to []
            - Clears results_label text
            - Restores info_label to initial message
        
        Raises:
            None: All operations are safe
        
        Example:
            ```
            State before clear:
            - Entry: "Gatsby"
            - Table: 3 rows with results
            - Results label: "📊 3 resultado(s) encontrado(s)"
            - Info label: "✅ Búsqueda completada..."
            
            User clicks "Limpiar"
            
            State after clear:
            - Entry: "" (placeholder visible)
            - Table: Empty
            - Results label: ""
            - Info label: "💡 La búsqueda es insensible..."
            ```
        """
        """Limpia la búsqueda y los resultados."""
        self.search_entry.delete(0, 'end')
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.current_results = []
        self.results_label.configure(text="")
        self.info_label.configure(
            text="💡 La búsqueda es insensible a mayúsculas y acentos. Usa palabras parciales."
        )


__all__ = ['BookSearch']
