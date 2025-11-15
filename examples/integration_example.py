"""Example: Integrating NiceCRUD into an existing NiceGUI app.

This example demonstrates:
1. Using NiceCRUD on a specific page (not the main app)
2. Custom table with onclick action to edit entries
3. Navigation between pages
"""

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD, NiceCRUDCard


class Product(BaseModel):
    id: int = Field(title="Product ID")
    name: str = Field(title="Product Name")
    price: float = Field(gt=0, title="Price ($)")
    in_stock: bool = Field(default=True, title="In Stock")


# Sample data
products = [
    Product(id=1, name="Laptop", price=999.99, in_stock=True),
    Product(id=2, name="Mouse", price=29.99, in_stock=True),
    Product(id=3, name="Keyboard", price=79.99, in_stock=False),
]


@ui.page("/")
def home_page():
    """Home page with custom table and edit buttons."""
    with ui.column().classes("w-full items-center"):
        ui.label("Product Catalog").classes("text-3xl mb-4")

        # Custom table with onclick navigation
        with ui.card().classes("w-full max-w-4xl"):
            ui.label("Click a row to edit").classes("text-sm text-gray-500 mb-2")

            columns = [
                {"name": "id", "label": "ID", "field": "id"},
                {"name": "name", "label": "Name", "field": "name"},
                {"name": "price", "label": "Price", "field": "price"},
                {"name": "in_stock", "label": "In Stock", "field": "in_stock"},
            ]

            rows = [
                {
                    "id": p.id,
                    "name": p.name,
                    "price": f"${p.price:.2f}",
                    "in_stock": "✓" if p.in_stock else "✗",
                }
                for p in products
            ]

            table = ui.table(columns=columns, rows=rows, row_key="id")

            # Navigate to edit page on row click
            table.on(
                "rowClick",
                lambda e: ui.navigate.to(f"/edit/{e.args[1]['id']}"),
            )

        # Link to full CRUD page
        with ui.row().classes("mt-4"):
            ui.button("Go to Full CRUD Manager", on_click=lambda: ui.navigate.to("/crud"))


@ui.page("/edit/{product_id}")
def edit_page(product_id: int):
    """Edit a single product using NiceCRUDCard."""
    with ui.column().classes("w-full items-center"):
        ui.label(f"Edit Product {product_id}").classes("text-2xl mb-4")

        # Find the product
        product = next((p for p in products if p.id == product_id), None)

        if product:
            with ui.card().classes("w-full max-w-2xl"):
                # Use NiceCRUDCard for single item editing
                NiceCRUDCard(product)

                # Add custom save button
                ui.button(
                    "Save & Return",
                    on_click=lambda: ui.navigate.to("/"),
                ).classes("mt-4")
        else:
            ui.label(f"Product {product_id} not found").classes("text-red-500")

        # Back button
        ui.button("← Back to Catalog", on_click=lambda: ui.navigate.to("/"))


@ui.page("/crud")
def crud_page():
    """Full CRUD interface on a dedicated page."""
    with ui.column().classes("w-full items-center"):
        ui.label("Product CRUD Manager").classes("text-2xl mb-4")

        # Full NiceCRUD interface
        NiceCRUD(
            basemodeltype=Product,
            basemodels=products,
            id_field="id",
            heading="Manage Products",
        )

        # Back button
        ui.button("← Back to Home", on_click=lambda: ui.navigate.to("/")).classes("mt-4")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceCRUD Integration Example")
