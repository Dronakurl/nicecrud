"""Playwright test fixtures for NiceCRUD examples.

Provides fixtures for launching example apps in background and managing browser contexts.
"""

import pytest
import subprocess
import time
import signal
import sys
import os
from pathlib import Path


@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Configure browser launch args for headless mode - FORCE headless, NEVER use user profile."""
    # Return a completely clean config without inheriting anything
    return {
        "headless": True,
        "args": [
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ],
    }


@pytest.fixture(scope="session")
def repo_root():
    """Get repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="function")
def minimal_app(repo_root):
    """Launch minimal.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "minimal.py"

    # Create clean environment without pytest markers
    env = os.environ.copy()
    # Remove pytest-related environment variables
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    # Start the app in background
    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    # Wait for server to start
    time.sleep(5)

    # Check if process is still running
    if proc.poll() is not None:
        output = proc.stdout.read().decode() if proc.stdout else ""
        raise RuntimeError(f"Example app failed to start. Output: {output}")

    # Yield the URL
    yield "http://localhost:8080"

    # Cleanup: kill the process
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
    except:
        proc.kill()


@pytest.fixture(scope="function")
def validation_app(repo_root):
    """Launch validation.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "validation.py"

    env = os.environ.copy()
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    time.sleep(5)

    if proc.poll() is not None:
        output = proc.stdout.read().decode() if proc.stdout else ""
        raise RuntimeError(f"Validation app failed to start. Output: {output}")

    yield "http://localhost:8080"

    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
    except:
        proc.kill()


@pytest.fixture(scope="function")
def input_choices_app(repo_root):
    """Launch input_choices.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "input_choices.py"

    env = os.environ.copy()
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    time.sleep(5)

    if proc.poll() is not None:
        output = proc.stdout.read().decode() if proc.stdout else ""
        raise RuntimeError(f"Input choices app failed to start. Output: {output}")

    yield "http://localhost:8080"

    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
    except:
        proc.kill()
