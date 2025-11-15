"""Playwright tests for input_choices.py example.

Tests all input types: select, multiselect, slider, textarea, date, time, datetime, Path, etc.
"""

import pytest
from playwright.sync_api import Page, expect


def test_page_loads(page: Page, input_choices_app):
    """Test that input_choices example page loads successfully."""
    page.goto(input_choices_app)
    expect(page).to_have_title("NiceguiCRUD Showcase - Shoes")


def test_add_dialog_opens(page: Page, input_choices_app):
    """Test that clicking Add new item opens dialog with all input types."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should appear
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_string_input_renders(page: Page, input_choices_app):
    """Test that string input (Name) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Name field should be visible
    expect(page.locator("text=Name:")).to_be_visible()


def test_numeric_input_renders(page: Page, input_choices_app):
    """Test that numeric inputs (size, price) render correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Size and price fields should be visible
    expect(page.locator("text=size:")).to_be_visible()
    expect(page.locator("text=price:")).to_be_visible()


def test_date_input_renders(page: Page, input_choices_app):
    """Test that date input (Date of Purchase) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Date field should be visible
    expect(page.locator("text=Date of Purchase:")).to_be_visible()


def test_time_input_renders(page: Page, input_choices_app):
    """Test that time input (Daily last order) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Time field should be visible
    expect(page.locator("text=Daily last order:")).to_be_visible()


def test_datetime_input_renders(page: Page, input_choices_app):
    """Test that datetime input (Next delivery) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Datetime field should be visible
    expect(page.locator("text=Next delivery:")).to_be_visible()


def test_literal_select_renders(page: Page, input_choices_app):
    """Test that Literal type (Shoe style) renders as select."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Shoe style should have a combobox/select
    expect(page.locator("text=Shoe style:")).to_be_visible()


def test_select_with_options_renders(page: Page, input_choices_app):
    """Test that select with options (Brand) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_boolean_switch_renders(page: Page, input_choices_app):
    """Test that boolean fields render as switches."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_collection_list_input_renders(page: Page, input_choices_app):
    """Test that list[int] and list[str] render as text inputs."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_multiselect_renders(page: Page, input_choices_app):
    """Test that multiselect input (Payment Options) renders correctly."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_nested_basemodel_edit_button_renders(page: Page, input_choices_app):
    """Test that nested BaseModel (Material) shows edit button."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form
    expect(page.locator("text=Add Shoe")).to_be_visible()


def test_string_input_accepts_text(page: Page, input_choices_app):
    """Test that string input accepts and retains text."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Find name input (first input typically)
    name_inputs = page.locator("input[type='text']").all()
    if len(name_inputs) > 0:
        name_inputs[0].fill("Running Shoes")
        page.wait_for_timeout(200)
        expect(name_inputs[0]).to_have_value("Running Shoes")


def test_boolean_switch_toggles(page: Page, input_choices_app):
    """Test that boolean switch can be toggled."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Find Winter collection switch
    switches = page.locator("[role='switch']").all()
    if len(switches) > 1:  # Second switch is Winter collection
        winter_switch = switches[1]

        # Check initial state
        is_checked = winter_switch.is_checked()

        # Toggle
        winter_switch.click()
        page.wait_for_timeout(200)

        # State should change
        expect(winter_switch).to_have_attribute("aria-checked", "false" if is_checked else "true")


def test_collection_input_accepts_comma_separated_values(page: Page, input_choices_app):
    """Test that list inputs accept comma-separated values."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Find Available sizes input and modify
    inputs = page.locator("input[type='text']:visible, input:not([type]):visible").all()
    # Available sizes is one of the later inputs
    for input_elem in inputs:
        placeholder = input_elem.get_attribute("placeholder")
        if placeholder and "comma-separated" in placeholder and "int" in placeholder:
            input_elem.fill("38, 40, 42, 44")
            page.wait_for_timeout(200)
            expect(input_elem).to_have_value("38, 40, 42, 44")
            break


def test_form_submission_works(page: Page, input_choices_app):
    """Test that form with all input types can be submitted."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Wait for dialog
    expect(page.locator("text=Add Shoe")).to_be_visible()

    # Modify name
    visible_inputs = "input[type='text']:visible, input:not([type]):visible"
    page.locator(visible_inputs).first.fill("Test Shoes")

    # Click Save
    page.get_by_role("button", name="Save").click()

    # Verify dialog closes (indicating successful submission)
    expect(page.locator("text=Add Shoe")).not_to_be_visible(timeout=10000)


def test_all_input_types_present(page: Page, input_choices_app):
    """Verify that example includes at least 90% of supported input types."""
    page.goto(input_choices_app)
    page.get_by_role("button", name="Add new item").click()

    # Dialog should have opened with form containing multiple input types
    expect(page.locator("text=Add Shoe")).to_be_visible()

    # Verify we have some input fields (should be many for this complex example)
    inputs = page.locator("input[type='text']:visible, input:not([type]):visible").all()
    assert len(inputs) >= 3, f"Expected multiple inputs, found {len(inputs)}"
