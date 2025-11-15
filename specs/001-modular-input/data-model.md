# Data Model: Modular Input Handler Architecture

**Feature**: 001-modular-input
**Date**: 2025-11-15
**Phase**: 1 - Design

## Overview

This document defines the core entities and their relationships for the modular input handler system. These are architectural components, not data persistence entities (no database/storage involved).

## Core Entities

### 1. InputHandlerProtocol

**Purpose**: Interface contract that all input handlers must implement

**Attributes**:
- `priority: int` - Handler priority for resolution order (higher = checked first)

**Methods**:
- `can_handle(field_info: FieldInfo) -> bool` - Returns True if this handler can process the given field
- `create_widget(context: InputContext) -> ui.Element | None` - Creates NiceGUI widget for the field

**Validation Rules**:
- `can_handle` must not modify state (pure function)
- `create_widget` must return valid NiceGUI element or None
- Priority must be integer >= 0

**Relationships**:
- Registered in `HandlerRegistry`
- Receives `InputContext` when creating widgets

---

### 2. InputContext

**Purpose**: Immutable container for all data needed by handlers to create widgets

**Attributes**:
- `field_name: str` - Name of the pydantic field
- `field_info: FieldInfo` - Pydantic field metadata (type, constraints, description, etc.)
- `current_value: Any` - Current value of the field on the model instance
- `validation_callback: Callable[[Any], None]` - Function to call when input changes
- `config: NiceCRUDConfig` - UI configuration (CSS classes, labels, etc.)
- `item: BaseModel` - The model instance being edited

**Validation Rules**:
- All attributes are read-only (frozen dataclass)
- `field_name` must exist in `item`'s model fields
- `validation_callback` must accept single argument matching field type

**Relationships**:
- Passed to `InputHandlerProtocol.create_widget`
- Contains reference to `NiceCRUDConfig`

---

### 3. HandlerRegistry

**Purpose**: Central registry mapping pydantic types to their input handlers

**Attributes**:
- `_handlers: list[InputHandlerProtocol]` - Registered handlers, sorted by priority descending
- `_cache: dict[type, InputHandlerProtocol]` - Memoization cache for type → handler lookups

**Methods**:
- `register(handler: InputHandlerProtocol, priority: int = 100) -> None` - Add handler to registry
- `get_handler(field_info: FieldInfo) -> InputHandlerProtocol` - Find first handler that can handle the field
- `clear_cache() -> None` - Reset lookup cache (useful for testing)

**Validation Rules**:
- Handlers must be checked in priority order (high to low)
- If no handler matches, raise `NoHandlerFoundError`
- Cache must be invalidated when new handlers registered

**Relationships**:
- Contains multiple `InputHandlerProtocol` instances
- Queried by `NiceCRUDCard.get_input` to find appropriate handler

---

### 4. Built-in Handler Implementations

Each handler module implements `InputHandlerProtocol` for specific type categories:

#### StringHandler (string.py)
- **Can handle**: `str`, `Path`, or field with `input_type="textarea"`
- **Creates**: `ui.input()` or `ui.textarea()`
- **Special handling**: Adds `clearable` prop for Optional fields

#### NumericHandler (numeric.py)
- **Can handle**: `int`, `float`
- **Creates**: `ui.number()` or `ui.slider()` based on `input_type` and min/max constraints
- **Special handling**: Extracts min/max from `annotated_types` metadata

#### BooleanHandler (boolean.py)
- **Can handle**: `bool`
- **Creates**: `ui.switch()`

#### TemporalHandler (temporal.py)
- **Can handle**: `date`, `time`, `datetime`
- **Creates**: `ui.input()` with date/time picker menu
- **Special handling**: Combined date+time picker for datetime

#### SelectionHandler (selection.py)
- **Can handle**: `Literal[...]`, or field with `input_type="select"|"multiselect"`
- **Creates**: `ui.select()` with options
- **Special handling**: Fetches dynamic options from `select_options` callback

#### NestedHandler (nested.py)
- **Can handle**: `BaseModel`, `Union[BaseModel, ...]`, `list[BaseModel]`
- **Creates**: Edit button that opens dialog with nested `NiceCRUDCard`
- **Special handling**: BaseModel switcher for Union types

#### CollectionHandler (collections.py)
- **Can handle**: `list[str]`, `list[int]`, `list[float]`
- **Creates**: `ui.input()` with comma-separated values
- **Special handling**: Parses/formats comma-delimited strings

---

### 5. FallbackHandler

**Purpose**: Catch-all handler when no specific handler matches

**Attributes**:
- `priority: int = -1000` (lowest priority, checked last)

**Behavior**:
- `can_handle`: Always returns True
- `create_widget`: Returns `ui.input(value="ERROR")` and logs warning
- Logs field type and suggests registering custom handler

---

## Entity Relationships

```
HandlerRegistry
├── contains [0..*] InputHandlerProtocol
│   ├── StringHandler
│   ├── NumericHandler
│   ├── BooleanHandler
│   ├── TemporalHandler
│   ├── SelectionHandler
│   ├── NestedHandler
│   ├── CollectionHandler
│   └── FallbackHandler
│
└── queried by NiceCRUDCard.get_input
    └── passes InputContext
        ├── references FieldInfo (from pydantic)
        ├── references NiceCRUDConfig
        └── references BaseModel instance
```

## State Transitions

### Handler Resolution Flow

```
1. NiceCRUDCard.get_input(field_name, field_info)
   └─> Create InputContext from field data
       └─> HandlerRegistry.get_handler(field_info)
           └─> Check cache for field_info.annotation
               ├─> Cache hit: return cached handler
               └─> Cache miss:
                   └─> Iterate handlers by priority (high to low)
                       └─> Call handler.can_handle(field_info)
                           ├─> True: cache and return handler
                           └─> False: continue to next handler
                   └─> If no handler found: raise NoHandlerFoundError
   └─> handler.create_widget(context)
       └─> Return NiceGUI element
```

### Custom Handler Registration Flow

```
1. User calls register_custom_handler(handler, priority=150)
   └─> HandlerRegistry.register(handler, priority)
       ├─> Insert handler in priority-sorted position
       └─> Clear lookup cache
           └─> Next get_handler call will re-evaluate all handlers
```

## Validation & Constraints

### Type Safety
- All handlers type-hinted with `InputHandlerProtocol`
- `InputContext` is frozen dataclass (runtime immutability)
- Registry enforces priority ordering

### Backward Compatibility
- Existing `NiceCRUDCard.get_input` signature unchanged
- Handlers encapsulate existing widget creation logic
- No changes to public API of `NiceCRUD` or `NiceCRUDCard`

### Performance
- Handler lookup cached by type after first resolution
- O(n) worst-case for first lookup (n = number of handlers)
- O(1) for subsequent lookups of same type

## Extension Points

Users can extend the system by:
1. Implementing `InputHandlerProtocol` for custom types
2. Registering handler via `register_custom_handler(handler, priority)`
3. Custom handlers checked before built-in handlers (if priority > 100)

Example:
```python
class ColorPickerHandler:
    priority = 150

    def can_handle(self, field_info: FieldInfo) -> bool:
        return field_info.annotation == Color

    def create_widget(self, ctx: InputContext) -> ui.Element:
        return ui.color_input(value=ctx.current_value, on_change=ctx.validation_callback)

register_custom_handler(ColorPickerHandler())
```
