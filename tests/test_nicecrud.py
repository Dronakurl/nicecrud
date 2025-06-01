import pytest
from pydantic import BaseModel, Field

from niceguicrud.nicecrud import NiceCRUD, NiceCRUDConfig


class MockModel(BaseModel):
    id: int = Field(...)
    name: str = Field(...)


@pytest.fixture
def mock_model_list():
    return [MockModel(id=1, name="Item 1"), MockModel(id=2, name="Item 2")]


@pytest.fixture
def empty_model_list():
    return []


@pytest.fixture
def nicecrud_config():
    return NiceCRUDConfig(id_field="id")


@pytest.fixture
def nicecrud_instance(mock_model_list, nicecrud_config):
    return NiceCRUD(basemodeltype=MockModel, basemodels=mock_model_list, config=nicecrud_config)


def test_inferbasemodel(mock_model_list):
    nn = NiceCRUD(basemodels=mock_model_list, id_field="id")
    assert nn.basemodeltype == MockModel, (
        "BaseModel typ is inferred from first element if necessary"
    )


def test_nicecrud_initialization(nicecrud_instance):
    assert nicecrud_instance.config.id_field == "id"
    assert isinstance(nicecrud_instance, NiceCRUD)
    assert len(nicecrud_instance.basemodels) == 2


@pytest.mark.asyncio
async def test_create_item(nicecrud_instance):
    new_item = MockModel(id=3, name="Item 3")
    await nicecrud_instance.create(new_item)
    assert len(nicecrud_instance.basemodels) == 3
    assert nicecrud_instance.basemodels[-1] == new_item


@pytest.mark.asyncio
async def test_update_item(nicecrud_instance):
    update_item = MockModel(id=1, name="Updated Item 1")
    await nicecrud_instance.update(update_item)
    assert nicecrud_instance.basemodels[0].name == "Updated Item 1"


@pytest.mark.asyncio
async def test_delete_item(nicecrud_instance):
    await nicecrud_instance.delete(1)
    assert len(nicecrud_instance.basemodels) == 1
    assert not any(item.id == 1 for item in nicecrud_instance.basemodels)


def test_get_by_id(nicecrud_instance):
    item = nicecrud_instance.get_by_id(1)
    assert item is not None
    assert item.name == "Item 1"


def test_field_exclusions(nicecrud_instance):
    model = MockModel.model_fields["id"]
    excluded = nicecrud_instance.is_excluded("id", model)
    assert not excluded
