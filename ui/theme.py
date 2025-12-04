"""Theme Module - Centralized Color Palette and Styling Configuration.

This module defines the global visual theme for the library management system,
inspired by a cozy Japanese aesthetic with warm beige tones, black line art,
and red accent colors. It provides color constants, font management with fallbacks,
and theme application utilities.

Design Philosophy - Cozy Japanese Aesthetic:
    The theme adapts to pixel-art background artwork featuring:
    - Warm beige base colors for comfort and readability
    - Black line art for strong visual definition and clarity
    - Deep red accents (sakura-inspired) for interactive elements
    - High contrast for accessibility and text legibility

Color Palette Structure:
    Base Colors:
        - BG_COLOR: Warm beige background (#EDE6D6)
        - TEXT_COLOR: Near-black for readability (#0B0B0B)
        - BORDER_COLOR: True black for strong definition (#000000)
    
    Interactive Colors:
        - BUTTON_COLOR: Slightly darker beige for buttons (#DCCFB8)
        - BUTTON_HOVER: Deep sakura red for hover states (#C0392B)
        - ACCENT_RED: Optional red accent for highlights (#C0392B)

Architecture - Centralized Theme Management:
    1. Color Constants: Single source of truth for all UI colors
    2. Font Fallback System: Graceful degradation across different systems
    3. Theme Application: One-time configuration for CustomTkinter roots
    4. Widget Styling Utilities: Consistent border/highlight application

Font Strategy:
    Preferred font families with fallback chain:
    1. 'Noto Sans JP': Japanese-optimized, modern sans-serif
    2. 'Yu Gothic UI': Windows Japanese font with good readability
    3. 'Segoe UI': Windows default, widely available
    4. System default: Fallback to Tk's default font

CustomTkinter Integration:
    - Light appearance mode enforced (matches beige aesthetic)
    - Root background color configuration
    - Font family detection via Tk font system
    - Border/highlight color utilities for widget consistency

Usage Pattern:
    ```python
    import customtkinter as ctk
    from ui import theme
    
    # Apply theme to root window
    root = ctk.CTk()
    theme.apply_theme(root)
    
    # Use color constants
    button = ctk.CTkButton(root, fg_color=theme.BUTTON_COLOR,
                          hover_color=theme.BUTTON_HOVER)
    
    # Get font with fallback
    font = theme.get_font(root, size=16, weight="bold")
    label = ctk.CTkLabel(root, font=font, text_color=theme.TEXT_COLOR)
    
    # Apply border styling
    theme.style_widget_border(frame)
    ```

Error Handling:
    All configuration operations wrapped in try-except blocks for:
    - Different CustomTkinter versions (API changes)
    - Missing font families (fallback chain)
    - Tk command failures (safe defaults)
    - Unsupported widget properties (graceful degradation)

See Also:
    - ui.widget_factory: Uses theme constants for widget creation
    - ui.main_menu: Applies theme to main application window
"""

import customtkinter as ctk

# =============================================================================
# COLOR PALETTE - Cozy Japanese Aesthetic
# =============================================================================
# Palette adapted for pixel-art background artwork:
# - Warm beige base for comfort and approachability
# - Black line art for clarity and strong visual definition  
# - Deep red accents matching red semicircles in background artwork

# Background: warm beige for comfortable reading and cozy atmosphere
BG_COLOR = "#EDE6D6"        # Warm Beige

# Buttons: slightly darker beige to create subtle contrast against background
BUTTON_COLOR = "#DCCFB8"    # Button Beige

# Hover / accent: deep red to match red semicircles in background artwork,
# provides strong visual feedback for interactive elements
BUTTON_HOVER = "#C0392B"    # Deep Sakura Red

# Main text: near-black for high contrast and readability,
# matches the black line art in background pixel art
TEXT_COLOR = "#0B0B0B"      # Near Black

# Borders and line accents: true black for strong definition and clarity,
# echoes the bold black outlines in background artwork
BORDER_COLOR = "#000000"    # Black

# Optional accent color available to UI components for small highlights,
# badges, or attention-grabbing elements
ACCENT_RED = "#C0392B"


def apply_theme(root: ctk.CTk):
    """Apply global theme configuration to CustomTkinter root window.
    
    Configures the root window with the cozy Japanese theme by setting
    light appearance mode and applying the warm beige background color.
    This should be called once during application initialization.
    
    Purpose:
        Centralizes theme application to ensure consistent visual appearance
        across the entire application. Sets foundation for all child widgets.
    
    Configuration Steps:
        1. Set CustomTkinter appearance mode to "light" (matches beige aesthetic)
        2. Apply BG_COLOR to root window background (warm beige)
    
    Font Handling:
        Does NOT force fonts globally. Instead, use get_font() function to
        retrieve fonts with proper fallback chain for each widget. This allows
        flexibility and graceful degradation across different systems.
    
    Error Handling:
        - Appearance mode setting wrapped in try-except (some CTk versions differ)
        - Background color tries fg_color first, falls back to bg parameter
        - All failures silently continue (non-critical for functionality)
    
    Args:
        root (ctk.CTk): CustomTkinter root window instance to configure
    
    Returns:
        None
    
    Side Effects:
        - Sets global CTk appearance mode to "light"
        - Modifies root window background color to BG_COLOR
    
    Example:
        >>> import customtkinter as ctk
        >>> from ui import theme
        >>> root = ctk.CTk()
        >>> theme.apply_theme(root)
        >>> root.mainloop()
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
    """Return font tuple with intelligent fallback chain for cross-platform compatibility.
    
    Queries the system for available fonts and selects the best match from a
    preferred list of Japanese-friendly, modern sans-serif fonts. Falls back
    gracefully if preferred fonts are unavailable.
    
    Purpose:
        Provides consistent font selection across different operating systems
        and configurations while ensuring Japanese character support and modern
        aesthetic alignment with the cozy theme.
    
    Algorithm - Font Fallback Chain:
        1. Query system for available font families via Tk font system
        2. Check preferred fonts in priority order:
           a. 'Noto Sans JP': Google's Japanese-optimized sans-serif
           b. 'Yu Gothic UI': Windows Japanese font with excellent readability
           c. 'Segoe UI': Windows default, widely available and modern
        3. If none found, fallback to Tk's default font option
        4. Ultimate fallback: "Segoe UI" as hardcoded safe default
    
    Font Selection Criteria:
        - Japanese character support (important for potential localization)
        - Modern, clean sans-serif design
        - Wide availability across platforms
        - Good readability at various sizes
    
    Error Handling:
        - Tk font query wrapped in try-except (handles Tk initialization issues)
        - Font option fallback wrapped in try-except (handles option retrieval failures)
        - Always returns valid font tuple (never None)
    
    Args:
        root: CustomTkinter or Tkinter root window with Tk handle for font queries
        size (int, optional): Font size in points. Defaults to 14.
        weight (str, optional): Font weight ("normal" or "bold"). Defaults to "normal".
    
    Returns:
        tuple: Font specification tuple (family: str, size: int, weight: str)
               Example: ("Noto Sans JP", 14, "normal")
    
    Side Effects:
        None (read-only system font query)
    
    Example:
        >>> font = get_font(root, size=16, weight="bold")
        >>> label = ctk.CTkLabel(root, font=font)
    
    Notes:
        - Safe to call multiple times (queries system each time for accuracy)
        - Root parameter required for Tk font system access
        - Returns tuple compatible with CustomTkinter and Tkinter font parameters
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
    """Apply consistent border styling to widget with graceful fallback.
    
    Attempts to configure widget border using the theme's BORDER_COLOR (black)
    to maintain visual consistency across all CustomTkinter widgets. Provides
    multiple fallback strategies for different widget types and CTk versions.
    
    Purpose:
        Ensures all frames, containers, and bordered widgets use the same
        black border color, echoing the strong black line art in the
        background pixel artwork.
    
    Algorithm - Fallback Strategy:
        1. Try CustomTkinter border_color and border_width (modern CTk widgets)
        2. If fails, try Tkinter highlightbackground (classic Tk widgets)
        3. If both fail, silently continue (widget may not support borders)
    
    Border Configuration:
        - Color: BORDER_COLOR (#000000 - true black)
        - Width: 1 pixel (subtle but visible definition)
    
    Compatibility:
        - CustomTkinter widgets: Uses border_color and border_width
        - Tkinter widgets: Uses highlightbackground
        - Unsupported widgets: Gracefully ignores without error
    
    Error Handling:
        All configuration attempts wrapped in nested try-except blocks.
        Failures are silent (borders are aesthetic enhancement, not critical).
    
    Args:
        widget: Any CustomTkinter or Tkinter widget instance
    
    Returns:
        None
    
    Side Effects:
        - May modify widget's border_color and border_width properties
        - May modify widget's highlightbackground property
        - No effect if widget doesn't support borders
    
    Example:
        >>> frame = ctk.CTkFrame(root)
        >>> style_widget_border(frame)  # Applies black border
    
    Notes:
        - Safe to call on any widget (no exceptions raised)
        - Idempotent (can be called multiple times safely)
        - Useful for frames, containers, and custom widgets
    """
    try:
        widget.configure(border_color=BORDER_COLOR, border_width=1)
    except Exception:
        try:
            widget.configure(highlightbackground=BORDER_COLOR)
        except Exception:
            pass
