"""Playwright tests for validation.py example.

Tests validation errors appear, error messages display, and save button disables on invalid input.
"""

import pytest
from playwright.sync_api import Page, expect


def test_page_loads(page: Page, validation_app):
    """Test that validation example page loads successfully."""
    page.goto(validation_app)
    expect(page).to_have_title("NiceGUI")


def test_character_table_displays(page: Page, validation_app):
    """Test that character table displays with initial data."""
    page.goto(validation_app)

    # Should show Character Database heading
    expect(page.locator("text=Character Database")).to_be_visible()

    # Should show existing characters
    expect(page.locator("text=Gandalf")).to_be_visible()
    expect(page.locator("text=Frodo")).to_be_visible()


def test_add_dialog_opens(page: Page, validation_app):
    """Test that clicking Add new item opens dialog."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should appear
    expect(page.locator("text=Add D&D Character")).to_be_visible()


def test_validation_constraint_enforced(page: Page, validation_app):
    """Test that magic level validation (le=100) is enforced."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Find magic level input and enter invalid value (>100)
    inputs = page.locator("input").all()
    # Magic Level is typically the 3rd input (id, name, magic_level)
    if len(inputs) >= 3:
        magic_input = inputs[2]
        magic_input.fill("150")

        # Wait for validation
        page.wait_for_timeout(300)

        # Error message should appear
        expect(page.locator("text=Input should be less than 101")).to_be_visible()


def test_save_button_disabled_on_invalid_input(page: Page, validation_app):
    """Test that Save button is disabled when validation fails."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Enter invalid magic level
    inputs = page.locator("input").all()
    if len(inputs) >= 3:
        inputs[2].fill("150")

    # Wait for validation
    page.wait_for_timeout(300)

    # Save button should be disabled
    save_button = page.get_by_role("button", name="Save")
    expect(save_button).to_be_disabled()


def test_save_button_enabled_on_valid_input(page: Page, validation_app):
    """Test that Save button is enabled when input is valid."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Initially save button should be enabled (default values are valid)
    save_button = page.get_by_role("button", name="Save")
    expect(save_button).to_be_enabled()


def test_literal_select_renders(page: Page, validation_app):
    """Test that Literal type (Species) renders as select dropdown."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Species field should have a dropdown/combobox
    expect(page.locator("text=Species:")).to_be_visible()


def test_validation_error_clears_on_fix(page: Page, validation_app):
    """Test that validation error clears when input is corrected."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    inputs = page.locator("input").all()
    if len(inputs) >= 3:
        magic_input = inputs[2]

        # Enter invalid value
        magic_input.fill("150")
        page.wait_for_timeout(300)

        # Error should be visible
        expect(page.locator("text=Input should be less than 101")).to_be_visible()

        # Fix the value
        magic_input.fill("95")
        page.wait_for_timeout(300)

        # Error should disappear
        expect(page.locator("text=Input should be less than 101")).not_to_be_visible()


def test_form_with_valid_data_submits(page: Page, validation_app):
    """Test that form with all valid data can be submitted."""
    page.goto(validation_app)
    page.get_by_role("button", name="Add new item").click()

    # Fill with valid data
    inputs = page.locator("input").all()
    if len(inputs) >= 3:
        inputs[0].fill("3")
        inputs[1].fill("Aragorn")
        inputs[2].fill("85")

    # Click Save
    page.get_by_role("button", name="Save").click()

    # Wait for submission
    page.wait_for_timeout(500)

    # New character should appear
    expect(page.locator("text=Aragorn")).to_be_visible()
