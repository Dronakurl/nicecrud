from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD


class MyModel(BaseModel, title="User"):
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")


instance1 = MyModel(id=1, name="Alice", age=30)
instance2 = MyModel(id=2, name="Bob", age=25)
crud_app = NiceCRUD(basemodels=[instance1, instance2], id_field="id", heading="User Management")

ui.run()
