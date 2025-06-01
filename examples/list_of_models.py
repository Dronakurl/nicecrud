import logging

from nicegui import ui
from pydantic import BaseModel, SerializationInfo, field_serializer, model_serializer

from niceguicrud import NiceCRUD, NiceCRUDConfig

log = logging.getLogger("nicecrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class MovieModel(BaseModel):
    title: str
    year: int

    @model_serializer(mode="wrap")
    def gui(self, default_serializer, info: SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return self.title
        return default_serializer(self)


class Actor(BaseModel):
    name: str
    age: int
    shoes: list[str] = []
    movies: list[MovieModel] = []

    @field_serializer("movies")
    def movies_show(self, v: list[MovieModel], info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return ", ".join([m.title for m in v])
        return v


actress = Actor(
    name="Scarlett Johansson",
    age=36,
    shoes=["heels", "sneakers"],
    movies=[
        MovieModel(title="Lost in Translation", year=2003),
        MovieModel(title="Lucy", year=2014),
    ],
)
another_actress = Actor(
    name="Natalie Portman",
    age=40,
    shoes=["ballet flats", "boots", "sneakers", "heels", "flip-flops", "sandals"],
    movies=[
        MovieModel(title="Black Swan", year=2010),
        MovieModel(title="V for Vendetta", year=2005),
    ],
)
crud_config = NiceCRUDConfig(id_field="name", heading="Actress Database")
crud_app = NiceCRUD(basemodels=[actress, another_actress], config=crud_config)

ui.run()
