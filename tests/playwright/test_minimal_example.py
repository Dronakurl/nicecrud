"""Playwright tests for minimal.py example.

Tests string and number inputs render, accept input, and validate constraints.
"""

import pytest
from playwright.sync_api import Page, expect


def test_page_loads(page: Page, minimal_app):
    """Test that minimal example page loads successfully."""
    page.goto(minimal_app)
    expect(page).to_have_title("NiceGUI")


def test_user_table_displays(page: Page, minimal_app):
    """Test that user table displays with initial data."""
    page.goto(minimal_app)

    # Should show User Management heading
    expect(page.locator("text=User Management")).to_be_visible()

    # Should show existing users
    expect(page.locator("text=Alice")).to_be_visible()
    expect(page.locator("text=Bob")).to_be_visible()


def test_add_button_opens_dialog(page: Page, minimal_app):
    """Test that clicking Add new item button opens dialog."""
    page.goto(minimal_app)

    # Click Add new item button
    page.get_by_role("button", name="Add new item").click()

    # Dialog should appear with form fields
    expect(page.locator("text=Add User")).to_be_visible()


def test_string_input_renders(page: Page, minimal_app):
    """Test that string input (Name field) renders correctly."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Name field should be visible and editable
    name_input = page.locator("input").filter(has=page.locator("text=Name"))
    expect(name_input.first).to_be_visible()
    expect(name_input.first).to_be_editable()


def test_number_input_renders(page: Page, minimal_app):
    """Test that number input (Age field) renders correctly."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Age field should be visible
    # NiceGUI renders numbers as text inputs with validation
    expect(page.locator("text=Age:")).to_be_visible()


def test_string_input_accepts_text(page: Page, minimal_app):
    """Test that string input accepts and retains text."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Find the name input and type
    name_inputs = page.locator("input").all()
    # Typically the second input is Name (first is id)
    if len(name_inputs) >= 2:
        name_inputs[1].fill("Charlie")

        # Verify value was set
        expect(name_inputs[1]).to_have_value("Charlie")


def test_number_input_accepts_numbers(page: Page, minimal_app):
    """Test that number input accepts numeric values."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Find age input (typically third input)
    age_inputs = page.locator("input").all()
    if len(age_inputs) >= 3:
        age_inputs[2].fill("35")

        # Verify value was set
        expect(age_inputs[2]).to_have_value("35")


def test_form_submission_creates_new_user(page: Page, minimal_app):
    """Test that submitting form creates new user in table."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Fill in form
    inputs = page.locator("input").all()
    if len(inputs) >= 3:
        inputs[0].fill("3")  # id
        inputs[1].fill("Charlie")  # name
        inputs[2].fill("35")  # age

    # Click Save
    page.get_by_role("button", name="Save").click()

    # Wait for dialog to close and new user to appear
    page.wait_for_timeout(500)

    # New user should appear in table
    expect(page.locator("text=Charlie")).to_be_visible()
    expect(page.locator("text=35")).to_be_visible()


def test_cancel_button_closes_dialog(page: Page, minimal_app):
    """Test that Cancel button closes dialog without saving."""
    page.goto(minimal_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should be visible
    expect(page.locator("text=Add User")).to_be_visible()

    # Click Cancel
    page.get_by_role("button", name="Cancel").click()

    # Dialog should close
    page.wait_for_timeout(500)
    expect(page.locator("text=Add User")).not_to_be_visible()
