# NiceCRUD

NiceCRUD is a CRUD (Create, Read, Update, Delete) interface built with python. The library integrates with pydantic models and [NiceGUI](https://nicegui.io) to handle data manipulation with a browser interface.

## Features

- Automatically generate CRUD interfaces from pydantic models.
- Field options, ranges, contraints, descriptions etc. are directly taken from your pydantic model
- Integrated validation and error handling with pydantic.
- Support for nested models and selection options.
- Inject your own (database?) update methods
- Minimal configuration required with sensible defaults.

## Screenshots

Taken from the [input_choices](/examples/input_choices.py) example:

![CRUD Interface Screenshot - Grid of objects](/examples/input_choices.png)
![CRUD Interface Screenshot - Editing objects](/examples/input_choices_add.png)

## Installation

To install NiceCRUD, use pip:

<!-- pip install 'git+https://github.com/Dronakurl/nicecrud.git'-->

```bash
pip install niceguicrud
```

## Quick Start

Here is a very basic example:

```python

from nicegui import ui
from pydantic import BaseModel, Field

from niceguicrud import NiceCRUD


class MyModel(BaseModel, title="User"):
    id: int
    name: str = Field(title="Name")
    age: int = Field(gt=0, title="Age")


instance1 = MyModel(id=1, name="Alice", age=30)
instance2 = MyModel(id=2, name="Bob", age=25)
crud_app = NiceCRUD(basemodels=[instance1, instance2], id_field="id", heading="User Management")

ui.run()
```

Find more in the [examples](/examples) folder.
| Example Name    | Description                             |
|-----------------|-----------------------------------------|
| [minimal](/examples/minimal.py)         | The above minimal example |
| [validation](/examples/validation.py)      | Example showcasing how pydantic validation features are used in the GUI |
| [submodel](/examples/submodel.py)        | Demonstrates usage of a pydantic submodel that can also be used in the GUI.        |
| [input_choices](/examples/input_choices.py)   | Shows the different input choices.   |
| [database](/examples/database.py)   | Shows how to customize the update, create and delete operations |

## Contributing

Contributions are welcome!

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE).
