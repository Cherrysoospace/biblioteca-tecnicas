"""Author Value Report Window - Stack Recursion Demonstration.

This module implements a UI window for calculating and displaying the total monetary
value of all books by a specific author using stack-based recursion. This serves as
both a functional reporting tool and a demonstration of the stack recursion algorithm
requirement from the project specifications.

Project Requirement:
    "Recursión de Pila: Implementar una función recursiva que calcule el Valor Total
    de todos los libros de un autor específico."

Algorithm - Stack Recursion:
    The calculation uses pure stack recursion (not tail recursion):
    
    ```
    def calculate_value(books, author, index=0):
        if index >= len(books):              # Base case
            return 0
        
        book = books[index]
        if book.author == author:
            contribution = book.price
        else:
            contribution = 0
        
        # Recursive call builds stack frames
        return contribution + calculate_value(books, author, index + 1)
    ```
    
    Stack Behavior:
    - Each book creates a new stack frame
    - Frames accumulate until base case is reached
    - Results sum up during stack unwinding
    - Space complexity: O(n) where n = total books
    - Time complexity: O(n)

UI Features:
    1. Author Selection:
       - Dropdown populated with all unique authors from book database
       - Read-only combobox for data integrity
       - Validation for empty/invalid selections
    
    2. Results Display:
       - Total value in Colombian Pesos (COP)
       - Book count for selected author
       - Detailed list of each book with price
       - Algorithm explanation with complexity analysis
    
    3. Visual Feedback:
       - Scrollable textbox for long result lists
       - Monospace font (Consolas) for alignment
       - Box-drawing characters for visual structure
       - Color-coded sections (emojis for visual hierarchy)

Architecture:
    Window Type: CTkToplevel (modal-like popup)
    Controller: BookController (handles business logic)
    Theme: Cozy Japanese aesthetic via theme module
    Widgets: Factory-created for consistency

Error Handling:
    - Author loading failures: Shows error message, provides fallback
    - Window centering failures: Logged but non-blocking
    - Calculation errors: UIErrorHandler with user-friendly messages
    - Invalid selections: Warning dialog before calculation

Usage Context:
    Launched from main menu via "Author Value Report" button. Used to:
    - Demonstrate stack recursion algorithm to stakeholders
    - Calculate inventory value segmented by author
    - Analyze author contribution to library's total value
    - Educational tool for recursion understanding

See Also:
    - controllers.book_controller.BookController.calculate_total_value_by_author:
      Contains the actual recursive implementation
    - ui.book.author_weight_report: Tail recursion variant for weight calculation
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


class AuthorValueReport(ctk.CTkToplevel):
    """Stack Recursion demonstration window for calculating author book values.
    
    This window provides an interactive interface for selecting an author and
    calculating the total monetary value of all their books using stack-based
    recursion. The UI emphasizes educational value by showing algorithm details
    and step-by-step explanations alongside practical results.
    
    Architecture:
        Window Type: CTkToplevel (popup window)
        Layout: Vertical stack with input section, calculation button, results area
        Controller: BookController for data access and recursive calculations
    
    UI Components:
        1. Header Section:
           - Title with emoji decoration
           - Subtitle explaining recursion type
        
        2. Input Section:
           - Author dropdown (ComboBox, read-only)
           - Populated with all unique authors from database
        
        3. Action Section:
           - Primary button to trigger calculation
        
        4. Results Section:
           - Scrollable textbox (600x300px)
           - Monospace font for alignment
           - Displays: total value, book count, book details, algorithm explanation
        
        5. Footer Section:
           - Clear button (resets to welcome message)
           - Close button (destroys window)
    
    Attributes:
        controller (BookController): Handles book data and recursive calculations
        authors (list[str]): List of all unique authors in system
        author_var (StringVar): Tracks selected author in dropdown
        author_dropdown (CTkComboBox): Author selection widget
        results_text (CTkTextbox): Scrollable results display area
    
    Window Configuration:
        - Dimensions: 700x600 pixels
        - Position: Screen-centered on creation
        - Theme: Cozy Japanese aesthetic (warm beige)
        - Title: "📚 Valor Total por Autor (Recursión de Pila)"
    
    Educational Value:
        Results include detailed algorithm explanation showing:
        - Recursive function pseudocode
        - Stack depth reached
        - Complexity analysis (time and space)
        - Number of recursive calls made
    
    See Also:
        - controllers.book_controller.BookController: Recursive calculation logic
        - ui.book.author_weight_report: Tail recursion variant
    """

    def __init__(self, parent):
        """Initialize the Author Value Report window with theme and components.
        
        Creates and configures the complete UI layout for stack recursion demonstration,
        including author selection dropdown, calculation button, and results display area.
        
        Purpose:
            Sets up an educational interface for demonstrating stack recursion while
            providing practical value calculation functionality.
        
        Initialization Workflow:
            1. Call parent CTkToplevel constructor
            2. Initialize BookController for data access
            3. Configure window (title, size, centering)
            4. Apply theme (colors, fonts)
            5. Create main container frame
            6. Build title and subtitle
            7. Create input section (author dropdown)
            8. Load all authors from database
            9. Create calculation button
            10. Build results display area
            11. Show welcome message
            12. Add footer buttons (clear, close)
            13. Log window opening
        
        Window Centering Algorithm:
            ```
            screen_center_x = screen_width // 2
            screen_center_y = screen_height // 2
            window_x = screen_center_x - (window_width // 2)
            window_y = screen_center_y - (window_height // 2)
            ```
        
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
        self.title("📚 Valor Total por Autor (Recursión de Pila)")
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
        title_label = wf.create_title_label(main_container, "📚 Valor Total por Autor")
        title_label.pack(pady=(0, 10))
        
        # Subtitle with explanation
        subtitle = ctk.CTkLabel(
            main_container,
            text="Calcula el valor total usando Recursión de Pila",
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
        
        # Calculate button
        calc_button = wf.create_primary_button(
            main_container,
            "🧮 Calcular Valor Total",
            command=self.calculate_value
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
        
        logger.info("Ventana de reporte de valor por autor abierta")
    
    def _display_welcome_message(self):
        """Display instructional welcome message in results text area.
        
        Clears the results textbox and shows a formatted welcome message that
        explains the tool's purpose, algorithm, and usage instructions. This
        provides educational context before the user performs calculations.
        
        Purpose:
            Provides clear instructions and algorithm explanation to help users
            understand both how to use the tool and the underlying stack recursion
            concept being demonstrated.
        
        Message Content:
            1. Header: Tool title in box-drawing frame
            2. Purpose: Explains stack recursion calculation
            3. Algorithm: High-level overview of recursive process
            4. Complexity: Time and space analysis
            5. Instructions: Step-by-step usage guide
            6. Call to Action: Prompts user to select author
        
        Visual Formatting:
            - Box-drawing characters (╔═╗║╚╝) for header
            - Emojis for visual hierarchy (📖🔄💡👉)
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
║                CALCULADORA DE VALOR POR AUTOR              ║
╚════════════════════════════════════════════════════════════╝

📖 Esta herramienta utiliza RECURSIÓN DE PILA para calcular
   el valor monetario total de todos los libros de un autor.

🔄 Algoritmo de Recursión de Pila:
   • Procesa un libro a la vez
   • Delega el resto a una llamada recursiva
   • Acumula el resultado en la vuelta de las llamadas
   • Complejidad: O(n) tiempo, O(n) espacio en pila

💡 Instrucciones:
   1. Seleccione un autor del menú desplegable
   2. Presione "Calcular Valor Total"
   3. Vea los resultados detallados aquí

👉 Seleccione un autor para comenzar...
"""
        self.results_text.insert("1.0", welcome)
        self.results_text.configure(state="disabled")
    
    def calculate_value(self):
        """Calculate and display total value for selected author using stack recursion.
        
        Validates author selection, invokes the stack recursion algorithm via controller,
        retrieves book details, and formats comprehensive results including algorithm
        explanation and complexity analysis.
        
        Purpose:
            Primary action method that orchestrates the entire calculation workflow
            and presents educational results showing both practical data and theoretical
            algorithm details.
        
        Workflow:
            1. Validation:
               - Check if author selected
               - Validate against placeholder/error values
               - Show warning dialog if invalid
            
            2. Data Collection:
               - Log calculation start
               - Retrieve all books from database
               - Filter books by selected author
               - Count matching books
            
            3. Calculation:
               - Call controller's stack recursion method
               - Returns total value in COP (Colombian Pesos)
            
            4. Results Formatting:
               - Clear previous results
               - Display header with author name
               - Show book count and total value
               - List each book with details (title, ISBN, price, status)
               - Add algorithm explanation with complexity
               - Include stack depth and call count
            
            5. Finalization:
               - Set results as read-only
               - Log success with summary
        
        Validation Logic:
            Invalid selections:
            - Empty string
            - "Seleccione un autor.." (placeholder)
            - "(No hay autores)" (empty database)
            - "(Error al cargar)" (load failure)
        
        Display Format:
            ```
            ╔═══════════════════════════════╗
            ║   RESULTADO DEL CÁLCULO       ║
            ╚═══════════════════════════════╝
            
            👤 Autor: [Author Name]
            📚 Libros encontrados: [Count]
            💰 VALOR TOTAL: $[Value] COP
            
            📋 Detalle de libros:
               1. [Title]
                  • ISBN: [Code]
                  • Precio: $[Price] COP
                  • Estado: [Available/Borrowed]
            
            🔄 Explicación del Algoritmo:
               [Pseudocode]
               📊 Llamadas recursivas: [Count]
               💾 Profundidad de pila: [Depth]
               ⏱️  Complejidad: O(n) tiempo, O(n) espacio
            ```
        
        Error Handling:
            - Validation errors: Warning dialog, no calculation
            - Calculation errors: UIErrorHandler with user message
            - All errors logged for debugging
        
        Args:
            None (uses self.author_var for selected author)
        
        Returns:
            None
        
        Side Effects:
            - Updates results_text widget with formatted results
            - Shows warning dialog if validation fails
            - Shows error dialog if calculation fails
            - Logs calculation start, result, and any errors
        
        Performance:
            - Time: O(n) where n = total books (filters + recursion)
            - Space: O(n) for stack frames during recursion
            - UI update: O(m) where m = books by author (formatting)
        
        See Also:
            - controllers.book_controller.BookController.calculate_total_value_by_author:
              Contains actual stack recursion implementation
        """
        author = self.author_var.get()
        
        # Validation
        if not author or author == "Seleccione un autor..." or author == "(No hay autores)" or author == "(Error al cargar)":
            messagebox.showwarning(
                "Autor no seleccionado",
                "Por favor, seleccione un autor de la lista."
            )
            return
        
        try:
            logger.info(f"Calculando valor total para autor: {author}")
            
            # Get all books to count how many belong to this author
            all_books = self.controller.get_all_books()
            author_books = [b for b in all_books if b.get_author() == author]
            book_count = len(author_books)
            
            # Calculate using stack recursion
            total_value = self.controller.calculate_total_value_by_author(author)
            
            # Display results
            self.results_text.configure(state="normal")
            self.results_text.delete("1.0", "end")
            
            result_text = f"""
╔════════════════════════════════════════════════════════════╗
║              RESULTADO DEL CÁLCULO (Recursión)             ║
╚════════════════════════════════════════════════════════════╝

👤 Autor: {author}

📚 Libros encontrados: {book_count}

💰 VALOR TOTAL: ${total_value:,.0f} COP

───────────────────────────────────────────────────────────────

📋 Detalle de libros:
"""
            self.results_text.insert("1.0", result_text)
            
            # Add book details
            if author_books:
                for i, book in enumerate(author_books, 1):
                    book_detail = f"""
   {i}. {book.get_title()}
      • ISBN: {book.get_ISBNCode()}
      • Precio: ${book.get_price():,.0f} COP
      • Estado: {"Prestado" if book.get_isBorrowed() else "Disponible"}
"""
                    self.results_text.insert("end", book_detail)
            
            # Add algorithm explanation
            explanation = f"""
───────────────────────────────────────────────────────────────

🔄 Explicación del Algoritmo (Recursión de Pila):

   La función procesa cada libro recursivamente:
   
   total_value_by_author(books, "{author}", index=0)
   ├─ Si index >= len(books): return 0  (caso base)
   ├─ book = books[index]
   ├─ Si book.author == "{author}":
   │     contribution = book.price
   │  Sino:
   │     contribution = 0
   └─ return contribution + total_value_by_author(..., index+1)
   
   📊 Llamadas recursivas realizadas: {len(all_books)}
   💾 Profundidad máxima de pila: {len(all_books)}
   ⏱️  Complejidad: O(n) tiempo, O(n) espacio

───────────────────────────────────────────────────────────────

✅ Cálculo completado exitosamente
"""
            self.results_text.insert("end", explanation)
            self.results_text.configure(state="disabled")
            
            logger.info(f"Valor total calculado: ${total_value:,.0f} COP para {book_count} libros de {author}")
            
        except Exception as e:
            UIErrorHandler.handle_error(
                logger, e,
                title="Error en el cálculo",
                user_message=f"No se pudo calcular el valor total.\nError: {str(e)}"
            )
