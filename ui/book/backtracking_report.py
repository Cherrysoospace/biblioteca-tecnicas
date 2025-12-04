"""Backtracking Algorithm Visualization Window - 0/1 Knapsack Problem Solver.

This module implements a UI window for visualizing and demonstrating the backtracking
algorithm applied to the 0/1 Knapsack Problem. It finds the optimal combination of books
that maximizes total value while respecting the shelf capacity constraint (default 8 Kg).

Problem Definition - 0/1 Knapsack:
    Given:
    - Set of books, each with weight (w) and value (price)
    - Shelf capacity constraint (C = 8 Kg by default)
    
    Find:
    - Subset of books that maximizes total value
    - Subject to: sum(weights) <= C
    - Each book can be selected 0 or 1 times (no duplicates)

Algorithm - Backtracking with Pruning:
    The backtracking algorithm explores all possible combinations using a
    decision tree approach with intelligent pruning:
    
    ```
    def backtrack(books, index, current_weight, current_value, capacity):
        # Base case: all books considered
        if index >= len(books):
            return (current_value, current_weight, [])
        
        # Pruning: if adding current book exceeds capacity, skip it
        if current_weight + books[index].weight > capacity:
            return backtrack(books, index+1, current_weight, current_value, capacity)
        
        # Explore two branches:
        # 1. Include current book
        include = backtrack(books, index+1,
                          current_weight + books[index].weight,
                          current_value + books[index].price,
                          capacity)
        
        # 2. Exclude current book
        exclude = backtrack(books, index+1, current_weight, current_value, capacity)
        
        # Return better solution
        return max(include, exclude, key=lambda x: x[0])
    ```
    
    Key Features:
    - Exhaustive search with pruning (explores valid combinations only)
    - Guaranteed optimal solution (global maximum)
    - Complexity: O(2^n) worst case, but pruning reduces practical runtime
    - Space: O(n) for recursion stack

UI Features:
    1. Statistics Dashboard:
       - Total books in catalog
       - Maximum value achieved
       - Total weight of selected books
       - Shelf capacity constraint
       - Number of books selected
       - Capacity utilization percentage
    
    2. Algorithm Information:
       - Brief explanation of backtracking approach
       - Pruning strategy description
    
    3. Results Display:
       - Scrollable textbox with formatted results
       - Solution summary (value, weight, efficiency metrics)
       - Detailed book list with individual metrics
       - Algorithm explanation and complexity analysis
       - Value-to-weight ratio for each book
    
    4. Interactive Controls:
       - Refresh button: Recalculate with current catalog
       - Change capacity button: Adjust shelf weight limit
       - Close button: Dismiss window

Architecture:
    Window Type: CTkToplevel (modal-like popup)
    Controller: BookController (handles backtracking logic)
    Theme: Cozy Japanese aesthetic with custom colors
    Layout: Vertical stack (stats → info → results → buttons)

Color Scheme:
    - SUCCESS_COLOR: Green (#2ECC71) for positive metrics
    - WARNING_COLOR: Orange (#F39C12) for warnings/limits
    - INFO_COLOR: Blue (#3498DB) for informational sections
    - CARD_BG_COLOR: Light gray (#F5F5F5) for card backgrounds

Metrics Displayed:
    1. Total Value: Sum of prices of selected books
    2. Total Weight: Sum of weights of selected books
    3. Book Count: Number of books in optimal solution
    4. Capacity Used: Percentage of shelf capacity utilized
    5. Average Value per Book: Total value / book count
    6. Average Weight per Book: Total weight / book count
    7. Efficiency (COP/Kg): Total value / total weight
    8. Per-book Efficiency: Individual book price / weight ratios

Dynamic Capacity:
    - Default: 8.0 Kg (standard shelf capacity)
    - User-adjustable via input dialog
    - Validates positive numeric input
    - Recalculates solution on capacity change

Error Handling:
    - Empty catalog: Displays informative message
    - Books exceeding capacity: Shows warning with reasons
    - Invalid capacity input: Shows error dialog
    - Calculation errors: Logged and displayed to user
    - Window centering failures: Non-blocking fallback

Use Cases:
    1. Library Planning:
       - Determine most valuable books for limited shelf space
       - Optimize shelf utilization for maximum value
    
    2. Educational:
       - Demonstrate backtracking algorithm visually
       - Show 0/1 Knapsack problem application
       - Teach optimization concepts
    
    3. Inventory Management:
       - Analyze value density of collection
       - Identify high-efficiency books (value/weight ratio)

See Also:
    - controllers.book_controller.BookController.find_optimal_shelf_selection:
      Contains actual backtracking implementation
    - ui.book.brute_force_report: Alternative exhaustive search approach
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
WARNING_COLOR = "#F39C12"  # Orange for warnings
INFO_COLOR = "#3498DB"     # Blue for info
CARD_BG_COLOR = "#F5F5F5"  # Light gray for cards


class BacktrackingReport(ctk.CTkToplevel):
    """Backtracking algorithm visualization window for optimal shelf book selection.
    
    This window provides an interactive dashboard for visualizing the backtracking
    algorithm's solution to the 0/1 Knapsack Problem applied to book selection.
    It displays statistics, solution details, and allows dynamic capacity adjustment.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Layout: Vertical stack with 4 main sections:
            1. Title and subtitle
            2. Statistics dashboard (6 metrics in grid)
            3. Algorithm info banner
            4. Scrollable results area
            5. Action buttons (refresh, change capacity, close)
        Controller: BookController for backtracking calculations
    
    UI Components:
        1. Header Section:
           - Title: "🎯 Algoritmo de Backtracking"
           - Subtitle: Objective description
        
        2. Statistics Dashboard:
           - Card-style frame with light gray background
           - Grid layout (3 rows x 2 columns)
           - Metrics:
             * Total books in catalog
             * Maximum value achieved
             * Total weight of selection
             * Shelf capacity constraint
             * Number of selected books
             * Capacity utilization percentage
        
        3. Info Banner:
           - Blue background (INFO_COLOR)
           - Brief algorithm explanation
           - Pruning strategy mention
        
        4. Results Display:
           - Large scrollable textbox
           - Formatted output with:
             * Solution summary header
             * Detailed book list
             * Per-book metrics (weight, price, efficiency)
             * Algorithm explanation footer
        
        5. Button Bar:
           - Refresh: Recalculate with current data
           - Change Capacity: Open input dialog
           - Close: Destroy window
    
    Attributes:
        controller (BookController): Handles backtracking algorithm execution
        max_capacity (float): Shelf weight limit in kilograms (default 8.0)
        lbl_total_books (CTkLabel): Displays total catalog size
        lbl_max_value (CTkLabel): Displays optimal value found
        lbl_total_weight (CTkLabel): Displays weight of selected books
        lbl_capacity (CTkLabel): Displays current capacity constraint
        lbl_books_selected (CTkLabel): Displays count of selected books
        lbl_capacity_used (CTkLabel): Displays capacity utilization percentage
        results_text (CTkTextbox): Scrollable area for detailed results
    
    Window Configuration:
        - Dimensions: 1000x700 pixels (wider for detailed metrics)
        - Position: Screen-centered on creation
        - Theme: Custom color scheme for clarity
        - Title: "🎯 Selección Óptima de Estantería - Backtracking"
    
    Color Coding:
        - SUCCESS_COLOR (green): Positive metrics, optimal values
        - WARNING_COLOR (orange): Warnings, capacity overruns
        - INFO_COLOR (blue): Informational banners
        - CARD_BG_COLOR (light gray): Card backgrounds for contrast
    
    Metrics Calculation:
        1. Capacity Used %: (total_weight / max_capacity) * 100
        2. Avg Value per Book: max_value / book_count
        3. Avg Weight per Book: total_weight / book_count
        4. Efficiency (COP/Kg): max_value / total_weight
        5. Per-book Efficiency: book_price / book_weight
    
    Dynamic Features:
        - Auto-refresh on capacity change
        - Real-time calculation on demand
        - Validates capacity input (positive numbers only)
    
    See Also:
        - controllers.book_controller.BookController: Backtracking implementation
        - ui.book.brute_force_report: Alternative algorithm comparison
    """

    def __init__(self, parent):
        """Initialize the Backtracking Report window with UI and initial data load.
        
        Creates the complete dashboard interface, centers the window, builds all
        UI components, and immediately loads the first calculation with default
        capacity (8.0 Kg).
        
        Purpose:
            Sets up an interactive visualization tool for demonstrating backtracking
            algorithm while providing practical shelf optimization functionality.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Initialize BookController for algorithm execution
            3. Set default max_capacity to 8.0 Kg
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
            - Capacity set to default 8.0 Kg
        
        Error Handling:
            - Window centering: update_idletasks() may fail on some systems (non-blocking)
            - Initial data load errors handled by _load_report() method
        
        Args:
            parent: Parent CTk window (typically MainMenu)
        
        Side Effects:
            - Creates new toplevel window
            - Executes backtracking algorithm immediately
            - Logs calculation results
            - Displays results in UI
        
        Raises:
            None: All exceptions caught in _load_report() method
        """
        super().__init__(parent)
        
        self.controller = BookController()
        self.max_capacity = 8.0  # Default shelf capacity
        
        # Window configuration
        self.title("🎯 Selección Óptima de Estantería - Backtracking")
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
        algorithm info banner, results display area, and action buttons. Uses a
        vertical stacking layout for clear visual hierarchy.
        
        Purpose:
            Creates a comprehensive dashboard interface that presents backtracking
            results in an organized, visually appealing manner with clear sections
            for different types of information.
        
        Layout Structure:
            ```
            Main Frame (BG_COLOR)
            ├─ Title Frame (transparent)
            │  ├─ Title label (18pt bold)
            │  └─ Subtitle label (12pt)
            ├─ Statistics Frame (CARD_BG_COLOR, 120px height)
            │  └─ Grid (3 rows x 2 columns)
            │     ├─ Total books | Max value
            │     ├─ Total weight | Capacity
            │     └─ Books selected | Capacity used
            ├─ Info Frame (INFO_COLOR banner)
            │  └─ Algorithm explanation text
            ├─ Results Label ("📋 Solución Óptima")
            ├─ Results Textbox (scrollable, expandable)
            └─ Button Frame (transparent)
               ├─ Refresh button (left)
               ├─ Change capacity button (left)
               └─ Close button (right)
            ```
        
        Component Details:
            
            1. Title Section:
               - Compact header with emoji decoration
               - Bold 18pt title, 12pt subtitle
               - No padding wastage for vertical space efficiency
            
            2. Statistics Dashboard:
               - Fixed height (120px) for consistency
               - Grid layout for aligned metrics
               - Labels stored as instance attributes for updates
               - Color-coded values (green for success, orange for warnings)
               - Column weights ensure balanced spacing
            
            3. Info Banner:
               - Blue background for visual distinction
               - White text for contrast
               - Concise algorithm explanation
               - 10pt font for compact display
            
            4. Results Area:
               - Expandable textbox (fill="both", expand=True)
               - Light gray background for readability
               - 12pt font for comfortable reading
               - Rounded corners (10px) for modern aesthetic
            
            5. Button Bar:
               - Transparent background (blends with main frame)
               - Primary buttons on left (refresh, change capacity)
               - Small close button on right
               - 5px padding between buttons
        
        Grid Configuration (Statistics):
            ```
            Row 0: Total books         | Max value (green, bold)
            Row 1: Total weight        | Capacity
            Row 2: Books selected      | Capacity used (color-coded)
            ```
            
            Both columns have equal weight (weight=1) for balanced layout.
        
        Responsive Design:
            - Main frame expands with window (fill="both", expand=True)
            - Results textbox expands vertically to use available space
            - Statistics frame fixed height prevents metric crowding
            - Grid columns auto-size with equal weights
        
        Font Strategy:
            - Title: 18pt bold (emphasis)
            - Subtitle: 12pt normal
            - Statistics: 11pt normal (compact)
            - Info: 10pt normal (compact)
            - Results label: 13pt bold
            - Results text: 12pt normal (readable)
        
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
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title (más compacto)
        title_frame = ctk.CTkFrame(main_frame, fg_color=theme.BG_COLOR)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            title_frame,
            text="🎯 Algoritmo de Backtracking",
            font=theme.get_font(self, size=18, weight="bold"),
            text_color=theme.TEXT_COLOR
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Maximizar valor sin exceder capacidad",
            font=theme.get_font(self, size=12),
            text_color=theme.TEXT_COLOR
        )
        subtitle.pack()
        
        # Statistics frame (más compacto)
        stats_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG_COLOR, corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 10))
        stats_frame.pack_propagate(False)
        stats_frame.configure(height=120)
        
        # Create a grid inside stats_frame
        stats_inner = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_inner.pack(expand=True, fill="both", padx=15, pady=12)
        
        # Stats labels (más compactos)
        self.lbl_total_books = ctk.CTkLabel(
            stats_inner, 
            text="Total de libros: -",
            font=theme.get_font(self, size=11),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_total_books.grid(row=0, column=0, sticky="w", padx=8, pady=3)
        
        self.lbl_max_value = ctk.CTkLabel(
            stats_inner, 
            text="Valor máximo: -",
            font=theme.get_font(self, size=11, weight="bold"),
            text_color=SUCCESS_COLOR
        )
        self.lbl_max_value.grid(row=0, column=1, sticky="w", padx=8, pady=3)
        
        self.lbl_total_weight = ctk.CTkLabel(
            stats_inner, 
            text="Peso total: -",
            font=theme.get_font(self, size=11),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_total_weight.grid(row=1, column=0, sticky="w", padx=8, pady=3)
        
        self.lbl_capacity = ctk.CTkLabel(
            stats_inner, 
            text=f"Capacidad: {self.max_capacity} Kg",
            font=theme.get_font(self, size=11),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_capacity.grid(row=1, column=1, sticky="w", padx=8, pady=3)
        
        self.lbl_books_selected = ctk.CTkLabel(
            stats_inner, 
            text="Libros seleccionados: -",
            font=theme.get_font(self, size=11),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_books_selected.grid(row=2, column=0, sticky="w", padx=8, pady=(8, 3))
        
        self.lbl_capacity_used = ctk.CTkLabel(
            stats_inner, 
            text="Capacidad usada: -",
            font=theme.get_font(self, size=11),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_capacity_used.grid(row=2, column=1, sticky="w", padx=8, pady=(8, 3))
        
        # Configure grid weights for proper spacing
        stats_inner.grid_columnconfigure(0, weight=1)
        stats_inner.grid_columnconfigure(1, weight=1)
        stats_inner.grid_rowconfigure(0, weight=1)
        stats_inner.grid_rowconfigure(1, weight=1)
        stats_inner.grid_rowconfigure(2, weight=1)
        
        # Algorithm info frame (más compacto)
        info_frame = ctk.CTkFrame(main_frame, fg_color=INFO_COLOR, corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_text = "💡 Backtracking: Explora combinaciones podando ramas inválidas. Garantiza solución óptima."
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=theme.get_font(self, size=10),
            text_color="white",
            justify="left"
        )
        info_label.pack(padx=12, pady=6)
        
        # Scrollable results frame (título más pequeño)
        results_label = ctk.CTkLabel(
            main_frame, 
            text="📋 Solución Óptima:",
            font=theme.get_font(self, size=13, weight="bold"),
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
        
        # Change capacity button
        btn_capacity = wf.create_primary_button(
            btn_frame,
            "⚙️ Cambiar Capacidad",
            command=self._change_capacity
        )
        btn_capacity.pack(side="left", padx=5)
        
        # Close button
        btn_close = wf.create_small_button(
            btn_frame,
            "Cerrar",
            command=self.destroy
        )
        btn_close.pack(side="right", padx=5)
    
    def _load_report(self):
        """Load and display backtracking algorithm results with formatted output.
        
        Executes the backtracking algorithm via controller, retrieves the optimal
        solution, updates all statistics labels, and formats comprehensive results
        in the textbox including book details, metrics, and algorithm explanation.
        
        Purpose:
            Primary data loading and display method that orchestrates calculation,
            UI updates, and result formatting to present backtracking solution in
            a clear, educational, and actionable format.
        
        Workflow:
            1. Data Retrieval:
               - Get all books from controller
               - Count total catalog size
            
            2. Algorithm Execution:
               - Call controller.find_optimal_shelf_selection(max_capacity)
               - Returns dict with: max_value, total_weight, books (list of dicts)
            
            3. Metrics Calculation:
               - Extract max_value, total_weight, selected_books
               - Count selected books
               - Calculate capacity utilization percentage
            
            4. Statistics Update:
               - Update all 6 dashboard labels
               - Color-code capacity_used (green if ≤100%, orange if >100%)
            
            5. Results Formatting:
               - Clear previous content
               - Check if solution empty (no books selected)
               - If empty: Display warning with reasons
               - If valid: Format detailed solution
            
            6. Detailed Solution Format:
               - Header: Success message, algorithm description
               - Summary: Key metrics (value, weight, averages, efficiency)
               - Book List: Each book with title, author, weight, price, efficiency
               - Footer: Algorithm explanation, complexity, guarantees
            
            7. Logging:
               - Log successful calculation with summary
        
        Algorithm Result Structure:
            ```python
            result = {
                'max_value': float,      # Total price of selected books
                'total_weight': float,   # Total weight of selected books
                'books': [               # List of selected book dictionaries
                    {
                        'id': str,       # Book ISBN
                        'title': str,
                        'author': str,
                        'weight': float,
                        'price': float
                    },
                    ...
                ]
            }
            ```
        
        Metrics Displayed:
            Dashboard:
            - Total catalog books
            - Maximum value ($ COP)
            - Total weight (Kg)
            - Capacity limit (Kg)
            - Books selected count
            - Capacity used percentage
            
            Summary Section:
            - Total value ($ COP)
            - Weight ratio (used/max)
            - Book count
            - Average value per book
            - Average weight per book
            - Efficiency (COP/Kg) - total value / total weight
            
            Per-book:
            - ID (ISBN)
            - Title
            - Author
            - Weight (Kg)
            - Price ($ COP)
            - Individual efficiency (COP/Kg)
        
        Empty Solution Handling:
            When no books can be selected:
            - Displays warning message (⚠️)
            - Lists possible reasons:
              * All books exceed capacity
              * No books in catalog
            - No detailed results shown
        
        Text Formatting:
            - Uses box-drawing characters (=) for section separators
            - Emojis for visual hierarchy (✅📊📚💡)
            - Indentation for nested information
            - Currency formatting: ${value:,.2f} COP
            - Weight formatting: {weight:.2f} Kg
            - Percentage formatting: {percent:.1f}%
        
        Error Handling:
            - Controller errors: Caught, logged, shown in error dialog
            - Division by zero: Protected (checks for zero denominators)
            - All exceptions non-fatal (messagebox shown)
        
        Args:
            None (uses self.max_capacity and self.controller)
        
        Returns:
            None
        
        Side Effects:
            - Updates all 6 statistics labels
            - Clears and repopulates results_text widget
            - Logs calculation results
            - Shows error dialog if calculation fails
        
        Performance:
            - Backtracking: O(2^n) worst case with pruning
            - UI update: O(m) where m = selected books
            - Text formatting: O(m) for iterating selected books
        
        See Also:
            - controllers.book_controller.BookController.find_optimal_shelf_selection:
              Contains backtracking implementation
        """
        try:
            # Get all books
            all_books = self.controller.get_all_books()
            total_books = len(all_books)
            
            # Run backtracking algorithm
            result = self.controller.find_optimal_shelf_selection(self.max_capacity)
            
            max_value = result['max_value']
            total_weight = result['total_weight']
            selected_books = result['books']
            books_count = len(selected_books)
            capacity_used = (total_weight / self.max_capacity * 100) if self.max_capacity > 0 else 0
            
            # Update statistics
            self.lbl_total_books.configure(text=f"📚 Total de libros en catálogo: {total_books}")
            self.lbl_max_value.configure(text=f"💰 Valor máximo: ${max_value:,.2f} COP")
            self.lbl_total_weight.configure(text=f"⚖️ Peso total: {total_weight:.2f} Kg")
            self.lbl_capacity.configure(text=f"📦 Capacidad máxima: {self.max_capacity} Kg")
            self.lbl_books_selected.configure(text=f"📖 Libros seleccionados: {books_count}")
            self.lbl_capacity_used.configure(
                text=f"📊 Capacidad usada: {capacity_used:.1f}%",
                text_color=SUCCESS_COLOR if capacity_used <= 100 else WARNING_COLOR
            )
            
            # Clear previous results
            self.results_text.delete("1.0", "end")
            
            # Display results
            if books_count == 0:
                msg = "⚠️ No se pudo seleccionar ningún libro.\n\n"
                msg += "Posibles razones:\n"
                msg += f"• Todos los libros exceden la capacidad de {self.max_capacity} Kg\n"
                msg += "• No hay libros en el catálogo\n"
                self.results_text.insert("1.0", msg)
            else:
                header = f"✅ Solución Óptima Encontrada\n"
                header += "=" * 80 + "\n\n"
                header += f"El algoritmo de backtracking exploró todas las posibles combinaciones\n"
                header += f"y encontró la solución que maximiza el valor sin exceder {self.max_capacity} Kg.\n\n"
                header += f"📊 RESUMEN:\n"
                header += f"  • Valor Total: ${max_value:,.2f} COP\n"
                header += f"  • Peso Total: {total_weight:.2f} Kg / {self.max_capacity} Kg\n"
                header += f"  • Libros: {books_count}\n"
                header += f"  • Valor promedio por libro: ${max_value/books_count:,.2f} COP\n"
                header += f"  • Peso promedio por libro: {total_weight/books_count:.2f} Kg\n"
                
                if total_weight > 0:
                    header += f"  • Eficiencia (COP/Kg): ${max_value/total_weight:,.2f}\n"
                
                header += "\n" + "=" * 80 + "\n\n"
                header += "📚 LIBROS SELECCIONADOS:\n\n"
                self.results_text.insert("1.0", header)
                
                for idx, book in enumerate(selected_books, 1):
                    book_text = f"{idx}. [{book['id']}] {book['title']}\n"
                    book_text += f"   👤 Autor: {book['author']}\n"
                    book_text += f"   ⚖️ Peso: {book['weight']:.2f} Kg\n"
                    book_text += f"   💰 Precio: ${book['price']:,.2f} COP\n"
                    
                    # Calculate value-to-weight ratio
                    if book['weight'] > 0:
                        ratio = book['price'] / book['weight']
                        book_text += f"   📈 Eficiencia: ${ratio:,.2f} COP/Kg\n"
                    
                    book_text += "\n"
                    self.results_text.insert("end", book_text)
                
                footer = "\n" + "=" * 80 + "\n\n"
                footer += "💡 ALGORITMO UTILIZADO:\n"
                footer += "  • Tipo: Backtracking (Exploración con retroceso)\n"
                footer += "  • Problema: Mochila 0/1 (Knapsack Problem)\n"
                footer += "  • Objetivo: Maximizar valor total\n"
                footer += "  • Restricción: Peso máximo de estantería\n"
                footer += "  • Complejidad: O(2^n) con poda efectiva\n"
                footer += "  • Garantía: Solución óptima global\n"
                self.results_text.insert("end", footer)
            
            logger.info(f"Reporte de backtracking cargado: {books_count} libros, valor ${max_value:,.2f}")
            
        except Exception as e:
            logger.error(f"Error al cargar reporte de backtracking: {e}")
            messagebox.showerror(
                "Error",
                f"No se pudo cargar el reporte.\n\nError: {str(e)}"
            )
    
    def _change_capacity(self):
        """Open input dialog to change shelf capacity and recalculate solution.
        
        Prompts user with an input dialog to enter a new shelf capacity value,
        validates the input, updates the capacity, and triggers a recalculation
        of the optimal solution with the new constraint.
        
        Purpose:
            Provides interactive capacity adjustment to allow users to explore
            how different weight constraints affect the optimal book selection,
            enabling what-if analysis and constraint sensitivity testing.
        
        Workflow:
            1. Dialog Display:
               - Show CTkInputDialog with current capacity
               - Prompt for new capacity value (in Kg)
               - Wait for user input or cancellation
            
            2. Cancellation Check:
               - If user cancels (None returned), exit early
               - No changes made to current state
            
            3. Input Validation:
               - Convert input to float
               - Check if value is positive (> 0)
               - Raise ValueError if invalid
            
            4. State Update:
               - Set self.max_capacity to new value
               - Log capacity change
            
            5. Recalculation:
               - Call _load_report() to recompute solution
               - Updates all UI elements automatically
            
            6. Error Handling:
               - Catch ValueError (invalid input or non-positive)
               - Show error dialog with explanation
               - Keep original capacity if error occurs
        
        Dialog Configuration:
            - Title: "Cambiar Capacidad"
            - Message: Shows current capacity value for reference
            - Input type: Text (validated to float)
            - Buttons: OK, Cancel (built-in CTkInputDialog)
        
        Validation Rules:
            - Must be numeric (convertible to float)
            - Must be positive (> 0)
            - Invalid examples:
              * Negative numbers: -5.0
              * Zero: 0
              * Non-numeric: "abc", "12.5kg"
        
        Error Messages:
            Invalid input:
            "Valor inválido.
            La capacidad debe ser un número positivo.
            Error: [specific error message]"
        
        Use Cases:
            1. Testing sensitivity:
               - How does solution change with 10 Kg vs 8 Kg?
            
            2. Planning scenarios:
               - What if we get smaller/larger shelves?
            
            3. Educational:
               - Demonstrate constraint impact on optimization
        
        Side Effects:
            - May update self.max_capacity
            - May trigger full recalculation via _load_report()
            - May update all UI statistics and results
            - Shows input dialog (blocks until user responds)
            - May show error dialog (blocks until dismissed)
            - Logs capacity change if successful
        
        Args:
            None
        
        Returns:
            None
        
        Raises:
            None: All exceptions caught and handled via dialog
        
        Example Interaction:
            ```
            User clicks "⚙️ Cambiar Capacidad"
            Dialog appears: "Ingrese la nueva capacidad... (Actual: 8.0 Kg)"
            User enters: "12.5"
            Result: Capacity updated to 12.5 Kg, solution recalculated
            ```
        """
        dialog = ctk.CTkInputDialog(
            text=f"Ingrese la nueva capacidad de la estantería (Kg):\n(Actual: {self.max_capacity} Kg)",
            title="Cambiar Capacidad"
        )
        
        new_capacity = dialog.get_input()
        
        if new_capacity is None:
            return  # User cancelled
        
        try:
            new_capacity = float(new_capacity)
            if new_capacity <= 0:
                raise ValueError("La capacidad debe ser mayor que 0")
            
            self.max_capacity = new_capacity
            logger.info(f"Capacidad actualizada a {self.max_capacity} Kg")
            self._load_report()
            
        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Valor inválido.\n\nLa capacidad debe ser un número positivo.\n\nError: {str(e)}"
            )
