# Quickstart: Adding a New Input Type

**Feature**: 001-modular-input
**Audience**: Developers extending NiceCRUD with custom input handlers

## Overview

This guide shows how to add support for a new pydantic type in NiceCRUD using the modular handler system. You'll learn to implement a custom handler, register it, and test it.

## When to Create a Custom Handler

Create a custom handler when:
- You have a domain-specific type (e.g., `Color`, `Currency`, `GeoCoordinate`)
- You want a specialized widget (e.g., color picker, map selector, rich text editor)
- Built-in handlers don't support your type
- You want to override default widget for an existing type

## 5-Minute Example: Color Picker

### Step 1: Define Your Pydantic Type

```python
from pydantic import BaseModel, field_validator

class Color(BaseModel):
    """RGB color represented as hex string."""
    hex: str

    @field_validator("hex")
    def validate_hex(cls, v):
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Must be 7-char hex color (#RRGGBB)")
        return v

class Product(BaseModel):
    name: str
    brand_color: Color  # Want a color picker for this field
```

---

### Step 2: Create Handler Class

```python
from niceguicrud.input_handlers import InputHandlerProtocol, InputContext
from pydantic.fields import FieldInfo
from nicegui import ui

class ColorPickerHandler:
    """Custom handler for Color type using NiceGUI color picker."""

    priority = 150  # Higher than built-ins (100)

    def can_handle(self, field_info: FieldInfo) -> bool:
        """Check if field is Color type."""
        return field_info.annotation == Color

    def create_widget(self, context: InputContext) -> ui.Element:
        """Create color picker widget."""
        current_hex = context.current_value.hex if context.current_value else "#000000"

        def on_color_change(e):
            """Convert hex string to Color and validate."""
            color = Color(hex=e.value)
            context.validation_callback(color)

        return ui.color_input(
            value=current_hex,
            on_change=on_color_change
        )
```

---

### Step 3: Register Handler

```python
from niceguicrud.input_handlers import register_custom_handler

# Register once at application startup (before creating CRUD)
register_custom_handler(ColorPickerHandler())

# Now Color fields automatically get color picker
crud = NiceCRUD(basemodels=[Product(...)])
```

---

### Step 4: Test It

```python
# Create test instance
product = Product(name="Widget", brand_color=Color(hex="#FF5733"))

# Open CRUD UI
crud = NiceCRUD(basemodels=[product], id_field="name")
ui.run()

# Click edit button → Color field shows color picker widget
# Select color → Validation runs automatically
# Save → Product.brand_color updated
```

---

## Common Patterns

### Pattern 1: Metadata-Based Handler

Trigger custom widget via field metadata instead of type:

```python
class RichTextHandler:
    priority = 150

    def can_handle(self, field_info: FieldInfo) -> bool:
        extra = field_info.json_schema_extra or {}
        return extra.get("input_type") == "richtext"

    def create_widget(self, context: InputContext) -> ui.Element:
        # Use a rich text editor widget
        return ui.editor(value=context.current_value, on_change=context.validation_callback)

# Usage in model
class Article(BaseModel):
    title: str
    content: str = Field(json_schema_extra={"input_type": "richtext"})
```

---

### Pattern 2: Complex Widget with Nested UI

Create composite widget with multiple UI elements:

```python
class GeoCoordinateHandler:
    priority = 150

    def can_handle(self, field_info: FieldInfo) -> bool:
        return field_info.annotation == GeoCoordinate

    def create_widget(self, context: InputContext) -> ui.Element:
        coord = context.current_value or GeoCoordinate(lat=0, lon=0)

        with ui.row() as row:
            lat_input = ui.number(
                value=coord.lat,
                label="Latitude",
                min=-90,
                max=90
            )
            lon_input = ui.number(
                value=coord.lon,
                label="Longitude",
                min=-180,
                max=180
            )

            def update_coord():
                new_coord = GeoCoordinate(lat=lat_input.value, lon=lon_input.value)
                context.validation_callback(new_coord)

            lat_input.on_value_change(update_coord)
            lon_input.on_value_change(update_coord)

        return row
```

---

### Pattern 3: Optional Field with Clearable Input

Handle Optional types properly:

```python
class CurrencyHandler:
    priority = 150

    def can_handle(self, field_info: FieldInfo) -> bool:
        import typing
        # Handle both Currency and Optional[Currency]
        origin = typing.get_origin(field_info.annotation)
        if origin in (typing.Union, typing.UnionType):
            args = typing.get_args(field_info.annotation)
            if type(None) in args:
                # Optional[Currency] - extract Currency from Union
                return any(arg == Currency for arg in args if arg is not type(None))
        return field_info.annotation == Currency

    def create_widget(self, context: InputContext) -> ui.Element:
        value_str = str(context.current_value.amount) if context.current_value else ""

        def on_change(e):
            if not e.value:
                context.validation_callback(None)  # Clear optional field
            else:
                context.validation_callback(Currency(amount=float(e.value), code="USD"))

        input_widget = ui.number(
            value=value_str,
            validation=on_change,
            prefix="$"
        )

        # Add clearable for optional fields
        if typing.get_origin(context.field_info.annotation) in (typing.Union, typing.UnionType):
            input_widget.props("clearable")

        return input_widget
```

---

## Testing Custom Handlers

### Unit Test Example

```python
import pytest
from pydantic import BaseModel, Field
from niceguicrud.input_handlers import InputContext, get_registry

def test_color_picker_handler():
    """Test ColorPickerHandler creates correct widget."""

    # Setup
    class TestModel(BaseModel):
        color: Color

    field_info = TestModel.model_fields["color"]
    registry = get_registry()

    # Test can_handle
    handler = registry.get_handler(field_info)
    assert isinstance(handler, ColorPickerHandler)

    # Test create_widget
    ctx = InputContext(
        field_name="color",
        field_info=field_info,
        current_value=Color(hex="#FF0000"),
        validation_callback=lambda x: None,
        config=NiceCRUDConfig(),
        item=TestModel(color=Color(hex="#FF0000"))
    )

    widget = handler.create_widget(ctx)
    assert widget is not None
    # Verify widget type (implementation-specific)
```

---

### Integration Test with Playwright

```python
import pytest
from playwright.sync_api import Page

@pytest.fixture
def color_app(page: Page):
    """Launch example app with Color field."""
    # Start app in background
    proc = subprocess.Popen(["python", "examples/color_picker_example.py"])
    page.goto("http://localhost:8080")
    yield page
    proc.terminate()

def test_color_picker_interaction(color_app: Page):
    """Test color picker widget in browser."""

    # Click edit button
    color_app.click('button[icon="edit"]')

    # Verify color picker rendered
    color_input = color_app.locator('input[type="color"]')
    assert color_input.is_visible()

    # Change color
    color_input.fill("#00FF00")

    # Verify validation callback fired (check for error message absence)
    error = color_app.locator('.error')
    assert not error.is_visible()

    # Save and verify
    color_app.click('button:has-text("Save")')
    assert color_app.locator(':has-text("#00FF00")').is_visible()
```

---

## Best Practices

### ✅ DO

1. **Set appropriate priority**
   - Built-in handlers: 100
   - Custom handlers: 150+ (checked first)
   - Fallback handlers: -1000

2. **Handle errors gracefully**
   ```python
   def create_widget(self, context):
       try:
           return ui.custom_widget(value=context.current_value)
       except Exception as e:
           log.warning(f"Widget creation failed: {e}")
           return None  # Registry will try next handler
   ```

3. **Respect configuration**
   ```python
   widget = ui.input(value=context.current_value)
   if context.config.readonly:
       widget.disable()
   return widget
   ```

4. **Add tooltips for descriptions**
   ```python
   with ui.label(field_info.title or field_name):
       if context.field_info.description:
           with ui.tooltip():
               ui.html(context.field_info.description)
   ```

---

### ❌ DON'T

1. **Don't modify field_info in can_handle**
   ```python
   # BAD
   def can_handle(self, field_info):
       field_info.annotation = str  # NEVER mutate!
       return True
   ```

2. **Don't bypass validation_callback**
   ```python
   # BAD
   ui.input(value=val, on_change=lambda e: setattr(context.item, "field", e.value))

   # GOOD
   ui.input(value=val, validation=context.validation_callback)
   ```

3. **Don't assume global state**
   ```python
   # BAD
   _current_value = None
   def create_widget(self, context):
       global _current_value
       _current_value = context.current_value  # Not thread-safe!
   ```

---

## Troubleshooting

### Handler Not Being Called

**Symptom**: Field renders as text input instead of custom widget

**Causes**:
1. Handler not registered: Call `register_custom_handler()` before creating CRUD
2. Priority too low: Increase priority above built-ins (>100)
3. `can_handle` returning False: Add logging to debug

**Fix**:
```python
# Add debugging
class MyHandler:
    def can_handle(self, field_info):
        result = field_info.annotation == MyType
        print(f"can_handle({field_info.annotation}) = {result}")
        return result
```

---

### Validation Not Working

**Symptom**: Changes not saved or validation errors not shown

**Cause**: Not using `context.validation_callback`

**Fix**:
```python
# Ensure on_change/validation uses callback
ui.input(value=val, validation=context.validation_callback)

# For custom events
def my_change_handler(e):
    new_value = transform(e.value)
    context.validation_callback(new_value)  # REQUIRED

ui.custom_widget(on_change=my_change_handler)
```

---

### Widget Not Rendering

**Symptom**: Blank space or error in UI

**Causes**:
1. Returning None from `create_widget`
2. Exception during widget creation
3. Invalid NiceGUI element

**Fix**:
```python
def create_widget(self, context):
    try:
        widget = ui.custom_widget(...)
        if widget is None:
            log.error("Widget creation returned None")
        return widget
    except Exception as e:
        log.exception(f"Widget creation failed: {e}")
        return None  # Graceful degradation
```

---

## Next Steps

- Review [input-handler-protocol.md](contracts/input-handler-protocol.md) for full API
- See [registry-api.md](contracts/registry-api.md) for advanced usage
- Check [data-model.md](data-model.md) for architecture details
- Explore built-in handlers in `niceguicrud/input_handlers/*.py` for examples
