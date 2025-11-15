"""Selection input handlers for Literal, select, and multiselect types."""

import logging
import typing
from typing import Literal
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class SelectionHandler:
    """Handler for Literal types and select/multiselect input types."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is Literal or has select/multiselect input_type."""
        # Check for Literal type
        if typing.get_origin(field_info.annotation) is Literal:
            return True

        # Check for select/multiselect in json_schema_extra
        extra = field_info.json_schema_extra
        if extra and isinstance(extra, dict):
            if extra.get("input_type") in ("select", "multiselect"):
                return True

        return False

    def create_widget(self, context: InputContext) -> ui.element:
        """Create select widget with options."""
        current_value = context.current_value

        # Get input type from extra
        extra = context.field_info.json_schema_extra
        is_multiselect = False
        selections_dict = None

        if extra and isinstance(extra, dict):
            is_multiselect = extra.get("input_type") == "multiselect"
            selections_dict = extra.get("selections")

        # Build options dict
        options = self._get_options(context.field_info, selections_dict, current_value)

        # Ensure current value is in options
        if not is_multiselect and current_value not in options and len(options) > 0:
            current_value = next(iter(options.keys()))

        # Handle dict type for multiselect
        if typing.get_origin(context.field_info.annotation) is dict:
            display_value = list(current_value.keys()) if current_value else []

            def list_to_dict_val(x: list):
                return context.validation_callback(dict.fromkeys(x))

            validation_fn = list_to_dict_val
        else:
            display_value = current_value
            validation_fn = lambda e: context.validation_callback(e.value)

        # Create select widget
        widget = ui.select(
            options=options,
            value=display_value,
            on_change=validation_fn,
            multiple=is_multiselect,
        )

        if is_multiselect:
            widget.props("use-chips")

        return widget

    def _get_options(
        self, field_info: FieldInfo, selections_dict: dict | None, current_value
    ) -> dict:
        """Extract options from Literal type or selections dict."""
        # Check for Literal type
        if typing.get_origin(field_info.annotation) is Literal:
            literal_args = typing.get_args(field_info.annotation)
            return {str(arg): str(arg) for arg in literal_args}

        # Use provided selections dict
        if selections_dict:
            return selections_dict

        # Fallback: create dict from current value if available
        if current_value:
            if isinstance(current_value, dict):
                return {k: str(v) for k, v in current_value.items()}
            else:
                return {str(current_value): str(current_value)}

        return {}
