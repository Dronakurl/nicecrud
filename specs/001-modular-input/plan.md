# Implementation Plan: Modular Input Element System

**Branch**: `001-modular-input` | **Date**: 2025-11-15 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-modular-input/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Refactor the monolithic `get_input` method in `NiceCRUDCard` (currently 300+ lines of nested conditionals) into a modular handler system where each pydantic type maps to a dedicated input generator. Add Playwright-based automated UI testing (90% coverage, run on PR/release) to verify all input types render correctly and handle user interactions properly. Enable extensibility through a handler registry that allows custom input widgets for domain-specific types. Documentation will be example-driven with complete working handlers and inline explanations.

## Technical Context

**Language/Version**: Python 3.12+ (per pyproject.toml requirement)
**Primary Dependencies**: pydantic v2.x, NiceGUI, pytest, pytest-asyncio, playwright (new), Python logging module
**Storage**: N/A (this is a UI refactoring feature)
**Testing**: pytest for unit tests, playwright for browser-based UI tests (run on PR/release workflows)
**Target Platform**: Web browsers (via NiceGUI server-side Python + client-side JavaScript)
**Project Type**: single (Python library)
**Performance Goals**: Prioritize architectural quality; verify no significant degradation in typical usage (10-20 field forms)
**Constraints**: Must maintain backward compatibility with all existing examples and user code
**Scale/Scope**: Refactor affects ~300 lines in nicecrud.py, add ~15 input handler modules, ~500 lines of Playwright tests, example-driven documentation with 5+ complete handlers

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Developer Experience First

✅ **PASS** - This refactoring directly improves developer experience:
- Makes codebase easier to understand (modular handlers vs 300-line method)
- Easier to extend (register new handler vs modify conditional chain)
- Better error messages possible (handler-specific failures with Python logging)
- Examples remain unchanged (backward compatibility preserved)
- Documentation will be example-driven tutorials per FR-009 and clarifications

### II. Pydantic-Native Integration

✅ **PASS** - Refactoring maintains pydantic integration:
- Handler registry still driven by pydantic type annotations
- Field metadata (constraints, descriptions) still extracted from FieldInfo
- No changes to pydantic model contracts or validation behavior
- Type hints continue to drive UI component selection

### III. Minimal Configuration

✅ **PASS** - No new configuration required:
- Handler registry is internal implementation detail
- Zero API changes for basic usage (NiceCRUD initialization unchanged)
- Custom handlers are optional (P3 user story, not required for basic usage)
- No new required parameters or global state

### Development Standards

✅ **Code Quality**: Type hints will be required for all new handler interfaces
✅ **Testing**: Playwright tests will cover 90% of input types with UI interaction tests, run on PR/release
✅ **Documentation**: Examples will continue to work without modification (SC-003), plus example-driven tutorials (FR-009, SC-007)

**Overall Gate Status**: ✅ **APPROVED** - All constitution principles satisfied, no violations to justify

---

### Post-Phase 1 Re-evaluation

After completing design (research.md, data-model.md, contracts/):

✅ **Developer Experience First**: Design confirms modular handlers improve DX - quickstart.md shows adding new handler takes <50 lines with example-driven approach
✅ **Pydantic-Native Integration**: InputContext passes FieldInfo directly to handlers, preserving pydantic as single source of truth
✅ **Minimal Configuration**: Custom handler registration is optional extension point, zero config required for basic usage

**Re-evaluation Result**: ✅ **STILL APPROVED** - Design phase reinforces constitutional compliance

## Project Structure

### Documentation (this feature)

```text
specs/001-modular-input/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (design patterns research)
├── data-model.md        # Phase 1 output (handler architecture)
├── quickstart.md        # Phase 1 output (example-driven developer workflow)
├── contracts/           # Phase 1 output (handler interfaces)
│   ├── input-handler-protocol.md
│   └── registry-api.md
├── checklists/
│   └── requirements.md  # Quality validation checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
niceguicrud/
├── __init__.py
├── nicecrud.py          # Main NiceCRUD and NiceCRUDCard classes (to be refactored)
├── basemodel_to_table.py
├── show_error.py
└── input_handlers/      # NEW: Modular input handler system
    ├── __init__.py      # Handler registry, dispatcher, public API
    ├── base.py          # Base handler protocol/ABC
    ├── string.py        # String and Path handlers
    ├── numeric.py       # Int, Float, slider handlers
    ├── boolean.py       # Boolean/switch handler
    ├── temporal.py      # Date, Time, DateTime handlers
    ├── selection.py     # Literal, select, multiselect handlers
    ├── nested.py        # BaseModel and list[BaseModel] handlers
    └── collections.py   # List[str], list[int/float] handlers

tests/
├── unit/                # Unit tests for individual handlers
│   └── test_input_handlers.py
├── integration/         # Integration tests for handler system
│   └── test_handler_registry.py
└── playwright/          # NEW: Browser-based UI tests (90% coverage)
    ├── conftest.py      # Playwright fixtures
    ├── test_minimal_example.py
    ├── test_input_choices.py
    └── test_validation.py

examples/                # Existing examples (must continue to work)
├── minimal.py
├── validation.py
├── submodel.py
├── input_choices.py
├── database.py
└── custom_handler_example.py  # NEW: Example-driven tutorial for custom handlers

docs/                    # NEW: Example-driven documentation
└── handler_examples/    # 5+ complete working handler examples
    ├── 01_basic_string_handler.md
    ├── 02_custom_type_color.md
    ├── 03_nested_object_handler.md
    ├── 04_validation_patterns.md
    └── 05_error_handling.md
```

**Structure Decision**: Single project structure (Python library). New `input_handlers/` package contains modular handler system. Playwright tests added under `tests/playwright/` to verify browser-based UI interactions. All existing code in `niceguicrud/` remains, with `nicecrud.py` refactored to use the new handler system. Example-driven documentation in `docs/handler_examples/` with inline explanations per clarifications.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitutional violations - this section intentionally left empty.
