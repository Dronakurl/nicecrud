import logging
from typing import Literal

from nicegui import ui
from pydantic import BaseModel, Field, model_validator

from niceguicrud import NiceCRUD, NiceCRUDConfig

log = logging.getLogger("niceguicrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class Character(BaseModel, title="D&D Character"):
    id: int
    character_name: str = Field(title="Character Name")
    magic_level: int = Field(gt=0, lt=101, title="Magic Level")
    species: Literal["Hobbit", "Wizard", "Orc"] = Field(title="Species")

    @model_validator(mode="before")
    @classmethod
    def model_val(cls, v):
        if v.get("species") == "Wizard" and (v.get("magic_level") or -999) < 10:
            raise ValueError(
                "All wizards in the western lands of the great planes of the stupidly long error texts have at least magic level 10"
            )
        return v


instance1 = Character(id=1, character_name="Gandalf", magic_level=95, species="Wizard")
instance2 = Character(id=2, character_name="Frodo", magic_level=10, species="Hobbit")
crud_config = NiceCRUDConfig(id_field="id", heading="Character Database")

crud_app = NiceCRUD(basemodeltype=Character, basemodels=[instance1, instance2], config=crud_config)

ui.run()
