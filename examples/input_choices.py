import logging
from typing import Literal, Optional, Union

from nicegui import ui
from pydantic import (BaseModel, ConfigDict, Field, SerializationInfo,
                      field_serializer, field_validator, model_serializer,
                      model_validator)

from nicecrud import FieldOptions, NiceCRUD, NiceCRUDCard

log = logging.getLogger("nicecrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class Material(BaseModel, title="Material"):
    material: Literal["leather", "canvas", "patent leather"] = Field(default="canvas", title="Top material")
    color: Literal["black", "maroon", "navy"] = Field(default="black", max_length=30, title="Color")

    @model_serializer(mode="wrap")
    def gui(self, default_ser, info=SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.color} {self.material}"
        return default_ser(self)


class ActiveWear(BaseModel, title="Outdoor"):
    performance_materials: str = Field(default="breathable fabric", title="Performance Materials")
    shock_absorption: bool = Field(default=True, title="Shock Absorption")

    @model_serializer(mode="wrap")
    def gui(self, default_ser, info=SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.performance_materials} "
        return default_ser(self)


class OfficeWear(BaseModel, title="Office"):
    note: str = Field(default="very strict", title="Notes")
    formality: Literal["Business casual", "Business attire"] = Field(default="Business casual", title="Formality")

    @model_serializer(mode="wrap")
    def gui(self, default_ser, info=SerializationInfo):
        context = info.context  # pyright: ignore[reportAttributeAccessIssue]
        if context and context.get("gui"):
            return f"{self.formality} "
        return default_ser(self)


class NiceShoes(BaseModel):
    name: str = Field(default="unknown", max_length=30, title="Name")
    size: int = Field(..., lt=49, gt=23, json_schema_extra=FieldOptions(input_type="slider", step=2).model_dump())
    price: float = Field(..., json_schema_extra=FieldOptions(step=2).model_dump(), lt=100, gt=2.20)
    style: Literal["sneakers", "heels", "ballet flats", "boots"] = Field(default="ballet flats", title="Shoe style")
    heelheight: Optional[float] = Field(default=None, title="height of heels")
    brand: Literal["Nike", "Adidas", "Converse", "Tamaris"] = Field(
        ..., title="Brand", description="<div>Only the <b>finest</b> brands<div>"
    )
    availsizes: list[int] = Field(default=[36, 39, 42], title="Available sizes")
    state: list[str] = Field(default=["used", "new"], title="Available states")
    avail: bool = Field(default=True, title="available?", json_schema_extra=FieldOptions(readonly=True).model_dump())
    winter: bool = Field(default=True, title="Winter collection")
    material: Material = Field(default_factory=Material, title="Material")
    occasion: Union[ActiveWear, OfficeWear] = Field(default_factory=OfficeWear, title="Occasion")

    model_config: ConfigDict = ConfigDict(validate_assignment=True, title="Shoe")

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
            v["brand"] = "Adudis"
        return v


def test_basemodel_annotation():
    x: NiceShoes = NiceShoes(name="Chucks", size=41, price=2.50, brand="Adidas")
    for k, v in x.model_fields.items():
        typ = v.annotation
        if k == "name":
            assert typ == str, "Expect that basemodel annotation can be used to get field types"


@ui.page("/")
async def nicecrudtest():
    mods = [
        NiceShoes(name="Chucks", size=41, price=2.50, brand="Converse"),
        NiceShoes(name="AirJordan", size=41, price=2.50, brand="Nike"),
    ]
    NiceCRUD(
        basemodel=NiceShoes,
        basemodellist=mods,
        id_label="Shoe model:",
        id_field="name",
    )


@ui.page("/shoes")
async def nicecrud_card():
    x: NiceShoes = NiceShoes(name="Chucks", size=41, price=2.50, brand="Converse")
    NiceCRUDCard(item=x)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run()