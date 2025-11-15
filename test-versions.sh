#!/bin/bash
# Multi-version compatibility testing script for NiceCRUD
# Tests Python 3.12, 3.13, 3.14 with different NiceGUI versions
#
# Usage:
#   ./test-versions.sh           # Test all Python versions + NiceGUI versions
#   ./test-versions.sh --current # Test only current Python version with different NiceGUI versions
#   ./test-versions.sh --quick   # Quick test with current Python and current NiceGUI

set -e  # Exit on error

# Parse arguments
TEST_MODE="all"
if [[ "$1" == "--current" ]]; then
    TEST_MODE="current"
elif [[ "$1" == "--quick" ]]; then
    TEST_MODE="quick"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0
SKIPPED=0

echo "========================================"
echo "NiceCRUD Version Compatibility Test"
echo "========================================"
echo ""

# Function to test a specific Python version
test_python_version() {
    local python_version=$1
    local python_cmd="python${python_version}"

    echo -e "${YELLOW}Testing Python ${python_version}...${NC}"

    # Check if Python version is available
    if ! command -v "$python_cmd" &> /dev/null; then
        echo -e "${YELLOW}  Python ${python_version} not found - SKIPPED${NC}"
        SKIPPED=$((SKIPPED + 1))
        return
    fi

    # Verify Python version
    ACTUAL_VERSION=$($python_cmd --version 2>&1 | grep -oP '[\d.]+' | head -1)
    echo "  Found: Python ${ACTUAL_VERSION}"

    # Create temporary venv
    VENV_DIR=".venv-test-${python_version}"
    echo "  Creating test environment: ${VENV_DIR}"

    # Clean up old venv if exists
    rm -rf "$VENV_DIR"

    # Create venv using uv
    if ! uv venv "$VENV_DIR" --python "$python_cmd" > /dev/null 2>&1; then
        echo -e "${RED}  Failed to create venv - FAILED${NC}"
        FAILED=$((FAILED + 1))
        return
    fi

    # Activate venv and install
    source "$VENV_DIR/bin/activate"

    echo "  Installing dependencies..."
    if ! uv pip install -e . > /dev/null 2>&1; then
        echo -e "${RED}  Failed to install dependencies - FAILED${NC}"
        FAILED=$((FAILED + 1))
        deactivate
        rm -rf "$VENV_DIR"
        return
    fi

    # Install test dependencies
    if [[ "$python_version" == "3.14" ]]; then
        # Python 3.14: pytest-playwright not supported
        if ! uv pip install pytest pytest-asyncio > /dev/null 2>&1; then
            echo -e "${RED}  Failed to install test dependencies - FAILED${NC}"
            FAILED=$((FAILED + 1))
            deactivate
            rm -rf "$VENV_DIR"
            return
        fi

        # Run tests without playwright
        echo "  Running tests (playwright not supported on 3.14)..."
        if pytest --ignore=tests/playwright -q > /dev/null 2>&1; then
            echo -e "${GREEN}  Tests PASSED${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}  Tests FAILED${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        # Python 3.12, 3.13: Install all test dependencies including playwright
        if ! uv pip install pytest pytest-asyncio playwright pytest-playwright > /dev/null 2>&1; then
            echo -e "${RED}  Failed to install test dependencies - FAILED${NC}"
            FAILED=$((FAILED + 1))
            deactivate
            rm -rf "$VENV_DIR"
            return
        fi

        # Install playwright browsers
        echo "  Installing playwright browsers..."
        if ! python -m playwright install chromium > /dev/null 2>&1; then
            echo -e "${YELLOW}  Playwright browser install warning - continuing${NC}"
        fi

        # Run all tests including playwright
        echo "  Running all tests (including playwright)..."
        if pytest -q > /dev/null 2>&1; then
            echo -e "${GREEN}  All tests PASSED${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}  Tests FAILED${NC}"
            FAILED=$((FAILED + 1))
        fi
    fi

    # Test example imports
    echo "  Testing examples..."
    if timeout 5 python -c "import sys; sys.path.insert(0, 'examples'); import minimal" > /dev/null 2>&1; then
        echo -e "${GREEN}  Examples import PASSED${NC}"
    else
        echo -e "${YELLOW}  Examples import WARNING (timeout or error)${NC}"
    fi

    # Cleanup
    deactivate
    rm -rf "$VENV_DIR"
    echo ""
}

# Function to test different NiceGUI versions
test_nicegui_version() {
    local nicegui_constraint=$1
    local description=$2

    echo -e "${YELLOW}Testing with NiceGUI ${description}...${NC}"

    # Use current venv
    if ! uv pip install "nicegui${nicegui_constraint}" > /dev/null 2>&1; then
        echo -e "${RED}  Failed to install NiceGUI ${description} - FAILED${NC}"
        FAILED=$((FAILED + 1))
        return
    fi

    echo "  Running tests..."
    # Check Python version
    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '[\d.]+' | head -1 | cut -d. -f1,2)
    if [[ "$PYTHON_VERSION" == "3.14" ]]; then
        if pytest --ignore=tests/playwright -q > /dev/null 2>&1; then
            echo -e "${GREEN}  Tests PASSED with NiceGUI ${description}${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}  Tests FAILED with NiceGUI ${description}${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        if pytest -q > /dev/null 2>&1; then
            echo -e "${GREEN}  All tests PASSED with NiceGUI ${description}${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}  Tests FAILED with NiceGUI ${description}${NC}"
            FAILED=$((FAILED + 1))
        fi
    fi
    echo ""
}

# Main test execution
if [[ "$TEST_MODE" == "all" ]]; then
    echo "=== Python Version Tests ==="
    echo ""

    # Test Python 3.12
    test_python_version "3.12"

    # Test Python 3.13
    test_python_version "3.13"

    # Test Python 3.14 (experimental)
    echo -e "${YELLOW}Python 3.14 (experimental - pytest-playwright not supported)${NC}"
    test_python_version "3.14"
fi

if [[ "$TEST_MODE" != "quick" ]]; then
    echo ""
    echo "=== NiceGUI Version Tests (current Python) ==="
    echo ""

    # Ensure we're in a venv
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating default venv..."
        source .venv/bin/activate
    fi

    # Test with NiceGUI v2.24.x
    test_nicegui_version "~=2.24.0" "v2.24.x"

    # Test with NiceGUI v3.x (latest)
    test_nicegui_version ">=3.3.0" "v3.x (latest)"

    # Restore original NiceGUI version
    echo "Restoring dependencies..."
    uv sync > /dev/null 2>&1
else
    # Quick mode: just run tests with current setup
    echo ""
    echo "=== Quick Test (current Python + current dependencies) ==="
    echo ""

    # Ensure we're in a venv
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating default venv..."
        source .venv/bin/activate
    fi

    PYTHON_VERSION=$(python --version 2>&1 | grep -oP '[\d.]+' | head -1)
    echo "Python version: $PYTHON_VERSION"

    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f1,2)

    echo "Running tests..."
    if [[ "$PYTHON_MINOR" == "3.14" ]]; then
        if pytest --ignore=tests/playwright -q; then
            echo -e "${GREEN}Tests PASSED (playwright not supported on 3.14)${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}Tests FAILED${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        if pytest -q; then
            echo -e "${GREEN}All tests PASSED (including playwright)${NC}"
            PASSED=$((PASSED + 1))
        else
            echo -e "${RED}Tests FAILED${NC}"
            FAILED=$((FAILED + 1))
        fi
    fi

    echo "Testing examples..."
    if timeout 5 python -c "import sys; sys.path.insert(0, 'examples'); import minimal" > /dev/null 2>&1; then
        echo -e "${GREEN}Examples import PASSED${NC}"
    else
        echo -e "${YELLOW}Examples import WARNING${NC}"
    fi
fi

echo ""
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "Passed:  ${GREEN}${PASSED}${NC}"
echo -e "Failed:  ${RED}${FAILED}${NC}"
echo -e "Skipped: ${YELLOW}${SKIPPED}${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All available tests passed!${NC}"
    exit 0
fi
