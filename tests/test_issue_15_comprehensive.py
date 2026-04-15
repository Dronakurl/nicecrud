"""Comprehensive test for issue #15: Optional nested model support with UI testing."""

import pytest
from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUDCard


class Address(BaseModel):
    """Address model."""
    street: str = Field(title="Street")
    city: str = Field(title="City")
    zip_code: str = Field(title="ZIP Code")


class UserWithOptionalAddress(BaseModel, title="User"):
    """User model with optional nested address - exact model from issue #15."""
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")
    address_1: Address = Field(title="Address")
    address_2: Address | None = None


def test_issue_15_exact_reproduction():
    """Test the exact scenario from issue #15 - optional nested model with None value."""
    instance = UserWithOptionalAddress(
        id=1,
        name="Alice",
        age=30,
        address_1=Address(street="123 Main St", city="Anytown", zip_code="12345")
        # address_2 is None by default - this was causing AttributeError
    )

    # This should not raise AttributeError: 'NoneType' object has no attribute 'model_dump'
    card = NiceCRUDCard(instance, heading="User Management")
    assert card is not None
    assert card.item.address_2 is None


def test_optional_address_with_value():
    """Test optional nested model when it has a value."""
    instance = UserWithOptionalAddress(
        id=1,
        name="Alice",
        age=30,
        address_1=Address(street="123 Main St", city="Anytown", zip_code="12345"),
        address_2=Address(street="456 Oak Ave", city="Sometown", zip_code="67890")
    )

    card = NiceCRUDCard(instance, heading="User Management")
    assert card is not None
    assert card.item.address_2 is not None
    assert card.item.address_2.street == "456 Oak Ave"


def test_multiple_optional_fields():
    """Test model with multiple optional nested models."""
    class ExtendedUser(BaseModel, title="Extended User"):
        id: int
        name: str
        work_address: Address | None = None
        home_address: Address | None = None
        other_address: Address | None = None

    instance = ExtendedUser(
        id=1,
        name="Bob",
        work_address=Address(street="123 Work St", city="Worktown", zip_code="11111")
        # home_address and other_address are None
    )

    card = NiceCRUDCard(instance, heading="Extended User")
    assert card is not None
    assert card.item.work_address is not None
    assert card.item.home_address is None
    assert card.item.other_address is None


def test_all_optional_fields_none():
    """Test model where all optional nested fields are None."""
    class UserWithAllOptionals(BaseModel):
        id: int
        name: str
        primary_address: Address | None = None
        secondary_address: Address | None = None

    instance = UserWithAllOptionals(
        id=1,
        name="Charlie"
        # All optional addresses are None
    )

    card = NiceCRUDCard(instance, heading="All Optionals User")
    assert card is not None
    assert card.item.primary_address is None
    assert card.item.secondary_address is None


def test_deeply_nested_optional_models():
    """Test deeply nested optional models."""
    class ContactInfo(BaseModel):
        email: str
        phone: str | None = None

    class Person(BaseModel):
        name: str
        contact: ContactInfo | None = None

    class Company(BaseModel):
        name: str
        ceo: Person | None = None

    instance = Company(
        name="Test Company",
        ceo=None  # This was causing the error
    )

    card = NiceCRUDCard(instance, heading="Company")
    assert card is not None
    assert card.item.ceo is None


def test_optional_model_list_with_none_items():
    """Test that lists containing None values are handled correctly."""
    class ModelWithOptionalList(BaseModel):
        id: int
        addresses: list[Address | None] = []

    instance = ModelWithOptionalList(
        id=1,
        addresses=[
            Address(street="123 Main St", city="Anytown", zip_code="12345"),
            None,  # This None in a list could also cause issues
            Address(street="456 Oak Ave", city="Sometown", zip_code="67890")
        ]
    )

    card = NiceCRUDCard(instance, heading="Model With Optional List")
    assert card is not None
    assert len(card.item.addresses) == 3
    assert card.item.addresses[1] is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
