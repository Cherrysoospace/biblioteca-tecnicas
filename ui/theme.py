import customtkinter as ctk

# Exact palette (do not change)
BG_COLOR = "#FAF9F6"        # White Rice
BUTTON_COLOR = "#F7E2E2"    # Sakura Pink
BUTTON_HOVER = "#CBDDB4"    # Wasabi Soft Green
TEXT_COLOR = "#2E2E2E"      # Charcoal Ink
BORDER_COLOR = "#E8DCC2"    # Hinoki Beige


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
