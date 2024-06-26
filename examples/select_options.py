import logging
import uuid
from typing import Any

from nicegui import ui
from pydantic import BaseModel, Field, SerializationInfo, field_serializer

from niceguicrud import FieldOptions, NiceCRUD
from niceguicrud.nicecrud import NiceCRUDField

log = logging.getLogger("nicecrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class NiceShoes(BaseModel, title="NiceShoes"):
    name: str = Field(default_factory=lambda: str(uuid.uuid4()), max_length=60, title="Name")
    payment_options: dict[str, Any] = NiceCRUDField(
        default_factory=dict[str, Any],
        title="Payment Options",
        nicecrud_options=FieldOptions(input_type="multiselect"),
    )

    @field_serializer("payment_options")
    def payment_show(self, v: dict[str, Any], info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return ", ".join(v)
        return v


class ShoeCRUD(NiceCRUD):
    async def select_options(self, field_name: str, obj: NiceShoes) -> dict:
        """Overwrite select_options to get custom selection options, call super for sane defaults"""
        if field_name == "payment_options":
            return {key: key for key in ("bla", "wurstpay", "paygroove")}
        else:
            return await super().select_options(field_name=field_name, obj=obj)


@ui.page("/")
async def nicecrudtest():
    tog = ui.toggle(["dark", "light"])
    ui.dark_mode(value=True).bind_value_from(tog, "value", backward=lambda x: x == "dark")
    mods = [
        NiceShoes(payment_options=dict(paygroove="paygrove data")),
        NiceShoes(payment_options=dict(wurstpay="wurstpay data")),
    ]
    ShoeCRUD(basemodeltype=NiceShoes, basemodels=mods, id_label="Shoe model:", id_field="name")


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceguiCRUD Showcase - selection options", favicon="👞", dark=True)
