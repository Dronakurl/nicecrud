import logging
from datetime import date, datetime, time
from typing import Any, Literal, Optional, Union

from nicegui import ui
from pydantic import (
    BaseModel,
    Field,
    SerializationInfo,
    field_serializer,
    field_validator,
    model_serializer,
    model_validator,
)

from niceguicrud import FieldOptions, NiceCRUD, NiceCRUDCard
from niceguicrud.nicecrud import NiceCRUDField

log = logging.getLogger("niceguicrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class Material(BaseModel, title="Material"):
    material: Literal["leather", "canvas", "patent leather"] = Field(
        default="canvas", title="Top material"
    )
    color: Literal["black", "maroon", "navy"] = Field(default="black", max_length=30, title="Color")

    @model_serializer(mode="wrap")
    def gui(self, default_serializer, info: SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.color} {self.material}"
        return default_serializer(self)


class ActiveWear(BaseModel, title="Outdoor"):
    performance_materials: str = Field(default="breathable fabric", title="Performance Materials")
    shock_absorption: bool = Field(default=True, title="Shock Absorption")

    @model_serializer(mode="wrap")
    def gui(self, default_serializer, info: SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.performance_materials} "
        return default_serializer(self)


class OfficeWear(BaseModel, title="Office"):
    note: str = Field(default="very strict", title="Notes")
    formality: Literal["Business casual", "Business attire"] = Field(
        default="Business casual", title="Formality"
    )

    @model_serializer(mode="wrap")
    def gui(self, default_serializer, info: SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.formality} "
        return default_serializer(self)


class NiceShoes(BaseModel, validate_assignment=True, title="Shoe"):
    name: str = Field(default="unknown", max_length=30, title="Name")
    size: int = Field(
        ..., lt=49, gt=23, json_schema_extra=FieldOptions(input_type="slider", step=2).model_dump()
    )
    price: float = Field(..., json_schema_extra=FieldOptions(step=2).model_dump(), lt=100, gt=2.20)
    date_of_purchase: date = Field(default_factory=date.today, title="Date of Purchase")
    last_order: time = Field(
        default_factory=lambda: datetime.now().replace(second=0, microsecond=0).time(),
        title="Daily last order",
    )
    next_delivery: datetime = Field(
        default_factory=lambda: datetime.now().replace(second=0, microsecond=0),
        title="Next delivery",
    )
    style: Literal["sneakers", "heels", "ballet flats", "boots"] = Field(
        default="ballet flats", title="Shoe style"
    )
    heelheight: Optional[float] = Field(default=None, title="height of heels")
    brand: Literal["Nike", "Adidas", "Converse", "Tamaris"] = Field(
        ..., title="Brand", description="<div>Only the <b>finest</b> brands<div>"
    )
    availsizes: list[int] = Field(default=[36, 39, 42], title="Available sizes")
    available_states: list[str] = Field(default=["used", "new"], title="Available States")
    avail: bool = Field(
        default=True, title="available?", json_schema_extra=FieldOptions(readonly=True).model_dump()
    )
    winter: bool = Field(default=True, title="Winter collection")
    material: Material = Field(default_factory=Material, title="Material")
    occasion: Union[ActiveWear, OfficeWear] = Field(default_factory=OfficeWear, title="Occasion")
    payment_options: list[str] = Field(
        default_factory=list,
        title="Payment Options",
        json_schema_extra=FieldOptions(
            input_type="multiselect",
            selections={
                k: k
                for k in (
                    "paygroove",
                    "flingfunds",
                    "quixcoin",
                    "bazookaPay",
                    "fizzFinance",
                    "glimmerGold",
                )
            },
        ).model_dump(),
    )
    shipment_options: dict[str, Any] = NiceCRUDField(
        default_factory=dict,
        title="Shipment Options",
        nicecrud_options=FieldOptions(
            input_type="multiselect",
            selections={k: k for k in ("Dparcel", "WackyWagon", "GiggleFreight", "ZoomBoom")},
        ),
    )

    @field_serializer("payment_options")
    def payment_show(self, v: list[str], info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return ", ".join(v)
        return v

    @field_serializer("shipment_options")
    def shipment_show(self, v: dict[str, Any], info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return ", ".join(v.keys())
        return v

    @field_serializer("occasion")
    def occasion_show(self, v: Union[ActiveWear, OfficeWear], info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return v.__class__.__name__
        return v

    @field_serializer("winter")
    def wintrshower(self, v: str, info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return "Yes, in winter collection" if v else "Not in winter collection "
        return v

    @field_serializer("avail")
    def availshow(self, v: bool, info: SerializationInfo):
        context = info.context
        if context and context.get("gui"):
            return "yes" if v else "no"
        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if not isinstance(v, int):
            raise ValueError("only integer Numbers")
        if v > 45:
            raise ValueError("Your feet a too big")
        return v

    @model_validator(mode="before")
    @classmethod
    def only_for_heels(cls, v):
        if v.get("style") != "heels" and v.get("heelheight") is not None:
            raise ValueError("Only heels should have heelheight")
        if v.get("style") == "sneakers":
            v["brand"] = "Adidas"
        return v


def test_basemodel_annotation():
    x: NiceShoes = NiceShoes(name="Chucks", size=41, price=2.50, brand="Adidas")
    for k, v in x.model_fields.items():
        typ = v.annotation
        if k == "name":
            assert typ is str, "Expect that basemodel annotation can be used to get field types"


@ui.page("/")
async def nicecrudtest():
    mods = [
        NiceShoes(
            name="Chucks",
            size=41,
            price=2.50,
            brand="Converse",
            style="sneakers",
            payment_options=["paygroove"],
        ),
        NiceShoes(
            name="AirJordan",
            size=41,
            price=2.50,
            brand="Nike",
            style="sneakers",
            shipment_options={"GiggleFreight": ["huh", 23]},
        ),
    ]
    NiceCRUD(
        basemodeltype=NiceShoes,
        basemodels=mods,
        id_label="Shoe model:",
        id_field="name",
    )


@ui.page("/shoes")
async def nicecrud_card():
    x: NiceShoes = NiceShoes(name="Chucks", size=41, price=2.50, brand="Converse")
    NiceCRUDCard(item=x)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="NiceguiCRUD Showcase - Shoes", favicon="👞")
