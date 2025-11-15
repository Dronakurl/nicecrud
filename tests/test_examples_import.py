"""Test that all example files can be imported without errors.

This catches syntax errors, missing imports, and basic runtime issues
in the example files before users encounter them.
"""

import sys
from pathlib import Path


def test_examples_can_be_compiled():
    """Test that all example Python files have valid syntax."""
    examples_dir = Path("examples")
    assert examples_dir.exists(), "examples/ directory not found"

    example_files = list(examples_dir.glob("*.py"))
    assert len(example_files) > 0, "No example files found"

    for example_file in example_files:
        with open(example_file) as f:
            code = f.read()

        # Test that code compiles without syntax errors
        try:
            compile(code, str(example_file), 'exec')
        except SyntaxError as e:
            raise AssertionError(f"{example_file} has syntax error: {e}")


def test_readme_examples_exist():
    """Test that all examples mentioned in README.md actually exist."""
    readme_examples = [
        "examples/minimal.py",
        "examples/validation.py",
        "examples/submodel.py",
        "examples/input_choices.py",
        "examples/database.py",
    ]

    for example_path in readme_examples:
        example_file = Path(example_path)
        assert example_file.exists(), f"README mentions {example_path} but file does not exist"


def test_quickstart_example_syntax():
    """Test that the Quick Start example from README has valid syntax."""
    quickstart_code = '''
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
'''

    # Test that quickstart code compiles
    try:
        compile(quickstart_code, 'README_quickstart', 'exec')
    except SyntaxError as e:
        raise AssertionError(f"README Quick Start has syntax error: {e}")
