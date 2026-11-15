"""Tests for NiceCRUD.from_http_request (httpx2 client + pydantic TypeAdapter validation)."""

import json

import httpx2
import pytest
from nicegui import Client, ui
from pydantic import BaseModel

from niceguicrud import nicecrud as nicecrud_module
from niceguicrud.nicecrud import NiceCRUD, NiceCRUDConfig

pytestmark = pytest.mark.asyncio


class Item(BaseModel):
    id: int
    name: str


# display_on_init=False: building UI elements needs a NiceGUI slot, which async tests lack.
CONFIG = NiceCRUDConfig(id_field="id", display_on_init=False)


@pytest.fixture
def notify(monkeypatch):
    calls = []
    monkeypatch.setattr(nicecrud_module.ui, "notify", lambda *a, **kw: calls.append((a, kw)))
    return calls


@pytest.fixture
def mock_server(monkeypatch):
    """Route the AsyncClient used by from_http_request to a mock handler; record requests."""
    requests: list[httpx2.Request] = []
    state = {"handler": None}
    real_client = httpx2.AsyncClient

    def handler(request: httpx2.Request) -> httpx2.Response:
        requests.append(request)
        return state["handler"](request)

    def client_factory(*args, **kwargs):
        return real_client(*args, transport=httpx2.MockTransport(handler), **kwargs)

    monkeypatch.setattr(nicecrud_module.httpx, "AsyncClient", client_factory)

    def set_handler(fn):
        state["handler"] = fn
        return requests

    return set_handler


async def test_valid_list(mock_server, notify):
    data = [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
    mock_server(lambda r: httpx2.Response(200, json=data))
    crud = await NiceCRUD.from_http_request(url="http://x/items", basemodeltype=Item, config=CONFIG)
    assert crud is not None
    assert crud.basemodels == [Item(id=1, name="a"), Item(id=2, name="b")]
    assert notify == []


async def test_empty_list(mock_server, notify):
    mock_server(lambda r: httpx2.Response(200, json=[]))
    crud = await NiceCRUD.from_http_request(url="http://x/items", basemodeltype=Item, config=CONFIG)
    assert crud is not None
    assert crud.basemodels == []


async def test_headers_are_sent(mock_server, notify):
    requests = mock_server(lambda r: httpx2.Response(200, json=[]))
    await NiceCRUD.from_http_request(
        url="http://x/items",
        headers={"Authorization": "Bearer t"},
        basemodeltype=Item,
        config=CONFIG,
    )
    assert requests[0].headers["authorization"] == "Bearer t"


async def test_follows_redirects(mock_server, notify):
    def handler(request):
        if request.url.path == "/old":
            return httpx2.Response(302, headers={"location": "http://x/new"})
        return httpx2.Response(200, json=[{"id": 1, "name": "a"}])

    mock_server(handler)
    crud = await NiceCRUD.from_http_request(url="http://x/old", basemodeltype=Item, config=CONFIG)
    assert crud is not None
    assert len(crud.basemodels) == 1


@pytest.mark.parametrize(
    "body",
    [
        json.dumps({"id": 1, "name": "a"}),  # object instead of list
        json.dumps([{"id": "x", "name": "a"}]),  # wrong field type
        json.dumps([{"id": 1}]),  # missing field
        json.dumps([1, 2]),  # list of non-objects
        "not json at all",  # invalid JSON
        "",  # empty body
    ],
)
async def test_invalid_payload_notifies_and_returns_none(mock_server, notify, body):
    mock_server(lambda r: httpx2.Response(200, content=body.encode()))
    crud = await NiceCRUD.from_http_request(url="http://x/items", basemodeltype=Item, config=CONFIG)
    assert crud is None
    assert len(notify) == 1
    assert notify[0][1]["color"] == "negative"


async def test_table_is_displayed(mock_server, notify):
    """With display_on_init=True the loaded rows end up in the table (needs a client context)."""
    mock_server(lambda r: httpx2.Response(200, json=[{"id": 1, "name": "a"}]))
    with Client(ui.page("/")):
        crud = await NiceCRUD.from_http_request(
            url="http://x/items",
            basemodeltype=Item,
            config=NiceCRUDConfig(id_field="id"),
        )
        assert crud is not None
        assert [row["name"] for row in crud.table.rows] == ["a"]
