"""Nested BaseModel input handlers."""

import logging
import typing
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class NestedHandler:
    """Handler for BaseModel, Union[BaseModel, ...], and list[BaseModel] types."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is a BaseModel or list of BaseModels."""
        annotation = field_info.annotation

        # Direct BaseModel type
        if annotation == BaseModel:
            return True

        # Subclass of BaseModel
        if isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return True

        # List of BaseModels
        if typing.get_origin(annotation) is list:
            args = typing.get_args(annotation)
            if args and isinstance(args[0], type) and issubclass(args[0], BaseModel):
                return True

        # Union of BaseModels (basemodelswitcher)
        origin = typing.get_origin(annotation)
        if origin is typing.Union:
            args = typing.get_args(annotation)
            if args:
                # Check if all non-None args are BaseModel
                non_none_args = [arg for arg in args if arg is not type(None)]
                if non_none_args and all(
                    isinstance(arg, type) and issubclass(arg, BaseModel)
                    for arg in non_none_args
                ):
                    return True

        return False

    def create_widget(self, context: InputContext) -> ui.element:
        """Create edit button or list for nested BaseModel(s)."""
        current_value = context.current_value
        annotation = context.field_info.annotation

        # List of BaseModels
        if typing.get_origin(annotation) is list:
            return self._create_list_widget(context, current_value or [])

        # Single BaseModel
        return self._create_edit_button(context, current_value)

    def _create_edit_button(self, context: InputContext, current_value) -> ui.element:
        """Create edit button for single BaseModel."""
        if not current_value:
            # Create default instance
            model_type = context.field_info.annotation
            if isinstance(model_type, type) and issubclass(model_type, BaseModel):
                current_value = model_type()

        with ui.row().classes("items-center justify-shrink w-full flex-nowrap"):
            label_text = str(current_value.model_dump(context=dict(gui=True))) if hasattr(current_value, 'model_dump') else str(current_value)
            ui.label(label_text).classes("text-slate-500")

            # For now, create a placeholder button
            # In full implementation, this would call handle_edit_subitem
            button = ui.button(icon="edit").props("flat round").classes("text-lightprimary dark:primary")
            button.tooltip("Edit nested object (handler needs NiceCRUDCard integration)")

        return button

    def _create_list_widget(self, context: InputContext, items: list) -> ui.element:
        """Create list widget for list of BaseModels."""
        with ui.list().classes("w-full").props("bordered separator") as list_widget:
            for i, subitem in enumerate(items):
                with ui.item():
                    with ui.item_section():
                        label_text = str(subitem.model_dump(context=dict(gui=True))) if hasattr(subitem, 'model_dump') else str(subitem)
                        ui.label(label_text)
                    with ui.item_section().props("side"):
                        button = ui.button(icon="edit").props("flat round")
                        button.tooltip("Edit item (needs NiceCRUDCard integration)")
                    with ui.item_section().props("side"):
                        button = ui.button(icon="delete").props("flat round")
                        button.tooltip("Delete item (needs NiceCRUDCard integration)")

            with ui.item():
                button = ui.button(icon="add").props("flat round")
                button.tooltip("Add item (needs NiceCRUDCard integration)")

        return list_widget
