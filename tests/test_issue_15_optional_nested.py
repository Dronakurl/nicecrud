"""Test for issue #15: Optional nested model support."""

import pytest
from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUDCard


class Address(BaseModel):
    """Address model."""
    street: str = Field(title="Street")
    city: str = Field(title="City")
    zip_code: str = Field(title="ZIP Code")


class MyModel(BaseModel, title="User"):
    """User model with optional nested address."""
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")
    address_1: Address = Field(title="Address")
    address_2: Address | None = None


def test_optional_nested_model_none_value():
    """Test that optional nested models with None values don't crash."""
    instance = MyModel(
        id=1,
        name="Alice",
        age=30,
        address_1=Address(street="123 Main St", city="Anytown", zip_code="12345")
    )

    # This should not raise an AttributeError
    card = NiceCRUDCard(instance, heading="User Management")
    assert card is not None
    assert card.item == instance


def test_optional_nested_model_with_value():
    """Test that optional nested models with values work correctly."""
    instance = MyModel(
        id=1,
        name="Alice",
        age=30,
        address_1=Address(street="123 Main St", city="Anytown", zip_code="12345"),
        address_2=Address(street="456 Oak Ave", city="Sometown", zip_code="67890")
    )

    # This should work fine
    card = NiceCRUDCard(instance, heading="User Management")
    assert card is not None
    assert card.item == instance
    assert card.item.address_2 is not None


def test_optional_nested_model_ui_render():
    """Test that UI rendering works with optional nested models."""
    instance = MyModel(
        id=1,
        name="Alice",
        age=30,
        address_1=Address(street="123 Main St", city="Anytown", zip_code="12345")
        # address_2 is None by default
    )

    # Create the card - this should not crash during UI creation
    card = NiceCRUDCard(instance, heading="User Management")
    assert card is not None

    # The card should be able to create its UI without errors
    # (This tests the get_input method that was failing in the original issue)
    # Note: We can't fully test UI rendering without a NiceGUI app context,
    # but the fact that the card was created without crashing is a good sign


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
