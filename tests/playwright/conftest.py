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
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    print(f"\n🔧 Starting minimal.py server...")

    # Start the app - DON'T capture output since NiceGUI doesn't write to stdout/stderr when redirected
    # Write output to a temporary file instead
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as log_file:
        log_path = log_file.name

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,  # Still capture to prevent terminal spam
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    # Wait for server to be ready by checking port availability
    import socket
    max_wait = 10
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            raise RuntimeError(f"Server process died unexpectedly")

        try:
            with socket.create_connection(("localhost", 8080), timeout=1) as sock:
                print(f"✅ Server is listening on port 8080")
                break
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError(f"Server did not start within {max_wait} seconds")

    # Yield the URL
    yield "http://localhost:8080"

    # Cleanup: kill the process
    print(f"🛑 Stopping server...")
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
        print(f"✅ Server stopped")
    except:
        proc.kill()
        print(f"⚠️  Server killed forcefully")


@pytest.fixture(scope="function")
def validation_app(repo_root):
    """Launch validation.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "validation.py"

    env = os.environ.copy()
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    print(f"\n🔧 Starting validation.py server...")

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    # Wait for server to be ready by checking port availability
    import socket
    max_wait = 10
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            raise RuntimeError(f"Server process died unexpectedly")

        try:
            with socket.create_connection(("localhost", 8080), timeout=1) as sock:
                print(f"✅ Server is listening on port 8080")
                break
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError(f"Server did not start within {max_wait} seconds")

    yield "http://localhost:8080"

    print(f"🛑 Stopping server...")
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
        print(f"✅ Server stopped")
    except:
        proc.kill()
        print(f"⚠️  Server killed forcefully")


@pytest.fixture(scope="function")
def input_choices_app(repo_root):
    """Launch input_choices.py example in background, yield URL, then cleanup."""
    example_path = repo_root / "examples" / "input_choices.py"

    env = os.environ.copy()
    env.pop('PYTEST_CURRENT_TEST', None)
    for key in list(env.keys()):
        if key.startswith('PYTEST_'):
            env.pop(key, None)

    print(f"\n🔧 Starting input_choices.py server...")

    proc = subprocess.Popen(
        [sys.executable, str(example_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=str(repo_root),
        env=env
    )

    # Wait for server to be ready by checking port availability
    import socket
    max_wait = 10
    start_time = time.time()

    while time.time() - start_time < max_wait:
        if proc.poll() is not None:
            raise RuntimeError(f"Server process died unexpectedly")

        try:
            with socket.create_connection(("localhost", 8080), timeout=1) as sock:
                print(f"✅ Server is listening on port 8080")
                break
        except (ConnectionRefusedError, socket.timeout):
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError(f"Server did not start within {max_wait} seconds")

    yield "http://localhost:8080"

    print(f"🛑 Stopping server...")
    try:
        proc.send_signal(signal.SIGTERM)
        proc.wait(timeout=5)
        print(f"✅ Server stopped")
    except:
        proc.kill()
        print(f"⚠️  Server killed forcefully")
