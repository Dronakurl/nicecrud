"""Modular input handler system for NiceCRUD.

This module provides a flexible, extensible system for generating NiceGUI input widgets
based on pydantic field types. The system uses a priority-based registry to map types
to their corresponding handlers.

Public API:
    - InputHandlerProtocol: Protocol that all handlers must implement
    - InputContext: Immutable context passed to handlers
    - register_custom_handler: Register a custom handler for domain-specific types
    - get_registry: Get the global handler registry instance
"""

import logging
from typing import TYPE_CHECKING
from pydantic.fields import FieldInfo

from .base import InputHandlerProtocol, InputContext, FallbackHandler, NoHandlerFoundError


if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)


class HandlerRegistry:
    """Central registry for input handlers.

    Maintains priority-ordered list of handlers and caches type lookups for performance.
    """

    def __init__(self):
        """Initialize registry with empty handler list and cache."""
        self._handlers: list[InputHandlerProtocol] = []
        self._cache: dict[type, InputHandlerProtocol] = {}

    def register(
        self, handler: InputHandlerProtocol, priority: int | None = None
    ) -> None:
        """Register a handler in the registry.

        Args:
            handler: Handler to register
            priority: Override handler.priority if provided

        Behavior:
            - Handler inserted in priority-sorted order (high to low)
            - Duplicate handlers allowed (same type, different instances)
            - Cache cleared after registration
        """
        if priority is not None:
            handler.priority = priority

        # Insert in priority-sorted order (highest first)
        insert_index = 0
        for i, existing_handler in enumerate(self._handlers):
            if handler.priority > existing_handler.priority:
                insert_index = i
                break
            insert_index = i + 1

        self._handlers.insert(insert_index, handler)
        self.clear_cache()

        logger.debug(
            f"Registered handler {handler.__class__.__name__} with priority {handler.priority}"
        )

    def get_handler(self, field_info: FieldInfo) -> InputHandlerProtocol:
        """Find handler for the given field.

        Args:
            field_info: Pydantic field metadata

        Returns:
            First handler where can_handle returns True

        Raises:
            NoHandlerFoundError: If no handler matches (should never happen due to FallbackHandler)

        Behavior:
            - Check cache first (keyed by field_info.annotation)
            - If cache miss, iterate handlers by priority (high to low)
            - First handler where can_handle returns True wins
            - Result cached for future lookups
        """
        # Check cache first
        cache_key = field_info.annotation
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Iterate handlers by priority
        for handler in self._handlers:
            if handler.can_handle(field_info):
                self._cache[cache_key] = handler
                logger.debug(
                    f"Selected handler {handler.__class__.__name__} for type {field_info.annotation}"
                )
                return handler

        # This should never happen if FallbackHandler is registered
        raise NoHandlerFoundError(field_info)

    def clear_cache(self) -> None:
        """Clear the type � handler lookup cache.

        Useful for:
        - Testing: Reset state between tests
        - Dynamic registration: Force re-evaluation after adding handlers
        """
        self._cache.clear()
        logger.debug("Handler registry cache cleared")

    def unregister(self, handler_type: type) -> bool:
        """Remove all handlers of the given type.

        Args:
            handler_type: Class of handler to remove

        Returns:
            True if any handlers were removed, False otherwise
        """
        initial_count = len(self._handlers)
        self._handlers = [
            h for h in self._handlers if not isinstance(h, handler_type)
        ]
        removed = initial_count - len(self._handlers)

        if removed > 0:
            self.clear_cache()
            logger.debug(f"Removed {removed} handler(s) of type {handler_type.__name__}")

        return removed > 0


# Global singleton registry
_registry = HandlerRegistry()


def get_registry() -> HandlerRegistry:
    """Get the global handler registry instance.

    Returns singleton registry used by all NiceCRUD instances.
    Useful for testing, introspection, or advanced customization.

    Returns:
        HandlerRegistry: The global registry
    """
    return _registry


def register_custom_handler(
    handler: InputHandlerProtocol, priority: int = 150
) -> None:
    """Register a custom input handler for domain-specific types.

    Custom handlers are checked before built-in handlers if priority > 100.

    Args:
        handler: Handler implementing InputHandlerProtocol
        priority: Resolution priority (default 150, higher = checked first)

    Raises:
        TypeError: If handler doesn't implement InputHandlerProtocol
        ValueError: If priority < 0

    Example:
        >>> class ColorHandler:
        ...     priority = 150
        ...     def can_handle(self, field_info): return field_info.annotation == Color
        ...     def create_widget(self, ctx): return ui.color_input(value=ctx.current_value)
        ...
        >>> register_custom_handler(ColorHandler())
    """
    if priority < 0:
        raise ValueError(f"Priority must be non-negative, got {priority}")

    # Verify handler has required protocol methods
    if not hasattr(handler, "can_handle") or not hasattr(handler, "create_widget"):
        raise TypeError(
            f"Handler {handler.__class__.__name__} must implement InputHandlerProtocol "
            f"(can_handle and create_widget methods)"
        )

    _registry.register(handler, priority)


# Register all built-in handlers at module import time
from .string import StringHandler
from .numeric import NumericHandler
from .boolean import BooleanHandler
from .temporal import TemporalHandler
from .selection import SelectionHandler
from .nested import NestedHandler
from .collections import CollectionHandler

# Register handlers with priority 100 (built-in default)
_registry.register(StringHandler(), priority=100)
_registry.register(NumericHandler(), priority=100)
_registry.register(BooleanHandler(), priority=100)
_registry.register(TemporalHandler(), priority=100)
_registry.register(SelectionHandler(), priority=100)
_registry.register(NestedHandler(), priority=100)
_registry.register(CollectionHandler(), priority=100)

# Register fallback handler last (lowest priority)
# This ensures there's always a handler available
_registry.register(FallbackHandler(), priority=-1000)

logger.info(f"Registered {len(_registry._handlers)} input handlers")


# Public API exports
__all__ = [
    "InputHandlerProtocol",
    "InputContext",
    "register_custom_handler",
    "get_registry",
    "NoHandlerFoundError",
]
