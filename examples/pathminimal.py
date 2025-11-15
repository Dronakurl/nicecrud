import logging
from pathlib import Path

from nicegui import ui
from pydantic import BaseModel

from niceguicrud import NiceCRUDCard

log = logging.getLogger("niceguicrud")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(name)s - %(message)s"))
log.addHandler(console_handler)


class TestModel(BaseModel):
    example: Path = Path("example.txt")


xx = TestModel()
NiceCRUDCard(xx)

ui.button("show", on_click=lambda: ui.notify(str(xx.example) + str(type(xx.example))))

ui.run()
