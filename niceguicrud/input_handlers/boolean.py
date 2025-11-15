"""Boolean input handler."""

import logging
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class BooleanHandler:
    """Handler for boolean type with ui.switch."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is bool."""
        return field_info.annotation is bool

    def create_widget(self, context: InputContext) -> ui.element:
        """Create switch widget for boolean field."""
        current_value = context.current_value or False

        widget = ui.switch(
            value=current_value,
            on_change=lambda e: context.validation_callback(e.value),
        )

        return widget
