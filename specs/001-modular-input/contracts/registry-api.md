# Contract: Handler Registry API

**Feature**: 001-modular-input
**Version**: 1.0
**Type**: Public API

## Purpose

Defines the public API for the handler registry system, including handler registration, lookup, and custom handler extension points.

## Public API

### Module: `niceguicrud.input_handlers`

```python
from niceguicrud.input_handlers import (
    InputHandlerProtocol,
    InputContext,
    HandlerRegistry,
    register_custom_handler,
    get_registry,
)
```

---

## Core Functions

### `register_custom_handler`

```python
def register_custom_handler(
    handler: InputHandlerProtocol,
    priority: int = 150
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
```

**Requirements**:
- Handler must implement `InputHandlerProtocol` (duck-typed via Protocol)
- Priority must be non-negative integer
- Handler added to global registry immediately
- Lookup cache cleared to force re-evaluation

---

### `get_registry`

```python
def get_registry() -> HandlerRegistry:
    """Get the global handler registry instance.

    Returns singleton registry used by all NiceCRUD instances.
    Useful for testing, introspection, or advanced customization.

    Returns:
        HandlerRegistry: The global registry

    Example:
        >>> registry = get_registry()
        >>> print(f"Registered handlers: {len(registry._handlers)}")
        Registered handlers: 8
    """
```

**Use Cases**:
- Testing: Reset registry between tests
- Introspection: List all registered handlers
- Advanced: Unregister specific handlers

---

## HandlerRegistry Class

### Constructor

```python
class HandlerRegistry:
    """Central registry for input handlers.

    Maintains priority-ordered list of handlers and caches type lookups.
    """

    def __init__(self):
        """Initialize registry with built-in handlers.

        Built-in handlers registered with priority 100:
        - StringHandler
        - NumericHandler
        - BooleanHandler
        - TemporalHandler
        - SelectionHandler
        - NestedHandler
        - CollectionHandler
        - FallbackHandler (priority -1000)
        """
```

---

### `register` Method

```python
def register(
    self,
    handler: InputHandlerProtocol,
    priority: int | None = None
) -> None:
    """Register a handler in the registry.

    Args:
        handler: Handler to register
        priority: Override handler.priority if provided

    Behavior:
        - Handler inserted in priority-sorted order
        - Duplicate handlers allowed (same type, different instances)
        - Cache cleared after registration

    Example:
        >>> registry = get_registry()
        >>> registry.register(CustomHandler(), priority=200)
    """
```

---

### `get_handler` Method

```python
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

    Example:
        >>> handler = registry.get_handler(field_info)
        >>> widget = handler.create_widget(context)
    """
```

---

### `clear_cache` Method

```python
def clear_cache(self) -> None:
    """Clear the type → handler lookup cache.

    Useful for:
    - Testing: Reset state between tests
    - Dynamic registration: Force re-evaluation after adding handlers

    Example:
        >>> registry.clear_cache()
        >>> # Next get_handler call will re-evaluate all handlers
    """
```

---

### `unregister` Method

```python
def unregister(self, handler_type: type) -> bool:
    """Remove all handlers of the given type.

    Args:
        handler_type: Class of handler to remove

    Returns:
        True if any handlers were removed, False otherwise

    Example:
        >>> registry.unregister(StringHandler)
        True
        >>> # All StringHandler instances removed from registry
    """
```

---

## Exceptions

### `NoHandlerFoundError`

```python
class NoHandlerFoundError(Exception):
    """Raised when no handler can process a field.

    This should never happen in practice due to FallbackHandler,
    but exists for type safety and testing.
    """

    def __init__(self, field_info: FieldInfo):
        self.field_info = field_info
        super().__init__(
            f"No handler found for field type: {field_info.annotation}"
        )
```

---

## Usage Patterns

### Basic Custom Handler

```python
from niceguicrud.input_handlers import InputHandlerProtocol, InputContext, register_custom_handler
from pydantic.fields import FieldInfo
from nicegui import ui

class EmailHandler:
    """Custom handler for email fields with validation."""

    priority = 150

    def can_handle(self, field_info: FieldInfo) -> bool:
        # Check for custom marker in json_schema_extra
        extra = field_info.json_schema_extra or {}
        return extra.get("format") == "email"

    def create_widget(self, context: InputContext) -> ui.Element:
        return ui.input(
            value=context.current_value,
            validation=context.validation_callback,
            placeholder="user@example.com"
        ).props('type="email"')

# Register once at application startup
register_custom_handler(EmailHandler())

# Use in models
class User(BaseModel):
    name: str
    email: str = Field(json_schema_extra={"format": "email"})  # Uses EmailHandler
```

---

### Testing with Registry Reset

```python
import pytest
from niceguicrud.input_handlers import get_registry

@pytest.fixture
def clean_registry():
    """Reset registry to default state for each test."""
    registry = get_registry()
    # Save current handlers
    original_handlers = registry._handlers.copy()

    yield registry

    # Restore original handlers
    registry._handlers = original_handlers
    registry.clear_cache()

def test_custom_handler(clean_registry):
    """Test custom handler registration."""
    register_custom_handler(MyCustomHandler())

    handler = clean_registry.get_handler(field_info)
    assert isinstance(handler, MyCustomHandler)
```

---

### Advanced: Handler Replacement

```python
from niceguicrud.input_handlers import get_registry, StringHandler

# Unregister default string handler
registry = get_registry()
registry.unregister(StringHandler)

# Register custom replacement
class CustomStringHandler:
    priority = 100

    def can_handle(self, field_info):
        return field_info.annotation == str

    def create_widget(self, context):
        # Custom string input with character counter
        input_widget = ui.input(value=context.current_value, validation=context.validation_callback)
        ui.label().bind_text_from(input_widget, "value", backward=lambda v: f"{len(v or '')} chars")
        return input_widget

registry.register(CustomStringHandler())
```

---

## Thread Safety

**Current Implementation**: NOT thread-safe

- Registry is module-level singleton
- Registration/unregistration modify shared state
- No locking on cache access

**Recommendation**:
- Register all custom handlers at application startup (before NiceGUI starts)
- Avoid dynamic registration during request handling
- If needed, protect with threading.Lock

---

## Performance Characteristics

### Handler Lookup
- **First lookup**: O(n) where n = number of registered handlers
- **Cached lookup**: O(1) dictionary access
- **Cache invalidation**: O(1) dict.clear()

### Registration
- **Insert**: O(n) to maintain sorted order
- **Cache clear**: O(1)

### Typical Overhead
- ~15 handlers registered (8 built-in + ~7 custom average)
- First lookup: <1ms (iterates max 15 handlers)
- Cached lookup: <0.01ms

---

## Migration Guide

### Upgrading from Monolithic System

**Before** (monolithic):
```python
# Custom input logic embedded in get_input method
if typ == MyCustomType:
    return ui.custom_widget(value=curval)
```

**After** (modular):
```python
# Define handler
class MyCustomTypeHandler:
    priority = 150

    def can_handle(self, field_info):
        return field_info.annotation == MyCustomType

    def create_widget(self, context):
        return ui.custom_widget(value=context.current_value)

# Register once at startup
register_custom_handler(MyCustomTypeHandler())
```

**Benefits**:
- Testable in isolation
- No modification of library code
- Clear extension point
- Can be distributed as separate package
