# Contract: InputHandlerProtocol

**Feature**: 001-modular-input
**Version**: 1.0
**Type**: Protocol Interface

## Purpose

Defines the interface contract that all input handlers must implement to participate in the modular input system. This protocol enables both built-in and custom handlers to generate NiceGUI widgets for pydantic model fields.

## Protocol Definition

```python
from typing import Protocol, Any
from pydantic.fields import FieldInfo
from nicegui import ui

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
            - SHOULD check field_info.annotation first (most common)
            - MAY check field_info.json_schema_extra for custom metadata

        Examples:
            # Type-based matching
            return field_info.annotation == str

            # Metadata-based matching
            extra = field_info.json_schema_extra or {}
            return extra.get("input_type") == "slider"

            # Complex type matching
            return typing.get_origin(field_info.annotation) == list
        """
        ...

    def create_widget(self, context: InputContext) -> ui.Element | None:
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
            - MAY modify context.item fields if creating nested editors

        Error Handling:
            - SHOULD catch widget creation errors and return None
            - MUST NOT raise exceptions that would crash the UI
            - MAY log warnings for debugging

        Examples:
            # Simple string input
            return ui.input(
                value=context.current_value,
                validation=context.validation_callback,
                placeholder=context.field_info.description or ""
            )

            # Number with constraints
            _min, _max = extract_min_max(context.field_info)
            return ui.number(
                value=context.current_value,
                validation=context.validation_callback,
                min=_min,
                max=_max
            )
        """
        ...
```

## InputContext Structure

```python
from dataclasses import dataclass
from typing import Any, Callable
from pydantic import BaseModel
from pydantic.fields import FieldInfo

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

    config: NiceCRUDConfig
    """UI configuration (CSS classes, labels, readonly settings, etc.)"""

    item: BaseModel
    """The model instance being edited. Used for nested object handlers."""
```

## Built-in Handler Contracts

### StringHandler

**Priority**: 100

**Can Handle**:
- `field_info.annotation == str`
- `field_info.annotation == Path`
- `field_info.json_schema_extra.get("input_type") == "textarea"`

**Creates**:
- `ui.input()` for str/Path
- `ui.textarea()` for textarea variant
- Adds `clearable` prop if field is Optional

---

### NumericHandler

**Priority**: 100

**Can Handle**:
- `field_info.annotation in (int, float)`

**Creates**:
- `ui.number()` with min/max from `annotated_types` metadata
- `ui.slider()` if `input_type=="slider"` and min/max defined
- Adds `clearable` prop if field is Optional

---

### BooleanHandler

**Priority**: 100

**Can Handle**:
- `field_info.annotation == bool`

**Creates**:
- `ui.switch()` with current boolean value

---

### TemporalHandler

**Priority**: 100

**Can Handle**:
- `field_info.annotation in (date, time, datetime)`

**Creates**:
- `ui.input()` with date picker menu for `date`
- `ui.input()` with time picker menu for `time`
- `ui.input()` with combined date+time picker for `datetime`

---

### SelectionHandler

**Priority**: 100

**Can Handle**:
- `typing.get_origin(field_info.annotation) == Literal`
- `field_info.json_schema_extra.get("input_type") in ("select", "multiselect")`

**Creates**:
- `ui.select()` with options from Literal args or `selections` metadata
- Supports `multiple=True` for multiselect variant
- Fetches dynamic options via `select_options` callback if needed

---

### NestedHandler

**Priority**: 100

**Can Handle**:
- `issubclass(field_info.annotation, BaseModel)`
- `Union[BaseModel1, BaseModel2, ...]` (all args are BaseModel subclasses)
- `list[BaseModel]`

**Creates**:
- Edit button that opens dialog with nested `NiceCRUDCard`
- BaseModel switcher for Union types (dropdown + edit button)
- List of edit/delete buttons for `list[BaseModel]`

---

### CollectionHandler

**Priority**: 100

**Can Handle**:
- `list[str]`, `set[str]`
- `list[int]`, `list[float]`

**Creates**:
- `ui.input()` that accepts comma-separated values
- Parses input on change and validates as list

---

### FallbackHandler

**Priority**: -1000

**Can Handle**:
- Always returns `True` (catch-all)

**Creates**:
- `ui.input(value="ERROR")` with warning logged
- Suggests registering custom handler for unknown type

## Usage Example

```python
# Custom handler for Color type
class ColorPickerHandler:
    priority = 150  # Higher than built-ins

    def can_handle(self, field_info: FieldInfo) -> bool:
        return field_info.annotation == Color

    def create_widget(self, context: InputContext) -> ui.Element:
        return ui.color_input(
            value=context.current_value.hex if context.current_value else "#000000",
            on_change=lambda e: context.validation_callback(Color(e.value))
        )

# Register before creating CRUD interface
register_custom_handler(ColorPickerHandler())

# Now Color fields automatically get color picker widget
class Product(BaseModel):
    name: str
    brand_color: Color  # Will use ColorPickerHandler
```

## Compliance Requirements

Handlers MUST:
1. Implement both `can_handle` and `create_widget` methods
2. Set `priority` attribute (int)
3. Return boolean from `can_handle` without side effects
4. Use `context.validation_callback` for input changes
5. Return `ui.Element` or `None` from `create_widget`

Handlers SHOULD:
1. Extract constraints from `field_info.metadata`
2. Respect `config.readonly` and similar settings
3. Add tooltips for fields with descriptions
4. Handle Optional types with clearable inputs
5. Log warnings for edge cases

Handlers MUST NOT:
1. Modify `field_info` in `can_handle`
2. Raise unhandled exceptions in `create_widget`
3. Directly mutate `context.item` (use validation_callback)
4. Assume global state or singletons
