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
        """Check if field is str, Path, or has textarea/markdown input_type."""
        if field_info.annotation in (str, Path):
            return True

        # Check for textarea/markdown variant in json_schema_extra
        extra = field_info.json_schema_extra
        if extra and isinstance(extra, dict):
            if extra.get("input_type") in ("textarea", "markdown"):
                return True

        return False

    def create_widget(self, context: InputContext) -> ui.element:
        """Create string input, textarea, or markdown widget."""
        current_value = context.current_value or ""

        # Check for special input types
        extra = context.field_info.json_schema_extra
        input_type = None
        if extra and isinstance(extra, dict):
            input_type = extra.get("input_type")

        # Check if field is Optional
        is_optional = self._is_optional(context.field_info)

        # Create widget based on input type
        if input_type == "markdown":
            # For markdown, use a textarea (markdown rendering handled in display)
            widget = ui.textarea(
                value=str(current_value),
                on_change=lambda e: context.validation_callback(e.value),
            ).classes('w-full').props('rows=10')

        elif input_type == "textarea":
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

        origin = typing.get_origin(field_info.annotation)
        if origin is typing.Union:
            args = typing.get_args(field_info.annotation)
            return len(args) > 1 and type(None) in args
        return False
