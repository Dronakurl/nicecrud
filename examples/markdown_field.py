"""Example: Using markdown field rendering in NiceCRUD.

This example demonstrates how to render string fields as markdown,
allowing rich text formatting with live preview.
"""

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD


class BlogPost(BaseModel):
    id: int = Field(title="Post ID")
    title: str = Field(title="Title")
    content: str = Field(
        title="Content (Markdown)",
        json_schema_extra={"input_type": "markdown"},
        default="# Welcome\n\nThis is a **markdown** field!\n\n- Edit to see live preview\n- Supports all markdown features",
    )
    summary: str = Field(
        title="Summary (Plain Text)",
        default="A brief summary",
    )


# Sample data with markdown content
posts = [
    BlogPost(
        id=1,
        title="Getting Started with NiceCRUD",
        content="""# Introduction

Welcome to **NiceCRUD**! This is a powerful CRUD interface for pydantic models.

## Features

- Automatic form generation
- Type-safe validation
- Markdown support
- And much more!

### Code Example

```python
from niceguicrud import NiceCRUD
crud = NiceCRUD(basemodels=data)
```

Visit [nicegui.io](https://nicegui.io) for more info.
""",
        summary="Learn how to use NiceCRUD",
    ),
    BlogPost(
        id=2,
        title="Markdown Field Tutorial",
        content="""## Markdown Fields

You can use markdown for rich text:

- **Bold text**
- *Italic text*
- `Code snippets`
- [Links](https://example.com)

> Blockquotes work too!

1. Numbered lists
2. Are supported
3. As well
""",
        summary="How to use markdown fields",
    ),
]


@ui.page("/")
def main_page():
    with ui.column().classes("w-full items-center p-4"):
        ui.label("Blog Post Manager").classes("text-3xl mb-4")

        ui.markdown("""
        This example demonstrates **markdown field rendering**.

        Click "Add new item" or "Edit" to see markdown fields with a larger textarea editor!
        The table display shows the markdown rendered.
        """).classes("mb-4")

        NiceCRUD(
            basemodeltype=BlogPost,
            basemodels=posts,
            id_field="id",
            heading="Blog Posts",
        )


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Markdown Field Example")
