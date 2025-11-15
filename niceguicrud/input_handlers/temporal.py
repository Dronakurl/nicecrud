"""Temporal input handlers for date, time, and datetime types."""

import logging
from datetime import date, time, datetime
from pydantic.fields import FieldInfo
from nicegui import ui

from .base import InputContext


logger = logging.getLogger(__name__)


class TemporalHandler:
    """Handler for date, time, and datetime types with picker widgets."""

    priority: int = 100

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is date, time, or datetime."""
        return field_info.annotation in (date, time, datetime)

    def create_widget(self, context: InputContext) -> ui.element:
        """Create date/time/datetime picker widget."""
        current_value = context.current_value
        field_type = context.field_info.annotation

        # Format current value as string for input
        if current_value is not None:
            if field_type is date:
                value_str = current_value.isoformat()
            elif field_type is time:
                value_str = current_value.isoformat()
            elif field_type is datetime:
                value_str = current_value.isoformat()
            else:
                value_str = str(current_value)
        else:
            value_str = ""

        # Create input with appropriate picker
        if field_type is date:
            widget = ui.input(
                value=value_str,
                on_change=lambda e: self._handle_date_change(e.value, context),
            )
            with widget:
                with ui.menu() as menu:
                    ui.date(on_change=lambda e: (
                        widget.set_value(e.value),
                        menu.close()
                    ))
            widget.props('append-icon="event"')

        elif field_type is time:
            widget = ui.input(
                value=value_str,
                on_change=lambda e: self._handle_time_change(e.value, context),
            )
            with widget:
                with ui.menu() as menu:
                    ui.time(on_change=lambda e: (
                        widget.set_value(e.value),
                        menu.close()
                    ))
            widget.props('append-icon="schedule"')

        elif field_type is datetime:
            widget = ui.input(
                value=value_str,
                on_change=lambda e: self._handle_datetime_change(e.value, context),
            )
            with widget:
                with ui.menu() as menu:
                    with ui.column():
                        ui.date(on_change=lambda e: widget.set_value(e.value + "T00:00"))
                        ui.time(on_change=lambda e: (
                            widget.set_value(widget.value.split("T")[0] + "T" + e.value),
                            menu.close()
                        ))
            widget.props('append-icon="event"')

        else:
            widget = ui.input(value=value_str)

        return widget

    def _handle_date_change(self, value: str, context: InputContext):
        """Convert string to date and call validation callback."""
        try:
            if value:
                date_obj = date.fromisoformat(value)
                context.validation_callback(date_obj)
            else:
                context.validation_callback(None)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid date format: {value}, error: {e}")

    def _handle_time_change(self, value: str, context: InputContext):
        """Convert string to time and call validation callback."""
        try:
            if value:
                time_obj = time.fromisoformat(value)
                context.validation_callback(time_obj)
            else:
                context.validation_callback(None)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid time format: {value}, error: {e}")

    def _handle_datetime_change(self, value: str, context: InputContext):
        """Convert string to datetime and call validation callback."""
        try:
            if value:
                datetime_obj = datetime.fromisoformat(value)
                context.validation_callback(datetime_obj)
            else:
                context.validation_callback(None)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid datetime format: {value}, error: {e}")
