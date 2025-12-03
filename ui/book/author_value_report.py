"""
Author Value Report Window - Stack Recursion Implementation

This module provides a UI window to calculate and display the total monetary value
of all books by a specific author using stack-style recursion.

This demonstrates the recursion requirement from the project:
"Recursión de Pila: Implementar una función recursiva que calcule el Valor Total
de todos los libros de un autor específico."
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
    """Window to calculate total value of books by author using stack recursion."""

    def __init__(self, parent):
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
        """Display welcome message in results area."""
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
        """Calculate total value for selected author using stack recursion."""
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
