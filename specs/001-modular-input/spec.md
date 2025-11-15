# Feature Specification: Modular Input Element System

**Feature Branch**: `001-modular-input`
**Created**: 2025-11-15
**Status**: Draft
**Input**: User description: "I want the supported input elements to be defined more modular and not in one giant if else if thing. It is not easy to integrate this so it actually works, so you should use playwright to test if it actually works"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Maintainable Input System (Priority: P1)

Developers can easily understand, extend, and modify the input element generation logic without navigating through complex conditional chains.

**Why this priority**: The current implementation has a monolithic `get_input` method (lines 260-563 in nicecrud.py) with deeply nested if-elif chains that are difficult to maintain, test, and extend. This is the core architectural improvement that enables all other benefits.

**Independent Test**: Can be fully tested by examining the refactored code structure - each input type should have its own handler that can be tested in isolation, and the system should pass all existing examples without regression.

**Acceptance Scenarios**:

1. **Given** the current monolithic `get_input` method, **When** refactoring to a modular system, **Then** each input type (string, number, date, BaseModel, etc.) should have its own dedicated handler/factory
2. **Given** a new input type needs to be added, **When** a developer wants to add support for it, **Then** they should only need to create a new handler class/function and register it, without modifying the core dispatching logic
3. **Given** the refactored system, **When** running all existing examples (minimal, validation, submodel, input_choices, database), **Then** all examples should work identically to before the refactor

---

### User Story 2 - Automated UI Testing (Priority: P2)

Developers can verify that UI input elements work correctly through automated browser tests, catching regressions before they reach users.

**Why this priority**: Manual testing of UI components is time-consuming and error-prone. Automated Playwright tests ensure input elements render correctly, accept user input, and trigger validation as expected.

**Independent Test**: Can be tested by running Playwright test suite against example applications - tests should verify input rendering, interaction, and validation for each supported input type.

**Acceptance Scenarios**:

1. **Given** the minimal example application, **When** Playwright tests run, **Then** the test should verify that input fields render, can accept text input, and validate constraints (e.g., age > 0)
2. **Given** the input_choices example, **When** Playwright tests run, **Then** the test should verify all input types (select, multiselect, slider, textarea, date, time, datetime, Path) render and accept input correctly
3. **Given** a pydantic model with validation errors, **When** invalid data is entered through the UI, **Then** Playwright tests should verify that error messages appear and the save button is disabled

---

### User Story 3 - Extensible Input Registry (Priority: P3)

Developers can register custom input handlers for domain-specific types without forking the library.

**Why this priority**: Enables customization for advanced use cases (e.g., custom widgets for specialized types) while maintaining the library's simplicity for common cases.

**Independent Test**: Can be tested by creating a custom input handler for a new type (e.g., a color picker for a custom Color type) and verifying it integrates seamlessly with the CRUD interface.

**Acceptance Scenarios**:

1. **Given** a custom type (e.g., Color with hex string validation), **When** a developer registers a custom input handler, **Then** the CRUD interface should use that handler when rendering fields of that type
2. **Given** multiple custom handlers registered, **When** the system needs to render inputs, **Then** it should prioritize custom handlers over default handlers
3. **Given** a custom handler that fails, **When** an error occurs, **Then** the system should fall back gracefully to a default text input with a warning

---

### Edge Cases

- What happens when a pydantic type has no registered handler (neither built-in nor custom)? → Log warning and render basic text input with field value converted to string
- How does the system handle Optional types with custom handlers? → Custom handler receives Optional-wrapped type, should add clearable property to input widget
- What happens when a custom handler raises an exception during rendering? → Log warning with exception details, fall back to rendering basic text input, preserve UI functionality
- How are Union types handled when multiple handlers might apply? → First matching handler by priority order wins; for Union[BaseModel, ...] use special basemodel switcher
- What happens when field metadata conflicts with handler expectations? → Handler validates metadata, logs warning if invalid, uses sensible defaults or falls back to simpler widget variant

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST refactor the monolithic `get_input` method into a modular handler system where each pydantic type maps to a dedicated input generator
- **FR-002**: System MUST maintain backward compatibility - all existing examples and use cases must continue to work without modification
- **FR-003**: System MUST support all currently implemented input types: string, Path, int, float, bool, date, time, datetime, Literal, BaseModel, list of BaseModel, list of strings, select/multiselect
- **FR-004**: System MUST include Playwright tests that verify input rendering and interaction for each supported input type
- **FR-005**: System MUST allow registration of custom input handlers for user-defined types
- **FR-006**: System MUST provide clear extension points for adding new input types without modifying core library code
- **FR-009**: Documentation MUST use example-driven tutorials showing complete working handlers with inline explanations, minimizing abstract API descriptions
- **FR-007**: Playwright tests MUST run against example applications to verify real-world usage scenarios, executed on pull request and release workflows (not on every commit)
- **FR-008**: System MUST handle edge cases gracefully (unknown types, failed handlers, conflicting metadata)
- **FR-010**: When a custom handler fails during widget creation, system MUST log warning with exception details and fall back to rendering a basic text input to preserve UI functionality
- **FR-011**: Handler system MUST use Python's standard logging module with configurable log levels, allowing integration with application logging infrastructure

### Key Entities

- **Input Handler**: Component responsible for generating NiceGUI elements for a specific pydantic type
- **Handler Registry**: Mapping from pydantic types/patterns to their corresponding input handlers
- **Input Context**: Information needed by handlers (field_name, field_info, current_value, validation_callback, config)
- **Test Scenario**: Playwright test case covering a specific input type or interaction pattern

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Code complexity reduced - the main dispatching logic should be under 50 lines (down from ~300 lines in current `get_input` method)
- **SC-002**: Each input handler should be independently testable with unit tests
- **SC-003**: All existing examples (minimal.py, validation.py, submodel.py, input_choices.py, database.py) pass without modification
- **SC-004**: Playwright test suite covers at least 90% of supported input types with automated browser interaction tests
- **SC-005**: Adding a new input type requires only creating a new handler and registering it (under 50 lines of code, no modifications to existing files)
- **SC-006**: Refactored system prioritizes architectural quality and maintainability; performance regression tests verify no significant degradation in typical usage scenarios (forms with 10-20 fields)
- **SC-007**: Documentation includes at least 5 complete, runnable example handlers with inline explanations covering common use cases (string variants, custom types, nested objects, validation patterns, error handling)

## Assumptions

- The pydantic model structure and validation behavior will remain unchanged
- NiceGUI API for creating input elements remains stable
- Existing field metadata conventions (json_schema_extra, FieldOptions) continue to be supported
- The refactor focuses on the input generation logic in `NiceCRUDCard.get_input` method
- Playwright is an acceptable testing framework for browser-based UI testing

## Clarifications

### Session 2025-11-15

- Q: Given your emphasis on example-based documentation, how should the documentation for the new handler system be structured? → A: Example-driven tutorials showing complete working handlers with inline explanations
- Q: What is the minimum acceptable Playwright test coverage strategy for this feature? → A: Core input types covered (90% target already specified), tests run on PR/release only
- Q: When a custom handler fails during widget creation, what should the fallback behavior be? → A: Log warning and render basic text input - preserve functionality with degraded UX
- Q: What logging mechanism should the handler system use for warnings and errors? → A: Python logging module with configurable levels - integrate with application logging infrastructure
- Q: What is the acceptable performance threshold for input rendering after the refactoring? → A: No specific threshold - focus on architectural quality over micro-optimizations
