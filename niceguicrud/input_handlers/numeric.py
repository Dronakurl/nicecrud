"""Numeric input handlers for int and float types."""

import logging
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class NumericHandler:
    """Handler for int and float types with number/slider variants."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is int or float."""
        return field_info.annotation in (int, float)

    def create_widget(self, context: InputContext) -> ui.element:
        """Create number input or slider widget."""
        current_value = context.current_value

        # Extract min/max constraints
        min_val, max_val = self._get_min_max(context.field_info)

        # Check for slider variant
        extra = context.field_info.json_schema_extra
        is_slider = False
        step = None
        if extra and isinstance(extra, dict):
            is_slider = extra.get("input_type") == "slider"
            step = extra.get("step")

        # Check if field is Optional
        is_optional = self._is_optional(context.field_info)

        # Create widget
        if is_slider and min_val is not None and max_val is not None:
            widget = ui.slider(
                min=min_val,
                max=max_val,
                value=current_value or min_val,
                step=step,
                on_change=lambda e: context.validation_callback(e.value),
            )
        else:
            widget = ui.number(
                value=current_value,
                on_change=lambda e: context.validation_callback(e.value),
                min=min_val,
                max=max_val,
                step=step,
            )

            # Add clearable prop for optional fields
            if is_optional:
                widget.props("clearable")

        return widget

    def _get_min_max(self, field_info: FieldInfo) -> tuple[float | None, float | None]:
        """Extract min/max from field metadata."""
        min_val = None
        max_val = None

        # Check field_info.metadata for annotated_types constraints
        if hasattr(field_info, "metadata") and field_info.metadata:
            for constraint in field_info.metadata:
                if hasattr(constraint, "gt"):
                    min_val = constraint.gt
                elif hasattr(constraint, "ge"):
                    min_val = constraint.ge
                elif hasattr(constraint, "lt"):
                    max_val = constraint.lt
                elif hasattr(constraint, "le"):
                    max_val = constraint.le

        return min_val, max_val

    def _is_optional(self, field_info: FieldInfo) -> bool:
        """Check if field is Optional (Union with None)."""
        import typing

        if typing.get_origin(field_info.annotation) in (typing.Union, typing.get_args(typing.Union)[0].__class__):
            args = typing.get_args(field_info.annotation)
            return len(args) > 1 and type(None) in args
        return False
