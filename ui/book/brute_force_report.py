"""Brute Force Algorithm Visualization Window.

This module provides a UI to visualize the brute force algorithm that finds
all combinations of 4 books exceeding the shelf capacity threshold (8 Kg).
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
    """Window to display brute force algorithm results for risky book combinations."""

    def __init__(self, parent):
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
