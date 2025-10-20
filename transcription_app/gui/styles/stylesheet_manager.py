"""
Centralized stylesheet management for the application
Provides theme switching and consistent styling across all widgets
"""
from enum import Enum
from typing import Dict
from dataclasses import dataclass


class Theme(Enum):
    """Available application themes"""
    LIGHT = "light"
    DARK = "dark"


@dataclass
class ColorPalette:
    """Color palette for a theme"""
    # Main colors
    background: str
    foreground: str

    # Primary accent
    primary: str
    primary_hover: str
    primary_pressed: str
    primary_disabled: str

    # Text colors
    text_primary: str
    text_secondary: str
    text_disabled: str

    # Border colors
    border: str
    border_focus: str
    border_hover: str

    # Surface colors (for cards, panels, etc.)
    surface: str
    surface_hover: str
    surface_selected: str

    # Status bar
    status_bar_bg: str
    status_bar_gradient_start: str
    status_bar_gradient_end: str
    status_bar_border: str

    # Scrollbar
    scrollbar_bg: str
    scrollbar_handle: str
    scrollbar_handle_hover: str

    # Splitter
    splitter_bg: str
    splitter_hover: str


class StyleSheetManager:
    """Manages application stylesheets and themes"""

    # Light theme color palette (Fluent Design-inspired)
    LIGHT_PALETTE = ColorPalette(
        background="#ffffff",
        foreground="#24292e",

        primary="#0078d4",
        primary_hover="#106ebe",
        primary_pressed="#005a9e",
        primary_disabled="#cccccc",

        text_primary="#24292e",
        text_secondary="#495057",
        text_disabled="#999999",

        border="#e1e4e8",
        border_focus="#0078d4",
        border_hover="#c1c8cd",

        surface="#fafbfc",
        surface_hover="#e8f4fc",
        surface_selected="#e8f4fc",

        status_bar_bg="#e9ecef",
        status_bar_gradient_start="#f8f9fa",
        status_bar_gradient_end="#e9ecef",
        status_bar_border="#dee2e6",

        scrollbar_bg="#f6f8fa",
        scrollbar_handle="#c1c8cd",
        scrollbar_handle_hover="#a8b0b8",

        splitter_bg="#dee2e6",
        splitter_hover="#0078d4"
    )

    # Dark theme color palette
    DARK_PALETTE = ColorPalette(
        background="#1e1e1e",
        foreground="#e0e0e0",

        primary="#0078d4",
        primary_hover="#106ebe",
        primary_pressed="#005a9e",
        primary_disabled="#444444",

        text_primary="#e0e0e0",
        text_secondary="#c0c0c0",
        text_disabled="#888888",

        border="#404040",
        border_focus="#0078d4",
        border_hover="#505050",

        surface="#252525",
        surface_hover="#094771",
        surface_selected="#094771",

        status_bar_bg="#1e1e1e",
        status_bar_gradient_start="#252525",
        status_bar_gradient_end="#1e1e1e",
        status_bar_border="#404040",

        scrollbar_bg="#252525",
        scrollbar_handle="#505050",
        scrollbar_handle_hover="#606060",

        splitter_bg="#404040",
        splitter_hover="#0078d4"
    )

    def __init__(self, theme: Theme = Theme.LIGHT):
        """
        Initialize the stylesheet manager

        Args:
            theme: Initial theme to use
        """
        self.current_theme = theme
        self._palette = self._get_palette(theme)

    def _get_palette(self, theme: Theme) -> ColorPalette:
        """Get color palette for theme"""
        if theme == Theme.DARK:
            return self.DARK_PALETTE
        return self.LIGHT_PALETTE

    def set_theme(self, theme: Theme):
        """
        Switch to a different theme

        Args:
            theme: Theme to switch to
        """
        self.current_theme = theme
        self._palette = self._get_palette(theme)

    def get_stylesheet(self) -> str:
        """
        Get complete stylesheet for current theme

        Returns:
            Complete QSS stylesheet string
        """
        components = [
            self._get_main_window_style(),
            self._get_button_style(),
            self._get_text_edit_style(),
            self._get_list_widget_style(),
            self._get_status_bar_style(),
            self._get_group_box_style(),
            self._get_menu_style(),
            self._get_scrollbar_style(),
            self._get_splitter_style(),
            self._get_line_edit_style(),
            self._get_label_style(),
            self._get_checkbox_style()
        ]
        return "\n".join(components)

    def _get_main_window_style(self) -> str:
        """Main window styling"""
        return f"""
        QMainWindow {{
            background-color: {self._palette.background};
        }}
        """

    def _get_button_style(self) -> str:
        """Button styling"""
        return f"""
        QPushButton {{
            background-color: {self._palette.primary};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 600;
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QPushButton:hover {{
            background-color: {self._palette.primary_hover};
        }}
        QPushButton:pressed {{
            background-color: {self._palette.primary_pressed};
        }}
        QPushButton:disabled {{
            background-color: {self._palette.primary_disabled};
            color: {self._palette.text_disabled};
        }}
        """

    def _get_text_edit_style(self) -> str:
        """Text edit styling"""
        bg_color = self._palette.surface if self.current_theme == Theme.DARK else "white"
        text_color = self._palette.text_primary if self.current_theme == Theme.DARK else "#24292e"

        return f"""
        QTextEdit {{
            background-color: {bg_color};
            color: {text_color};
            border: 2px solid {self._palette.border};
            border-radius: 6px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
        }}
        QTextEdit:focus {{
            border: 2px solid {self._palette.border_focus};
        }}
        """

    def _get_list_widget_style(self) -> str:
        """List widget styling"""
        bg_color = self._palette.surface if self.current_theme == Theme.DARK else "white"
        text_color = self._palette.text_primary if self.current_theme == Theme.DARK else "#24292e"
        item_border = "#3f3f3f" if self.current_theme == Theme.DARK else "#f0f0f0"
        selected_text = "white" if self.current_theme == Theme.DARK else "#000"

        return f"""
        QListWidget {{
            background-color: {bg_color};
            color: {text_color};
            border: 2px solid {self._palette.border};
            border-radius: 6px;
            padding: 10px;
            font-family: 'Consolas', 'Courier New', monospace;
        }}
        QListWidget:focus {{
            border: 2px solid {self._palette.border_focus};
        }}
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {item_border};
        }}
        QListWidget::item:selected {{
            background-color: {self._palette.surface_selected};
            color: {selected_text};
        }}
        """

    def _get_status_bar_style(self) -> str:
        """Status bar styling"""
        return f"""
        QStatusBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self._palette.status_bar_gradient_start},
                stop:1 {self._palette.status_bar_gradient_end});
            color: {self._palette.text_secondary};
            border-top: 2px solid {self._palette.status_bar_border};
            font-size: 12px;
            font-weight: 500;
            padding: 4px;
        }}
        """

    def _get_group_box_style(self) -> str:
        """Group box styling"""
        return f"""
        QGroupBox {{
            font-weight: bold;
            font-size: 13px;
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
            background-color: {self._palette.surface};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {self._palette.text_primary};
        }}
        """

    def _get_menu_style(self) -> str:
        """Menu and menu bar styling"""
        menu_bg = self._palette.surface if self.current_theme == Theme.DARK else "white"
        menubar_gradient_start = self._palette.surface if self.current_theme == Theme.DARK else "#ffffff"
        menubar_gradient_end = self._palette.background if self.current_theme == Theme.DARK else "#f6f8fa"

        return f"""
        QMenuBar {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {menubar_gradient_start}, stop:1 {menubar_gradient_end});
            color: {self._palette.text_primary};
            border-bottom: 2px solid {self._palette.border};
            font-size: 13px;
            font-weight: 500;
        }}
        QMenuBar::item {{
            padding: 6px 12px;
            background-color: transparent;
            color: {self._palette.text_primary};
        }}
        QMenuBar::item:selected {{
            background-color: {self._palette.surface_hover};
            color: {self._palette.primary if self.current_theme == Theme.LIGHT else "white"};
        }}
        QMenu {{
            background-color: {menu_bg};
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: 6px;
            padding: 4px;
        }}
        QMenu::item {{
            padding: 8px 32px 8px 24px;
            border-radius: 4px;
        }}
        QMenu::item:selected {{
            background-color: {self._palette.surface_hover};
            color: {self._palette.primary if self.current_theme == Theme.LIGHT else "white"};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {self._palette.border};
            margin: 4px 8px;
        }}
        """

    def _get_scrollbar_style(self) -> str:
        """Scrollbar styling"""
        return f"""
        QScrollBar:vertical {{
            border: none;
            background: {self._palette.scrollbar_bg};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {self._palette.scrollbar_handle};
            border-radius: 6px;
            min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {self._palette.scrollbar_handle_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """

    def _get_splitter_style(self) -> str:
        """Splitter styling"""
        return f"""
        QSplitter::handle {{
            background-color: {self._palette.splitter_bg};
            margin: 2px 0;
        }}
        QSplitter::handle:hover {{
            background-color: {self._palette.splitter_hover};
        }}
        """

    def _get_line_edit_style(self) -> str:
        """Line edit styling"""
        if self.current_theme == Theme.DARK:
            return f"""
            QLineEdit {{
                background-color: {self._palette.surface};
                color: {self._palette.text_primary};
                border: 2px solid {self._palette.border};
                border-radius: 6px;
                padding: 8px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self._palette.border_focus};
            }}
            """
        return ""  # Light theme line edits use default styling

    def _get_label_style(self) -> str:
        """Label styling"""
        if self.current_theme == Theme.DARK:
            return f"""
            QLabel {{
                color: {self._palette.text_primary};
            }}
            """
        return ""  # Light theme labels use default styling

    def _get_checkbox_style(self) -> str:
        """Checkbox styling"""
        if self.current_theme == Theme.DARK:
            return f"""
            QCheckBox {{
                color: {self._palette.text_primary};
            }}
            """
        return ""  # Light theme checkboxes use default styling

    def get_palette(self) -> ColorPalette:
        """
        Get current color palette

        Returns:
            Current ColorPalette instance
        """
        return self._palette

    @staticmethod
    def get_available_themes() -> list:
        """
        Get list of available themes

        Returns:
            List of Theme enum values
        """
        return [Theme.LIGHT, Theme.DARK]
