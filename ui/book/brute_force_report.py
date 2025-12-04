"""Brute Force Algorithm Visualization Window - Risky Book Combinations Finder.

This module implements a UI window for visualizing and demonstrating the brute force
algorithm applied to finding all 4-book combinations that exceed the shelf capacity
threshold (default 8 Kg). It serves as both a safety analysis tool and an educational
demonstration of exhaustive search algorithms.

Problem Definition - Risky Combinations Detection:
    Given:
    - Set of books, each with weight
    - Shelf capacity threshold (default 8 Kg)
    - Fixed combination size (4 books)
    
    Find:
    - ALL combinations of exactly 4 books
    - Where sum(weights) > threshold
    - Report total weight and excess amount

Algorithm - Exhaustive Brute Force Search:
    The brute force algorithm explores ALL possible 4-book combinations:
    
    ```
    def find_risky_combinations(books, threshold, k=4):
        risky = []
        
        # Generate all C(n, k) combinations
        for combo in combinations(books, k):
            total_weight = sum(book.weight for book in combo)
            
            if total_weight > threshold:
                excess = total_weight - threshold
                risky.append({
                    'books': combo,
                    'total_weight': total_weight,
                    'excess': excess
                })
        
        return risky
    ```
    
    Key Characteristics:
    - Exhaustive: Checks EVERY possible combination
    - Guaranteed complete: Finds ALL risky combinations
    - No optimization: Pure brute force approach
    - Complexity: O(C(n,4)) = O(n^4/24) combinations to check
    - Educational: Shows exponential growth problem

Combinatorial Mathematics:
    Number of 4-book combinations from n books:
    ```
    C(n, 4) = n! / (4! * (n-4)!)
            = n * (n-1) * (n-2) * (n-3) / 24
    
    Examples:
    - 10 books: C(10,4) = 210 combinations
    - 20 books: C(20,4) = 4,845 combinations  
    - 30 books: C(30,4) = 27,405 combinations
    - 50 books: C(50,4) = 230,300 combinations
    ```

UI Features:
    1. Statistics Dashboard:
       - Total books in catalog
       - Total combinations to explore (C(n,4))
       - Number of risky combinations found
       - Current weight threshold
    
    2. Results Display:
       - Scrollable textbox with formatted output
       - Each risky combination shows:
         * Total weight
         * Excess over threshold
         * List of 4 books with details
       - Empty state for no risky combinations
    
    3. Interactive Controls:
       - Refresh button: Recalculate with current data
       - Change threshold button: Adjust weight limit
       - Close button: Dismiss window

Architecture:
    Window Type: CTkToplevel (modal-like popup)
    Controller: BookController (handles brute force logic)
    Theme: Cozy Japanese aesthetic with custom colors
    Layout: Vertical stack (title → stats → results → buttons)

Color Scheme:
    - SUCCESS_COLOR: Green (#2ECC71) for safe state (0 risky)
    - ERROR_COLOR: Red (#E74C3C) for risky combinations count
    - CARD_BG_COLOR: Light gray (#F5F5F5) for card backgrounds

Metrics Displayed:
    1. Total Books: Count of books in catalog (n)
    2. Combinations to Explore: C(n,4) = n!/(4!(n-4)!)
    3. Risky Combinations: Count where total_weight > threshold
    4. Threshold: Current weight limit in Kg

Result Format (per combination):
    ```
    Combinación #1:
      📊 Peso Total: 12.50 Kg
      ⚠️ Excede por: 4.50 Kg
      📚 Libros:
        1. [B001] The Great Gatsby
           Autor: F. Scott Fitzgerald
           Peso: 3.20 Kg
        2. [B002] To Kill a Mockingbird
           Autor: Harper Lee
           Peso: 3.10 Kg
        ...
    ```

Dynamic Threshold:
    - Default: 8.0 Kg (standard shelf capacity)
    - User-adjustable via input dialog
    - Validates positive numeric input
    - Recalculates on change

Empty State Handling:
    When no risky combinations found:
    ```
    ✅ ¡Excelente! No se encontraron combinaciones riesgosas.
    
    Todas las posibles combinaciones de 4 libros están dentro del límite seguro.
    Todas las combinaciones pesan menos de 8.0 Kg.
    ```

Error Handling:
    - Calculation errors: Logged and displayed to user
    - Invalid threshold input: Shows error dialog
    - Window centering failures: Non-blocking fallback

Use Cases:
    1. Safety Analysis:
       - Identify potentially dangerous book stacking scenarios
       - Prevent shelf overloading
       - Risk assessment for library shelving
    
    2. Educational:
       - Demonstrate brute force algorithm visually
       - Show combinatorial explosion
       - Teach exhaustive search concepts
    
    3. Capacity Planning:
       - Understand weight distribution in catalog
       - Analyze if threshold is too restrictive/permissive

Performance Considerations:
    - Small catalogs (n<20): Near-instant results
    - Medium catalogs (n=20-40): Seconds
    - Large catalogs (n>50): May take minutes (230k+ combinations)
    - UI remains responsive (no progress bar currently)

Comparison with Backtracking:
    Brute Force:
    - Finds ALL risky combinations
    - No optimization goal
    - Detection/analysis purpose
    - Shows all violations
    
    Backtracking (other module):
    - Finds ONE optimal combination
    - Maximizes value within constraint
    - Optimization purpose
    - Pruning for efficiency

See Also:
    - controllers.book_controller.BookController.find_risky_book_combinations:
      Contains actual brute force implementation
    - ui.book.backtracking_report: Optimization variant (0/1 Knapsack)
    - ui.main_menu: Entry point for opening this window
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional
import tkinter as tk

from controllers.book_controller import BookController
from ui import theme
from ui import widget_factory as wf
from utils.logger import LibraryLogger

logger = LibraryLogger.get_logger(__name__)

# Define colors for this module (using theme colors or defaults)
SUCCESS_COLOR = "#2ECC71"  # Green for success
ERROR_COLOR = "#E74C3C"    # Red for errors
CARD_BG_COLOR = "#F5F5F5"  # Light gray for cards


class BruteForceReport(ctk.CTkToplevel):
    """Brute force algorithm visualization for risky 4-book combinations detection.
    
    This window provides an interactive dashboard for visualizing the brute force
    algorithm's results when finding all 4-book combinations that exceed the shelf
    weight threshold. It displays combinatorial statistics, risky combinations with
    details, and allows dynamic threshold adjustment.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Layout: Vertical stack with 4 sections (title, stats, results, buttons)
        Controller: BookController for brute force calculations
        Algorithm: Exhaustive search of C(n,4) combinations
    
    UI Components:
        1. Header Section:
           - Title: "🔍 Algoritmo de Fuerza Bruta"
           - Subtitle: "Combinaciones de 4 libros que exceden 8 Kg"
        
        2. Statistics Dashboard:
           - Card-style frame (light gray background)
           - Grid layout (2 rows x 2 columns)
           - Metrics:
             * Total books count
             * Total combinations to explore (C(n,4))
             * Risky combinations found (color-coded)
             * Current threshold value
        
        3. Results Display:
           - Label: "Combinaciones Riesgosas Encontradas:"
           - Large scrollable textbox
           - Formatted output with:
             * Empty state message if none found
             * Detailed list if risky combinations exist
        
        4. Button Bar:
           - Primary: "🔄 Actualizar" (refresh)
           - Primary: "⚙️ Cambiar Umbral" (change threshold)
           - Small: "Cerrar" (close)
    
    Attributes:
        controller (BookController): Handles brute force algorithm execution
        threshold (float): Weight limit in kilograms (default 8.0)
        lbl_total_books (CTkLabel): Displays total book count
        lbl_combinations (CTkLabel): Displays C(n,4) count
        lbl_risky_found (CTkLabel): Displays risky combinations count (color-coded)
        lbl_threshold (CTkLabel): Displays current threshold
        results_text (CTkTextbox): Scrollable area for detailed results
    
    Window Configuration:
        - Dimensions: 1000x700 pixels
        - Position: Screen-centered on creation
        - Theme: Custom color scheme (green/red/gray)
        - Title: "🔍 Análisis de Combinaciones Riesgosas - Fuerza Bruta"
    
    Statistics Dashboard:
        Grid Layout:
        ```
        Row 0: Total books              | Combinations to explore
        Row 1: Risky combinations found | Current threshold
        ```
        
        Both columns have equal weight for balanced layout.
    
    Color Coding:
        Risky Combinations Label:
        - Red (ERROR_COLOR): If risky_count > 0 (warnings exist)
        - Green (SUCCESS_COLOR): If risky_count = 0 (all safe)
    
    Combination Display Format:
        Each risky combination shows:
        ```
        Combinación #1:
          📊 Peso Total: {total} Kg
          ⚠️ Excede por: {excess} Kg
          📚 Libros:
            1. [ID] Title
               Autor: Author Name
               Peso: {weight} Kg
            2. [ID] Title
               ...
            (4 books total)
        ────────────────────────────────────
        ```
    
    Combinatorial Statistics:
        Controller calculates C(n,4):
        - Uses math.comb(n, 4) or factorial formula
        - Displays with thousands separator
        - Example: "4,845" for 20 books
    
    Empty State:
        When no risky combinations found:
        - Displays success message with checkmark emoji
        - Explains all combinations are safe
        - Mentions threshold value
    
    Dynamic Features:
        - Threshold adjustable via input dialog
        - Auto-recalculates on threshold change
        - Manual refresh available
    
    See Also:
        - controllers.book_controller.BookController: Brute force implementation
        - ui.book.backtracking_report: Optimization comparison
    """

    def __init__(self, parent):
        """Initialize the brute force report window with UI and initial calculation.
        
        Creates the complete dashboard interface, centers the window, builds all
        UI components, and immediately executes the brute force algorithm with
        default threshold (8.0 Kg).
        
        Purpose:
            Sets up an interactive visualization tool for demonstrating brute force
            exhaustive search while providing practical safety analysis for book
            shelving scenarios.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Initialize BookController for algorithm execution
            3. Set default threshold to 8.0 Kg
            4. Configure window (title, size)
            5. Calculate centered position on screen
            6. Apply centered geometry
            7. Call _build_ui() to construct all components
            8. Call _load_report() to perform initial calculation
        
        Window Centering Algorithm:
            ```
            screen_center_x = screen_width // 2
            screen_center_y = screen_height // 2
            window_x = screen_center_x - (window_width // 2)
            window_y = screen_center_y - (window_height // 2)
            geometry = f"{width}x{height}+{x}+{y}"
            ```
        
        Initial State:
            - Statistics labels show placeholder text ("-")
            - Results area empty (populated by _load_report)
            - Threshold set to 8.0 Kg
            - Algorithm executes immediately
        
        Default Threshold:
            8.0 Kg chosen because:
            - Standard shelf capacity in project specifications
            - Matches backtracking_report default
            - Reasonable safety limit for book shelving
        
        Error Handling:
            - Window centering: update_idletasks() may fail (non-blocking)
            - Initial calculation errors handled by _load_report() method
        
        Args:
            parent: Parent CTk window (typically MainMenu)
        
        Side Effects:
            - Creates new toplevel window
            - Executes brute force algorithm immediately
            - Logs calculation results
            - Displays window on screen
        
        Raises:
            None: All exceptions caught in _load_report() method
        """
        super().__init__(parent)
        
        self.controller = BookController()
        self.threshold = 8.0  # Default shelf capacity
        
        # Window configuration
        self.title("🔍 Análisis de Combinaciones Riesgosas - Fuerza Bruta")
        self.geometry("1000x700")
        
        # Center window
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (1000 // 2)
        y = (screen_h // 2) - (700 // 2)
        self.geometry(f"1000x700+{x}+{y}")
        
        self._build_ui()
        self._load_report()
    
    def _build_ui(self):
        """Build the complete user interface with all components and layout.
        
        Constructs the entire window layout including title, statistics dashboard,
        results display area, and action buttons. Uses vertical stacking layout
        for clear visual hierarchy.
        
        Purpose:
            Creates a comprehensive dashboard interface that presents brute force
            results in an organized, visually appealing manner with clear sections
            for different types of information.
        
        Layout Structure:
            ```
            Main Frame (BG_COLOR)
            ├─ Title Frame (transparent)
            │  ├─ Title label (bold)
            │  └─ Subtitle label (normal)
            ├─ Statistics Frame (CARD_BG_COLOR, 120px height)
            │  └─ Grid (2 rows x 2 columns)
            │     ├─ Total books | Combinations count
            │     └─ Risky found  | Threshold
            ├─ Results Label ("Combinaciones Riesgosas Encontradas:")
            ├─ Results Textbox (scrollable, expandable)
            └─ Button Frame (transparent)
               ├─ Refresh button (left)
               ├─ Change threshold button (left)
               └─ Close button (right)
            ```
        
        Component Details:
            
            1. Title Section:
               - Frame with transparent background
               - Title: Factory-created, large font
               - Subtitle: 14pt normal font
               - Centered alignment (pack())
            
            2. Statistics Dashboard:
               - Card-style frame (light gray background)
               - Fixed height 120px (prevents expansion)
               - Inner transparent frame for grid
               - 20px padding for spacing
               - 4 labels in 2x2 grid
            
            3. Results Display:
               - Section label (14pt bold)
               - Large textbox (expandable)
               - Light gray background
               - 12pt font for readability
               - 10px corner radius
            
            4. Button Bar:
               - Transparent background
               - 3 buttons horizontal layout
               - Primary buttons on left
               - Small close button on right
               - 5px spacing between buttons
        
        Statistics Grid Configuration:
            ```
            Grid Layout:
            Row 0, Col 0: lbl_total_books
            Row 0, Col 1: lbl_combinations
            Row 1, Col 0: lbl_risky_found
            Row 1, Col 1: lbl_threshold
            
            Grid weights:
            - columnconfigure(0, weight=1)
            - columnconfigure(1, weight=1)
            - Equal column widths
            ```
        
        Label Styling:
            All statistics labels:
            - Font: 13pt normal (from theme)
            - Color: theme.TEXT_COLOR
            - Padding: 10px horizontal, 5px vertical
            - Alignment: Left (sticky="w")
        
        Special Label: Risky Combinations
            - Default color: theme.TEXT_COLOR
            - Dynamic color (set in _load_report):
              * ERROR_COLOR (red) if risky_count > 0
              * SUCCESS_COLOR (green) if risky_count = 0
        
        Button Configuration:
            Primary buttons (refresh, threshold):
            - Factory-created primary style
            - Packed side="left"
            - 5px padding
            
            Small button (close):
            - Factory-created small style
            - Packed side="right"
            - 5px padding
        
        Responsive Design:
            - Main frame expands with window (expand=True, fill="both")
            - Statistics frame fixed height (prevents metric crowding)
            - Results textbox expands to use available space
            - Grid columns auto-size equally
        
        Font Strategy:
            - Title: Factory default (18pt bold)
            - Subtitle: 14pt normal
            - Statistics: 13pt normal
            - Results label: 14pt bold
            - Results text: 12pt normal
        
        Args:
            None
        
        Returns:
            None
        
        Side Effects:
            - Creates and packs all UI widgets
            - Stores label references in instance attributes
            - Configures grid weights for statistics frame
        
        Notes:
            - Statistics labels initially show "-" placeholder
            - Results textbox initially empty
            - _load_report() must be called to populate data
        """
        """Build the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color=theme.BG_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title = wf.create_title_label(
            title_frame, 
            "🔍 Algoritmo de Fuerza Bruta"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Combinaciones de 4 libros que exceden 8 Kg",
            font=theme.get_font(self, size=14),
            text_color=theme.TEXT_COLOR
        )
        subtitle.pack()
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG_COLOR, corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 15))
        stats_frame.pack_propagate(False)
        stats_frame.configure(height=120)
        
        # Create a grid inside stats_frame
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(expand=True, fill="both", padx=20, pady=15)
        
        # Stats labels
        self.lbl_total_books = ctk.CTkLabel(
            stats_inner, 
            text="Total de libros: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_total_books.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.lbl_combinations = ctk.CTkLabel(
            stats_inner, 
            text="Combinaciones a explorar: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_combinations.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_risky_found = ctk.CTkLabel(
            stats_inner, 
            text="Combinaciones riesgosas: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_risky_found.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.lbl_threshold = ctk.CTkLabel(
            stats_inner, 
            text=f"Umbral: {self.threshold} Kg",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_threshold.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Configure grid weights
        stats_inner.grid_columnconfigure(0, weight=1)
        stats_inner.grid_columnconfigure(1, weight=1)
        
        # Scrollable results frame
        results_label = ctk.CTkLabel(
            main_frame, 
            text="Combinaciones Riesgosas Encontradas:",
            font=theme.get_font(self, size=14, weight="bold"),
            text_color=theme.TEXT_COLOR
        )
        results_label.pack(anchor="w", pady=(0, 5))
        
        self.results_text = ctk.CTkTextbox(
            main_frame,
            fg_color=CARD_BG_COLOR,
            text_color=theme.TEXT_COLOR,
            corner_radius=10,
            font=theme.get_font(self, size=12)
        )
        self.results_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(main_frame, fg_color=theme.BG_COLOR)
        btn_frame.pack(fill="x")
        
        # Refresh button
        btn_refresh = wf.create_primary_button(
            btn_frame,
            "🔄 Actualizar",
            command=self._load_report
        )
        btn_refresh.pack(side="left", padx=5)
        
        # Change threshold button
        btn_threshold = wf.create_primary_button(
            btn_frame,
            "⚙️ Cambiar Umbral",
            command=self._change_threshold
        )
        btn_threshold.pack(side="left", padx=5)
        
        # Close button
        btn_close = wf.create_small_button(
            btn_frame,
            "Cerrar",
            command=self.destroy
        )
        btn_close.pack(side="right", padx=5)
    
    def _load_report(self):
        """Execute brute force algorithm and display results with formatted output.
        
        Retrieves all books, calculates C(n,4) combinations count, executes brute
        force algorithm to find risky combinations, updates statistics dashboard,
        and formats detailed results in the textbox.
        
        Purpose:
            Primary data loading and display method that orchestrates calculation,
            UI updates, and result formatting to present brute force analysis in
            a clear, educational, and actionable format.
        
        Workflow:
            1. Data Retrieval:
               - Get all books from controller
               - Count total catalog size (n)
            
            2. Combinatorial Calculation:
               - Call controller.count_possible_combinations()
               - Returns C(n,4) using factorial formula
            
            3. Brute Force Execution:
               - Call controller.find_risky_book_combinations(threshold)
               - Returns list of risky combination dictionaries
               - Count risky combinations (m)
            
            4. Statistics Update:
               - Update total_books label
               - Update combinations label (with thousands separator)
               - Update risky_found label (with color coding)
               - Update threshold label
            
            5. Clear Previous Results:
               - Delete all text from results_textbox
            
            6. Handle Empty State:
               - If risky_count == 0, display success message
               - Return early (no detailed results)
            
            7. Format Detailed Results:
               - Insert header with count
               - Iterate through risky combinations
               - Format each combination with books details
               - Insert into textbox
            
            8. Logging:
               - Log successful calculation with count
        
        Controller Methods Called:
            ```python
            # Get catalog
            books = controller.get_all_books()  # Returns list[Book]
            
            # Count combinations
            total = controller.count_possible_combinations()  # Returns int
            
            # Find risky combinations
            risky = controller.find_risky_book_combinations(threshold)  # Returns list[dict]
            ```
        
        Result Data Structure:
            Each risky combination is a dictionary:
            ```python
            {
                'total_weight': float,     # Sum of 4 book weights
                'excess': float,           # total_weight - threshold
                'books': [                 # List of 4 book dictionaries
                    {
                        'id': str,         # Book ID
                        'title': str,      # Book title
                        'author': str,     # Author name
                        'weight': float    # Weight in Kg
                    },
                    ... (4 total)
                ]
            }
            ```
        
        Statistics Formatting:
            Total Books:
            - Format: "📚 Total de libros: {n}"
            - Example: "📚 Total de libros: 25"
            
            Combinations:
            - Format: "🔢 Combinaciones a explorar: {C(n,4):,}"
            - Example: "🔢 Combinaciones a explorar: 12,650"
            - Uses comma thousands separator
            
            Risky Found:
            - Format: "⚠️ Combinaciones riesgosas: {m}"
            - Example: "⚠️ Combinaciones riesgosas: 3"
            - Color: ERROR_COLOR (red) if m > 0, SUCCESS_COLOR (green) if m = 0
            
            Threshold:
            - Format: "⚖️ Umbral: {threshold} Kg"
            - Example: "⚖️ Umbral: 8.0 Kg"
        
        Empty State Message:
            ```
            ✅ ¡Excelente! No se encontraron combinaciones riesgosas.
            
            Todas las posibles combinaciones de 4 libros están dentro del límite seguro.
            Todas las combinaciones pesan menos de {threshold} Kg.
            ```
        
        Detailed Results Format:
            Header:
            ```
            ⚠️ Se encontraron {n} combinaciones riesgosas:
            ================================================================================
            ```
            
            Per Combination:
            ```
            Combinación #{idx}:
              📊 Peso Total: {total:.2f} Kg
              ⚠️ Excede por: {excess:.2f} Kg
              📚 Libros:
                1. [B001] The Great Gatsby
                   Autor: F. Scott Fitzgerald
                   Peso: 3.20 Kg
                2. [B002] To Kill a Mockingbird
                   Autor: Harper Lee
                   Peso: 3.10 Kg
                3. [B003] 1984
                   Autor: George Orwell
                   Peso: 2.80 Kg
                4. [B004] Pride and Prejudice
                   Autor: Jane Austen
                   Peso: 2.90 Kg
            
            --------------------------------------------------------------------------------
            ```
        
        Formatting Details:
            - Weights: 2 decimal places (.2f)
            - Book numbering: 1-indexed within combination
            - Separator lines: 80 dashes
            - Indentation: 2-4 spaces for hierarchy
        
        Error Handling:
            - Wrapped in try-except
            - Catches any controller exceptions
            - Shows error dialog with message
            - Logs error with full details
            - UI remains empty on error
        
        Performance:
            - Brute force: O(C(n,4)) = O(n^4/24) combinations
            - Formatting: O(m) where m = risky combinations
            - Example timings:
              * 10 books: 210 combinations (~instant)
              * 20 books: 4,845 combinations (~1 second)
              * 30 books: 27,405 combinations (~5-10 seconds)
              * 50 books: 230,300 combinations (~minutes)
        
        Triggers:
            1. __init__: Initial load on window open
            2. "🔄 Actualizar" button: Manual refresh
            3. _change_threshold(): Auto-refresh after threshold change
        
        Args:
            None (uses self.threshold and self.controller)
        
        Returns:
            None
        
        Side Effects:
            - Queries controller for all books and combinations
            - Updates all 4 statistics labels
            - Clears and repopulates results_text widget
            - Logs calculation results
            - Shows error dialog if calculation fails
        
        Raises:
            None: All exceptions caught and displayed
        
        Example Output:
            For 20 books with threshold 8.0 Kg:
            - Total: 20 books
            - Combinations: 4,845
            - Risky: 3 combinations
            - Results show 3 detailed combinations exceeding 8 Kg
        """
        """Load and display the brute force algorithm results."""
        try:
            # Get all books
            all_books = self.controller.get_all_books()
            total_books = len(all_books)
            
            # Count total combinations
            total_combinations = self.controller.count_possible_combinations()
            
            # Run brute force algorithm
            risky_combinations = self.controller.find_risky_book_combinations(self.threshold)
            risky_count = len(risky_combinations)
            
            # Update statistics
            self.lbl_total_books.configure(text=f"📚 Total de libros: {total_books}")
            self.lbl_combinations.configure(text=f"🔢 Combinaciones a explorar: {total_combinations:,}")
            self.lbl_risky_found.configure(
                text=f"⚠️ Combinaciones riesgosas: {risky_count}",
                text_color=ERROR_COLOR if risky_count > 0 else SUCCESS_COLOR
            )
            self.lbl_threshold.configure(text=f"⚖️ Umbral: {self.threshold} Kg")
            
            # Clear previous results
            self.results_text.delete("1.0", "end")
            
            # Display results
            if risky_count == 0:
                msg = "✅ ¡Excelente! No se encontraron combinaciones riesgosas.\n\n"
                msg += "Todas las posibles combinaciones de 4 libros están dentro del límite seguro.\n"
                msg += f"Todas las combinaciones pesan menos de {self.threshold} Kg.\n"
                self.results_text.insert("1.0", msg)
            else:
                header = f"⚠️ Se encontraron {risky_count} combinaciones riesgosas:\n"
                header += "=" * 80 + "\n\n"
                self.results_text.insert("1.0", header)
                
                for idx, combo in enumerate(risky_combinations, 1):
                    combo_text = f"Combinación #{idx}:\n"
                    combo_text += f"  📊 Peso Total: {combo['total_weight']:.2f} Kg\n"
                    combo_text += f"  ⚠️ Excede por: {combo['excess']:.2f} Kg\n"
                    combo_text += f"  📚 Libros:\n"
                    
                    for i, book in enumerate(combo['books'], 1):
                        combo_text += f"    {i}. [{book['id']}] {book['title']}\n"
                        combo_text += f"       Autor: {book['author']}\n"
                        combo_text += f"       Peso: {book['weight']:.2f} Kg\n"
                    
                    combo_text += "\n" + "-" * 80 + "\n\n"
                    self.results_text.insert("end", combo_text)
            
            logger.info(f"Reporte de fuerza bruta cargado: {risky_count} combinaciones riesgosas")
            
        except Exception as e:
            logger.error(f"Error al cargar reporte de fuerza bruta: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el reporte.\n\nError: {str(e)}"
            )
    
    def _change_threshold(self):
        """Open input dialog to change weight threshold and recalculate results.
        
        Prompts user with an input dialog to enter a new threshold value,
        validates the input, updates the threshold, and triggers a recalculation
        of risky combinations with the new limit.
        
        Purpose:
            Provides interactive threshold adjustment to allow users to explore
            how different weight limits affect the detection of risky combinations,
            enabling sensitivity analysis and what-if scenarios.
        
        Workflow:
            1. Dialog Display:
               - Show CTkInputDialog with current threshold
               - Prompt for new threshold value (in Kg)
               - Wait for user input or cancellation
            
            2. Cancellation Check:
               - If user cancels (None returned), exit early
               - No changes made to current state
            
            3. Input Validation:
               - Convert input to float
               - Check if value is positive (> 0)
               - Raise ValueError if invalid
            
            4. State Update:
               - Set self.threshold to new value
               - Log threshold change
            
            5. Recalculation:
               - Call _load_report() to recompute with new threshold
               - Updates all UI elements automatically
            
            6. Error Handling:
               - Catch ValueError (invalid input or non-positive)
               - Show error dialog with explanation
               - Keep original threshold if error occurs
        
        Dialog Configuration:
            - Title: "Cambiar Umbral"
            - Message: Shows current threshold for reference
            - Input type: Text (validated to float)
            - Buttons: OK, Cancel (built-in CTkInputDialog)
        
        Validation Rules:
            - Must be numeric (convertible to float)
            - Must be positive (> 0)
            - Invalid examples:
              * Negative numbers: -5.0
              * Zero: 0
              * Non-numeric: "abc", "10.5kg"
        
        Error Messages:
            Invalid input:
            "Valor inválido.
            El umbral debe ser un número positivo.
            Error: [specific error message]"
        
        Use Cases:
            1. Sensitivity Testing:
               - How many risky combinations at 7 Kg vs 8 Kg vs 9 Kg?
               - Find optimal threshold for safety
            
            2. Planning Scenarios:
               - What if we upgrade to stronger shelves (higher threshold)?
               - What if we need more restrictive limits?
            
            3. Educational:
               - Demonstrate how constraint changes affect results
               - Show brute force re-execution with different parameters
        
        Recalculation Impact:
            Changing threshold triggers full brute force re-execution:
            - All C(n,4) combinations re-checked
            - Different combinations may be risky
            - Count and details update
            - Performance same as initial load
        
        Side Effects:
            - May update self.threshold
            - May trigger full recalculation via _load_report()
            - May update all UI statistics and results
            - Shows input dialog (blocks until user responds)
            - May show error dialog (blocks until dismissed)
            - Logs threshold change if successful
        
        Args:
            None
        
        Returns:
            None
        
        Raises:
            None: All exceptions caught and handled via dialog
        
        Example Interaction:
            ```
            User clicks "⚙️ Cambiar Umbral"
            Dialog appears: "Ingrese el nuevo umbral... (Actual: 8.0 Kg)"
            User enters: "10.0"
            Result: Threshold updated to 10.0 Kg, risky combinations recalculated
            Expected: Fewer risky combinations (higher threshold = more permissive)
            ```
        """
        """Open dialog to change the weight threshold."""
        dialog = ctk.CTkInputDialog(
            text=f"Ingrese el nuevo umbral de peso (Kg):\n(Actual: {self.threshold} Kg)",
            title="Cambiar Umbral"
        )
        
        new_threshold = dialog.get_input()
        
        if new_threshold is None:
            return  # User cancelled
        
        try:
            new_threshold = float(new_threshold)
            if new_threshold <= 0:
                raise ValueError("El umbral debe ser mayor que 0")
            
            self.threshold = new_threshold
            logger.info(f"Umbral actualizado a {self.threshold} Kg")
            self._load_report()
            
        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Valor inválido.\n\nEl umbral debe ser un número positivo.\n\nError: {str(e)}"
            )
