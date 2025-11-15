"""Collection input handlers for list types."""

import logging
import typing
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class CollectionHandler:
    """Handler for list[str], list[int], list[float] with comma-separated input."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is list of primitives (str, int, float)."""
        annotation = field_info.annotation

        if typing.get_origin(annotation) is list:
            args = typing.get_args(annotation)
            if args and args[0] in (str, int, float):
                return True

        if typing.get_origin(annotation) is set:
            args = typing.get_args(annotation)
            if args and args[0] in (str, int, float):
                return True

        return False

    def create_widget(self, context: InputContext) -> ui.element:
        """Create input widget with comma-separated values."""
        current_value = context.current_value or []

        # Get the element type
        args = typing.get_args(context.field_info.annotation)
        element_type = args[0] if args else str

        # Convert list to comma-separated string
        if current_value:
            value_str = ", ".join(str(v) for v in current_value)
        else:
            value_str = ""

        def parse_and_validate(value_str: str):
            """Parse comma-separated string into list and validate."""
            if not value_str or not value_str.strip():
                context.validation_callback([])
                return

            try:
                # Split by comma and strip whitespace
                parts = [p.strip() for p in value_str.split(",") if p.strip()]

                # Convert to appropriate type
                if element_type is int:
                    parsed = [int(p) for p in parts]
                elif element_type is float:
                    parsed = [float(p) for p in parts]
                else:
                    parsed = parts

                context.validation_callback(parsed)
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse collection: {value_str}, error: {e}")
                # Keep the string value but don't validate
                pass

        widget = ui.input(
            value=value_str,
            on_change=lambda e: parse_and_validate(e.value),
            placeholder=f"Enter comma-separated {element_type.__name__} values",
        )

        widget.tooltip(f"Enter values separated by commas (e.g., value1, value2, value3)")

        return widget
