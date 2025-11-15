"""Playwright test fixtures for NiceCRUD examples.

Provides fixtures for launching example apps in background and managing browser contexts.
"""

import pytest
import subprocess
import time
import signal
import sys
from pathlib import Path


@pytest.fixture(scope="session")
def repo_root():
    """Get repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="function")
def minimal_app(repo_root):
    """Launch minimal.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "minimal.py"

    # Start the app in background
    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(repo_root)
    )

    # Wait for server to start
    time.sleep(3)

    # Yield the URL
    yield "http://localhost:8080"

    # Cleanup: kill the process
    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)


@pytest.fixture(scope="function")
def validation_app(repo_root):
    """Launch validation.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "validation.py"

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(repo_root)
    )

    time.sleep(3)
    yield "http://localhost:8080"

    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)


@pytest.fixture(scope="function")
def input_choices_app(repo_root):
    """Launch input_choices.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "input_choices.py"

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(repo_root)
    )

    time.sleep(3)
    yield "http://localhost:8080"

    proc.send_signal(signal.SIGTERM)
    proc.wait(timeout=5)
