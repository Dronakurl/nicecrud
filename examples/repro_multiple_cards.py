# This is an example to show how NiceCRUDCard can be used as a standalone item.
# In github issue 14, there was also a problem with cards not showing the actual data, but just the same data over and over.

from nicegui import ui
from pydantic import BaseModel

from niceguicrud import NiceCRUDCard


class Shoe(BaseModel, title="Shoe"):
    id: int
    name: str
    size: int
    brand: str


@ui.page("/")
async def repro_page():
    x = Shoe(id=1, name="Chucks", size=41, brand="Converse")
    y = Shoe(id=2, name="AirJordan", size=42, brand="Nike")
    ui.label("Below are two NiceCRUDCard instances:")
    with ui.row():
        _a = NiceCRUDCard(item=x)
        _b = NiceCRUDCard(item=y)


ui.run()
