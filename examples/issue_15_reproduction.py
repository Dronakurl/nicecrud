"""Example to reproduce issue #15: Optional nested model."""

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


instance1 = MyModel(
    id=1, name="Alice", age=30, address_1=Address(street="123 Main St", city="Anytown", zip_code="12345")
)


def crud_page():
    """Full CRUD interface on a dedicated page."""
    with ui.column().classes("w-full items-center"):
        ui.label("User CRUD Manager").classes("text-2xl mb-4")

        # Full NiceCRUD interface
        NiceCRUDCard(instance1)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(root=crud_page, title="Issue #15 - Optional Nested Model")
