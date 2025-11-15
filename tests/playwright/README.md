# Playwright Tests for NiceCRUD

This directory contains Playwright browser tests for NiceCRUD UI components.

## Purpose

These tests verify that input handlers render correctly in the browser and accept user interactions. They provide automated regression detection for UI changes.

## Test Coverage

- **test_minimal_example.py**: Tests basic string and number inputs
- **test_validation.py**: Tests validation error display and save button state
- **test_input_choices.py**: Tests all supported input types (90%+ coverage)

## Prerequisites

**Note**: Playwright tests are optional. The core handler system works without them.

1. Install Playwright package:
   ```bash
   uv pip install playwright pytest-playwright
   ```

2. Install Playwright browser:
   ```bash
   playwright install chromium
   ```

If you don't install Playwright, you can still run all other tests:
```bash
pytest tests/ --ignore=tests/playwright
```

## Running Tests

### Run all Playwright tests:
```bash
pytest tests/playwright/ -v
```

### Run specific test file:
```bash
pytest tests/playwright/test_minimal_example.py -v
```

### Run with headed browser (visible):
```bash
pytest tests/playwright/ --headed
```

### Run with slow motion (for debugging):
```bash
pytest tests/playwright/ --slowmo 500
```

## How Tests Work

1. Each test fixture (`minimal_app`, `validation_app`, `input_choices_app`) launches the corresponding example in a background process
2. Tests navigate to `http://localhost:8080` and interact with the UI
3. After test completion, the background process is terminated
4. Tests use Playwright's `expect` API for assertions

## Test Organization

```
tests/playwright/
├── conftest.py                  # Fixtures for launching apps
├── test_minimal_example.py      # Basic input tests
├── test_validation.py           # Validation and error handling tests
├── test_input_choices.py        # Comprehensive input type coverage
└── README.md                    # This file
```

## CI/CD Integration

Per FR-007, Playwright tests should run:
- On pull requests (to catch regressions before merge)
- On releases (to verify production readiness)
- **NOT** on every commit (to avoid slow feedback loops)

To configure in GitHub Actions, see `.github/workflows/` for the Playwright test job.

## Troubleshooting

### Port already in use
If tests fail with "address already in use", ensure no other NiceGUI apps are running on port 8080:
```bash
pkill -f "python examples/"
```

### Timeout errors
If tests timeout waiting for elements:
1. Increase wait timeout: `page.wait_for_timeout(5000)`
2. Check that example app starts successfully
3. Verify network connectivity to localhost:8080

### Browser not installed
```bash
playwright install chromium
```

## Adding New Tests

1. Add fixture to `conftest.py` if testing a new example
2. Create test file following naming convention `test_<example_name>.py`
3. Use `expect()` assertions for readability
4. Clean up background processes in fixture teardown
