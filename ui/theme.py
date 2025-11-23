import customtkinter as ctk

# Palette adapted for the background artwork (beige base, black lines, red accents)
# Background: warm beige
BG_COLOR = "#EDE6D6"        # Warm Beige
# Buttons: a slightly darker beige to sit on the background
BUTTON_COLOR = "#DCCFB8"    # Button Beige
# Hover / accent: deep red to match the red semicircles in the background
BUTTON_HOVER = "#C0392B"    # Deep Sakura Red
# Main text should be black to match the black line art
TEXT_COLOR = "#0B0B0B"      # Near Black
# Borders and line accents use true black for strong definition
BORDER_COLOR = "#000000"    # Black

# Optional accent color available to UI for small highlights
ACCENT_RED = "#C0392B"


def apply_theme(root: ctk.CTk):
    """Apply global theme to a CTk root instance.

    - Sets appearance mode to light and adjusts root background.
    - Does not force fonts globally; provides `get_font` to choose fonts with fallbacks.
    """
    try:
        ctk.set_appearance_mode("light")
    except Exception:
        pass

    # Configure root background color
    try:
        root.configure(fg_color=BG_COLOR)
    except Exception:
        try:
            root.configure(bg=BG_COLOR)
        except Exception:
            pass


def get_font(root, size: int = 14, weight: str = "normal"):
    """Return a font tuple (family, size, weight) using fallbacks.

    Preferred families in order: 'Noto Sans JP', 'Yu Gothic UI', 'Segoe UI'.
    We query available font families from the provided `root` (safe, uses existing Tk handle).
    """
    preferred = ["Noto Sans JP", "Yu Gothic UI", "Segoe UI"]
    try:
        families = list(root.tk.call("font", "families"))
    except Exception:
        # Fallback to a safe generic family name
        families = []

    chosen = None
    for fam in preferred:
        if fam in families:
            chosen = fam
            break

    if chosen is None:
        # fallback to default font family returned by Tk
        try:
            chosen = root.option_get("font", "*") or "Segoe UI"
        except Exception:
            chosen = "Segoe UI"

    return (chosen, size, weight)


def style_widget_border(widget):
    """Apply subtle border color to a widget if it supports `fg_color` or `border_color`.
    This keeps visual consistency across CTk widgets.
    """
    try:
        widget.configure(border_color=BORDER_COLOR, border_width=1)
    except Exception:
        try:
            widget.configure(highlightbackground=BORDER_COLOR)
        except Exception:
            pass
