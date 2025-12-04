"""Book Form Window - Dual-Mode CRUD Interface for Book Management.

This module implements a versatile form window that operates in two modes:
create mode (for adding new books) and edit mode (for updating existing books).
It provides a clean, user-friendly interface following the cozy Japanese theme.

Dual-Mode Architecture:
    The form adapts its behavior based on the 'mode' parameter:
    
    Create Mode:
    - ID field auto-generated (disabled, shows placeholder)
    - All fields empty with placeholders
    - Submit button labeled "Crear Libro"
    - On success: Form closes, returns to parent window
    
    Edit Mode:
    - ID field populated and disabled (read-only)
    - All fields pre-populated with existing book data
    - Submit button labeled "Actualizar Libro"
    - On success: Shows confirmation message

Form Fields:
    1. ID: Auto-generated in create mode, read-only in edit mode
    2. ISBN: Book's ISBN code (required)
    3. Title: Book title (required)
    4. Author: Book author name (required)
    5. Weight: Physical weight in kilograms (required, numeric)
    6. Price: Book price in Colombian Pesos (required, numeric)
    
    Note: Stock is NOT editable in this form. It's managed by InventoryService
    and calculated from inventory entries.

UI Components:
    1. Header:
       - Book pile icon (twemoji asset)
       - Title label "Crear Libro" (factory-created)
    
    2. Form Fields:
       - 6 entry fields stacked vertically
       - Consistent spacing (6px padding)
       - Placeholder text for guidance
       - Theme-styled via widget_factory
    
    3. Action Buttons:
       - Primary button: Create/Update (mode-dependent)
       - Small button: "Regresar" (cancel/back)
       - Horizontal layout for better UX

Window Configuration:
    - Type: CTkToplevel (modal-like popup)
    - Dimensions: 500x600 pixels
    - Theme: Cozy Japanese aesthetic (warm beige)
    - Title: "Book Manager"
    - Parent-aware: Restores focus to parent on close

Asset Integration:
    - Icon: bookpile.png (36x36) from twemoji assets
    - Path: ui/book/assets/twemoji/bookpile.png
    - Graceful fallback if image unavailable

Focus Management:
    - Stores parent window reference (_parent_window)
    - On cancel/close: Destroys form and restores parent focus
    - Uses deiconify(), lift(), focus_force() for reliable focus restoration
    - Handles WM_DELETE_WINDOW protocol for window manager close button

Validation:
    - Performed by BookController layer
    - Errors displayed as red labels in form
    - Success messages shown as normal labels

Error Handling:
    - Extensive try-except blocks for robustness
    - Graceful degradation for:
      * Window scaling configuration
      * Theme application
      * Icon loading
      * Window protocol setup
      * Focus restoration
    - All UI operations non-fatal (continues if fails)

Data Flow:
    Create Mode:
    ```
    User fills form → create_book() → BookController.create_book(data)
    → Success: Close form, restore parent focus
    → Error: Display error message in red
    ```
    
    Edit Mode:
    ```
    load_book() → BookController.get_book(id) → Populate fields
    User edits → update_book() → BookController.update_book(id, data)
    → Success: Show confirmation
    → Error: Display error message in red
    ```

Usage Pattern:
    ```python
    # Create mode
    form = BookForm(parent=main_window, mode="create")
    
    # Edit mode
    form = BookForm(parent=main_window, mode="edit", book_id="B001")
    ```

Limitations:
    - Stock field not included (managed by InventoryService)
    - No inline validation (relies on controller validation)
    - Success messages in edit mode stack (no clearing mechanism)

See Also:
    - controllers.book_controller.BookController: Handles CRUD operations
    - ui.widget_factory: Provides themed widget creation
    - ui.theme: Theme constants and styling
"""

import os
import customtkinter as ctk
try:
    from PIL import Image
except Exception:
    Image = None
from controllers.book_controller import BookController
from ui import theme
from ui import widget_factory as wf

class BookForm(ctk.CTkToplevel):
    """Dual-mode form window for creating and editing book records.
    
    This form provides a unified interface for both creating new books and editing
    existing ones. The mode parameter determines the form's behavior, field states,
    and button labels. It integrates with BookController for data operations and
    follows the application's theme for visual consistency.
    
    Architecture:
        Window Type: CTkToplevel (popup window attached to parent)
        Layout: Vertical stack (header → form fields → action buttons)
        Controller: BookController for CRUD operations
        Theme: Cozy Japanese aesthetic via theme module
    
    Modes:
        Create Mode (mode="create"):
        - ID field disabled with "Auto (se asignará)" placeholder
        - All fields empty, ready for input
        - Button: "Crear Libro"
        - On success: Form closes and parent regains focus
        
        Edit Mode (mode="edit", book_id required):
        - ID field populated and disabled (read-only)
        - All fields pre-filled with existing book data
        - Button: "Actualizar Libro"
        - On success: Confirmation message displayed
    
    UI Layout:
        ```
        Container Frame (theme.BG_COLOR, rounded)
        ├─ Title Frame
        │  ├─ Icon (bookpile.png, 36x36)
        │  └─ Title Label ("Crear Libro")
        ├─ Form Frame
        │  ├─ ID Entry (disabled in create mode)
        │  ├─ ISBN Entry
        │  ├─ Title Entry
        │  ├─ Author Entry
        │  ├─ Weight Entry
        │  └─ Price Entry
        └─ Action Frame
           ├─ Primary Button (Create/Update)
           └─ Small Button ("Regresar")
        ```
    
    Attributes:
        controller (BookController): Handles book CRUD operations
        mode (str): Operating mode ("create" or "edit")
        book_id (str): Book ID for edit mode (None in create mode)
        icon_book (CTkImage): Bookpile icon image (None if load fails)
        entry_id (CTkEntry): ID field (disabled in create mode)
        entry_isbn (CTkEntry): ISBN code field
        entry_title (CTkEntry): Book title field
        entry_author (CTkEntry): Author name field
        entry_weight (CTkEntry): Weight in Kg field
        entry_price (CTkEntry): Price in COP field
        _parent_window: Reference to parent window for focus restoration
    
    Window Configuration:
        - Dimensions: 500x600 pixels
        - Title: "Book Manager"
        - Close Protocol: Custom handler (_on_cancel) for window manager X button
        - Scaling: Inherits window scaling from parent
    
    Focus Management:
        - Stores parent reference for focus restoration
        - On close: Destroys form, then calls parent.deiconify(), lift(), focus_force()
        - Ensures user returns to main menu seamlessly
    
    Asset Loading:
        - Icon path: ui/book/assets/twemoji/bookpile.png
        - Fallback: Sets icon_book to None if image unavailable
        - Non-blocking: Form still functional without icon
    
    Error Resilience:
        - All optional operations wrapped in try-except
        - Window scaling: Continues if configuration fails
        - Theme application: Fallback to direct fg_color setting
        - Icon loading: Gracefully handles missing images
        - Protocol setup: Form still closable if protocol fails
    
    Validation Strategy:
        - No client-side validation in form
        - Relies on BookController to validate data
        - Displays controller error messages in red labels
    
    Stock Management:
        - Stock field intentionally omitted from form
        - Stock is calculated by InventoryService from inventory entries
        - Users cannot directly set stock via this form
    
    See Also:
        - controllers.book_controller.BookController: Data operations
        - ui.widget_factory: Widget creation utilities
    """
    
    def __init__(self, parent=None, mode="create", book_id=None):
        """Initialize the book form with specified mode and optional book ID.
        
        Creates and configures the complete form interface including theme application,
        icon loading, field setup, and mode-specific behavior. In edit mode, automatically
        loads existing book data.
        
        Purpose:
            Provides a flexible, theme-consistent form interface for book management
            that adapts to create/edit contexts while maintaining visual and functional
            consistency across the application.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor with parent reference
            2. Store parent window reference for focus restoration
            3. Attempt window scaling configuration
            4. Apply theme to window (with fallback)
            5. Load bookpile icon from assets (with fallback)
            6. Set window title and geometry
            7. Initialize BookController
            8. Store mode and book_id
            9. Create main container frame
            10. Build title area (icon + label)
            11. Build form fields (6 entries)
            12. Configure ID field based on mode
            13. Build action buttons (primary + cancel)
            14. If edit mode: Load book data via load_book()
            15. Set window close protocol to _on_cancel
        
        Mode-Specific Behavior:
            Create Mode:
            - ID entry disabled with placeholder "Auto (se asignará)"
            - All other fields empty
            - Primary button: "Crear Libro"
            
            Edit Mode:
            - ID entry populated with book ID and disabled
            - All fields populated with existing data (via load_book)
            - Primary button: "Actualizar Libro"
        
        Window Scaling:
            Attempts to inherit scaling from parent window using:
            `ctk.set_window_scaling(ctk._get_window_scaling(self))`
            
            Fallback: Uses default scaling if configuration fails
        
        Theme Application:
            Primary: `theme.apply_theme(self)`
            Fallback: `self.configure(fg_color=theme.BG_COLOR)`
            
            Ensures consistent warm beige background
        
        Icon Loading:
            Path: `ui/book/assets/twemoji/bookpile.png`
            Size: 36x36 pixels
            Format: CTkImage (supports HiDPI scaling)
            
            Fallback: icon_book = None (title still displays without icon)
        
        Field Configuration:
            All entries use 6px vertical padding for consistent spacing.
            All entries fill horizontally (fill="x") for uniform width.
            
            ID field special handling:
            - Create mode: disabled, placeholder "Auto (se asignará)"
            - Edit mode: disabled, populated with book.get_id()
        
        Button Layout:
            Horizontal side-by-side layout:
            - Primary button on left (8px right padding)
            - Small cancel button on right
            - Both have 6px vertical padding
        
        Error Handling:
            All optional operations protected:
            - Window scaling: Non-fatal if fails
            - Theme application: Tries fallback method
            - Icon loading: Continues without icon
            - State configuration: Continues if state change fails
            - Protocol setup: Form still closable via _on_cancel button
        
        Args:
            parent (CTk, optional): Parent window for focus restoration. Defaults to None.
            mode (str, optional): Operating mode ("create" or "edit"). Defaults to "create".
            book_id (str, optional): Book ID for edit mode. Defaults to None.
        
        Side Effects:
            - Creates new toplevel window
            - Loads icon image from disk
            - Initializes BookController
            - If edit mode: Loads book data from controller
            - Sets window close protocol
            - Displays window on screen
        
        Raises:
            None: All exceptions caught and handled gracefully
        
        Example:
            >>> # Create new book
            >>> form = BookForm(parent=main_menu, mode="create")
            
            >>> # Edit existing book
            >>> form = BookForm(parent=main_menu, mode="edit", book_id="B001")
        """
        # Initialize as a Toplevel attached to the main CTk root
        super().__init__(parent)
        # keep parent reference to restore focus when closing
        self._parent_window = parent
        
        # Apply window scaling for this toplevel
        try:
            ctk.set_window_scaling(ctk._get_window_scaling(self))
        except Exception:
            pass
        
        # Apply theme colors to this window and create a main container to match MainMenu
        try:
            theme.apply_theme(self)
        except Exception:
            try:
                self.configure(fg_color=theme.BG_COLOR)
            except Exception:
                pass

        # Load twemoji assets (defensive)
        assets_path = os.path.join(os.path.dirname(__file__), "assets", "twemoji")
        try:
            # load bookpile icon for consistency with main menu
            self.icon_book = ctk.CTkImage(Image.open(os.path.join(assets_path, "bookpile.png")), size=(36, 36))
        except Exception:
            self.icon_book = None

        # Ensure window is initially visible and properly titled
        self.title("Book Manager")
        self.geometry("500x600")

        self.controller = BookController()
        self.mode = mode
        self.book_id = book_id

        # Main container (keeps spacing and background consistent)
        container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR, corner_radius=12)
        container.pack(expand=True, fill="both", padx=20, pady=20)

        # Title area
        title_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        title_frame.pack(pady=(6, 12))
        if self.icon_book is not None:
            icon_lbl = ctk.CTkLabel(title_frame, image=self.icon_book, text="")
            icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = wf.create_title_label(title_frame, "Crear Libro")
        title_lbl.pack(side="left")

        # Form fields placed in a simple vertical stack inside the container
        form_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        form_frame.pack(expand=True, fill="both")

        # Campos
        # For create mode we show an ID entry but disabled and with a hint
        # (the controller/service will auto-generate the ID). In edit mode we
        # allow showing the current ID but keep it disabled so it can't be
        # changed.
        id_placeholder = "ID" if mode == "edit" else "Auto (se asignará)"
        self.entry_id = ctk.CTkEntry(form_frame, placeholder_text=id_placeholder)
        self.entry_id.pack(pady=6, fill="x")
        if mode == "create":
            try:
                # disable manual editing in create mode
                self.entry_id.configure(state="disabled")
            except Exception:
                pass

        self.entry_isbn = ctk.CTkEntry(form_frame, placeholder_text="ISBN")
        self.entry_isbn.pack(pady=6, fill="x")

        self.entry_title = ctk.CTkEntry(form_frame, placeholder_text="Título")
        self.entry_title.pack(pady=6, fill="x")

        self.entry_author = ctk.CTkEntry(form_frame, placeholder_text="Autor")
        self.entry_author.pack(pady=6, fill="x")

        self.entry_weight = ctk.CTkEntry(form_frame, placeholder_text="Peso")
        self.entry_weight.pack(pady=6, fill="x")

        self.entry_price = ctk.CTkEntry(form_frame, placeholder_text="Precio")
        self.entry_price.pack(pady=6, fill="x")

        # Action button area (primary + small 'Regresar' cancel button)
        action_frame = ctk.CTkFrame(container, fg_color=theme.BG_COLOR, corner_radius=0)
        action_frame.pack(pady=(12, 6))

        # Botón según modo
        if mode == "create":
            btn = wf.create_primary_button(action_frame, text="Crear Libro", command=self.create_book)
        else:
            btn = wf.create_primary_button(action_frame, text="Actualizar Libro", command=self.update_book)

        # small cancel/back button to return to main menu
        cancel_btn = wf.create_small_button(action_frame, text="Regresar", command=self._on_cancel)

        # pack side-by-side for better UX
        btn.pack(side="left", padx=(0, 8), pady=6)
        cancel_btn.pack(side="left", pady=6)

        # Si estás en modo edición, carga los datos
        if mode == "edit" and book_id:
            self.load_book()

        # Ensure closing via window manager also triggers our cancel logic
        try:
            self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        except Exception:
            pass

    def load_book(self):
        """Load existing book data and populate form fields in edit mode.
        
        Retrieves book data from the controller using the stored book_id and
        populates all form fields with the existing values. The ID field is
        populated and then disabled to prevent modification.
        
        Purpose:
            Prepares the form for editing by pre-filling all fields with current
            book data, allowing users to see existing values and modify only what
            needs to change.
        
        Workflow:
            1. Call controller.get_book(book_id)
            2. Check if book exists (early return if None)
            3. Populate ID field and disable it
            4. Populate all data fields (ISBN, title, author, weight, price)
        
        Field Population:
            - ID: Inserted and disabled (read-only)
            - ISBN: book.get_ISBNCode()
            - Title: book.get_title()
            - Author: book.get_author()
            - Weight: book.get_weight()
            - Price: book.get_price()
        
        Stock Field:
            Stock is intentionally NOT loaded or editable in this form.
            Stock is managed by InventoryService and calculated from inventory
            entries, not directly editable via book records.
        
        Early Return:
            If controller.get_book() returns None (book not found), the method
            returns early without modifying form fields. This can happen if:
            - Book was deleted between form opening and data load
            - Invalid book_id was provided
            - Database/JSON file corruption
        
        State Management:
            ID field is disabled AFTER insertion to ensure the value is visible
            but cannot be modified. This follows the pattern:
            ```python
            entry.insert(0, value)        # Populate
            entry.configure(state="disabled")  # Make read-only
            ```
        
        Args:
            None (uses self.book_id and self.controller)
        
        Returns:
            None
        
        Side Effects:
            - Queries controller for book data
            - Populates all form entry fields
            - Disables ID entry field
        
        Raises:
            None: Implicitly relies on controller error handling
        
        Called By:
            - __init__: Automatically called in edit mode after UI construction
        
        Example State After Load:
            ```
            ID Entry: "B001" (disabled, grayed out)
            ISBN Entry: "978-3-16-148410-0"
            Title Entry: "The Great Gatsby"
            Author Entry: "F. Scott Fitzgerald"
            Weight Entry: "0.5"
            Price Entry: "25000"
            ```
        """
        book = self.controller.get_book(self.book_id)
        if not book:
            return
        
        self.entry_id.insert(0, book.get_id())
        self.entry_id.configure(state="disabled")

        self.entry_isbn.insert(0, book.get_ISBNCode())
        self.entry_title.insert(0, book.get_title())
        self.entry_author.insert(0, book.get_author())
        self.entry_weight.insert(0, book.get_weight())
        self.entry_price.insert(0, book.get_price())
        # stock is managed by InventoryService (calculated from inventory entries)
        # the form does not allow editing stock directly

    def create_book(self):
        """Collect form data and create new book via controller in create mode.
        
        Gathers all field values into a dictionary and passes them to the controller
        for validation and creation. On success, closes the form and restores parent
        focus. On error, displays the error message in red within the form.
        
        Purpose:
            Primary action method for create mode that orchestrates data collection,
            controller invocation, success handling (form closure), and error display.
        
        Workflow:
            1. Data Collection:
               - Build dictionary from all entry field values
               - Include all fields: id, ISBNCode, title, author, weight, price
            
            2. Controller Invocation:
               - Call controller.create_book(data)
               - Controller validates and persists the book
            
            3. Success Handling:
               - Call _on_cancel() to close form
               - Restores parent window focus
               - Returns user to main menu/parent window
            
            4. Error Handling:
               - Catch any exceptions from controller
               - Create red label with error message
               - Pack label into form (stacks below buttons)
        
        Data Structure:
            ```python
            data = {
                "id": str,          # Auto-generated by controller (field disabled)
                "ISBNCode": str,    # ISBN from entry
                "title": str,       # Title from entry
                "author": str,      # Author from entry
                "weight": str,      # Weight from entry (controller converts to float)
                "price": str        # Price from entry (controller converts to float)
            }
            ```
        
        Validation:
            - No client-side validation performed
            - Controller validates all fields:
              * Required fields presence
              * Numeric formats for weight and price
              * ISBN format/uniqueness
              * Business rules
        
        Success Path:
            ```
            User clicks "Crear Libro"
            → create_book() collects data
            → controller.create_book(data) validates and saves
            → Success: _on_cancel() closes form
            → Parent window regains focus
            ```
        
        Error Path:
            ```
            User clicks "Crear Libro"
            → create_book() collects data
            → controller.create_book(data) raises exception
            → Exception caught: Red error label created
            → Error message displayed in form
            → Form remains open for correction
            ```
        
        Error Display Limitations:
            - Error labels stack (no clearing mechanism)
            - Multiple failed attempts create multiple error labels
            - No validation feedback until submission
        
        Args:
            None (reads from form entry fields)
        
        Returns:
            None
        
        Side Effects:
            - Calls controller to create book
            - On success: Closes form and restores parent focus
            - On error: Creates and displays error label in form
        
        Raises:
            None: All exceptions caught and displayed as error labels
        
        Example Error Messages:
            - "ISBN is required"
            - "Weight must be a positive number"
            - "Price must be greater than 0"
            - "ISBN already exists"
        """
        data = {
            "id": self.entry_id.get(),
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
        }

        try:
            self.controller.create_book(data)
            # Close form after successful creation and restore main menu focus
            try:
                self._on_cancel()
            except Exception:
                try:
                    ctk.CTkLabel(self, text="Libro creado exitosamente!").pack()
                except Exception:
                    pass
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def update_book(self):
        """Collect form data and update existing book via controller in edit mode.
        
        Gathers all editable field values into a dictionary and passes them to the
        controller for validation and update. On success, displays a confirmation
        message. On error, displays the error message in red within the form.
        
        Purpose:
            Primary action method for edit mode that orchestrates data collection,
            controller invocation, and success/error feedback display.
        
        Workflow:
            1. Data Collection:
               - Build dictionary from editable fields only
               - Exclude ID (read-only, uses self.book_id)
               - Include: ISBNCode, title, author, weight, price
            
            2. Controller Invocation:
               - Call controller.update_book(book_id, data)
               - Controller validates and persists changes
            
            3. Success Handling:
               - Create success label: "Libro actualizado!"
               - Pack label into form (visible feedback)
               - Form remains open (allows viewing updated data)
            
            4. Error Handling:
               - Catch any exceptions from controller
               - Create red label with error message
               - Pack label into form (stacks below buttons)
        
        Data Structure:
            ```python
            data = {
                "ISBNCode": str,    # Updated ISBN from entry
                "title": str,       # Updated title from entry
                "author": str,      # Updated author from entry
                "weight": str,      # Updated weight from entry
                "price": str        # Updated price from entry
            }
            ```
            
            Note: ID is NOT included (passed separately as book_id parameter)
        
        Validation:
            - No client-side validation performed
            - Controller validates all fields:
              * Required fields presence
              * Numeric formats for weight and price
              * ISBN uniqueness (if changed)
              * Business rules
        
        Success Path:
            ```
            User edits fields and clicks "Actualizar Libro"
            → update_book() collects data
            → controller.update_book(book_id, data) validates and saves
            → Success: "Libro actualizado!" label displayed
            → Form remains open with updated values
            ```
        
        Error Path:
            ```
            User edits fields and clicks "Actualizar Libro"
            → update_book() collects data
            → controller.update_book(book_id, data) raises exception
            → Exception caught: Red error label created
            → Error message displayed in form
            → Form remains open for correction
            ```
        
        Success Message Limitations:
            - Success labels stack (no clearing mechanism)
            - Multiple successful updates create multiple success labels
            - Form remains open (user must manually close)
        
        Difference from create_book:
            1. Uses self.book_id instead of data["id"]
            2. Shows success message instead of closing form
            3. Form remains open after success
            4. Only editable fields included in data dictionary
        
        Args:
            None (reads from form entry fields and uses self.book_id)
        
        Returns:
            None
        
        Side Effects:
            - Calls controller to update book
            - Creates and displays success/error label in form
        
        Raises:
            None: All exceptions caught and displayed as error labels
        
        Example Messages:
            Success: "Libro actualizado!"
            Error: "Weight must be a positive number"
        """
        data = {
            "id": self.entry_id.get(),
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
        }

        try:
            self.controller.create_book(data)
            # Close form after successful creation and restore main menu focus
            try:
                self._on_cancel()
            except Exception:
                try:
                    ctk.CTkLabel(self, text="Libro creado exitosamente!").pack()
                except Exception:
                    pass
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def update_book(self):
        data = {
            "ISBNCode": self.entry_isbn.get(),
            "title": self.entry_title.get(),
            "author": self.entry_author.get(),
            "weight": self.entry_weight.get(),
            "price": self.entry_price.get(),
        }

        try:
            self.controller.update_book(self.book_id, data)
            ctk.CTkLabel(self, text="Libro actualizado!").pack()
        except Exception as e:
            ctk.CTkLabel(self, text=str(e), text_color="red").pack()

    def _on_cancel(self):
        """Close form window and restore focus to parent window.
        
        Destroys the form toplevel window and attempts to restore focus to the
        parent window (typically main menu) using multiple focus restoration
        techniques for reliability across different systems.
        
        Purpose:
            Provides clean form closure with proper focus management, ensuring
            users seamlessly return to the parent window without needing to
            manually click or activate it.
        
        Workflow:
            1. Form Destruction:
               - Call self.destroy() to close toplevel window
               - Fallback: self.withdraw() if destroy fails (hides window)
            
            2. Parent Window Check:
               - Check if _parent_window attribute exists
               - Exit if no parent reference available
            
            3. Focus Restoration:
               - Call parent.deiconify() to ensure window is visible
               - Call parent.lift() to bring window to front
               - Call parent.focus_force() to grab keyboard focus
               - Each step wrapped in try-except for robustness
        
        Focus Restoration Strategy:
            Multiple methods used for cross-platform reliability:
            
            1. deiconify():
               - Makes window visible if minimized/iconified
               - No effect if already visible
               - Ensures window is on screen
            
            2. lift():
               - Raises window above other windows
               - Brings to front of window stack
               - Makes window visible to user
            
            3. focus_force():
               - Forcefully grabs keyboard focus
               - More aggressive than focus()
               - Works on most platforms
        
        Error Handling:
            All operations protected with try-except blocks:
            - destroy(): Fallback to withdraw() if fails
            - Parent access: Checks attribute existence
            - Each focus operation: Individual try-except
            - Continues silently on any failure
        
        Use Cases:
            1. Cancel Button Click:
               - User clicks "Regresar" button
               - Form closes without saving
               - Parent regains focus
            
            2. Successful Creation:
               - create_book() succeeds
               - Calls _on_cancel() to close form
               - Parent regains focus
            
            3. Window Manager Close:
               - User clicks X button in title bar
               - WM_DELETE_WINDOW protocol triggers _on_cancel
               - Form closes gracefully
        
        Parent Window Types:
            Typically the parent is:
            - MainMenu: Main application window
            - Other toplevel windows: Dialog or form windows
        
        Fallback Behavior:
            If any focus restoration fails:
            - Form still closes successfully
            - User must manually click parent window
            - Non-fatal degradation (usability impact only)
        
        Args:
            None (uses self and self._parent_window)
        
        Returns:
            None
        
        Side Effects:
            - Destroys/hides form window
            - Restores parent window visibility and focus
        
        Raises:
            None: All exceptions silently caught and handled
        
        Protocol Integration:
            Set in __init__ via:
            ```python
            self.protocol("WM_DELETE_WINDOW", self._on_cancel)
            ```
            
            Ensures window manager close button (X) triggers this method.
        
        Example Flow:
            ```
            User clicks "Regresar"
            → _on_cancel() called
            → self.destroy() closes form window
            → parent.deiconify() ensures parent visible
            → parent.lift() brings parent to front
            → parent.focus_force() grabs keyboard focus
            → User sees parent window active and focused
            ```
        """
        """Close this form and return focus to the parent/main menu."""
        try:
            # destroy this toplevel
            self.destroy()
        except Exception:
            try:
                self.withdraw()
            except Exception:
                pass

        # try to restore focus to parent window
        try:
            if getattr(self, '_parent_window', None):
                parent = self._parent_window
                try:
                    parent.deiconify()
                except Exception:
                    pass
                try:
                    parent.lift()
                    parent.focus_force()
                except Exception:
                    pass
        except Exception:
            pass

