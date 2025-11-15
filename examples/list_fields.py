"""Example: Using improved list field handling in NiceCRUD.

This example demonstrates the enhanced UI for list fields (str, int, float)
with add/remove buttons for each item.
"""

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD


class ShoppingList(BaseModel):
    id: int = Field(title="List ID")
    name: str = Field(title="List Name")
    items: list[str] = Field(
        title="Items",
        default_factory=list,
    )
    quantities: list[int] = Field(
        title="Quantities",
        default_factory=list,
    )
    prices: list[float] = Field(
        title="Prices ($)",
        default_factory=list,
    )


# Sample data
shopping_lists = [
    ShoppingList(
        id=1,
        name="Groceries",
        items=["Milk", "Bread", "Eggs", "Cheese"],
        quantities=[1, 2, 12, 1],
        prices=[3.99, 2.49, 4.99, 5.99],
    ),
    ShoppingList(
        id=2,
        name="Hardware Store",
        items=["Screws", "Nails", "Hammer"],
        quantities=[50, 100, 1],
        prices=[5.99, 3.99, 15.99],
    ),
]


@ui.page("/")
def main_page():
    with ui.column().classes("w-full items-center p-4"):
        ui.label("Shopping List Manager").classes("text-3xl mb-4")

        ui.markdown("""
        This example demonstrates **improved list field handling**.

        Each list field (strings, integers, floats) now has:
        - Individual input for each item
        - Delete button for each item
        - Add button to add new items

        Click "Add new item" or "Edit" to see the enhanced list UI!
        """).classes("mb-4")

        NiceCRUD(
            basemodeltype=ShoppingList,
            basemodels=shopping_lists,
            id_field="id",
            heading="Shopping Lists",
        )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="List Fields Example")
