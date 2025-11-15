<!--
  Sync Impact Report:
  - Version: NEW → 1.0.0 (initial constitution)
  - Principles established:
    1. Developer Experience First
    2. Pydantic-Native Integration
    3. Minimal Configuration
  - Templates status:
    ✅ plan-template.md: Constitution Check section ready for gates
    ✅ spec-template.md: Aligned with user-first requirements approach
    ✅ tasks-template.md: Compatible with principle-driven task organization
  - Follow-up: None required
-->

# NiceCRUD Constitution

## Core Principles

### I. Developer Experience First

**MUST deliver exceptional developer experience through:**
- Zero-configuration defaults that work out of the box
- Intuitive API that mirrors pydantic model patterns developers already know
- Clear, actionable error messages when validation fails
- Comprehensive examples covering common use cases (minimal, validation, submodels, database integration)

**Rationale**: NiceCRUD exists to eliminate boilerplate and friction. Any feature that increases cognitive load or requires excessive configuration violates the core mission. The library succeeds when developers can go from pydantic model to working CRUD UI in under 5 lines of code.

---

### II. Pydantic-Native Integration

**MUST maintain seamless pydantic integration:**
- All field metadata (constraints, descriptions, titles, defaults) automatically reflected in UI
- Validation rules enforced consistently between pydantic models and UI inputs
- Support for pydantic v2 features (Field constraints, nested models, custom validators)
- Type hints drive UI component selection (int → number input, Literal → dropdown, etc.)

**Rationale**: Pydantic is the single source of truth. Developers should never duplicate constraints, validation logic, or metadata. Breaking this principle fragments the data model and creates maintenance burden.

**Compatibility guarantee**: Minimum Python 3.12, support latest stable pydantic v2.x, track NiceGUI API changes.

---

### III. Minimal Configuration

**MUST prefer convention over configuration:**
- Sensible defaults for all UI behaviors (create, read, update, delete operations)
- Single parameter required: basemodels (list of instances)
- Optional overrides only for advanced use cases (custom update handlers, database integration)
- No global state or complex initialization sequences

**Rationale**: Complexity is the enemy of adoption. Every required parameter, every configuration option is a barrier. Users should customize through familiar patterns (subclassing, dependency injection) rather than configuration DSLs.

**Forbidden**: Mandatory configuration files, global registry patterns, framework-specific decorators that leak into user models.

---

## Development Standards

### Code Quality
- Type hints required for all public APIs
- Pydantic models must have clear field descriptions for UI rendering
- Examples must run standalone with `python examples/<name>.py`
- Breaking changes require major version bump per semantic versioning

### Testing
- All pydantic field types must have corresponding UI input examples
- Validation edge cases (min/max, regex, custom validators) must have test coverage
- Examples serve as integration tests - if an example breaks, it's a release blocker

### Documentation
- README quick start must work in under 30 seconds from `pip install`
- Each example must have comment explaining its purpose and which feature it demonstrates
- Error messages must suggest corrective action, not just report failure

---

## Governance

**Amendment process**:
1. Proposed changes must include rationale and impact assessment
2. Breaking changes to principles require demonstration that alternatives are insufficient
3. Version bump according to semantic versioning rules documented in this constitution

**Versioning policy**:
- MAJOR: Backward incompatible principle changes (e.g., dropping pydantic v1 support)
- MINOR: New principle added or expanded guidance that changes expected behavior
- PATCH: Clarifications, wording improvements, no semantic changes

**Compliance review**:
- All pull requests must verify adherence to the three core principles
- Features that require >3 parameters to basic usage must justify complexity
- Any new dependency must justify why existing tools (pydantic, NiceGUI) insufficient

**Version**: 1.0.0 | **Ratified**: 2025-11-15 | **Last Amended**: 2025-11-15
