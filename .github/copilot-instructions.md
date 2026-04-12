# Copilot instructions for nicecrud

This file provides repository-specific guidance for GitHub Copilot/CLI sessions working on NiceCRUD.

## Quick commands

- Create dev venv and sync deps (uses uv):
  - uv venv --python 3.13
  - source .venv/bin/activate
  - uv sync

- Run tests:
  - Full (compatibility matrix): ./test-versions.sh
  - Quick: ./test-versions.sh --quick
  - Local single-Python full test run: pytest
  - Run a single test: pytest tests/path/to_file.py::TestClass::test_name
  - Run pytest with specific Python: python3.13 -m pytest

- Playwright/browser tests: pytest is configured to run headless chromium by default (see pytest.ini and pyproject.toml tool.playwright). Use ./test-versions.sh to run multi-version Playwright runs.

- Lint / format:
  - ruff check .
  - black .
  - pre-commit run --all-files

- Build / publish (packaging):
  - uv build
  - export UV_PUBLISH_TOKEN=... ; uv publish

## High-level architecture

- Purpose: a small Python library that generates a NiceGUI-based CRUD interface from pydantic models.
- Package: top-level package is `niceguicrud` (entrypoint defined in pyproject.toml). Core surface: a `NiceCRUD` class that accepts pydantic models/instances and exposes CRUD UI built on NiceGUI.
- Tests: split into `unit`, `integration`, and `playwright` tests under `tests/`. Examples under `examples/` are used both as runnable demos and as import-validation in CI.
- Tooling: uses `uv` for developer workflows, `hatchling` for packaging, `pytest`/`pytest-asyncio`/`pytest-playwright` for tests, `ruff` and `black` for linting/formatting.

## Key conventions and repo-specific notes

- Python versions: targeting Python >=3.12 (pyproject.toml lists 3.12, 3.13 compatibility; 3.14 experimental). Use `test-versions.sh` when verifying multi-Python compatibility.
- NiceGUI compatibility: tests exercise NiceGUI v2.24.x and v3.x. See TESTING.md for the exact commands to switch NiceGUI versions (uv pip install ...).
- Tests import-mode: pytest is set to `--import-mode=importlib` (pyproject.toml). Keep tests import-safe; some examples start servers on import — the import tests are designed only to verify the example modules import cleanly.
- Playwright CI: Playwright is configured via pyproject.toml and pytest.ini; CI/locally expect headless Chromium (no GUI). Use `tool.playwright.browsers` setting in pyproject.toml for changes.
- Formatting: ruff/black line-length configured to 100 in pyproject.toml.
- Packaging: build via `uv build` (requires uv); publishing requires UV_PUBLISH_TOKEN environment variable.
- CI helpers: see `.github/workflows/publish.yml` for the repository's publishing workflow.
- AI assistant files: CLAUDE.md and the `.claude/` directory contain additional project-specific assistant guidance; consult them when available.

## Where to look first when modifying code

- `niceguicrud/` — primary library code
- `examples/` — runnable usage patterns that are also validated in CI
- `tests/` — unit/integration/playwright tests reflect behavior and compatibility expectations
- `pyproject.toml` and `pytest.ini` — project toolchain and test runner configuration
