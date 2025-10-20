"""
Animation helper for smooth UI transitions and effects
Provides reusable animation utilities for Qt widgets
"""
from PySide6.QtCore import (
    QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
    QSequentialAnimationGroup, QPoint, QSize, Property, QObject
)
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtGui import QColor
from typing import Optional, Callable


class AnimationHelper:
    """Helper class for creating smooth UI animations"""

    # Standard animation durations (in milliseconds)
    DURATION_FAST = 150
    DURATION_NORMAL = 300
    DURATION_SLOW = 500

    # Standard easing curves
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic
    EASE_BOUNCE = QEasingCurve.Type.OutBounce

    @staticmethod
    def fade_in(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        on_finished: Optional[Callable] = None
    ) -> QPropertyAnimation:
        """
        Fade in a widget from transparent to opaque

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        # Ensure widget has an opacity effect
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        effect = widget.graphicsEffect()
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        return animation

    @staticmethod
    def fade_out(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        on_finished: Optional[Callable] = None
    ) -> QPropertyAnimation:
        """
        Fade out a widget from opaque to transparent

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            on_finished: Optional callback when animation completes

        Returns:
            QPropertyAnimation instance
        """
        # Ensure widget has an opacity effect
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        effect = widget.graphicsEffect()
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.setEasingCurve(AnimationHelper.EASE_IN)

        if on_finished:
            animation.finished.connect(on_finished)

        animation.start()
        return animation

    @staticmethod
    def slide_in_from_top(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        distance: Optional[int] = None
    ) -> QPropertyAnimation:
        """
        Slide widget in from top

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide (uses widget height if None)

        Returns:
            QPropertyAnimation instance
        """
        if distance is None:
            distance = widget.height()

        start_pos = QPoint(widget.x(), widget.y() - distance)
        end_pos = widget.pos()

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        widget.move(start_pos)
        animation.start()
        return animation

    @staticmethod
    def slide_in_from_bottom(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        distance: Optional[int] = None
    ) -> QPropertyAnimation:
        """
        Slide widget in from bottom

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide (uses widget height if None)

        Returns:
            QPropertyAnimation instance
        """
        if distance is None:
            distance = widget.height()

        start_pos = QPoint(widget.x(), widget.y() + distance)
        end_pos = widget.pos()

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        widget.move(start_pos)
        animation.start()
        return animation

    @staticmethod
    def slide_in_from_left(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        distance: Optional[int] = None
    ) -> QPropertyAnimation:
        """
        Slide widget in from left

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            distance: Distance to slide (uses widget width if None)

        Returns:
            QPropertyAnimation instance
        """
        if distance is None:
            distance = widget.width()

        start_pos = QPoint(widget.x() - distance, widget.y())
        end_pos = widget.pos()

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        widget.move(start_pos)
        animation.start()
        return animation

    @staticmethod
    def grow_from_center(
        widget: QWidget,
        duration: int = DURATION_NORMAL
    ) -> QPropertyAnimation:
        """
        Grow widget from center point

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds

        Returns:
            QPropertyAnimation instance
        """
        target_size = widget.size()
        start_size = QSize(0, 0)

        animation = QPropertyAnimation(widget, b"size")
        animation.setDuration(duration)
        animation.setStartValue(start_size)
        animation.setEndValue(target_size)
        animation.setEasingCurve(AnimationHelper.EASE_OUT)

        animation.start()
        return animation

    @staticmethod
    def fade_and_slide(
        widget: QWidget,
        duration: int = DURATION_NORMAL,
        slide_direction: str = "bottom"
    ) -> QParallelAnimationGroup:
        """
        Combine fade in with slide animation

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            slide_direction: Direction to slide from ("top", "bottom", "left", "right")

        Returns:
            QParallelAnimationGroup containing both animations
        """
        group = QParallelAnimationGroup()

        # Fade animation
        if not widget.graphicsEffect():
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        effect = widget.graphicsEffect()
        fade_anim = QPropertyAnimation(effect, b"opacity")
        fade_anim.setDuration(duration)
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setEasingCurve(AnimationHelper.EASE_OUT)

        # Slide animation
        distance = 30  # Subtle slide distance
        current_pos = widget.pos()

        if slide_direction == "top":
            start_pos = QPoint(current_pos.x(), current_pos.y() - distance)
        elif slide_direction == "bottom":
            start_pos = QPoint(current_pos.x(), current_pos.y() + distance)
        elif slide_direction == "left":
            start_pos = QPoint(current_pos.x() - distance, current_pos.y())
        else:  # right
            start_pos = QPoint(current_pos.x() + distance, current_pos.y())

        slide_anim = QPropertyAnimation(widget, b"pos")
        slide_anim.setDuration(duration)
        slide_anim.setStartValue(start_pos)
        slide_anim.setEndValue(current_pos)
        slide_anim.setEasingCurve(AnimationHelper.EASE_OUT)

        widget.move(start_pos)

        group.addAnimation(fade_anim)
        group.addAnimation(slide_anim)
        group.start()

        return group

    @staticmethod
    def pulse(
        widget: QWidget,
        duration: int = DURATION_FAST,
        scale_factor: float = 1.1
    ) -> QSequentialAnimationGroup:
        """
        Create a pulse effect (grow and shrink)

        Args:
            widget: Widget to animate
            duration: Duration for each phase of the pulse
            scale_factor: How much to scale the widget

        Returns:
            QSequentialAnimationGroup containing pulse animation
        """
        original_size = widget.size()
        scaled_size = QSize(
            int(original_size.width() * scale_factor),
            int(original_size.height() * scale_factor)
        )

        # Grow animation
        grow_anim = QPropertyAnimation(widget, b"size")
        grow_anim.setDuration(duration)
        grow_anim.setStartValue(original_size)
        grow_anim.setEndValue(scaled_size)
        grow_anim.setEasingCurve(AnimationHelper.EASE_OUT)

        # Shrink animation
        shrink_anim = QPropertyAnimation(widget, b"size")
        shrink_anim.setDuration(duration)
        shrink_anim.setStartValue(scaled_size)
        shrink_anim.setEndValue(original_size)
        shrink_anim.setEasingCurve(AnimationHelper.EASE_IN)

        group = QSequentialAnimationGroup()
        group.addAnimation(grow_anim)
        group.addAnimation(shrink_anim)
        group.start()

        return group

    @staticmethod
    def smooth_show(
        widget: QWidget,
        animation_type: str = "fade",
        duration: int = DURATION_NORMAL
    ):
        """
        Show widget with animation

        Args:
            widget: Widget to show
            animation_type: Type of animation ("fade", "slide_bottom", "slide_top", "fade_slide")
            duration: Animation duration in milliseconds
        """
        widget.show()

        if animation_type == "fade":
            AnimationHelper.fade_in(widget, duration)
        elif animation_type == "slide_bottom":
            AnimationHelper.slide_in_from_bottom(widget, duration)
        elif animation_type == "slide_top":
            AnimationHelper.slide_in_from_top(widget, duration)
        elif animation_type == "fade_slide":
            AnimationHelper.fade_and_slide(widget, duration)

    @staticmethod
    def smooth_hide(
        widget: QWidget,
        animation_type: str = "fade",
        duration: int = DURATION_FAST
    ):
        """
        Hide widget with animation

        Args:
            widget: Widget to hide
            animation_type: Type of animation ("fade")
            duration: Animation duration in milliseconds
        """
        if animation_type == "fade":
            AnimationHelper.fade_out(widget, duration, lambda: widget.hide())
        else:
            widget.hide()
