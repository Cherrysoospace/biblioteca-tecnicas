import customtkinter as ctk
from . import theme
from typing import Callable, Optional
from utils.logger import LibraryLogger, UIErrorHandler

# Configurar logger para este módulo
logger = LibraryLogger.get_logger(__name__)


def create_title_label(parent, text: str):
    """Create a centered title label following the cozy Japanese theme."""
    font = theme.get_font(parent, size=30, weight="bold")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=theme.TEXT_COLOR)
    return lbl


def create_body_label(parent, text: str, size: int = 14):
    """Create a body text label with normal font weight."""
    font = theme.get_font(parent, size=size, weight="normal")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=theme.TEXT_COLOR)
    return lbl


def create_entry(parent, placeholder: str = "", width: int = 300):
    """Create an entry widget with theme styling."""
    font = theme.get_font(parent, size=13, weight="normal")
    entry = ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        font=font,
        fg_color=theme.BG_COLOR,
        text_color=theme.TEXT_COLOR,
        border_color=theme.BORDER_COLOR,
        border_width=1,
        corner_radius=8,
        width=width,
        height=36
    )
    return entry


def create_primary_button(parent, text: str, command: Optional[Callable] = None, width: int = 360, height: int = 64, image: Optional[object] = None):
    """Create a big rounded primary button using exact palette colors."""
    font = theme.get_font(parent, size=16, weight="bold")
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        image=image,
        fg_color=theme.BUTTON_COLOR,
        hover_color=theme.BUTTON_HOVER,
        text_color=theme.TEXT_COLOR,
        corner_radius=14,
        font=font,
        width=width,
        height=height,
    )
    # use strong border to echo the black line art in the background
    try:
        btn.configure(border_width=1, border_color=theme.BORDER_COLOR)
    except Exception as e:
        UIErrorHandler.log_and_pass(logger, "configurar borde de botón primario", e)
    return btn


def create_small_button(parent, text: str, command: Optional[Callable] = None, width: int = 160, height: int = 44, image: Optional[object] = None):
    font = theme.get_font(parent, size=14, weight="normal")
    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        image=image,
        fg_color=theme.BUTTON_COLOR,
        hover_color=theme.BUTTON_HOVER,
        text_color=theme.TEXT_COLOR,
        corner_radius=12,
        font=font,
        width=width,
        height=height,
    )
    try:
        btn.configure(border_width=1, border_color=theme.BORDER_COLOR)
    except Exception as e:
        UIErrorHandler.log_and_pass(logger, "configurar borde de botón pequeño", e)
    return btn
