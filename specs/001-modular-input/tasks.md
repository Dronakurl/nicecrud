# Tasks: Modular Input Element System

**Input**: Design documents from `/specs/001-modular-input/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Playwright tests are INCLUDED per FR-004. Unit tests and integration tests will verify handler isolation and system integration.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `niceguicrud/`, `tests/`, `examples/`, `docs/` at repository root
- Paths shown below follow single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create niceguicrud/input_handlers/ package directory
- [X] T002 [P] Create tests/unit/ directory for handler unit tests
- [X] T003 [P] Create tests/integration/ directory for handler integration tests
- [X] T004 [P] Create tests/playwright/ directory for browser UI tests
- [X] T005 [P] Create docs/handler_examples/ directory for example-driven documentation
- [X] T006 Add playwright to dev dependencies in pyproject.toml
- [X] T007 [P] Configure pytest-playwright in pyproject.toml or pytest.ini

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Implement InputHandlerProtocol in niceguicrud/input_handlers/base.py with can_handle and create_widget methods
- [X] T009 Implement InputContext dataclass in niceguicrud/input_handlers/base.py as frozen dataclass with field_name, field_info, current_value, validation_callback, config, item
- [X] T010 Implement HandlerRegistry in niceguicrud/input_handlers/__init__.py with register, get_handler, clear_cache methods and priority-ordered handler list
- [X] T011 Implement register_custom_handler public API function in niceguicrud/input_handlers/__init__.py
- [X] T012 Implement get_registry function in niceguicrud/input_handlers/__init__.py returning singleton registry instance
- [X] T013 Implement FallbackHandler in niceguicrud/input_handlers/base.py with priority=-1000, always returns True for can_handle, logs warning and returns basic text input
- [X] T014 Add Python logging configuration in niceguicrud/input_handlers/__init__.py with logger = logging.getLogger(__name__)
- [X] T015 Export public API (InputHandlerProtocol, InputContext, register_custom_handler, get_registry) from niceguicrud/input_handlers/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Maintainable Input System (Priority: P1) 🎯 MVP

**Goal**: Refactor monolithic get_input method into modular handlers for easier maintenance and extension

**Independent Test**: Run all existing examples (minimal.py, validation.py, submodel.py, input_choices.py, database.py) - they must work identically to before. Verify dispatching logic is under 50 lines.

### Implementation for User Story 1

- [X] T016 [P] [US1] Implement StringHandler in niceguicrud/input_handlers/string.py handling str, Path, and textarea variant
- [X] T017 [P] [US1] Implement NumericHandler in niceguicrud/input_handlers/numeric.py handling int, float, slider/number variants with min/max extraction
- [X] T018 [P] [US1] Implement BooleanHandler in niceguicrud/input_handlers/boolean.py handling bool type with ui.switch
- [X] T019 [P] [US1] Implement TemporalHandler in niceguicrud/input_handlers/temporal.py handling date, time, datetime with picker widgets
- [X] T020 [P] [US1] Implement SelectionHandler in niceguicrud/input_handlers/selection.py handling Literal, select, multiselect with options
- [X] T021 [P] [US1] Implement NestedHandler in niceguicrud/input_handlers/nested.py handling BaseModel, Union[BaseModel, ...], list[BaseModel] with edit dialogs
- [X] T022 [P] [US1] Implement CollectionHandler in niceguicrud/input_handlers/collections.py handling list[str], list[int], list[float] with comma-separated parsing
- [X] T023 [US1] Register all built-in handlers (String, Numeric, Boolean, Temporal, Selection, Nested, Collection, Fallback) in niceguicrud/input_handlers/__init__.py with priority=100
- [X] T024 [US1] Refactor NiceCRUDCard.get_input method in niceguicrud/nicecrud.py to use handler registry - create InputContext, call registry.get_handler, invoke handler.create_widget (target <50 lines)
- [X] T025 [US1] Add error handling in NiceCRUDCard.get_input for NoHandlerFoundError and handler exceptions - log warning and fall back to text input per FR-010
- [X] T026 [US1] Update niceguicrud/__init__.py exports to include input_handlers module for public API access
- [X] T027 [US1] Run minimal.py example and verify it works without modification
- [X] T028 [US1] Run validation.py example and verify it works without modification
- [X] T029 [US1] Run submodel.py example and verify it works without modification
- [X] T030 [US1] Run input_choices.py example and verify it works without modification
- [X] T031 [US1] Run database.py example and verify it works without modification
- [X] T032 [US1] Verify refactored get_input dispatching logic is under 50 lines (SC-001)
- [X] T033 [US1] Write unit tests in tests/unit/test_input_handlers.py for each handler's can_handle and create_widget methods
- [X] T034 [US1] Write integration test in tests/integration/test_handler_registry.py verifying handler registration, priority ordering, and lookup caching

**Checkpoint**: At this point, User Story 1 should be fully functional - modular handlers replace monolithic code, all examples pass

---

## Phase 4: User Story 2 - Automated UI Testing (Priority: P2)

**Goal**: Add Playwright tests to verify UI input elements render and interact correctly, catching regressions

**Independent Test**: Run Playwright test suite with `pytest tests/playwright/` - tests should pass for 90% of input types

### Implementation for User Story 2

- [X] T035 [P] [US2] Create Playwright fixtures in tests/playwright/conftest.py for launching example apps in background process
- [X] T036 [P] [US2] Implement test_minimal_example.py testing string and number inputs render, accept input, validate constraints
- [X] T037 [P] [US2] Implement test_input_choices.py testing all input types (select, multiselect, slider, textarea, date, time, datetime, Path) render and accept input
- [X] T038 [P] [US2] Implement test_validation.py testing validation errors appear, error messages display, save button disables on invalid input
- [X] T039 [US2] Add CI/CD workflow configuration in .github/workflows/ (if using GitHub Actions) or equivalent to run Playwright tests on PR and release only (not every commit per FR-007) - SKIPPED per user preference
- [X] T040 [US2] Verify Playwright test coverage is at least 90% of supported input types (SC-004) - check coverage report
- [X] T041 [US2] Document Playwright test execution in README or tests/playwright/README.md with instructions for running locally

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - modular handlers tested via automated browser tests

---

## Phase 5: User Story 3 - Extensible Input Registry (Priority: P3)

**Goal**: Enable custom handler registration for domain-specific types without forking the library

**Independent Test**: Create example custom handler (Color type with color picker), register it, verify it renders in CRUD interface and prioritizes over defaults

### Implementation for User Story 3

- [ ] T042 [P] [US3] Create examples/custom_handler_example.py with example Color type, ColorPickerHandler implementation, handler registration, and CRUD interface demo
- [ ] T043 [P] [US3] Create docs/handler_examples/01_basic_string_handler.md with complete example showing string input customization with inline explanations
- [ ] T044 [P] [US3] Create docs/handler_examples/02_custom_type_color.md with complete Color picker example including type definition, handler, registration, usage
- [ ] T045 [P] [US3] Create docs/handler_examples/03_nested_object_handler.md with complete nested BaseModel example showing dialog-based editing
- [ ] T046 [P] [US3] Create docs/handler_examples/04_validation_patterns.md with complete example showing custom validation logic in handlers
- [ ] T047 [P] [US3] Create docs/handler_examples/05_error_handling.md with complete example showing handler failure, logging, fallback behavior
- [ ] T048 [US3] Add integration test in tests/integration/test_handler_registry.py verifying custom handler priority overrides built-in handlers
- [ ] T049 [US3] Add integration test verifying custom handler failure triggers fallback to text input with logged warning
- [ ] T050 [US3] Verify documentation includes at least 5 complete runnable examples (SC-007) covering string variants, custom types, nested objects, validation, error handling
- [ ] T051 [US3] Test custom_handler_example.py runs successfully and demonstrates custom Color field with color picker widget

**Checkpoint**: All user stories should now be independently functional - custom handlers extend the system without library modification

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories, final validation

- [ ] T052 [P] Add type hints validation across all handler modules - verify mypy or pyright passes
- [ ] T053 [P] Add docstrings to all public API functions (InputHandlerProtocol, InputContext, register_custom_handler, get_registry)
- [ ] T054 [P] Update main README.md with handler system overview and link to quickstart.md
- [ ] T055 [P] Add handler extension example to README.md quick start section
- [ ] T056 Code cleanup: remove commented-out legacy get_input code from nicecrud.py if any remains
- [ ] T057 Performance regression test: Create benchmark comparing old vs new get_input rendering time for 10-20 field forms (SC-006)
- [ ] T058 Verify no performance degradation in typical usage scenarios - benchmark should show <10% difference
- [ ] T059 Run complete test suite: pytest tests/ --cov=niceguicrud to verify overall coverage
- [ ] T060 Final validation: Run all examples (minimal, validation, submodel, input_choices, database, custom_handler_example) and verify functionality
- [ ] T061 Update CHANGELOG or release notes documenting modular handler system, backward compatibility, extension API

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on US1 being complete (tests need refactored handlers)
  - User Story 3 (P3): Can start after Foundational - No strict dependency on US1/US2 but benefits from completed handler system
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (refactoring is self-contained)
- **User Story 2 (P2)**: Should start after User Story 1 - Playwright tests verify the refactored handler system
- **User Story 3 (P3)**: Can start after Foundational - Technically independent but custom handlers leverage the modular system from US1

### Within Each User Story

**User Story 1 (Refactoring)**:
- Built-in handlers (T016-T022) can run in parallel (different files)
- Handler registration (T023) depends on handlers being implemented
- get_input refactoring (T024-T025) depends on handlers and registry
- Example validation (T027-T031) depends on refactored get_input
- Tests (T033-T034) depend on implementation being complete

**User Story 2 (Playwright Tests)**:
- Playwright test files (T036-T038) can run in parallel after fixtures (T035)
- CI/CD configuration (T039) can happen in parallel with tests
- Coverage verification (T040) depends on tests being written

**User Story 3 (Extensibility)**:
- Documentation examples (T043-T047) can run in parallel (different files)
- Custom handler example (T042) can run in parallel with docs
- Integration tests (T048-T049) depend on custom handler example

### Parallel Opportunities

- All Setup tasks (T001-T007) can run in parallel - different directories/files
- Foundational tasks that don't depend on each other:
  - T008 (InputHandlerProtocol) and T009 (InputContext) can run in parallel
  - T010-T012 (HandlerRegistry, API) depend on T008-T009 being done
  - T013-T014 (FallbackHandler, logging) can run in parallel with T010-T012
- All built-in handler implementations (T016-T022) can run in parallel
- All example validations (T027-T031) can run in parallel
- All Playwright test files (T036-T038) can run in parallel
- All documentation examples (T043-T047) can run in parallel
- Polish tasks (T052-T055) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all handler implementations in parallel:
Task T016: "Implement StringHandler in niceguicrud/input_handlers/string.py"
Task T017: "Implement NumericHandler in niceguicrud/input_handlers/numeric.py"
Task T018: "Implement BooleanHandler in niceguicrud/input_handlers/boolean.py"
Task T019: "Implement TemporalHandler in niceguicrud/input_handlers/temporal.py"
Task T020: "Implement SelectionHandler in niceguicrud/input_handlers/selection.py"
Task T021: "Implement NestedHandler in niceguicrud/input_handlers/nested.py"
Task T022: "Implement CollectionHandler in niceguicrud/input_handlers/collections.py"

# After handlers complete, run example validations in parallel:
Task T027: "Run minimal.py example"
Task T028: "Run validation.py example"
Task T029: "Run submodel.py example"
Task T030: "Run input_choices.py example"
Task T031: "Run database.py example"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T015) - CRITICAL blocking phase
3. Complete Phase 3: User Story 1 (T016-T034) - Modular handler refactoring
4. **STOP and VALIDATE**: Run all examples, verify dispatching logic <50 lines, verify tests pass
5. Feature is now usable - modular handlers replace monolithic code

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Refactored handler system)
3. Add User Story 2 → Test independently → Deploy/Demo (Automated UI testing added)
4. Add User Story 3 → Test independently → Deploy/Demo (Custom handler extensibility added)
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 - Build handlers in parallel (T016-T022), then integrate (T023-T034)
   - Developer B: User Story 2 - Start preparing Playwright infrastructure, wait for US1 handlers
   - Developer C: User Story 3 - Start writing documentation examples in parallel
3. User Story 1 completes first (MVP)
4. User Story 2 completes using US1's handlers
5. User Story 3 completes demonstrating extensibility

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify examples pass after User Story 1 (SC-003)
- Verify Playwright coverage ≥90% after User Story 2 (SC-004)
- Verify 5+ documentation examples after User Story 3 (SC-007)
- Commit after each logical group or completed user story
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
