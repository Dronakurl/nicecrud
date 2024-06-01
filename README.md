# NiceCRUD

NiceCRUD is a versatile and easy-to-use CRUD (Create, Read, Update, Delete) interface built with python. The library integrates with pydantic models and offers comprehensive use of the [NiceGUI](https://nicegui.io) library to easily handle data manipulation with a user-friendly interface.

## Features

- Automatically generate CRUD interfaces from pydantic models.
- Field options, ranges, contraints, descriptions etc. are directly taken from your pydantic model
- Integrated validation and error handling with pydantic.
- Support for nested models and selection options.
- Minimal configuration required with sensible defaults.

## Installation

To install NiceCRUD, you can use pip:

```bash
pip install 'git+https://github.com/Dronakurl/nicecrud.git'
```

## Quick Start

Here is a very basic example, find more in the [examples](/examples) folder.

```python
from pydantic import BaseModel, Field
from nicecrud import NiceCRUD, NiceCRUDConfig
from nicegui import ui, run

class MyModel(BaseModel):
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")

instance1 = MyModel(id=1, name="Alice", age=30)
instance2 = MyModel(id=2, name="Bob", age=25)

crud_config = NiceCRUDConfig(
    id_field="id",
    heading="User Management",
)

crud_app = NiceCRUD(
    basemodel=MyModel,
    basemodellist=[instance1, instance2],
    config=crud_config
)

ui.run()
```

## Documentation

- For detailed information on usage and customization, please refer to the source code.
- A comprehensive set of docstrings is present to help understand the classes and functionality in detail.

## Logging and Error Handling

- The library emits logs through Python's `logging` library, prefixed with `[mvp.nicecrud]`.

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
