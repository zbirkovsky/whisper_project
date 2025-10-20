"""
Icon manager for consistent iconography across the application
Uses Qt standard icons and Unicode symbols for Material Design-style appearance
"""
from PySide6.QtWidgets import QStyle, QApplication
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt, QSize
from typing import Optional


class IconManager:
    """Manages icons for the application"""

    # Icon names mapped to Unicode symbols
    ICONS = {
        # File operations
        'folder-open': '\U0001F4C2',  # 📂
        'file': '\U0001F4C4',  # 📄
        'save': '\U0001F4BE',  # 💾

        # Media controls
        'record': '\u25CF',  # ⚫ (filled circle)
        'play': '\u25B6',  # ▶
        'pause': '\u23F8',  # ⏸
        'stop': '\u23F9',  # ⏹

        # Actions
        'clear': '\U0001F5D1',  # 🗑
        'settings': '\u2699',  # ⚙
        'search': '\U0001F50D',  # 🔍
        'copy': '\U0001F4CB',  # 📋
        'edit': '\u270E',  # ✎

        # Navigation
        'close': '\u2715',  # ✕
        'check': '\u2713',  # ✓
        'plus': '\u002B',  # +
        'minus': '\u2212',  # −
        'arrow-up': '\u25B2',  # ▲
        'arrow-down': '\u25BC',  # ▼

        # Status
        'error': '\u26A0',  # ⚠
        'info': '\u2139',  # ℹ
        'success': '\u2714',  # ✔

        # Microphone
        'microphone': '\U0001F3A4',  # 🎤

        # Document types
        'text': '\U0001F4DD',  # 📝
        'subtitle': '\U0001F4FA',  # 📺
    }

    def __init__(self, default_size: int = 16):
        """
        Initialize icon manager

        Args:
            default_size: Default icon size in pixels
        """
        self.default_size = default_size
        self._icon_cache = {}

    @staticmethod
    def get_standard_icon(icon_type: QStyle.StandardPixmap) -> QIcon:
        """
        Get Qt standard icon

        Args:
            icon_type: Qt standard icon type

        Returns:
            QIcon instance
        """
        style = QApplication.style()
        if style:
            return style.standardIcon(icon_type)
        return QIcon()

    def create_text_icon(
        self,
        text: str,
        size: Optional[int] = None,
        color: Optional[QColor] = None,
        background: Optional[QColor] = None
    ) -> QIcon:
        """
        Create an icon from text (Unicode symbol)

        Args:
            text: Text/symbol to use
            size: Icon size in pixels (uses default if None)
            color: Text color (black if None)
            background: Background color (transparent if None)

        Returns:
            QIcon instance
        """
        if size is None:
            size = self.default_size

        if color is None:
            color = QColor(Qt.GlobalColor.black)

        # Create cache key
        cache_key = f"{text}_{size}_{color.name()}_{background.name() if background else 'transparent'}"
        if cache_key in self._icon_cache:
            return self._icon_cache[cache_key]

        # Create pixmap
        pixmap = QPixmap(size, size)
        pixmap.fill(background if background else Qt.GlobalColor.transparent)

        # Draw text
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(color)

        # Use appropriate font size (slightly smaller than icon size for padding)
        font = painter.font()
        font.setPixelSize(int(size * 0.7))
        painter.setFont(font)

        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        painter.end()

        icon = QIcon(pixmap)
        self._icon_cache[cache_key] = icon
        return icon

    def get_icon(
        self,
        name: str,
        size: Optional[int] = None,
        color: Optional[QColor] = None
    ) -> QIcon:
        """
        Get icon by name

        Args:
            name: Icon name from ICONS dict
            size: Icon size (uses default if None)
            color: Icon color (uses default if None)

        Returns:
            QIcon instance
        """
        if name in self.ICONS:
            return self.create_text_icon(self.ICONS[name], size, color)

        # Fallback to standard Qt icons
        standard_icon_map = {
            'folder-open': QStyle.StandardPixmap.SP_DirOpenIcon,
            'file': QStyle.StandardPixmap.SP_FileIcon,
            'save': QStyle.StandardPixmap.SP_DialogSaveButton,
            'help': QStyle.StandardPixmap.SP_DialogHelpButton,
            'close': QStyle.StandardPixmap.SP_DialogCloseButton,
            'error': QStyle.StandardPixmap.SP_MessageBoxCritical,
            'info': QStyle.StandardPixmap.SP_MessageBoxInformation,
            'warning': QStyle.StandardPixmap.SP_MessageBoxWarning,
        }

        if name in standard_icon_map:
            return self.get_standard_icon(standard_icon_map[name])

        return QIcon()

    def get_button_icon(
        self,
        name: str,
        color: Optional[QColor] = None
    ) -> QIcon:
        """
        Get icon sized appropriately for buttons

        Args:
            name: Icon name
            color: Icon color

        Returns:
            QIcon instance sized for buttons (20px)
        """
        return self.get_icon(name, size=20, color=color)

    def get_toolbar_icon(
        self,
        name: str,
        color: Optional[QColor] = None
    ) -> QIcon:
        """
        Get icon sized appropriately for toolbars

        Args:
            name: Icon name
            color: Icon color

        Returns:
            QIcon instance sized for toolbars (24px)
        """
        return self.get_icon(name, size=24, color=color)

    def get_menu_icon(
        self,
        name: str,
        color: Optional[QColor] = None
    ) -> QIcon:
        """
        Get icon sized appropriately for menus

        Args:
            name: Icon name
            color: Icon color

        Returns:
            QIcon instance sized for menus (16px)
        """
        return self.get_icon(name, size=16, color=color)

    @staticmethod
    def get_colored_icon(base_icon: QIcon, color: QColor, size: QSize) -> QIcon:
        """
        Create a colored version of an existing icon

        Args:
            base_icon: Base icon to colorize
            color: Color to apply
            size: Icon size

        Returns:
            Colorized QIcon
        """
        pixmap = base_icon.pixmap(size)
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        return QIcon(pixmap)

    def clear_cache(self):
        """Clear the icon cache"""
        self._icon_cache.clear()


# Global icon manager instance
_icon_manager = None


def get_icon_manager() -> IconManager:
    """
    Get global icon manager instance

    Returns:
        IconManager instance
    """
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager()
    return _icon_manager
