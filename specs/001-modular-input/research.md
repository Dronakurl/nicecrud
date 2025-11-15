# Research: Modular Input Element System

**Date**: 2025-11-15
**Feature**: 001-modular-input
**Phase**: 0 - Research & Design Patterns

## Overview

This document consolidates research findings for refactoring the monolithic `get_input` method into a modular handler system. No "NEEDS CLARIFICATION" items existed in the technical context - all dependencies and patterns are well-established.

## 1. Handler Registry Pattern

### Decision: Protocol-based registry with type-to-handler mapping

**Rationale**:
- Python's `typing.Protocol` provides structural typing without inheritance overhead
- Allows handler registration by type pattern (exact type, origin type, callable predicate)
- Supports both built-in and custom handlers through unified interface
- Maintains backward compatibility (handlers encapsulate existing logic)

**Alternatives considered**:
1. **Abstract Base Classes (ABC)**: More rigid, requires inheritance, harder to add custom handlers
2. **String-based dispatch**: Error-prone, no type safety, difficult to debug
3. **Visitor pattern**: Over-engineered for this use case, adds unnecessary complexity

**Implementation approach**:
- `InputHandlerProtocol`: Defines `can_handle(field_info) -> bool` and `create_widget(context) -> ui.Element`
- `HandlerRegistry`: Maps type patterns to handler instances with priority ordering
- Custom handlers registered with higher priority than built-in defaults

## 2. Playwright Testing Strategy

### Decision: Pytest-playwright with page object pattern

**Rationale**:
- `pytest-playwright` integrates seamlessly with existing pytest setup
- Page object pattern encapsulates example app interactions for reusability
- NiceGUI apps can be launched as background processes for testing
- Playwright provides cross-browser testing (Chromium, Firefox, WebKit)

**Alternatives considered**:
1. **Selenium**: More verbose API, slower, less modern tooling
2. **Manual browser testing**: Not automatable, regression-prone
3. **Unit tests only**: Cannot verify actual browser rendering and interaction

**Testing architecture**:
```python
# Fixture launches example app in background
@pytest.fixture
async def minimal_app(page):
    proc = subprocess.Popen(["python", "examples/minimal.py"])
    await page.goto("http://localhost:8080")
    yield page
    proc.terminate()

# Page object encapsulates UI interactions
class CRUDPage:
    def fill_field(self, label, value):
        return self.page.locator(f"label:has-text('{label}') + input").fill(value)
```

## 3. Input Context Design

### Decision: Immutable dataclass with all handler dependencies

**Rationale**:
- Handlers need access to: field_name, field_info, current_value, validation callback, config
- Immutable context prevents handlers from modifying shared state
- Type-safe with dataclass annotations
- Easy to extend without breaking existing handlers

**Implementation**:
```python
@dataclass(frozen=True)
class InputContext:
    field_name: str
    field_info: FieldInfo
    current_value: Any
    validation_callback: Callable[[Any], None]
    config: NiceCRUDConfig
    item: BaseModel  # For nested object handlers
```

## 4. Handler Modularization Strategy

### Decision: Organize handlers by semantic type category

**Handler modules**:
- `string.py`: str, Path, textarea variant
- `numeric.py`: int, float, slider/number variants
- `boolean.py`: bool → switch
- `temporal.py`: date, time, datetime with picker widgets
- `selection.py`: Literal, select/multiselect with options
- `nested.py`: BaseModel, Union[BaseModel, ...], basemodel switcher
- `collections.py`: list[str], list[int], list[BaseModel]

**Rationale**:
- Groups related handlers for easier maintenance
- Each module ~50-100 lines (vs current 300-line method)
- Clear separation of concerns
- Easy to locate handler for specific type

## 5. Backward Compatibility Strategy

### Decision: Proxy pattern with gradual migration

**Approach**:
1. Implement new handler system in `input_handlers/` package
2. Modify `NiceCRUDCard.get_input` to dispatch to handler registry
3. Keep existing logic as fallback handlers initially
4. Run all examples as integration tests
5. Gradually migrate logic to dedicated handlers

**Verification**:
- All existing examples must pass without modification (SC-003)
- No API changes to `NiceCRUD` or `NiceCRUDCard` public interfaces
- Performance tests ensure no degradation

## 6. Custom Handler Extension API

### Decision: Simple registration function with priority

```python
# User code
def register_custom_handler(
    handler: InputHandlerProtocol,
    priority: int = 100  # Higher = checked first
) -> None:
    """Register a custom input handler for domain-specific types."""
    _registry.register(handler, priority)

# Example usage
class ColorHandler:
    def can_handle(self, field_info: FieldInfo) -> bool:
        return field_info.annotation == Color

    def create_widget(self, ctx: InputContext) -> ui.Element:
        return ui.color_input(value=ctx.current_value, on_change=ctx.validation_callback)

register_custom_handler(ColorHandler(), priority=150)
```

**Rationale**:
- Simple, pythonic API
- Priority system allows overriding built-in handlers
- No global state pollution (registry is module-level)
- Clear extension point

## 7. Error Handling Strategy

### Decision: Graceful degradation with logging

**Approach**:
- If handler raises exception → log warning, fall back to text input
- If no handler matches → log warning, use generic text input
- Error messages guide user to fix type annotation or register custom handler

**Example**:
```python
try:
    handler = registry.get_handler(field_info)
    return handler.create_widget(context)
except Exception as e:
    log.warning(f"Handler failed for {field_name}: {e}")
    return ui.input(value=str(current_value), on_change=validation_callback)
```

## 8. Performance Considerations

### Decision: Lazy handler instantiation with caching

**Rationale**:
- Handlers instantiated once per type, cached in registry
- Type checking happens at dispatch time (unavoidable)
- Minimize allocations in hot path (input rendering)

**Optimizations**:
- Cache type → handler lookups after first resolution
- Use `functools.lru_cache` for type origin checks
- Reuse NiceGUI widget instances where possible

## Key Takeaways

1. **Pattern**: Protocol-based registry with priority-ordered handlers
2. **Testing**: Playwright with page objects for real browser interaction
3. **Modularity**: ~8 handler modules replacing 300-line method
4. **Compatibility**: Proxy pattern ensures zero breaking changes
5. **Extensibility**: Simple registration API for custom handlers
6. **Performance**: Caching and lazy instantiation prevent regression

## Next Steps

Proceed to Phase 1:
- **data-model.md**: Define handler protocol, registry architecture, context structure
- **contracts/**: Document handler interface and registry API
- **quickstart.md**: Developer workflow for adding new input type
