"""
Centralized stylesheet management for the application
Provides theme switching and consistent styling across all widgets
Modern 2025 design system with complete design tokens
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
    """Complete color palette and design tokens for a theme"""

    # ===== PRIMARY COLORS =====
    primary_50: str
    primary_100: str
    primary_300: str
    primary_500: str   # Main primary
    primary_600: str   # Hover
    primary_700: str   # Pressed

    # ===== NEUTRAL SCALE =====
    neutral_0: str     # White/Black
    neutral_50: str
    neutral_100: str
    neutral_200: str
    neutral_300: str
    neutral_400: str
    neutral_500: str
    neutral_600: str
    neutral_700: str
    neutral_900: str

    # ===== SEMANTIC COLORS =====
    success_light: str
    success_main: str
    success_dark: str

    warning_light: str
    warning_main: str
    warning_dark: str

    error_light: str
    error_main: str
    error_dark: str

    info_light: str
    info_main: str
    info_dark: str

    # ===== SURFACE ELEVATION =====
    surface_0: str     # Base
    surface_1: str     # Cards
    surface_2: str     # Elevated cards
    surface_3: str     # Dialogs

    # ===== SHADOWS =====
    shadow_sm: str
    shadow_md: str
    shadow_lg: str
    shadow_xl: str

    # ===== LEGACY COMPATIBILITY =====
    # (For components that still reference old names)
    background: str
    foreground: str
    text_primary: str
    text_secondary: str
    border: str
    border_focus: str


# ===== DESIGN TOKENS (Module-level constants) =====

# Spacing scale (compact 4px grid system)
SPACING = {
    'xs': '2px',    # Extra small
    'sm': '4px',    # Small
    'md': '8px',    # Medium
    'base': '12px', # Base unit
    'lg': '16px',   # Large
    'xl': '20px',   # Extra large
    '2xl': '24px',  # 2x large
    '3xl': '32px',  # 3x large
    '4xl': '40px',  # 4x large
}

# Border radius scale (more subtle)
RADIUS = {
    'sm': '2px',    # Small
    'md': '4px',    # Medium
    'lg': '6px',    # Large
    'xl': '8px',    # Extra large
    'full': '9999px', # Circle/pill
}

# Typography scale (compact professional sizing)
TYPOGRAPHY = {
    # Font families
    'font_primary': "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    'font_mono': "'SF Mono', 'Consolas', 'Monaco', 'Courier New', monospace",

    # Font sizes (reduced for compact look)
    'size_xs': '10px',
    'size_sm': '11px',
    'size_base': '12px',
    'size_lg': '13px',
    'size_xl': '14px',
    'size_2xl': '18px',
    'size_3xl': '24px',
    'size_4xl': '32px',

    # Font weights
    'weight_regular': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
}


class StyleSheetManager:
    """Manages application stylesheets with modern 2025 design system"""

    # ===== MODERN LIGHT THEME (Material Design 3 inspired) =====
    LIGHT_PALETTE = ColorPalette(
        # Primary colors
        primary_50="#E3F2FD",
        primary_100="#BBDEFB",
        primary_300="#64B5F6",
        primary_500="#2196F3",
        primary_600="#1E88E5",
        primary_700="#1976D2",

        # Neutrals
        neutral_0="#FFFFFF",
        neutral_50="#FAFAFA",
        neutral_100="#F5F5F5",
        neutral_200="#EEEEEE",
        neutral_300="#E0E0E0",
        neutral_400="#BDBDBD",
        neutral_500="#9E9E9E",
        neutral_600="#757575",
        neutral_700="#616161",
        neutral_900="#212121",

        # Semantic colors
        success_light="#E8F5E9",
        success_main="#4CAF50",
        success_dark="#2E7D32",

        warning_light="#FFF3E0",
        warning_main="#FF9800",
        warning_dark="#E65100",

        error_light="#FFEBEE",
        error_main="#F44336",
        error_dark="#C62828",

        info_light="#E3F2FD",
        info_main="#2196F3",
        info_dark="#1565C0",

        # Surface elevation
        surface_0="#FFFFFF",
        surface_1="#FAFAFA",
        surface_2="#F5F5F5",
        surface_3="#F0F0F0",

        # Shadows (Material Design elevation)
        shadow_sm="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        shadow_md="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
        shadow_xl="0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",

        # Legacy compatibility
        background="#FFFFFF",
        foreground="#212121",
        text_primary="#212121",
        text_secondary="#616161",
        border="#E0E0E0",
        border_focus="#2196F3",
    )

    # ===== MODERN DARK THEME (Material Design 3 Dark) =====
    DARK_PALETTE = ColorPalette(
        # Primary colors (adjusted for dark)
        primary_50="#0D47A1",
        primary_100="#1565C0",
        primary_300="#64B5F6",
        primary_500="#42A5F5",
        primary_600="#2196F3",
        primary_700="#1E88E5",

        # Dark neutrals (Material Design dark baseline)
        neutral_0="#FFFFFF",
        neutral_50="#E5E5E5",
        neutral_100="#CFCFCF",
        neutral_200="#9E9E9E",
        neutral_300="#6B6B6B",
        neutral_400="#525252",
        neutral_500="#3D3D3D",
        neutral_600="#2D2D2D",
        neutral_700="#1E1E1E",
        neutral_900="#121212",

        # Semantic colors (adjusted for dark)
        success_light="#1B5E20",
        success_main="#66BB6A",
        success_dark="#A5D6A7",

        warning_light="#E65100",
        warning_main="#FFA726",
        warning_dark="#FFCC80",

        error_light="#B71C1C",
        error_main="#EF5350",
        error_dark="#E57373",

        info_light="#0D47A1",
        info_main="#42A5F5",
        info_dark="#90CAF9",

        # Surface elevation (Material Design dark surfaces)
        surface_0="#121212",
        surface_1="#1E1E1E",
        surface_2="#232323",
        surface_3="#2C2C2C",

        # Shadows (softer for dark theme)
        shadow_sm="0 1px 2px 0 rgba(0, 0, 0, 0.3)",
        shadow_md="0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3)",
        shadow_lg="0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -2px rgba(0, 0, 0, 0.3)",
        shadow_xl="0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.3)",

        # Legacy compatibility
        background="#121212",
        foreground="#E0E0E0",
        text_primary="#E0E0E0",
        text_secondary="#CFCFCF",
        border="#3D3D3D",
        border_focus="#42A5F5",
    )

    # Design tokens (spacing, typography, etc.)
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'base': '16px',
        'lg': '20px',
        'xl': '24px',
        '2xl': '32px',
        '3xl': '40px',
        '4xl': '48px',
    }

    RADIUS = {
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',
    }

    TYPOGRAPHY = {
        'font_primary': "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Helvetica Neue', sans-serif",
        'font_mono': "'Consolas', 'Monaco', 'Courier New', monospace",
        'size_xs': '11px',
        'size_sm': '13px',
        'size_base': '14px',
        'size_md': '16px',
        'size_lg': '20px',
        'size_xl': '24px',
        'size_2xl': '32px',
        'size_3xl': '40px',
        'weight_regular': '400',
        'weight_medium': '500',
        'weight_semibold': '600',
        'weight_bold': '700',
    }

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
            self._get_base_style(),
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
            self._get_checkbox_style(),
            self._get_progress_bar_style(),
            self._get_combo_box_style(),
        ]
        return "\n".join(components)

    def _get_base_style(self) -> str:
        """Base styling and transitions"""
        return """
        * {
            outline: none;
        }
        """

    def _get_main_window_style(self) -> str:
        """Main window styling"""
        return f"""
        QMainWindow {{
            background-color: {self._palette.background};
        }}

        QWidget {{
            font-family: {self.TYPOGRAPHY['font_primary']};
            font-size: {self.TYPOGRAPHY['size_base']};
        }}
        """

    def _get_button_style(self) -> str:
        """Modern button styling with shadows and transitions"""
        return f"""
        QPushButton {{
            background-color: {self._palette.primary_500};
            color: white;
            border: none;
            border-radius: {self.RADIUS['md']};
            padding: 12px 24px;
            font-size: {self.TYPOGRAPHY['size_base']};
            font-weight: {self.TYPOGRAPHY['weight_semibold']};
            font-family: {self.TYPOGRAPHY['font_primary']};
        }}
        QPushButton:hover {{
            background-color: {self._palette.primary_600};
        }}
        QPushButton:pressed {{
            background-color: {self._palette.primary_700};
        }}
        QPushButton:disabled {{
            background-color: {self._palette.neutral_300};
            color: {self._palette.neutral_500};
        }}

        /* Secondary button variant */
        QPushButton[variant="secondary"] {{
            background-color: transparent;
            color: {self._palette.primary_500};
            border: 2px solid {self._palette.neutral_300};
            padding: 10px 22px;
        }}
        QPushButton[variant="secondary"]:hover {{
            border-color: {self._palette.primary_500};
            background-color: {self._palette.primary_50};
        }}
        """

    def _get_text_edit_style(self) -> str:
        """Modern text edit styling"""
        bg_color = self._palette.surface_0 if self.current_theme == Theme.DARK else "white"

        return f"""
        QTextEdit {{
            background-color: {bg_color};
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            padding: {self.SPACING['md']};
            font-family: {self.TYPOGRAPHY['font_mono']};
            font-size: {self.TYPOGRAPHY['size_sm']};
        }}
        QTextEdit:focus {{
            border-color: {self._palette.border_focus};
        }}
        """

    def _get_list_widget_style(self) -> str:
        """Modern list widget styling"""
        bg_color = self._palette.surface_0 if self.current_theme == Theme.DARK else "white"

        return f"""
        QListWidget {{
            background-color: {bg_color};
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            padding: {self.SPACING['sm']};
            font-family: {self.TYPOGRAPHY['font_mono']};
        }}
        QListWidget:focus {{
            border-color: {self._palette.border_focus};
        }}
        QListWidget::item {{
            padding: {self.SPACING['sm']};
            border-radius: {self.RADIUS['sm']};
            margin: 2px 0;
        }}
        QListWidget::item:selected {{
            background-color: {self._palette.primary_50 if self.current_theme == Theme.LIGHT else self._palette.surface_2};
            color: {self._palette.text_primary};
        }}
        QListWidget::item:hover {{
            background-color: {self._palette.surface_1};
        }}
        """

    def _get_status_bar_style(self) -> str:
        """Flat, modern status bar"""
        return f"""
        QStatusBar {{
            background-color: {self._palette.surface_1};
            color: {self._palette.text_secondary};
            border-top: 1px solid {self._palette.border};
            font-size: {self.TYPOGRAPHY['size_sm']};
            font-weight: {self.TYPOGRAPHY['weight_medium']};
            padding: {self.SPACING['xs']};
        }}
        """

    def _get_group_box_style(self) -> str:
        """Modern, lightweight group box"""
        return f"""
        QGroupBox {{
            font-weight: {self.TYPOGRAPHY['weight_semibold']};
            font-size: {self.TYPOGRAPHY['size_md']};
            color: {self._palette.text_primary};
            border: 1px solid {self._palette.border};
            border-radius: {self.RADIUS['lg']};
            margin-top: {self.SPACING['base']};
            padding: {self.SPACING['xl']} {self.SPACING['base']} {self.SPACING['base']} {self.SPACING['base']};
            background-color: {self._palette.surface_1};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 {self.SPACING['md']};
            background-color: {self._palette.background};
            color: {self._palette.text_primary};
        }}
        """

    def _get_menu_style(self) -> str:
        """Modern menu styling"""
        menu_bg = self._palette.surface_1 if self.current_theme == Theme.DARK else "white"

        return f"""
        QMenuBar {{
            background-color: {self._palette.background};
            color: {self._palette.text_primary};
            border-bottom: 1px solid {self._palette.border};
            font-size: {self.TYPOGRAPHY['size_sm']};
            font-weight: {self.TYPOGRAPHY['weight_medium']};
            padding: {self.SPACING['xs']} 0;
        }}
        QMenuBar::item {{
            padding: {self.SPACING['sm']} {self.SPACING['md']};
            background-color: transparent;
            color: {self._palette.text_primary};
            border-radius: {self.RADIUS['sm']};
            margin: 0 {self.SPACING['xs']};
        }}
        QMenuBar::item:selected {{
            background-color: {self._palette.surface_1};
            color: {self._palette.primary_500};
        }}

        QMenu {{
            background-color: {menu_bg};
            color: {self._palette.text_primary};
            border: 1px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            padding: {self.SPACING['xs']};
        }}
        QMenu::item {{
            padding: {self.SPACING['sm']} {self.SPACING['xl']} {self.SPACING['sm']} {self.SPACING['lg']};
            border-radius: {self.RADIUS['sm']};
            margin: 2px {self.SPACING['xs']};
        }}
        QMenu::item:selected {{
            background-color: {self._palette.primary_50 if self.current_theme == Theme.LIGHT else self._palette.surface_2};
            color: {self._palette.primary_500 if self.current_theme == Theme.LIGHT else "white"};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {self._palette.border};
            margin: {self.SPACING['xs']} {self.SPACING['md']};
        }}
        """

    def _get_scrollbar_style(self) -> str:
        """Thinner, modern scrollbar"""
        return f"""
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 0;
        }}
        QScrollBar::handle:vertical {{
            background: {self._palette.neutral_400};
            border-radius: {self.RADIUS['sm']};
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {self._palette.neutral_500};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
            height: 0;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 8px;
            margin: 0;
        }}
        QScrollBar::handle:horizontal {{
            background: {self._palette.neutral_400};
            border-radius: {self.RADIUS['sm']};
            min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: {self._palette.neutral_500};
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            border: none;
            background: none;
            width: 0;
        }}
        """

    def _get_splitter_style(self) -> str:
        """Minimal splitter styling"""
        return f"""
        QSplitter::handle {{
            background-color: {self._palette.border};
            margin: 0;
        }}
        QSplitter::handle:hover {{
            background-color: {self._palette.primary_500};
        }}
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        """

    def _get_line_edit_style(self) -> str:
        """Modern input field styling"""
        bg_color = self._palette.surface_1 if self.current_theme == Theme.DARK else "white"

        return f"""
        QLineEdit {{
            background-color: {bg_color};
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            padding: {self.SPACING['md']} {self.SPACING['base']};
            font-size: {self.TYPOGRAPHY['size_base']};
        }}
        QLineEdit:hover {{
            border-color: {self._palette.neutral_400};
        }}
        QLineEdit:focus {{
            border-color: {self._palette.border_focus};
        }}
        QLineEdit:disabled {{
            background-color: {self._palette.neutral_100};
            color: {self._palette.neutral_500};
        }}
        """

    def _get_label_style(self) -> str:
        """Label styling"""
        return f"""
        QLabel {{
            color: {self._palette.text_primary};
        }}
        """

    def _get_checkbox_style(self) -> str:
        """Checkbox styling"""
        return f"""
        QCheckBox {{
            color: {self._palette.text_primary};
            spacing: {self.SPACING['sm']};
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: {self.RADIUS['sm']};
            border: 2px solid {self._palette.border};
            background-color: {self._palette.background};
        }}
        QCheckBox::indicator:hover {{
            border-color: {self._palette.neutral_400};
        }}
        QCheckBox::indicator:checked {{
            background-color: {self._palette.primary_500};
            border-color: {self._palette.primary_500};
        }}
        """

    def _get_progress_bar_style(self) -> str:
        """Modern, thin progress bar"""
        return f"""
        QProgressBar {{
            border: none;
            border-radius: {self.RADIUS['full']};
            background-color: {self._palette.neutral_200};
            height: 8px;
            text-align: center;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self._palette.primary_500},
                stop:1 {self._palette.primary_300});
            border-radius: {self.RADIUS['full']};
        }}
        """

    def _get_combo_box_style(self) -> str:
        """Modern combo box styling"""
        bg_color = self._palette.surface_1 if self.current_theme == Theme.DARK else "white"

        return f"""
        QComboBox {{
            background-color: {bg_color};
            color: {self._palette.text_primary};
            border: 2px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            padding: {self.SPACING['md']} {self.SPACING['base']};
            font-size: {self.TYPOGRAPHY['size_base']};
            min-height: 20px;
        }}
        QComboBox:hover {{
            border-color: {self._palette.neutral_400};
        }}
        QComboBox:focus {{
            border-color: {self._palette.border_focus};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 32px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border: 2px solid {self._palette.neutral_600};
            width: 8px;
            height: 8px;
            border-top: none;
            border-left: none;
            margin-right: {self.SPACING['md']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {bg_color};
            border: 1px solid {self._palette.border};
            border-radius: {self.RADIUS['md']};
            selection-background-color: {self._palette.primary_50 if self.current_theme == Theme.LIGHT else self._palette.surface_2};
            selection-color: {self._palette.text_primary};
        }}
        """

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
