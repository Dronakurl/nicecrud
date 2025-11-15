"""Integration tests for handler registry system.

Tests verify handler registration, priority ordering, cache behavior, and public API.
"""

import pytest
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from niceguicrud.input_handlers import (
    get_registry,
    register_custom_handler,
    InputHandlerProtocol,
    InputContext,
    NoHandlerFoundError,
)
from niceguicrud.input_handlers.base import FallbackHandler
from niceguicrud.input_handlers.string import StringHandler
from niceguicrud.input_handlers.numeric import NumericHandler


class DummyModel(BaseModel):
    test_field: str = ""


class CustomHandler:
    """Custom handler for testing registration."""

    priority: int = 200

    def can_handle(self, field_info: FieldInfo) -> bool:
        # Custom logic: only handles fields named "custom"
        return hasattr(field_info, 'annotation') and field_info.annotation == str

    def create_widget(self, context: InputContext):
        from nicegui import ui
        return ui.input(value="custom_handler", label="Custom")


class TestHandlerRegistry:
    """Test handler registry core functionality."""

    def test_registry_singleton(self):
        """Verify get_registry returns singleton instance."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2

    def test_registry_has_built_in_handlers(self):
        """Verify built-in handlers are registered at module load."""
        registry = get_registry()
        assert len(registry._handlers) > 0

        # Should have at least: String, Numeric, Boolean, Temporal, Selection, Nested, Collection, Fallback
        assert len(registry._handlers) >= 8

    def test_priority_ordering(self):
        """Verify handlers are ordered by priority (high to low)."""
        registry = get_registry()

        # Check that priorities are in descending order
        priorities = [h.priority for h in registry._handlers]
        assert priorities == sorted(priorities, reverse=True)

        # Fallback should be last (priority -1000)
        assert registry._handlers[-1].priority == -1000
        assert isinstance(registry._handlers[-1], FallbackHandler)

    def test_handler_lookup_by_type(self):
        """Verify registry finds correct handler for given type."""
        registry = get_registry()

        # String type should get StringHandler
        str_field = FieldInfo(annotation=str, default="")
        handler = registry.get_handler(str_field)
        assert isinstance(handler, StringHandler)

        # Int type should get NumericHandler
        int_field = FieldInfo(annotation=int, default=0)
        handler = registry.get_handler(int_field)
        assert isinstance(handler, NumericHandler)

    def test_cache_behavior(self):
        """Verify cache stores and returns handlers."""
        registry = get_registry()
        registry.clear_cache()

        # First lookup - not cached
        str_field = FieldInfo(annotation=str, default="")
        handler1 = registry.get_handler(str_field)

        # Second lookup - should be cached
        handler2 = registry.get_handler(str_field)
        assert handler1 is handler2

        # Cache should have entry for str type
        assert str in registry._cache

    def test_cache_cleared_after_registration(self):
        """Verify cache is cleared when new handler is registered."""
        registry = get_registry()
        registry.clear_cache()

        # Populate cache
        str_field = FieldInfo(annotation=str, default="")
        registry.get_handler(str_field)
        assert len(registry._cache) > 0

        # Register new handler - cache should clear
        custom = CustomHandler()
        registry.register(custom, priority=150)
        assert len(registry._cache) == 0

        # Cleanup
        registry.unregister(CustomHandler)

    def test_fallback_handler_always_matches(self):
        """Verify fallback handler catches unknown types."""
        registry = get_registry()

        # Create a custom type that no handler recognizes
        class UnknownType:
            pass

        field_info = FieldInfo(annotation=UnknownType, default=None)
        handler = registry.get_handler(field_info)

        # Should get FallbackHandler
        assert isinstance(handler, FallbackHandler)


class TestCustomHandlerRegistration:
    """Test custom handler registration via public API."""

    def test_register_custom_handler(self):
        """Verify custom handler can be registered and used."""
        registry = get_registry()
        initial_count = len(registry._handlers)

        # Register custom handler
        custom = CustomHandler()
        register_custom_handler(custom, priority=200)

        # Verify it's registered
        assert len(registry._handlers) == initial_count + 1

        # Cleanup
        registry.unregister(CustomHandler)

    def test_custom_handler_priority(self):
        """Verify custom handler with high priority is checked first."""
        registry = get_registry()

        # Register with priority higher than built-in handlers (100)
        custom = CustomHandler()
        register_custom_handler(custom, priority=200)

        # Find position of custom handler
        custom_index = next(
            i for i, h in enumerate(registry._handlers)
            if isinstance(h, CustomHandler)
        )

        # Find position of built-in StringHandler
        string_index = next(
            i for i, h in enumerate(registry._handlers)
            if isinstance(h, StringHandler)
        )

        # Custom should come before built-in
        assert custom_index < string_index

        # Cleanup
        registry.unregister(CustomHandler)

    def test_unregister_handler(self):
        """Verify handler can be unregistered."""
        registry = get_registry()

        # Register custom handler
        custom = CustomHandler()
        register_custom_handler(custom, priority=150)

        # Verify it exists
        has_custom = any(isinstance(h, CustomHandler) for h in registry._handlers)
        assert has_custom is True

        # Unregister
        removed = registry.unregister(CustomHandler)
        assert removed is True

        # Verify it's gone
        has_custom = any(isinstance(h, CustomHandler) for h in registry._handlers)
        assert has_custom is False

    def test_invalid_handler_raises_error(self):
        """Verify invalid handler raises TypeError."""
        class BadHandler:
            # Missing can_handle and create_widget methods
            priority = 100

        with pytest.raises(TypeError, match="must implement InputHandlerProtocol"):
            register_custom_handler(BadHandler())

    def test_negative_priority_raises_error(self):
        """Verify negative priority raises ValueError."""
        custom = CustomHandler()

        with pytest.raises(ValueError, match="Priority must be non-negative"):
            register_custom_handler(custom, priority=-5)


class TestHandlerIntegration:
    """Test end-to-end handler integration."""

    def test_handler_chain_execution(self):
        """Verify handlers are checked in priority order until match."""
        registry = get_registry()
        registry.clear_cache()

        # String field should match StringHandler (priority 100)
        # and not reach FallbackHandler (priority -1000)
        str_field = FieldInfo(annotation=str, default="test")
        handler = registry.get_handler(str_field)

        assert isinstance(handler, StringHandler)
        assert not isinstance(handler, FallbackHandler)

    def test_custom_handler_overrides_builtin(self):
        """Verify custom handler with higher priority wins."""
        registry = get_registry()

        # Register custom handler that handles str with priority 200
        custom = CustomHandler()
        register_custom_handler(custom, priority=200)

        # String field should now match CustomHandler instead of StringHandler
        str_field = FieldInfo(annotation=str, default="test")
        registry.clear_cache()  # Clear cache to force re-lookup
        handler = registry.get_handler(str_field)

        assert isinstance(handler, CustomHandler)

        # Cleanup
        registry.unregister(CustomHandler)
