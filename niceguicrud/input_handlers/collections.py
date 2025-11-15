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
        """Create list widget with add/remove buttons for each item."""
        current_value = context.current_value or []

        # Get the element type
        args = typing.get_args(context.field_info.annotation)
        element_type = args[0] if args else str

        # Create a mutable container for the list
        items = list(current_value)

        def update_list():
            """Update the list and trigger validation."""
            context.validation_callback(items)

        def add_item():
            """Add a new item to the list."""
            # Default values by type
            if element_type is int:
                default_value = 0
            elif element_type is float:
                default_value = 0.0
            else:
                default_value = ""

            items.append(default_value)
            update_list()
            list_container.clear()
            with list_container:
                render_items()

        def remove_item(index: int):
            """Remove an item from the list."""
            items.pop(index)
            update_list()
            list_container.clear()
            with list_container:
                render_items()

        def update_item(index: int, value: str):
            """Update an item in the list."""
            try:
                if element_type is int:
                    items[index] = int(value) if value else 0
                elif element_type is float:
                    items[index] = float(value) if value else 0.0
                else:
                    items[index] = value
                update_list()
            except (ValueError, TypeError) as e:
                logger.warning(f"Failed to parse value: {value}, error: {e}")

        def render_items():
            """Render the list of items."""
            for i, item in enumerate(items):
                with ui.item():
                    with ui.item_section():
                        ui.input(
                            value=str(item),
                            on_change=lambda e, idx=i: update_item(idx, e.value),
                            placeholder=f"{element_type.__name__} value"
                        ).classes("flex-grow")
                    with ui.item_section().props("side"):
                        ui.button(
                            icon="delete",
                            on_click=lambda idx=i: remove_item(idx)
                        ).props("flat round dense").classes("text-red-500")

            # Add button
            with ui.item():
                ui.button(
                    icon="add",
                    on_click=add_item
                ).props("flat round").classes("text-primary")

        # Create the list container
        with ui.list().classes("w-full").props("bordered separator") as list_container:
            render_items()

        return list_container
