# pyright: reportIncompatibleMethodOverride=false
import logging

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import FieldOptions, NiceCRUD

log = logging.getLogger("niceguicrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class Unicorn(BaseModel):
    id: str
    horn_length: float
    color: str = Field(..., json_schema_extra=FieldOptions(input_type="select").model_dump())
    sparkle_level: int = 100


class UnicornCRUD(NiceCRUD):
    async def update(self, unicorn: Unicorn):
        ui.notify(f"Custom database update operation on unicorn {unicorn.color}")
        await super().update(unicorn)

    async def create(self, unicorn: Unicorn):
        ui.notify(f"Custom database create operation on unicorn {unicorn.color}")
        await super().update(unicorn)

    async def delete(self, unicorn: Unicorn):
        ui.notify(f"Custom database delete operation on unicorn {unicorn.color}")
        await super().update(unicorn)

    async def select_options(self, field_name: str, unicorn: Unicorn) -> dict:
        if field_name == "color":
            # this can be taken from the database, too
            if unicorn.sparkle_level > 10:
                return dict(red="Red", pink="Pink", rainbow="Rainbow")
            else:
                return dict(red="Red", pink="Pink")
        else:
            return await super().select_options(field_name, unicorn)


unicorn1 = Unicorn(id="honcho", horn_length=5.5, color="rainbow", sparkle_level=50)
unicorn2 = Unicorn(id="poncho", horn_length=7.0, color="pink")

crud_app = UnicornCRUD(basemodels=[unicorn1, unicorn2], id_field="id")

ui.run()
