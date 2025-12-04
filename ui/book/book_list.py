"""Book List Viewer - Tabular Display with CRUD Operations.

This module implements a comprehensive book catalog viewer using a Treeview table
for displaying all books with full CRUD (Create, Read, Update, Delete) capabilities.
It serves as the primary interface for browsing and managing the book collection.

Architecture - Hybrid Tk/CTk Approach:
    The window uses CustomTkinter for the container and controls, but employs
    native Tkinter's ttk.Treeview for the table display. This hybrid approach
    provides:
    - Modern CTk styling for buttons and containers
    - Mature, feature-rich Treeview for tabular data
    - Custom styling to match the cozy Japanese theme

Table Display:
    Columns (7):
    1. ID: Book identifier (70px, centered)
    2. ISBN: ISBN code (200px, left-aligned)
    3. Título: Book title (200px, left-aligned)
    4. Autor: Author name (200px, left-aligned)
    5. Peso: Weight in Kg (90px, centered)
    6. Precio: Price in COP (90px, centered)
    7. Prestado: Borrowed status Sí/No (80px, centered)
    
    Features:
    - Vertical scrollbar for long lists
    - Alternating row colors (even/odd) for readability
    - Selection highlighting with theme accent color (red)
    - Double-click to edit functionality
    - Theme-matched fonts and colors

CRUD Operations:
    Create:
    - Handled by separate BookForm window (not in this module)
    - Accessed via main menu
    
    Read:
    - load_books(): Loads all books from controller
    - Displays in Treeview table
    - Auto-refresh on window open
    
    Update:
    - open_selected_for_edit(): Opens BookForm in edit mode
    - Triggered by "Editar" button or double-click
    - Requires row selection
    
    Delete:
    - delete_selected(): Removes book from system
    - Requires confirmation dialog
    - Validates borrow status and removes from shelves
    - Auto-refreshes table after deletion

Search Integration:
    - "🔍 Buscar Libros" button opens BookSearch window
    - Primary button styling for emphasis
    - Allows advanced filtering and search operations

Styling Strategy:
    Treeview Theme Customization:
    - Theme: 'clam' (modern, customizable)
    - Row font: theme.get_font(size=10, normal)
    - Heading font: theme.get_font(size=11, bold)
    - Row height: 24px for comfortable reading
    - Background: theme.BG_COLOR (warm beige)
    - Heading background: theme.BORDER_COLOR (black)
    - Heading foreground: theme.BG_COLOR (beige text on black)
    - Selection: theme.ACCENT_RED (deep red) with white text
    - Alternating rows: #F7F1E6 (odd) / theme.BG_COLOR (even)

Action Buttons:
    1. 🔍 Buscar Libros: Opens search window (primary button)
    2. Refrescar: Reloads table data (small button)
    3. Editar: Opens edit form for selected book (small button)
    4. Eliminar: Deletes selected book with confirmation (small button)
    5. Regresar: Closes window and returns to parent (small button)
    
    Layout: Horizontal left-to-right with consistent spacing

Window Management:
    - Type: CTkToplevel (popup window)
    - Transient: Attached to parent window
    - Close protocol: Custom _on_close handler
    - Focus restoration: Returns focus to parent on close
    - Child window tracking: Maintains _open_windows list for BookForm/BookSearch

Data Flow:
    Load:
    ```
    load_books() → BookController.get_all_books() → Book objects
    → Format as tuples → Insert into Treeview rows
    ```
    
    Edit:
    ```
    User selects row → open_selected_for_edit() → Extract book_id
    → BookForm(mode="edit", book_id=id) → User edits → Controller updates
    → Manual refresh needed
    ```
    
    Delete:
    ```
    User selects row → delete_selected() → Confirmation dialog
    → Controller.delete_book(id) → Validates and removes
    → Auto-refresh table → Shows success message
    ```

Error Handling:
    - Load failures: Shows error dialog, empty table
    - Edit/Delete with no selection: Shows info dialog
    - Delete validation errors: Shows error dialog (borrowed books, etc.)
    - Row parsing errors: Skips invalid rows, continues loading
    - Window operations: Extensive try-except for robustness

Validation (Delete):
    BookController.delete_book() enforces:
    - Book cannot be borrowed
    - Removes book from all shelves
    - Updates inventory reports
    - Deletes from books.json

User Experience:
    - Clear visual feedback via dialogs
    - Row selection highlighting
    - Double-click shortcut for editing
    - Confirmation for destructive operations
    - Alternating row colors for readability
    - Horizontal scrolling if columns exceed window width

Limitations:
    - No inline editing (must open separate form)
    - Manual refresh after edit (no auto-update)
    - No column sorting (future enhancement)
    - No column resizing persistence
    - No multi-select delete

See Also:
    - ui.book.book_form.BookForm: Edit/create form window
    - ui.book.book_search.BookSearch: Advanced search window
    - controllers.book_controller.BookController: Business logic
"""

import os
import tkinter as tk
import tkinter.font as tkfont
import customtkinter as ctk
from tkinter import ttk, messagebox
from ui import theme
from ui import widget_factory as wf
from ui.book.book_form import BookForm
from ui.book.book_search import BookSearch
from controllers.book_controller import BookController


class BookList(ctk.CTkToplevel):
    """Tabular book catalog viewer with CRUD operations and search integration.
    
    This window provides a comprehensive interface for viewing and managing the
    book collection using a styled Treeview table with 7 columns. It supports
    browsing, searching, editing, and deleting books with proper validation and
    user feedback.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Table: ttk.Treeview (native Tkinter widget)
        Layout: Vertical stack (title → table → action buttons)
        Controller: BookController for data operations
    
    UI Components:
        1. Title Section:
           - Title label: "Listado de Libros" (factory-created)
        
        2. Table Section:
           - Treeview with 7 columns (ID, ISBN, Title, Author, Weight, Price, Borrowed)
           - Vertical scrollbar
           - Alternating row colors
           - Selection highlighting
           - Custom fonts matching theme
        
        3. Action Button Bar:
           - Primary: "🔍 Buscar Libros" (opens search window)
           - Small: "Refrescar" (reloads data)
           - Small: "Editar" (opens edit form)
           - Small: "Eliminar" (deletes with confirmation)
           - Small: "Regresar" (closes window)
    
    Table Configuration:
        Column Specifications:
        ```
        Column      Width   Alignment   Heading
        ------      -----   ---------   -------
        id          70px    center      "ID"
        ISBNCode    200px   left        "ISBN"
        title       200px   left        "Título"
        author      200px   left        "Autor"
        weight      90px    center      "Peso"
        price       90px    center      "Precio"
        isBorrowed  80px    center      "Prestado"
        ```
    
    Styling:
        Theme: 'clam' (customizable ttk theme)
        
        Fonts:
        - Rows: 10pt normal (from theme.get_font)
        - Headings: 11pt bold (from theme.get_font)
        
        Colors:
        - Row background (even): theme.BG_COLOR (#EDE6D6)
        - Row background (odd): #F7F1E6 (lighter beige)
        - Heading background: theme.BORDER_COLOR (black)
        - Heading text: theme.BG_COLOR (beige on black)
        - Selection background: theme.ACCENT_RED (deep red)
        - Selection text: white (#ffffff)
        
        Dimensions:
        - Row height: 24px
        - Window: 900x500px
    
    Attributes:
        tree (ttk.Treeview): Main table widget displaying books
        book_controller (BookController): Handles data operations
        _parent_window: Reference to parent for focus restoration
        _open_windows (list): Tracks child windows (BookForm, BookSearch)
    
    Event Bindings:
        - Double-click on row: Opens edit form for that book
        - WM_DELETE_WINDOW: Custom close handler (_on_close)
    
    Data Display Format:
        - isBorrowed: Converted to "Sí"/"No" for readability
        - All other fields: Direct string representation
        - Empty cells: Displayed as-is from Book object getters
    
    Row Tagging:
        Each row tagged as 'even' or 'odd' based on index for alternating colors.
        Provides visual separation without borders.
    
    Window Behavior:
        - Transient to parent (stays on top of parent)
        - Modal-like (blocks parent interaction in some window managers)
        - Auto-loads data on open
        - Restores parent focus on close
    
    Child Windows:
        Manages two types of child windows:
        1. BookForm (edit mode): Opens when editing selected book
        2. BookSearch: Opens when clicking search button
        
        Both tracked in _open_windows list to prevent garbage collection.
    
    Error Resilience:
        - Continues loading valid books if individual book parsing fails
        - Graceful degradation for styling failures
        - Comprehensive error dialogs for user-facing operations
    
    See Also:
        - ui.book.book_form.BookForm: Edit form interface
        - ui.book.book_search.BookSearch: Search interface
        - controllers.book_controller.BookController: Data layer
    """
    
    def __init__(self, parent=None):
        """Initialize the book list window with table and controls.
        
        Creates and configures the complete book catalog viewer including themed
        Treeview table, custom styling, action buttons, and event bindings. Loads
        initial data automatically.
        
        Purpose:
            Provides a complete, ready-to-use book browsing and management interface
            with proper theming, error handling, and user interaction capabilities.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Store parent reference for focus restoration
            3. Apply window scaling configuration
            4. Apply theme to window
            5. Set window title and geometry
            6. Set transient to parent
            7. Create main container frame
            8. Build title section
            9. Create table holder frame (native tk.Frame)
            10. Configure Treeview style (theme, fonts, colors)
            11. Create Treeview widget with 7 columns
            12. Configure column headings and widths
            13. Add vertical scrollbar
            14. Create action button frame
            15. Add 5 action buttons (search, refresh, edit, delete, close)
            16. Initialize BookController
            17. Load initial book data via load_books()
            18. Set window close protocol
            19. Bind double-click event to edit action
        
        Treeview Styling Process:
            1. Create ttk.Style instance
            2. Set theme to 'clam' (fallback to default if unavailable)
            3. Get row font from theme.get_font(size=10)
            4. Configure Treeview style with font, row height, background
            5. Get heading font from theme.get_font(size=11, bold)
            6. Configure Treeview.Heading style with font and colors
            7. Map selection colors using theme.ACCENT_RED
        
        Column Configuration:
            For each of 7 columns:
            - Set heading text (Spanish labels)
            - Set column width based on content type
            - Set alignment (center for IDs/numbers, left for text)
        
        Scrollbar Integration:
            ```python
            vsb = ttk.Scrollbar(orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            ```
            Provides synchronized vertical scrolling for long lists.
        
        Button Configuration:
            Primary button (search):
            - Larger, more prominent styling
            - Left-most position for emphasis
            - 12px right padding for separation
            
            Small buttons (refresh, edit, delete, close):
            - Compact styling
            - 8px spacing between buttons
            - Horizontal left-to-right layout
        
        Event Binding:
            Double-click:
            ```python
            tree.bind("<Double-1>", lambda e: open_selected_for_edit())
            ```
            Provides quick access to edit functionality.
        
        Transient Behavior:
            ```python
            self.transient(parent)
            ```
            Makes window:
            - Stay on top of parent
            - Minimize/restore with parent
            - Close when parent closes (in some window managers)
        
        Error Handling:
            Protected operations:
            - Window scaling: Continues with default if fails
            - Theme application: Tries fallback fg_color setting
            - Transient setup: Continues if parent is None or fails
            - Style configuration: Continues with defaults if fails
            - Event binding: Continues if binding fails
            - Protocol setup: Window still closable via _on_close button
        
        Initial State:
            - Window visible and centered (default geometry)
            - Table populated with all books from database
            - No row selected
            - Scrollbar at top position
            - Focus on window (default)
        
        Args:
            parent (CTk, optional): Parent window for transient behavior and focus
                                   restoration. Defaults to None.
        
        Side Effects:
            - Creates new toplevel window
            - Initializes BookController
            - Loads all books from database via controller
            - Displays window on screen
            - Applies custom Treeview styling globally (ttk.Style affects all Treeviews)
        
        Raises:
            None: All exceptions caught and handled gracefully
        
        Example:
            >>> # Open from main menu
            >>> book_list = BookList(parent=main_menu)
        """
        super().__init__(parent)
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
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

        # Window basics
        self.title("Listado de Libros")
        self.geometry("900x500")
        try:
            if parent is not None:
                self.transient(parent)
        except Exception:
            pass

        # Main container
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=12, pady=12)

        # Title
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 8), fill="x")
        title_lbl = wf.create_title_label(title_frame, "Listado de Libros")
        title_lbl.pack(side="left")

        # Table frame uses a native tk.Frame to hold the ttk.Treeview
        table_holder = tk.Frame(container, bg=theme.BG_COLOR)
        table_holder.pack(expand=True, fill="both", pady=(8, 8))

        cols = ("id", "ISBNCode", "title", "author", "weight", "price", "isBorrowed")

        # Style the Treeview to match app fonts and palette
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Use theme font for rows
        try:
            fam, fsize, fweight = theme.get_font(self, size=10)
        except Exception:
            fam, fsize, fweight = ("Segoe UI", 10, "normal")
        row_font = tkfont.Font(family=fam, size=fsize)
        style.configure("Treeview", font=row_font, rowheight=24, fieldbackground=theme.BG_COLOR)

        # Heading font (same family, slightly larger/bold)
        try:
            hfam, hfsize, _ = theme.get_font(self, size=11, weight="bold")
        except Exception:
            hfam, hfsize = (fam, fsize + 1)
        head_font = tkfont.Font(family=hfam, size=hfsize, weight="bold")
        style.configure("Treeview.Heading", font=head_font, background=theme.BORDER_COLOR, foreground=theme.BG_COLOR)

        # Selection color -> use accent red
        try:
            style.map("Treeview",
                      background=[('selected', theme.ACCENT_RED)],
                      foreground=[('selected', '#ffffff')])
        except Exception:
            pass

        self.tree = ttk.Treeview(table_holder, columns=cols, show="headings")

        # Define headings
        headings = {
            "id": "ID",
            "ISBNCode": "ISBN",
            "title": "Título",
            "author": "Autor",
            "weight": "Peso",
            "price": "Precio",
            "isBorrowed": "Prestado",
        }
        for c in cols:
            self.tree.heading(c, text=headings.get(c, c))
            # set a reasonable width per column
            if c == "id":
                self.tree.column(c, width=70, anchor="center")
            elif c in ("price", "weight"):
                self.tree.column(c, width=90, anchor="center")
            elif c == "isBorrowed":
                self.tree.column(c, width=80, anchor="center")
            else:
                self.tree.column(c, width=200, anchor="w")

        # Vertical scrollbar
        vsb = ttk.Scrollbar(table_holder, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.tree.pack(expand=True, fill="both", side="left")

        # Action row
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(fill="x", pady=(8, 4))

        # Botón de búsqueda (más destacado)
        search_btn = wf.create_primary_button(action_frame, text="🔍 Buscar Libros", command=self.open_book_search)
        search_btn.pack(side="left", padx=(0, 12))

        refresh_btn = wf.create_small_button(action_frame, text="Refrescar", command=self.load_books)
        refresh_btn.pack(side="left", padx=(0, 8))
        # Edit and Delete buttons operate on the selected row
        edit_btn = wf.create_small_button(action_frame, text="Editar", command=self.open_selected_for_edit)
        edit_btn.pack(side="left", padx=(0, 8))

        delete_btn = wf.create_small_button(action_frame, text="Eliminar", command=self.delete_selected)
        delete_btn.pack(side="left", padx=(0, 8))

        close_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_close)
        close_btn.pack(side="left")

        # Initialize controller
        self.book_controller = BookController()
        
        # Load data initially
        self.load_books()

        try:
            self.protocol("WM_DELETE_WINDOW", self._on_close)
        except Exception:
            pass

        # bind double-click to open edit for selected row
        try:
            self.tree.bind("<Double-1>", lambda e: self.open_selected_for_edit())
        except Exception:
            pass

    def load_books(self):
        """Load all books from controller and populate Treeview table.
        
        Clears existing table rows, retrieves all books from the database via
        controller, formats book data as tuples, and inserts into Treeview with
        alternating row tags for visual distinction.
        
        Purpose:
            Primary data loading method that refreshes the table display with
            current book catalog data, ensuring users see up-to-date information.
        
        Workflow:
            1. Clear Existing Data:
               - Get all tree children (rows)
               - Delete each row from Treeview
            
            2. Data Retrieval:
               - Call controller.get_all_books()
               - Catch and display errors if retrieval fails
            
            3. Row Population:
               - Iterate through book objects
               - Format each book as 7-element tuple
               - Insert into Treeview with alternating tags
               - Skip invalid books (continue on error)
            
            4. Style Application:
               - Configure 'odd' tag: lighter beige (#F7F1E6)
               - Configure 'even' tag: theme background (BG_COLOR)
        
        Data Transformation:
            Book object → Row tuple:
            ```python
            row = (
                book.get_id(),           # "B001"
                book.get_ISBNCode(),     # "978-3-16-148410-0"
                book.get_title(),        # "The Great Gatsby"
                book.get_author(),       # "F. Scott Fitzgerald"
                book.get_weight(),       # 0.5
                book.get_price(),        # 25000
                "Sí" or "No"            # Formatted isBorrowed
            )
            ```
        
        Borrowed Status Formatting:
            - book.get_isBorrowed() returns boolean
            - Converted to Spanish: True → "Sí", False → "No"
            - Improves readability for Spanish-speaking users
        
        Row Tagging Algorithm:
            ```python
            for i, book in enumerate(books):
                tag = 'even' if i % 2 == 0 else 'odd'
            ```
            
            Results in alternating pattern:
            - Row 0: even (theme.BG_COLOR)
            - Row 1: odd (#F7F1E6)
            - Row 2: even (theme.BG_COLOR)
            - ...
        
        Tag Styling:
            After all rows inserted:
            ```python
            tree.tag_configure('odd', background='#F7F1E6')
            tree.tag_configure('even', background=theme.BG_COLOR)
            ```
            
            Provides subtle visual separation without borders.
        
        Error Handling:
            Data Retrieval Errors:
            - Shows error dialog with exception message
            - Returns early (table remains empty)
            - User can retry via "Refrescar" button
            
            Individual Book Errors:
            - Try-except around row insertion
            - Continues with next book if one fails
            - Ensures partial data displayed (graceful degradation)
            
            Styling Errors:
            - Tag configuration wrapped in try-except
            - Continues without alternating colors if fails
            - Rows still displayed (functionality preserved)
        
        Performance:
            - Time: O(n) where n = number of books
            - Space: O(n) for book list in memory
            - UI: Treeview handles large datasets efficiently
        
        Refresh Triggers:
            Called by:
            1. __init__: Initial load on window open
            2. "Refrescar" button: Manual user refresh
            3. delete_selected(): Auto-refresh after deletion
            
            NOT called after:
            - Edit operations (manual refresh required)
            - External changes to books.json
        
        Args:
            None (uses self.book_controller and self.tree)
        
        Returns:
            None
        
        Side Effects:
            - Clears all Treeview rows
            - Queries controller for all books
            - Populates Treeview with formatted data
            - Applies alternating row styling
            - Shows error dialog if retrieval fails
        
        Raises:
            None: All exceptions caught and handled
        
        Example State After Load:
            ```
            Tree contains:
            [even] B001 | 978-... | The Great Gatsby    | F. Scott... | 0.5 | 25000 | No
            [odd]  B002 | 978-... | To Kill a Mockingbird | Harper...  | 0.6 | 30000 | Sí
            [even] B003 | 978-... | 1984               | George...  | 0.4 | 22000 | No
            ...
            ```
        """
        # Clear existing rows
        for r in self.tree.get_children():
            self.tree.delete(r)

        try:
            books = self.book_controller.get_all_books()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los libros: {e}")
            return

        # insert rows with alternating tag for subtle row striping
        for i, book in enumerate(books):
            try:
                # Format isBorrowed as Sí/No for better readability
                is_borrowed = "Sí" if book.get_isBorrowed() else "No"
                row = (
                    book.get_id(),
                    book.get_ISBNCode(),
                    book.get_title(),
                    book.get_author(),
                    book.get_weight(),
                    book.get_price(),
                    is_borrowed,
                )
                tag = 'even' if i % 2 == 0 else 'odd'
                self.tree.insert("", "end", values=row, tags=(tag,))
            except Exception:
                continue

        # configure row tag colors (subtle beige alternation)
        try:
            self.tree.tag_configure('odd', background='#F7F1E6')
            self.tree.tag_configure('even', background=theme.BG_COLOR)
        except Exception:
            pass

    def _on_close(self):
        """Close the book list window and restore focus to parent.
        
        Destroys the window and attempts to restore focus to the parent window
        (typically main menu) using lift() and focus_force() for reliable focus
        restoration.
        
        Purpose:
            Provides clean window closure with proper focus management, ensuring
            users seamlessly return to the parent window.
        
        Workflow:
            1. Window Destruction:
               - Call self.destroy() to close window
               - Fallback: self.withdraw() if destroy fails
            
            2. Parent Focus Restoration:
               - Check if _parent_window exists
               - Call parent.lift() to bring to front
               - Call parent.focus_force() to grab focus
        
        Focus Restoration Strategy:
            Uses two methods for reliability:
            
            1. lift():
               - Raises window above other windows
               - Brings to front of window stack
            
            2. focus_force():
               - Forcefully grabs keyboard focus
               - Works on most platforms
        
        Error Handling:
            All operations wrapped in try-except:
            - destroy(): Fallback to withdraw()
            - Parent access: Checks attribute existence
            - Focus operations: Individual try-except
            - Continues silently on failures
        
        Difference from BookForm._on_cancel:
            - Does NOT call parent.deiconify() (parent likely not minimized)
            - Simpler focus restoration (2 steps vs 3)
            - No need to unhide parent
        
        Triggers:
            1. "Regresar" button click
            2. Window manager close button (X) via WM_DELETE_WINDOW protocol
        
        Args:
            None (uses self and self._parent_window)
        
        Returns:
            None
        
        Side Effects:
            - Destroys/hides window
            - Restores parent window focus
        
        Raises:
            None: All exceptions silently caught
        """
        try:
            self.destroy()
        except Exception:
            try:
                self.withdraw()
            except Exception:
                pass

        try:
            if getattr(self, '_parent_window', None):
                try:
                    self._parent_window.lift()
                    self._parent_window.focus_force()
                except Exception:
                    pass
        except Exception:
            pass

    def open_selected_for_edit(self):
        """Open BookForm in edit mode for the selected table row.
        
        Retrieves the book ID from the selected Treeview row and opens a BookForm
        window in edit mode. Manages child window references to prevent garbage
        collection and ensures proper window visibility.
        
        Purpose:
            Provides quick access to book editing functionality from the table view,
            triggered either by button click or double-click on row.
        
        Workflow:
            1. Selection Validation:
               - Get current Treeview selection
               - Check if any row selected
               - Show info dialog if no selection
            
            2. Book ID Extraction:
               - Get row values from selected item
               - Extract book_id from first column (index 0)
            
            3. Parent Window Selection:
               - Use stored _parent_window if available
               - Fallback to self if no parent
            
            4. Form Creation:
               - Create BookForm(parent, mode="edit", book_id=id)
               - Add to _open_windows list (prevent GC)
            
            5. Window Management:
               - Call win.deiconify() to ensure visibility
               - Call win.lift() to bring to front
               - Call win.focus() to grab focus
        
        Selection Check:
            ```python
            sel = tree.selection()
            if not sel:
                # No selection
            ```
            
            Returns tuple of selected item IDs (usually 1 element).
        
        Value Extraction:
            ```python
            values = tree.item(sel[0], "values")
            book_id = values[0]  # First column is ID
            ```
            
            Values is a tuple: (id, isbn, title, author, weight, price, borrowed)
        
        Parent Selection Logic:
            Prefers _parent_window (main menu) over self (BookList) because:
            - BookForm should be child of main menu, not BookList
            - Better window hierarchy
            - Proper focus restoration on form close
        
        Garbage Collection Prevention:
            ```python
            if not hasattr(self, '_open_windows'):
                self._open_windows = []
            self._open_windows.append(win)
            ```
            
            Keeps strong reference to prevent premature destruction.
        
        Window Visibility Sequence:
            1. deiconify(): Ensure not minimized/hidden
            2. lift(): Bring to front of window stack
            3. focus(): Grab keyboard focus
            
            Triple approach ensures visibility across platforms.
        
        Manual Refresh Required:
            After editing in BookForm:
            - User must click "Refrescar" to see changes
            - No automatic refresh implemented
            - Future enhancement opportunity
        
        Error Handling:
            Selection Check:
            - Info dialog: "Selecciona primero un libro en la tabla."
            - Returns early without action
            
            Value Extraction:
            - Generic error dialog if row read fails
            - Should not occur with valid selection
            
            Form Creation:
            - Error dialog with exception message
            - Prevents crash on form initialization failures
            
            Window Management:
            - Each operation wrapped individually
            - Continues if visibility operations fail
            - Form still opens (just may not be focused)
        
        Triggers:
            1. "Editar" button click
            2. Double-click on table row (via <Double-1> binding)
        
        Args:
            None (uses self.tree for selection)
        
        Returns:
            None
        
        Side Effects:
            - Creates and displays BookForm window
            - Adds window to _open_windows tracking list
            - Shows info/error dialogs for validation failures
        
        Raises:
            None: All exceptions caught and shown in dialogs
        
        Example Flow:
            ```
            User double-clicks row with ID "B001"
            → open_selected_for_edit() called
            → Extracts "B001" from row values
            → BookForm(parent=main_menu, mode="edit", book_id="B001")
            → Form loads book data and displays
            → User edits and saves
            → Form closes, returns to BookList (unchanged)
            → User clicks "Refrescar" to see changes
            ```
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un libro en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            book_id = values[0]
            # open BookForm in edit mode; parent should be main menu if available
            parent = self._parent_window or self
            win = BookForm(parent, mode="edit", book_id=book_id)
            try:
                # keep a reference to avoid GC
                if getattr(self, "_open_windows", None) is None:
                    self._open_windows = []
                self._open_windows.append(win)
                win.deiconify()
                win.lift()
                win.focus()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el editor: {e}")

    def open_book_search(self):
        """Open the book search window for advanced filtering and search.
        
        Creates and displays a BookSearch window, manages window references for
        garbage collection prevention, and ensures proper window visibility.
        
        Purpose:
            Provides access to advanced search functionality from the book list,
            allowing users to filter and find books based on multiple criteria.
        
        Workflow:
            1. Parent Selection:
               - Use _parent_window if available
               - Fallback to self if no parent
            
            2. Window Creation:
               - Create BookSearch(parent)
               - Add to _open_windows list
            
            3. Window Management:
               - Call win.deiconify() to ensure visibility
               - Call win.lift() to bring to front
               - Call win.focus() to grab focus
        
        Garbage Collection Prevention:
            Same pattern as open_selected_for_edit():
            ```python
            if not hasattr(self, '_open_windows'):
                self._open_windows = []
            self._open_windows.append(win)
            ```
        
        Integration with BookSearch:
            BookSearch window provides:
            - Linear search algorithm demonstration
            - Multi-field filtering (title, author, ISBN)
            - Results display in separate window
            - Educational algorithm visualization
        
        Error Handling:
            - Wrapped in try-except for window creation
            - Shows error dialog with exception message
            - Non-blocking (BookList remains functional)
        
        Trigger:
            - "🔍 Buscar Libros" primary button click
        
        Args:
            None (uses self._parent_window)
        
        Returns:
            None
        
        Side Effects:
            - Creates and displays BookSearch window
            - Adds window to _open_windows tracking list
            - Shows error dialog if creation fails
        
        Raises:
            None: All exceptions caught and shown in dialog
        """
        """Abrir ventana de búsqueda de libros."""
        try:
            parent = self._parent_window or self
            win = BookSearch(parent)
            try:
                # keep a reference to avoid GC
                if getattr(self, "_open_windows", None) is None:
                    self._open_windows = []
                self._open_windows.append(win)
                win.deiconify()
                win.lift()
                win.focus()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la búsqueda: {e}")

    def delete_selected(self):
        """Delete the selected book after confirmation with validation checks.
        
        Retrieves the book ID from the selected row, shows confirmation dialog,
        validates deletion via controller (checks borrow status, removes from
        shelves), and refreshes the table on success.
        
        Purpose:
            Provides safe book deletion with user confirmation and automatic
            cleanup of related data (shelf assignments, inventory reports).
        
        Workflow:
            1. Selection Validation:
               - Get current Treeview selection
               - Show info dialog if no selection
            
            2. Book ID Extraction:
               - Get row values from selected item
               - Extract book_id from first column
               - Show error dialog if extraction fails
            
            3. Confirmation Dialog:
               - Show yes/no confirmation with book ID
               - Warn about irreversibility
               - Return if user cancels
            
            4. Deletion Execution:
               - Create BookController instance
               - Call controller.delete_book(book_id)
               - Controller performs validation and cleanup
            
            5. Success Handling:
               - Show success message
               - Call load_books() to refresh table
            
            6. Error Handling:
               - Catch and display controller exceptions
               - Table remains unchanged on error
        
        Controller Validation:
            BookController.delete_book() enforces:
            
            1. Borrow Check:
               - Cannot delete borrowed books
               - Raises exception if isBorrowed=True
            
            2. Shelf Removal:
               - Removes book from all shelves
               - Updates shelf data files
            
            3. Inventory Update:
               - Updates inventory reports
               - Recalculates totals
            
            4. Database Deletion:
               - Removes from books.json
               - Persists changes
        
        Confirmation Dialog:
            ```
            Title: "Confirmar"
            Message: "¿Eliminar el libro {book_id}? Esta acción no se puede deshacer?"
            Buttons: Yes, No
            ```
            
            Returns True if Yes clicked, False if No or closed.
        
        Success Message:
            "Libro eliminado correctamente de catálogo y estanterías."
            
            Emphasizes that deletion affects:
            - Book catalog (books.json)
            - Shelf assignments (shelves.json)
        
        Error Messages (from Controller):
            Common errors:
            - "Cannot delete borrowed book"
            - "Book not found"
            - "Error removing book from shelves"
            - File I/O errors
        
        Auto-Refresh:
            After successful deletion:
            - Calls load_books() automatically
            - User sees updated table immediately
            - No manual refresh needed
        
        Row Extraction Error:
            If tree.item() fails:
            - Shows error: "No se pudo leer la fila seleccionada."
            - Should not occur with valid selection
            - Defensive programming
        
        Deletion Flow:
            ```
            User selects row (B001)
            → Clicks "Eliminar"
            → delete_selected() called
            → Confirmation: "¿Eliminar el libro B001?..."
            → User clicks Yes
            → Controller validates (not borrowed, removes from shelves)
            → Success: "Libro eliminado correctamente..."
            → load_books() refreshes table
            → Row B001 disappears from table
            ```
        
        Validation Failure Example:
            ```
            User selects borrowed book (B002)
            → Clicks "Eliminar"
            → Confirmation: Yes
            → Controller.delete_book("B002") raises exception
            → Error dialog: "Cannot delete borrowed book"
            → Table unchanged, book still visible
            ```
        
        Trigger:
            - "Eliminar" button click
        
        Args:
            None (uses self.tree for selection)
        
        Returns:
            None
        
        Side Effects:
            - Shows confirmation dialog (blocking)
            - Deletes book from database via controller
            - Removes book from all shelves
            - Updates inventory reports
            - Refreshes table display
            - Shows success/error dialogs
        
        Raises:
            None: All exceptions caught and shown in dialogs
        """
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona primero un libro en la tabla.")
            return
        try:
            values = self.tree.item(sel[0], "values")
            book_id = values[0]
        except Exception:
            messagebox.showerror("Error", "No se pudo leer la fila seleccionada.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el libro {book_id}? Esta acción no se puede deshacer?"):
            return

        try:
            # use controller to delete (this also updates reports and removes from shelves)
            controller = BookController()
            # BookService.delete_book enforces borrow/stock checks and removes from shelves
            controller.delete_book(book_id)
            messagebox.showinfo("Borrado", "Libro eliminado correctamente de catálogo y estanterías.")
            self.load_books()
        except Exception as e:
            messagebox.showerror("Error", str(e))


__all__ = ["BookList"]
