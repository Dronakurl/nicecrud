"""Base classes and protocols for the modular input handler system."""

import logging
from dataclasses import dataclass
from typing import Protocol, Any, Callable
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from nicegui import ui


logger = logging.getLogger(__name__)


class InputHandlerProtocol(Protocol):
    """Protocol for input handlers that generate NiceGUI widgets for pydantic fields.

    Handlers must implement two methods:
    - can_handle: Determines if this handler can process a given field
    - create_widget: Generates the appropriate NiceGUI widget

    Handlers are checked in priority order (highest first) by the registry.
    """

    priority: int
    """Handler priority for resolution order. Higher values checked first.

    Built-in handlers use priority 100.
    Custom handlers should use priority > 100 to override built-ins.
    Fallback handler uses priority -1000 (always checked last).
    """

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if this handler can process the given pydantic field.

        Args:
            field_info: Pydantic FieldInfo containing type, constraints, metadata

        Returns:
            True if this handler should be used for this field type

        Requirements:
            - MUST be a pure function (no side effects)
            - MUST NOT modify field_info
            - MUST return deterministically for same input
        """
        ...

    def create_widget(self, context: "InputContext") -> ui.element | None:
        """Generate NiceGUI widget for the field.

        Args:
            context: InputContext containing all data needed for widget creation

        Returns:
            NiceGUI UI element (ui.input, ui.select, ui.switch, etc.) or None
            Returns None if widget creation fails (registry will try next handler)

        Requirements:
            - MUST use context.validation_callback for on_change/validation events
            - MUST respect context.config settings (CSS classes, readonly, etc.)
            - MUST handle Optional types appropriately (add clearable prop)
            - SHOULD extract constraints from context.field_info.metadata
            - SHOULD add tooltip if context.field_info.description exists
        """
        ...


@dataclass(frozen=True)
class InputContext:
    """Immutable context passed to handlers for widget creation.

    Contains all information needed to generate appropriate input widget.
    """

    field_name: str
    """Name of the pydantic field (e.g., "age", "email")"""

    field_info: FieldInfo
    """Pydantic field metadata containing type, constraints, description, etc."""

    current_value: Any
    """Current value of the field on the model instance"""

    validation_callback: Callable[[Any], None]
    """Callback to invoke when input value changes. Handles validation and updates model."""

    config: Any  # NiceCRUDConfig type
    """UI configuration (CSS classes, labels, readonly settings, etc.)"""

    item: BaseModel
    """The model instance being edited. Used for nested object handlers."""


class FallbackHandler:
    """Catch-all handler when no specific handler matches.

    This handler always returns True for can_handle, ensuring there's always
    a handler available. It logs a warning and renders a basic text input.
    """

    priority: int = -1000  # Lowest priority, checked last

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Always returns True - this is the fallback handler."""
        return True

    def create_widget(self, context: InputContext) -> ui.element:
        """Return basic text input with warning logged.

        Args:
            context: InputContext with field information

        Returns:
            Basic ui.input with field value converted to string
        """
        logger.warning(
            f"No specific handler found for field '{context.field_name}' "
            f"of type {context.field_info.annotation}. "
            f"Consider registering a custom handler for this type. "
            f"Falling back to text input."
        )

        # Convert current value to string for fallback text input
        value_str = str(context.current_value) if context.current_value is not None else ""

        return ui.input(
            label=context.field_name,
            value=value_str,
            on_change=lambda e: context.validation_callback(e.value),
        )


class NoHandlerFoundError(Exception):
    """Raised when no handler can process a field.

    This should never happen in practice due to FallbackHandler,
    but exists for type safety and testing.
    """

    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info
        super().__init__(f"No handler found for field type: {field_info.annotation}")
