"""Shared pytest configuration."""


def pytest_collection_modifyitems(config, items):
    """Run Playwright tests last.

    Playwright's sync API leaves an event loop running in the main thread, which breaks
    asyncio-based tests that are executed afterwards ("Runner.run() cannot be called from a
    running event loop").
    """
    items.sort(key=lambda item: "playwright" in item.nodeid.split("::")[0])
