"""Playwright test for issue #15: Optional nested model UI rendering."""

import pytest
from playwright.sync_api import Page, expect


def test_issue_15_page_loads(page: Page, issue_15_app):
    """Test that the page loads without AttributeError for optional nested models."""
    page.goto(issue_15_app)

    # Check that the page loaded successfully (no AttributeError crash)
    expect(page).to_have_title("Issue #15 - Optional Nested Model")


def test_issue_15_user_interface_displays(page: Page, issue_15_app):
    """Test that the user interface displays correctly with optional nested model."""
    page.goto(issue_15_app)

    # Should show the heading
    expect(page.locator("text=User CRUD Manager")).to_be_visible()

    # The main goal is that the page loads without crashing
    # The user data should be somewhere in the interface
    # (Testing exact UI text is fragile, focus on functionality)


def test_issue_15_no_crash_on_none_optional_field(page: Page, issue_15_app):
    """Test that having a None optional field doesn't crash the UI."""
    page.goto(issue_15_app)

    # The main test is that the page loads at all
    # Before the fix, this would crash with AttributeError
    expect(page).to_have_title("Issue #15 - Optional Nested Model")

    # Verify the page content is visible
    expect(page.locator("text=User CRUD Manager")).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
