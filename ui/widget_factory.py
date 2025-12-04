"""Widget Factory - Centralized UI Component Creation with Consistent Theming.

This module implements the Factory Pattern for creating themed CustomTkinter widgets
with consistent styling across the entire application. It provides a centralized
point for widget creation, ensuring visual consistency and simplifying theme changes.

Architecture - Factory Pattern:
    Instead of creating widgets directly with individual styling parameters scattered
    throughout the codebase, this factory provides pre-configured widget creation
    functions that apply the theme automatically. This centralizes styling logic
    and enables easy theme modifications.

Design Benefits:
    1. Consistency: All widgets use the same theme colors and styling
    2. Maintainability: Theme changes only require updates in one place
    3. Simplicity: UI code becomes cleaner without repetitive styling parameters
    4. Type Safety: Factory functions provide clear interfaces for widget creation
    5. Error Handling: Centralized error handling for styling edge cases

Widget Types Provided:
    Labels:
        - Title Labels: Large, bold headers (30pt font)
        - Body Labels: Normal text labels (14pt font, customizable)
    
    Input:
        - Entry Fields: Styled text input with borders and placeholders
    
    Buttons:
        - Primary Buttons: Large action buttons (360x64px) with icons
        - Small Buttons: Compact buttons (160x44px) for secondary actions

Theme Integration:
    All widgets automatically use colors and fonts from the theme module:
    - Colors: BG_COLOR, TEXT_COLOR, BUTTON_COLOR, BUTTON_HOVER, BORDER_COLOR
    - Fonts: Retrieved via theme.get_font() for consistency
    - Borders: Consistent border width and corner radius

Error Handling:
    - Border configuration wrapped in try-except (some CTk versions don't support borders)
    - Errors logged via UIErrorHandler.log_and_pass (non-blocking)
    - Graceful degradation if optional features fail

Usage Pattern:
    ```python
    from ui import widget_factory as wf
    
    # Create title
    title = wf.create_title_label(parent, "Library System")
    
    # Create entry
    entry = wf.create_entry(parent, placeholder="Enter book title", width=400)
    
    # Create primary button with icon
    btn = wf.create_primary_button(parent, "Save Book", command=save_func, image=icon)
    
    # Create small button
    cancel = wf.create_small_button(parent, "Cancel", command=close_func)
    ```

CustomTkinter Integration:
    All widgets are CustomTkinter (ctk) components, providing:
    - Modern, themed appearance
    - Cross-platform consistency
    - Dark/light mode support (via theme)
    - Scalable UI elements

See Also:
    - ui.theme: Theme constants and font management
    - utils.logger: Logging infrastructure for error handling
"""

import customtkinter as ctk
from . import theme
from typing import Callable, Optional
from utils.logger import LibraryLogger, UIErrorHandler

# Configurar logger para este módulo
logger = LibraryLogger.get_logger(__name__)


def create_title_label(parent, text: str):
    """Create a large, bold title label with theme styling.
    
    Creates a centered title label suitable for page headers and section titles.
    Uses large font size (30pt) with bold weight for visual hierarchy.
    
    Purpose:
        Provides consistent title styling across all windows and dialogs in the
        application, following the cozy Japanese aesthetic theme.
    
    Styling:
        - Font: 30pt, bold weight
        - Color: theme.TEXT_COLOR
        - Alignment: Left (controlled by parent layout)
    
    Args:
        parent: Parent widget/frame to contain the label
        text (str): Title text to display
    
    Returns:
        CTkLabel: Configured title label widget
    
    Side Effects:
        None (widget not packed/placed, caller manages layout)
    """
    font = theme.get_font(parent, size=30, weight="bold")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=theme.TEXT_COLOR)
    return lbl


def create_body_label(parent, text: str, size: int = 14):
    """Create a normal-weight body text label with theme styling.
    
    Creates a text label for general content, instructions, and descriptions.
    Uses normal font weight with customizable size for flexibility.
    
    Purpose:
        Provides consistent body text styling for content display, form labels,
        and instructional text throughout the application.
    
    Styling:
        - Font: Customizable size (default 14pt), normal weight
        - Color: theme.TEXT_COLOR
        - Alignment: Left (controlled by parent layout)
    
    Args:
        parent: Parent widget/frame to contain the label
        text (str): Body text to display
        size (int, optional): Font size in points. Defaults to 14.
    
    Returns:
        CTkLabel: Configured body text label widget
    
    Side Effects:
        None (widget not packed/placed, caller manages layout)
    """
    font = theme.get_font(parent, size=size, weight="normal")
    lbl = ctk.CTkLabel(parent, text=text, font=font, text_color=theme.TEXT_COLOR)
    return lbl


def create_entry(parent, placeholder: str = "", width: int = 300):
    """Create a styled text entry field with theme colors and borders.
    
    Creates a single-line text input field with placeholder text, rounded corners,
    and consistent theme styling for forms and dialogs.
    
    Purpose:
        Provides consistent input field styling for all text entry needs across
        the application, including book titles, user names, ISBNs, etc.
    
    Styling:
        - Font: 13pt, normal weight
        - Colors: BG_COLOR background, TEXT_COLOR text, BORDER_COLOR border
        - Border: 1px solid border with 8px corner radius
        - Dimensions: Customizable width, fixed 36px height
    
    Features:
        - Placeholder text support (grayed out until user types)
        - Rounded corners for modern aesthetic
        - Border for clear input field definition
    
    Args:
        parent: Parent widget/frame to contain the entry field
        placeholder (str, optional): Placeholder text shown when empty. Defaults to "".
        width (int, optional): Entry field width in pixels. Defaults to 300.
    
    Returns:
        CTkEntry: Configured text entry widget
    
    Side Effects:
        None (widget not packed/placed, caller manages layout)
    """
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
    """Create a large, rounded primary action button with theme colors.
    
    Creates a prominent button for primary actions (save, create, submit, etc.)
    with large dimensions, bold text, optional icon, and hover effects.
    
    Purpose:
        Provides consistent styling for main action buttons in forms, dialogs,
        and the main menu. Large size and bold styling emphasize importance
        in the UI hierarchy.
    
    Styling:
        - Font: 16pt, bold weight
        - Colors: BUTTON_COLOR background, BUTTON_HOVER on hover, TEXT_COLOR text
        - Border: 1px solid BORDER_COLOR (echoes black line art in backgrounds)
        - Corners: 14px radius for strong rounded appearance
        - Dimensions: Default 360x64px (customizable)
    
    Features:
        - Icon support: Optional image displayed alongside text
        - Hover effect: Automatic color change on mouse hover
        - Strong border: Complements pixel-art aesthetic
        - Click callback: Executes command function on click
    
    Error Handling:
        Border configuration wrapped in try-except for CTk version compatibility.
        Logs and continues if border configuration fails.
    
    Args:
        parent: Parent widget/frame to contain the button
        text (str): Button label text
        command (Optional[Callable], optional): Function to call on button click. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 360.
        height (int, optional): Button height in pixels. Defaults to 64.
        image (Optional[object], optional): CTkImage icon to display. Defaults to None.
    
    Returns:
        CTkButton: Configured primary action button widget
    
    Side Effects:
        - May log error if border configuration fails (non-blocking)
        - Widget not packed/placed, caller manages layout
    """
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
    """Create a compact, rounded button for secondary actions.
    
    Creates a smaller button for secondary actions (cancel, close, back, etc.)
    with normal font weight and reduced dimensions to indicate lower priority
    in the UI hierarchy.
    
    Purpose:
        Provides consistent styling for secondary action buttons that complement
        primary buttons without competing for visual attention. Used for cancel,
        close, and auxiliary actions.
    
    Styling:
        - Font: 14pt, normal weight
        - Colors: BUTTON_COLOR background, BUTTON_HOVER on hover, TEXT_COLOR text
        - Border: 1px solid BORDER_COLOR
        - Corners: 12px radius (slightly less rounded than primary)
        - Dimensions: Default 160x44px (customizable)
    
    Features:
        - Icon support: Optional image displayed alongside text
        - Hover effect: Automatic color change on mouse hover
        - Smaller footprint: Takes less space than primary buttons
        - Click callback: Executes command function on click
    
    Differences from Primary Button:
        - Smaller dimensions (160x44 vs 360x64)
        - Normal font weight (vs bold)
        - Less rounded corners (12px vs 14px)
        - Smaller font size (14pt vs 16pt)
    
    Error Handling:
        Border configuration wrapped in try-except for CTk version compatibility.
        Logs and continues if border configuration fails.
    
    Args:
        parent: Parent widget/frame to contain the button
        text (str): Button label text
        command (Optional[Callable], optional): Function to call on button click. Defaults to None.
        width (int, optional): Button width in pixels. Defaults to 160.
        height (int, optional): Button height in pixels. Defaults to 44.
        image (Optional[object], optional): CTkImage icon to display. Defaults to None.
    
    Returns:
        CTkButton: Configured secondary action button widget
    
    Side Effects:
        - May log error if border configuration fails (non-blocking)
        - Widget not packed/placed, caller manages layout
    """
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
