"""Backtracking Algorithm Visualization Window.

This module provides a UI to visualize the backtracking algorithm that finds
the optimal combination of books that maximizes value without exceeding
the shelf capacity threshold (8 Kg).
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
    """Window to display backtracking algorithm results for optimal shelf selection."""

    def __init__(self, parent):
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
        """Build the user interface."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=theme.BG_COLOR)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color=theme.BG_COLOR)
        title_frame.pack(fill="x", pady=(0, 20))
        
        title = wf.create_title_label(
            title_frame, 
            "🎯 Algoritmo de Backtracking"
        )
        title.pack()
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Problema de la Mochila - Maximizar valor sin exceder capacidad",
            font=theme.get_font(self, size=14),
            text_color=theme.TEXT_COLOR
        )
        subtitle.pack()
        
        # Statistics frame
        stats_frame = ctk.CTkFrame(main_frame, fg_color=CARD_BG_COLOR, corner_radius=10)
        stats_frame.pack(fill="x", pady=(0, 15))
        stats_frame.pack_propagate(False)
        stats_frame.configure(height=140)
        
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
        
        self.lbl_max_value = ctk.CTkLabel(
            stats_inner, 
            text="Valor máximo: -",
            font=theme.get_font(self, size=13, weight="bold"),
            text_color=SUCCESS_COLOR
        )
        self.lbl_max_value.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_total_weight = ctk.CTkLabel(
            stats_inner, 
            text="Peso total: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_total_weight.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        self.lbl_capacity = ctk.CTkLabel(
            stats_inner, 
            text=f"Capacidad: {self.max_capacity} Kg",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_capacity.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        self.lbl_books_selected = ctk.CTkLabel(
            stats_inner, 
            text="Libros seleccionados: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_books_selected.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        self.lbl_capacity_used = ctk.CTkLabel(
            stats_inner, 
            text="Capacidad usada: -",
            font=theme.get_font(self, size=13),
            text_color=theme.TEXT_COLOR
        )
        self.lbl_capacity_used.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # Configure grid weights
        stats_inner.grid_columnconfigure(0, weight=1)
        stats_inner.grid_columnconfigure(1, weight=1)
        
        # Algorithm info frame
        info_frame = ctk.CTkFrame(main_frame, fg_color=INFO_COLOR, corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        info_text = "💡 Este algoritmo explora sistemáticamente todas las posibles combinaciones\n"
        info_text += "   de libros usando backtracking, podando ramas que exceden la capacidad.\n"
        info_text += "   Garantiza encontrar la solución óptima (máximo valor)."
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=theme.get_font(self, size=11),
            text_color="white",
            justify="left"
        )
        info_label.pack(padx=15, pady=10)
        
        # Scrollable results frame
        results_label = ctk.CTkLabel(
            main_frame, 
            text="Solución Óptima Encontrada:",
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
        """Load and display the backtracking algorithm results."""
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
        """Open dialog to change the shelf capacity."""
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
