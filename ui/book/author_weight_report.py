"""
Author Weight Report Window - Queue (Tail) Recursion Implementation

This module provides a UI window to calculate and display the average weight
of all books by a specific author using tail-style (queue) recursion.

This demonstrates the recursion requirement from the project:
"Recursión de Cola: Implementar una función recursiva que calcule el Peso Promedio
de la colección de un autor, demostrando la lógica de la recursión de cola por consola."
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
    """Window to calculate average weight of books by author using tail recursion."""

    def __init__(self, parent):
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
        """Display welcome message in results area."""
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
        """Calculate average weight for selected author using tail recursion."""
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
