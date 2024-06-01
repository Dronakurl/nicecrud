from nicegui import ui
from pydantic import BaseModel, Field

from nicecrud import NiceCRUD, NiceCRUDConfig


class MyModel(BaseModel):
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")


instance1 = MyModel(id=1, name="Alice", age=30)
instance2 = MyModel(id=2, name="Bob", age=25)

crud_config = NiceCRUDConfig(
    id_field="id",
    heading="User Management",
)

crud_app = NiceCRUD(basemodel=MyModel, basemodellist=[instance1, instance2], config=crud_config)

ui.run()
