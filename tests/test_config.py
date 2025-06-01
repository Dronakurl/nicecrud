from pydantic import BaseModel, Field

from niceguicrud.nicecrud import NiceCRUD, NiceCRUDCard, NiceCRUDConfig


class Bicycle(BaseModel):
    model: str = Field(default="", title="Model")
    brand: str = Field(..., title="Brand")


def test_set_config():
    x = NiceCRUD(Bicycle, [], config=NiceCRUDConfig(id_label="Model name"), id_field="model")
    assert x.config.id_label == "Model name", "Configuration can be set by passing the config"
    assert x.config.id_field == "model", "Configuration can be set by passing keywords"
    x.config.heading = "Bicycles"
    assert x.config.id_label == "Model name", (
        "Config can be changed without affecting the already set values"
    )
    assert x.config.heading == "Bicycles", "Config can be changed"


def test_set_config_card():
    x = NiceCRUDCard(
        Bicycle(brand="Trek"), config=NiceCRUDConfig(id_label="Model name"), id_field="model"
    )
    assert x.config.id_label == "Model name", (
        "Configuration can be set in NiceCRUDCard by passing the config"
    )
    assert x.config.id_field == "model", (
        "Configuration can be set in NiceCRUDCard by passing keywords"
    )
