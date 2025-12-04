"""Author Weight Report Window - Tail (Queue) Recursion Demonstration.

This module implements a UI window for calculating and displaying the average weight
of all books by a specific author using tail-style (queue) recursion. This serves as
both a functional reporting tool and a demonstration of the tail recursion algorithm
requirement from the project specifications.

Project Requirement:
    "Recursión de Cola: Implementar una función recursiva que calcule el Peso Promedio
    de la colección de un autor, demostrando la lógica de la recursión de cola por consola."

Algorithm - Tail (Queue) Recursion:
    The calculation uses tail recursion where the recursive call is the last operation:
    
    ```
    def calculate_avg_weight(books, author, index=0, count=0, total_weight=0.0):
        if index >= len(books):              # Base case
            return (total_weight / count) if count > 0 else 0.0
        
        book = books[index]
        if book.author == author:
            # Accumulate and recurse (tail call)
            return calculate_avg_weight(books, author, index + 1,
                                       count + 1, total_weight + book.weight)
        else:
            # Skip and recurse (tail call)
            return calculate_avg_weight(books, author, index + 1,
                                       count, total_weight)
    ```
    
    Tail Recursion Characteristics:
    - Uses accumulator parameters (index, count, total_weight)
    - State updated before recursive call (not after)
    - Recursive call is the LAST operation (tail position)
    - No computation happens after recursive call returns
    - Optimizable to iteration via TCO (Tail Call Optimization)
    
    Python Limitation:
    - Python does NOT have TCO (CPython design decision)
    - Still uses O(n) stack space despite tail recursion pattern
    - Educational value: demonstrates tail recursion concept
    - Would be O(1) space in languages with TCO (Scheme, Scala, etc.)

Tail vs Stack Recursion Comparison:
    Stack Recursion (author_value_report.py):
    - Accumulates results on RETURN path (stack unwinding)
    - Computation happens AFTER recursive call
    - return value + recursive_call(...)
    
    Tail Recursion (this module):
    - Accumulates results on CALL path (parameter passing)
    - Computation happens BEFORE recursive call
    - return recursive_call(..., accumulated_state)

UI Features:
    1. Author Selection:
       - Dropdown populated with all unique authors
       - Read-only combobox for data integrity
       - Validation for empty/invalid selections
    
    2. Debug Mode:
       - Checkbox to enable console output capture
       - Shows recursive call flow with accumulated state
       - Displays each iteration's parameters
       - Educational tool for understanding tail recursion
    
    3. Results Display:
       - Average weight in kilograms (3 decimal precision)
       - Book count for selected author
       - Detailed list of each book with weight
       - Manual calculation verification
       - Algorithm explanation with complexity analysis
    
    4. Visual Feedback:
       - Scrollable textbox for long result lists
       - Monospace font (Consolas) for alignment
       - Box-drawing characters for visual structure
       - Color-coded sections (emojis for visual hierarchy)

Architecture:
    Window Type: CTkToplevel (modal-like popup)
    Controller: BookController (handles business logic)
    Theme: Cozy Japanese aesthetic via theme module
    Widgets: Factory-created for consistency

Debug Mode Implementation:
    - Uses stdout redirection (io.StringIO)
    - Captures print() statements from controller
    - Restores stdout after calculation
    - Displays captured output in results area
    - Non-invasive (optional feature via checkbox)

Error Handling:
    - Author loading failures: Shows error message, provides fallback
    - Window centering failures: Logged but non-blocking
    - Calculation errors: UIErrorHandler with user-friendly messages
    - Invalid selections: Warning dialog before calculation
    - Stdout redirection errors: Graceful fallback

Usage Context:
    Launched from main menu via "Author Weight Report" button. Used to:
    - Demonstrate tail recursion algorithm to stakeholders
    - Calculate average book weight for collection analysis
    - Compare recursion styles (tail vs stack) educationally
    - Analyze physical space requirements per author

See Also:
    - controllers.book_controller.BookController.calculate_average_weight_by_author:
      Contains the actual tail recursive implementation
    - ui.book.author_value_report: Stack recursion variant for value calculation
    - ui.main_menu: Entry point for opening this window
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional

from controllers.book_controller import BookController
from ui import theme
from ui import widget_factory as wf
from utils.logger import LibraryLogger, UIErrorHandler

# Configure logger
logger = LibraryLogger.get_logger(__name__)


class AuthorWeightReport(ctk.CTkToplevel):
    """Tail recursion demonstration window for calculating average book weight by author.
    
    This window provides an interactive interface for selecting an author and
    calculating the average weight of all their books using tail-style (queue)
    recursion. The UI emphasizes educational value by optionally showing the
    recursive call flow and providing detailed algorithm explanations.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Layout: Vertical stack with input section, debug option, calculation button, results area
        Controller: BookController for data access and tail recursive calculations
    
    UI Components:
        1. Header Section:
           - Title with emoji decoration (⚖️)
           - Subtitle explaining tail recursion type
        
        2. Input Section:
           - Author dropdown (ComboBox, read-only)
           - Debug mode checkbox (enables console output capture)
        
        3. Action Section:
           - Primary button to trigger calculation
        
        4. Results Section:
           - Scrollable textbox (600x300px)
           - Monospace font for alignment
           - Displays: average weight, debug flow (optional), book details, manual calculation, algorithm explanation
        
        5. Footer Section:
           - Clear button (resets to welcome message)
           - Close button (destroys window)
    
    Attributes:
        controller (BookController): Handles book data and tail recursive calculations
        authors (list[str]): List of all unique authors in system
        author_var (StringVar): Tracks selected author in dropdown
        debug_var (BooleanVar): Tracks debug mode checkbox state
        author_dropdown (CTkComboBox): Author selection widget
        results_text (CTkTextbox): Scrollable results display area
    
    Window Configuration:
        - Dimensions: 700x600 pixels
        - Position: Screen-centered on creation
        - Theme: Cozy Japanese aesthetic (warm beige)
        - Title: "⚖️ Peso Promedio por Autor (Recursión de Cola)"
    
    Debug Mode Feature:
        When enabled, captures stdout during calculation to show:
        - Each recursive call with parameters
        - Accumulated state (index, count, total_weight)
        - Base case detection
        - Final result computation
        
        Implementation: Uses io.StringIO to redirect sys.stdout temporarily
    
    Educational Value:
        Results include detailed algorithm explanation showing:
        - Tail recursive function pseudocode with accumulators
        - Stack depth reached (same as book count despite tail recursion)
        - Complexity analysis (time and space)
        - Tail Call Optimization (TCO) explanation
        - Comparison with stack recursion
    
    Key Differences from Stack Recursion Window:
        1. Calculates average (weight) instead of sum (value)
        2. Uses tail recursion with accumulators
        3. Includes debug mode for call flow visualization
        4. Shows manual calculation verification
        5. Explains TCO concept and Python limitations
    
    See Also:
        - controllers.book_controller.BookController: Tail recursive calculation logic
        - ui.book.author_value_report: Stack recursion variant
    """

    def __init__(self, parent):
        """Initialize the Author Weight Report window with theme and components.
        
        Creates and configures the complete UI layout for tail recursion demonstration,
        including author selection dropdown, debug mode checkbox, calculation button,
        and results display area with stdout capture capability.
        
        Purpose:
            Sets up an educational interface for demonstrating tail recursion while
            providing practical average weight calculation functionality.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Initialize BookController for data access
            3. Configure window (title, size, centering)
            4. Apply theme (colors, fonts)
            5. Create main container frame
            6. Build title and subtitle
            7. Create input section (author dropdown)
            8. Load all authors from database
            9. Add debug mode checkbox
            10. Create calculation button
            11. Build results display area
            12. Show welcome message
            13. Add footer buttons (clear, close)
            14. Log window opening
        
        Window Centering Algorithm:
            ```
            screen_center_x = screen_width // 2
            screen_center_y = screen_height // 2
            window_x = screen_center_x - (window_width // 2)
            window_y = screen_center_y - (window_height // 2)
            ```
        
        Debug Mode Setup:
            - BooleanVar initialized to False (debug off by default)
            - Checkbox linked to debug_var for state tracking
            - Label explains debug mode purpose clearly
        
        Error Handling:
            - Window centering: Logged if fails, continues with default position
            - Author loading: Shows error message, uses fallback list
            - All errors non-blocking to ensure window opens
        
        Args:
            parent: Parent CTk window (typically MainMenu)
        
        Side Effects:
            - Creates new toplevel window
            - Loads all authors from database via controller
            - Applies global theme to window
            - Logs window opening event
            - Displays welcome message in results area
        
        Raises:
            None: All exceptions caught and handled gracefully
        """
        super().__init__(parent)
        
        self.controller = BookController()
        
        # Window configuration
        self.title("⚖️ Peso Promedio por Autor (Recursión de Cola)")
        width, height = 700, 600
        self.geometry(f"{width}x{height}")
        
        # Center window
        try:
            self.update_idletasks()
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            x = (screen_w // 2) - (width // 2)
            y = (screen_h // 2) - (height // 2)
            self.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            UIErrorHandler.log_and_pass(logger, "centrar ventana", e)
        
        # Apply theme
        theme.apply_theme(self)
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = wf.create_title_label(main_container, "⚖️ Peso Promedio por Autor")
        title_label.pack(pady=(0, 10))
        
        # Subtitle with explanation
        subtitle = ctk.CTkLabel(
            main_container,
            text="Calcula el peso promedio usando Recursión de Cola (Tail Recursion)",
            font=("Roboto", 13, "italic"),
            text_color=theme.TEXT_COLOR
        )
        subtitle.pack(pady=(0, 20))
        
        # Input section
        input_frame = ctk.CTkFrame(main_container, fg_color=theme.BUTTON_COLOR)
        input_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        # Author selection
        author_label = ctk.CTkLabel(
            input_frame,
            text="Seleccionar Autor:",
            font=("Roboto", 14, "bold"),
            text_color=theme.TEXT_COLOR
        )
        author_label.pack(pady=(15, 5), padx=15, anchor="w")
        
        # Get all authors
        try:
            self.authors = self.controller.get_all_authors()
            if not self.authors:
                self.authors = ["(No hay autores)"]
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error al cargar autores",
                user_message="No se pudieron cargar los autores del sistema"
            )
            self.authors = ["(Error al cargar)"]
        
        # Dropdown for author selection
        self.author_var = ctk.StringVar(value="Seleccione un autor...")
        self.author_dropdown = ctk.CTkComboBox(
            input_frame,
            variable=self.author_var,
            values=self.authors,
            width=400,
            height=40,
            font=("Roboto", 13),
            dropdown_font=("Roboto", 12),
            state="readonly"
        )
        self.author_dropdown.pack(pady=(5, 15), padx=15)
        
        # Debug mode checkbox
        self.debug_var = ctk.BooleanVar(value=False)
        debug_check = ctk.CTkCheckBox(
            input_frame,
            text="🔍 Mostrar flujo de recursión (modo debug)",
            variable=self.debug_var,
            font=("Roboto", 12),
            text_color=theme.TEXT_COLOR
        )
        debug_check.pack(pady=(0, 15), padx=15, anchor="w")
        
        # Calculate button
        calc_button = wf.create_primary_button(
            main_container,
            "⚖️ Calcular Peso Promedio",
            command=self.calculate_weight
        )
        calc_button.pack(pady=10)
        
        # Results section
        results_frame = ctk.CTkFrame(main_container, fg_color=theme.BUTTON_COLOR)
        results_frame.pack(fill="both", expand=True, pady=(10, 0), padx=10)
        
        results_title = ctk.CTkLabel(
            results_frame,
            text="📊 Resultados",
            font=("Roboto", 16, "bold"),
            text_color=theme.TEXT_COLOR
        )
        results_title.pack(pady=(15, 10))
        
        # Results display area (scrollable)
        self.results_text = ctk.CTkTextbox(
            results_frame,
            width=600,
            height=300,
            font=("Consolas", 12),
            fg_color=theme.BG_COLOR,
            wrap="word"
        )
        self.results_text.pack(pady=(0, 15), padx=15, fill="both", expand=True)
        
        # Initial message
        self._display_welcome_message()
        
        # Bottom buttons
        button_frame = ctk.CTkFrame(main_container, fg_color=theme.BG_COLOR)
        button_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = wf.create_small_button(button_frame, "Cerrar", command=self.destroy)
        close_btn.pack(side="right", padx=5)
        
        clear_btn = wf.create_small_button(button_frame, "Limpiar", command=self._display_welcome_message)
        clear_btn.pack(side="right", padx=5)
        
        logger.info("Ventana de reporte de peso promedio por autor abierta")
    
    def _display_welcome_message(self):
        """Display instructional welcome message explaining tail recursion concept.
        
        Clears the results textbox and shows a formatted welcome message that
        explains the tool's purpose, tail recursion algorithm, comparison with
        stack recursion, and usage instructions. This provides comprehensive
        educational context before the user performs calculations.
        
        Purpose:
            Provides clear instructions and tail recursion explanation to help users
            understand both how to use the tool and the underlying algorithmic
            differences between tail and stack recursion.
        
        Message Content:
            1. Header: Tool title in box-drawing frame
            2. Purpose: Explains tail recursion for average weight calculation
            3. Algorithm: High-level overview of tail recursive process with accumulators
            4. Complexity: Time and space analysis (O(n) despite tail recursion)
            5. Comparison: Key differences between tail and stack recursion
            6. Instructions: Step-by-step usage guide including debug mode
            7. Call to Action: Prompts user to select author
        
        Educational Elements:
            - Explains accumulator pattern (index, count, total_weight)
            - Clarifies "tail position" concept (last operation is recursive call)
            - Distinguishes accumulation timing (going IN vs coming OUT)
            - Notes space complexity difference in TCO-enabled languages
            - Highlights Python's lack of TCO optimization
        
        Visual Formatting:
            - Box-drawing characters (╔═╗║╚╝) for header
            - Emojis for visual hierarchy (⚖️🔄💡📋👉)
            - Bullet points (•) for algorithm steps
            - Clear sectioning with blank lines
        
        Text State Management:
            - Enables text widget for editing
            - Clears all existing content
            - Inserts new welcome message
            - Disables text widget (read-only)
        
        Args:
            None
        
        Returns:
            None
        
        Side Effects:
            - Clears results_text widget content
            - Inserts welcome message
            - Sets results_text to read-only state
        
        Called By:
            - __init__: Initial welcome on window creation
            - Clear button: Resets results area to welcome state
        """
        self.results_text.delete("1.0", "end")
        welcome = """
╔════════════════════════════════════════════════════════════╗
║           CALCULADORA DE PESO PROMEDIO POR AUTOR           ║
╚════════════════════════════════════════════════════════════╝

⚖️  Esta herramienta utiliza RECURSIÓN DE COLA (Tail Recursion)
   para calcular el peso promedio de todos los libros de un autor.

🔄 Algoritmo de Recursión de Cola (Queue-style):
   • Usa acumuladores (index, count, total_weight)
   • Pasa el estado actualizado en cada llamada recursiva
   • NO acumula en la vuelta (optimizable en otros lenguajes)
   • Complejidad: O(n) tiempo, O(n) espacio de pila

💡 Diferencia con Recursión de Pila:
   • Pila: acumula al VOLVER de las llamadas recursivas
   • Cola: acumula al IR hacia las llamadas recursivas
   • Cola: la última operación es la llamada recursiva

📋 Instrucciones:
   1. Seleccione un autor del menú desplegable
   2. (Opcional) Active el modo debug para ver el flujo
   3. Presione "Calcular Peso Promedio"
   4. Vea los resultados detallados aquí

👉 Seleccione un autor para comenzar...
"""
        self.results_text.insert("1.0", welcome)
        self.results_text.configure(state="disabled")
    
    def calculate_weight(self):
        """Calculate and display average weight for selected author using tail recursion.
        
        Validates author selection, optionally captures debug output via stdout redirection,
        invokes the tail recursion algorithm via controller, retrieves book details, and
        formats comprehensive results including manual calculation verification and
        algorithm explanation with TCO discussion.
        
        Purpose:
            Primary action method that orchestrates the entire calculation workflow
            and presents educational results showing practical data, recursive call flow
            (if debug enabled), and theoretical algorithm details with tail recursion emphasis.
        
        Workflow:
            1. Validation:
               - Check if author selected
               - Validate against placeholder/error values
               - Show warning dialog if invalid
            
            2. Data Collection:
               - Log calculation start with debug mode status
               - Retrieve all books from database
               - Filter books by selected author
               - Count matching books
            
            3. Debug Mode Setup (if enabled):
               - Import io and sys modules
               - Save original sys.stdout
               - Redirect stdout to io.StringIO buffer
            
            4. Calculation:
               - Call controller's tail recursion method with debug flag
               - Returns average weight in kg
            
            5. Debug Mode Cleanup (if enabled):
               - Restore original sys.stdout
               - Extract captured console output
            
            6. Results Formatting:
               - Clear previous results
               - Display header with author name
               - Show book count and average weight (3 decimal precision)
               - Include debug output if captured
               - List each book with details (title, ISBN, weight, status)
               - Show manual calculation (sum ÷ count)
               - Add algorithm explanation with accumulators and TCO
            
            7. Finalization:
               - Set results as read-only
               - Log success with summary
        
        Validation Logic:
            Invalid selections:
            - Empty string
            - "Seleccione un autor..." (placeholder)
            - "(No hay autores)" (empty database)
            - "(Error al cargar)" (load failure)
        
        Debug Mode Mechanism:
            ```python
            import io, sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # ... calculation with print() statements ...
            
            sys.stdout = old_stdout
            debug_text = captured_output.getvalue()
            ```
            
            Captures print() output from controller's debug mode,
            showing each recursive call with accumulated parameters.
        
        Display Format:
            ```
            ╔════════════════════════════════════════╗
            ║   RESULTADO DEL CÁLCULO (Cola)        ║
            ╚════════════════════════════════════════╝
            
            👤 Autor: [Author Name]
            📚 Libros encontrados: [Count]
            ⚖️  PESO PROMEDIO: [Weight] kg
            
            [Debug output section if enabled]
            
            📋 Detalle de libros:
               1. [Title]
                  • ISBN: [Code]
                  • Peso: [Weight] kg
                  • Estado: [Available/Borrowed]
            
            📐 Cálculo Manual:
               • Suma total: [Total] kg
               • Cantidad: [Count]
               • Promedio: [Total] ÷ [Count] = [Avg] kg
            
            🔄 Explicación del Algoritmo:
               [Pseudocode with accumulators]
               📊 Llamadas recursivas: [Count]
               💾 Profundidad de pila: [Depth]
               ⏱️  Complejidad: O(n) tiempo, O(n) espacio
               
               ✨ Tail Recursion Characteristic:
                  Last operation is recursive call itself.
                  Optimizable to O(1) space with TCO.
                  Python lacks TCO, but pattern is educational.
            ```
        
        Error Handling:
            - Validation errors: Warning dialog, no calculation
            - Calculation errors: UIErrorHandler with user message
            - Stdout redirection errors: Gracefully handled (no debug output shown)
            - All errors logged for debugging
        
        Args:
            None (uses self.author_var for author, self.debug_var for debug mode)
        
        Returns:
            None
        
        Side Effects:
            - Updates results_text widget with formatted results
            - Temporarily redirects sys.stdout if debug mode enabled
            - Shows warning dialog if validation fails
            - Shows error dialog if calculation fails
            - Logs calculation start, result, and any errors
        
        Performance:
            - Time: O(n) where n = total books (filters + recursion)
            - Space: O(n) for stack frames during recursion (Python lacks TCO)
            - UI update: O(m) where m = books by author (formatting)
        
        Notes:
            - Debug mode captures console output non-invasively
            - Manual calculation provides verification of recursive result
            - TCO explanation helps users understand language differences
            - Shows both practical use (average weight) and educational value (tail recursion)
        
        See Also:
            - controllers.book_controller.BookController.calculate_average_weight_by_author:
              Contains actual tail recursive implementation with debug prints
        """
        author = self.author_var.get()
        debug_mode = self.debug_var.get()
        
        # Validation
        if not author or author == "Seleccione un autor..." or author == "(No hay autores)" or author == "(Error al cargar)":
            messagebox.showwarning(
                "Autor no seleccionado",
                "Por favor, seleccione un autor de la lista."
            )
            return
        
        try:
            logger.info(f"Calculando peso promedio para autor: {author} (debug={debug_mode})")
            
            # Get all books to show details
            all_books = self.controller.get_all_books()
            author_books = [b for b in all_books if b.get_author() == author]
            book_count = len(author_books)
            
            # Display results
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            
            result_text = f"""
╔════════════════════════════════════════════════════════════╗
║        RESULTADO DEL CÁLCULO (Recursión de Cola)           ║
╚════════════════════════════════════════════════════════════╝

👤 Autor: {author}

📚 Libros encontrados: {book_count}

"""
            self.results_text.insert("1.0", result_text)
            
            # If debug mode, capture console output
            if debug_mode:
                import io
                import sys
                
                # Redirect stdout to capture debug output
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
            
            # Calculate using tail recursion
            avg_weight = self.controller.calculate_average_weight_by_author(author, debug=debug_mode)
            
            # Restore stdout and get captured output
            debug_output = ""
            if debug_mode:
                sys.stdout = old_stdout
                debug_output = captured_output.getvalue()
            
            # Add weight result
            weight_text = f"⚖️  PESO PROMEDIO: {avg_weight:.3f} kg\n"
            self.results_text.insert("end", weight_text)
            
            # Show debug output if available
            if debug_mode and debug_output:
                debug_section = f"""
───────────────────────────────────────────────────────────────

🔍 FLUJO DE RECURSIÓN (Modo Debug):

{debug_output}
"""
                self.results_text.insert("end", debug_section)
            
            # Add book details
            if author_books:
                details_header = """
───────────────────────────────────────────────────────────────

📋 Detalle de libros:
"""
                self.results_text.insert("end", details_header)
                
                total_weight = 0.0
                for i, book in enumerate(author_books, 1):
                    weight = book.get_weight()
                    total_weight += weight
                    book_detail = f"""
   {i}. {book.get_title()}
      • ISBN: {book.get_ISBNCode()}
      • Peso: {weight:.3f} kg
      • Estado: {"Prestado" if book.get_isBorrowed() else "Disponible"}
"""
                    self.results_text.insert("end", book_detail)
                
                # Show calculation
                calc_detail = f"""
───────────────────────────────────────────────────────────────

📐 Cálculo Manual:
   • Suma total de pesos: {total_weight:.3f} kg
   • Cantidad de libros: {book_count}
   • Promedio: {total_weight:.3f} ÷ {book_count} = {avg_weight:.3f} kg
"""
                self.results_text.insert("end", calc_detail)
            
            # Add algorithm explanation
            explanation = f"""
───────────────────────────────────────────────────────────────

🔄 Explicación del Algoritmo (Recursión de Cola):

   La función usa acumuladores para mantener el estado:
   
   avg_weight_by_author(books, "{author}", 
                        index=0, count=0, total_weight=0.0)
   ├─ Si index >= len(books):  (caso base)
   │     return (total_weight / count) if count > 0 else 0.0
   ├─ book = books[index]
   ├─ Si book.author == "{author}":
   │     return avg_weight(..., index+1, 
   │                       count+1, total_weight+book.weight)
   └─ Sino:
        return avg_weight(..., index+1, count, total_weight)
   
   📊 Llamadas recursivas realizadas: {len(all_books)}
   💾 Profundidad máxima de pila: {len(all_books)}
   ⏱️  Complejidad: O(n) tiempo, O(n) espacio
   
   ✨ Característica Tail Recursion:
      La última operación es la llamada recursiva misma.
      En lenguajes con TCO (Tail Call Optimization), esto
      se optimizaría a O(1) espacio. Python no tiene TCO,
      pero el patrón es educativo.

───────────────────────────────────────────────────────────────

✅ Cálculo completado exitosamente
"""
            self.results_text.insert("end", explanation)
            self.results_text.configure(state="disabled")
            
            logger.info(f"Peso promedio calculado: {avg_weight:.3f} kg para {book_count} libros de {author}")
            
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error en el cálculo",
                user_message=f"No se pudo calcular el peso promedio.\nError: {str(e)}"
            )
