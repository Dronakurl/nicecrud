import logging

from nicegui import ui
from pydantic import BaseModel, SerializationInfo, model_serializer

from niceguicrud import NiceCRUD, NiceCRUDConfig

log = logging.getLogger("niceguicrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class SpouseModel(BaseModel):
    name: str
    age: int
    is_employed: bool = False

    @model_serializer(mode="wrap")
    def gui(self, default_serializer, info: SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return self.name + (" (unemployed)" if not self.is_employed else "")
        return default_serializer(self)


class Actor(BaseModel):
    name: str
    age: int
    spouse: SpouseModel


actress = Actor(
    name="Scarlett Joh",
    age=36,
    spouse=SpouseModel(name="Colin Jost", age=39, is_employed=True),
)
another_actress = Actor(
    name="Natalie Portman",
    age=40,
    spouse=SpouseModel(name="Benjamin Millepied", age=45),
)
crud_config = NiceCRUDConfig(id_field="name", heading="Actress Database")
crud_app = NiceCRUD(basemodels=[actress, another_actress], config=crud_config)

ui.run()
