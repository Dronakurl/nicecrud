"""String and Path input handlers."""

import logging
from pathlib import Path
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class StringHandler:
    """Handler for string and Path types with textarea variant."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is str, Path, or has textarea input_type."""
        if field_info.annotation in (str, Path):
            return True

        # Check for textarea variant in json_schema_extra
        extra = field_info.json_schema_extra
        if extra and isinstance(extra, dict):
            if extra.get("input_type") == "textarea":
                return True

        return False

    def create_widget(self, context: InputContext) -> ui.element:
        """Create string input or textarea widget."""
        current_value = context.current_value or ""

        # Check for textarea variant
        extra = context.field_info.json_schema_extra
        is_textarea = False
        if extra and isinstance(extra, dict):
            is_textarea = extra.get("input_type") == "textarea"

        # Check if field is Optional
        is_optional = self._is_optional(context.field_info)

        # Create widget
        if is_textarea:
            widget = ui.textarea(
                value=str(current_value),
                on_change=lambda e: context.validation_callback(e.value),
            )
        else:
            placeholder = context.field_info.description or ""
            widget = ui.input(
                value=str(current_value),
                on_change=lambda e: context.validation_callback(e.value),
                placeholder=placeholder,
            )

        # Add clearable prop for optional fields
        if is_optional:
            widget.props("clearable")

        return widget

    def _is_optional(self, field_info: FieldInfo) -> bool:
        """Check if field is Optional (Union with None)."""
        import typing

        if typing.get_origin(field_info.annotation) in (typing.Union, typing.get_args(typing.Union)[0].__class__):
            args = typing.get_args(field_info.annotation)
            return len(args) > 1 and type(None) in args
        return False
