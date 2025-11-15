"""Example: Nested list of BaseModels.

This example demonstrates that list[BaseModel] nesting works correctly,
addressing issue #8.
"""

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD


class IntentSpec(BaseModel):
    """Nested model representing an intent."""
    name: str = Field(title="Intent Name")
    description: str = Field(title="Description", default="")
    confidence: float = Field(title="Confidence", ge=0.0, le=1.0, default=0.5)


class Agent(BaseModel):
    """Agent model with nested list of intents."""
    id: int = Field(title="Agent ID")
    name: str = Field(title="Agent Name")
    intents: list[IntentSpec] = Field(
        title="Intents",
        default_factory=list,
    )


# Sample data with nested lists
agents = [
    Agent(
        id=1,
        name="Customer Service Bot",
        intents=[
            IntentSpec(name="greeting", description="Welcome users", confidence=0.95),
            IntentSpec(name="help", description="Provide assistance", confidence=0.90),
            IntentSpec(name="goodbye", description="End conversation", confidence=0.85),
        ],
    ),
    Agent(
        id=2,
        name="Sales Bot",
        intents=[
            IntentSpec(name="product_inquiry", description="Answer product questions", confidence=0.92),
            IntentSpec(name="pricing", description="Provide pricing info", confidence=0.88),
        ],
    ),
]


@ui.page("/")
def main_page():
    with ui.column().classes("w-full items-center p-4"):
        ui.label("Agent Manager - Nested Lists").classes("text-3xl mb-4")

        ui.markdown("""
        This example demonstrates **complete nesting support** including `list[BaseModel]`.

        The `intents` field is a `list[IntentSpec]` (list of nested BaseModels).

        Click "Edit" to see the nested list with add/edit/delete functionality!
        """).classes("mb-4")

        NiceCRUD(
            basemodeltype=Agent,
            basemodels=agents,
            id_field="id",
            heading="AI Agents",
        )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Nested Lists Example")
