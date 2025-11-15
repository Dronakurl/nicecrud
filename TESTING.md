# Testing Guide for NiceCRUD

## Version Compatibility Testing

NiceCRUD supports multiple Python and NiceGUI versions. Use the `test-versions.sh` script to validate compatibility.

### Quick Test (Current Environment)

Test with your current Python version and dependencies:

```bash
./test-versions.sh --quick
```

This runs:
- All unit and integration tests
- All playwright tests (on Python 3.12-3.13)
- Example import validation

**Use this for**: Quick validation during development.

### Current Python, Multiple NiceGUI Versions

Test current Python with both NiceGUI v2.24.x and v3.x:

```bash
./test-versions.sh --current
```

This tests:
- NiceGUI ~=2.24.0
- NiceGUI >=3.3.0

**Use this for**: Validating NiceGUI version compatibility without changing Python.

### Full Multi-Version Test

Test all Python versions (3.12, 3.13, 3.14) + NiceGUI versions:

```bash
./test-versions.sh
```

This tests:
- Python 3.12 with both NiceGUI versions (all tests including playwright)
- Python 3.13 with both NiceGUI versions (all tests including playwright)
- Python 3.14 (experimental) with NiceGUI 3.x (playwright not supported)
- Skips tests if Python version not installed

**Use this for**: Comprehensive validation before releases.

**Requirements**:
- `pyenv` or multiple Python installations (3.12, 3.13, 3.14)
- `uv` package manager

## Manual Testing

### Test Specific Python Version

```bash
# Using pyenv
pyenv local 3.13
uv venv --python 3.13
source .venv/bin/activate
uv sync
pytest
```

### Test Specific NiceGUI Version

```bash
# Test with NiceGUI v2.24.x
uv pip install "nicegui~=2.24.0"
pytest

# Test with NiceGUI v3.x
uv pip install "nicegui>=3.3.0"
pytest

# Restore original dependencies
uv sync
```

## Supported Versions

### Python
- ✅ **3.12** - Fully supported
- ✅ **3.13** - Fully supported
- ⚠️ **3.14** - Experimental (pytest-playwright not yet supported)

### NiceGUI
- ✅ **2.24.x** - Supported
- ✅ **3.0+** - Fully supported (recommended)

### Known Limitations

- **Python 3.14**: pytest-playwright v0.7.1 does not support Python 3.14. Playwright tests are skipped on this version.
- **Deprecation warnings**: Python 3.13+ shows deprecation warnings from vbuild (used by NiceGUI). These are cosmetic and don't affect functionality.

## CI/CD Integration

For automated testing in CI/CD:

1. **Local testing script** (no external CI required):
   ```bash
   ./test-versions.sh
   ```

2. **Individual Python version** (for custom CI):
   ```bash
   python3.13 -m pytest
   ```

3. **Docker-based** (for isolated testing):
   ```bash
   docker run --rm -v $(pwd):/app -w /app python:3.13 bash -c "pip install uv && uv sync && uv run pytest"
   ```

## Troubleshooting

### "Python X.XX not found"

Install the required Python version:
```bash
pyenv install 3.13
```

### "Failed to create venv"

Ensure `uv` is installed:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Tests fail with NiceGUI v2.x

Some features may require NiceGUI v3.x. Check test output for specific errors.

### Examples timeout

Examples start a web server that may not terminate cleanly in automated tests. This is expected behavior - the import test validates the code loads correctly.
