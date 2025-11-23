import customtkinter as ctk
from . import theme
from typing import Callable, Optional


def create_title_label(parent, text: str):
    """Create a centered title label following the cozy Japanese theme."""
    font = theme.get_font(parent, size=30, weight="bold")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=theme.TEXT_COLOR)
    return lbl


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
    # subtle border for tactile feeling
    try:
        btn.configure(border_width=1, border_color=theme.BORDER_COLOR)
    except Exception:
        pass
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
    except Exception:
        pass
    return btn
