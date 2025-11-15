"""Unit tests for individual input handlers.

Tests verify each handler's can_handle logic and create_widget behavior.
"""

import pytest
from datetime import date, time, datetime
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

from niceguicrud.input_handlers.string import StringHandler
from niceguicrud.input_handlers.numeric import NumericHandler
from niceguicrud.input_handlers.boolean import BooleanHandler
from niceguicrud.input_handlers.temporal import TemporalHandler
from niceguicrud.input_handlers.selection import SelectionHandler
from niceguicrud.input_handlers.nested import NestedHandler
from niceguicrud.input_handlers.collections import CollectionHandler
from niceguicrud.input_handlers.base import FallbackHandler, InputContext


class SampleModel(BaseModel):
    name: str
    value: int


# Test StringHandler
class TestStringHandler:
    def test_can_handle_str(self):
        handler = StringHandler()
        field_info = FieldInfo(annotation=str, default="test")
        assert handler.can_handle(field_info) is True

    def test_can_handle_path(self):
        handler = StringHandler()
        field_info = FieldInfo(annotation=Path, default=Path("."))
        assert handler.can_handle(field_info) is True

    def test_can_handle_textarea(self):
        handler = StringHandler()
        field_info = FieldInfo(
            annotation=str,
            default="",
            json_schema_extra={"input_type": "textarea"}
        )
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_int(self):
        handler = StringHandler()
        field_info = FieldInfo(annotation=int, default=0)
        assert handler.can_handle(field_info) is False


# Test NumericHandler
class TestNumericHandler:
    def test_can_handle_int(self):
        handler = NumericHandler()
        field_info = FieldInfo(annotation=int, default=0)
        assert handler.can_handle(field_info) is True

    def test_can_handle_float(self):
        handler = NumericHandler()
        field_info = FieldInfo(annotation=float, default=0.0)
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_str(self):
        handler = NumericHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test BooleanHandler
class TestBooleanHandler:
    def test_can_handle_bool(self):
        handler = BooleanHandler()
        field_info = FieldInfo(annotation=bool, default=False)
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_str(self):
        handler = BooleanHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test TemporalHandler
class TestTemporalHandler:
    def test_can_handle_date(self):
        handler = TemporalHandler()
        field_info = FieldInfo(annotation=date, default=date.today())
        assert handler.can_handle(field_info) is True

    def test_can_handle_time(self):
        handler = TemporalHandler()
        field_info = FieldInfo(annotation=time, default=time())
        assert handler.can_handle(field_info) is True

    def test_can_handle_datetime(self):
        handler = TemporalHandler()
        field_info = FieldInfo(annotation=datetime, default=datetime.now())
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_str(self):
        handler = TemporalHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test SelectionHandler
class TestSelectionHandler:
    def test_can_handle_literal(self):
        handler = SelectionHandler()
        field_info = FieldInfo(annotation=Literal["a", "b", "c"], default="a")
        assert handler.can_handle(field_info) is True

    def test_can_handle_select_input_type(self):
        handler = SelectionHandler()
        field_info = FieldInfo(
            annotation=str,
            default="",
            json_schema_extra={"input_type": "select"}
        )
        assert handler.can_handle(field_info) is True

    def test_can_handle_multiselect_input_type(self):
        handler = SelectionHandler()
        field_info = FieldInfo(
            annotation=dict,
            default={},
            json_schema_extra={"input_type": "multiselect"}
        )
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_str(self):
        handler = SelectionHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test NestedHandler
class TestNestedHandler:
    def test_can_handle_basemodel(self):
        handler = NestedHandler()
        field_info = FieldInfo(annotation=SampleModel, default=None)
        assert handler.can_handle(field_info) is True

    def test_can_handle_list_basemodel(self):
        handler = NestedHandler()
        field_info = FieldInfo(annotation=list[SampleModel], default_factory=list)
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_str(self):
        handler = NestedHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test CollectionHandler
class TestCollectionHandler:
    def test_can_handle_list_str(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=list[str], default_factory=list)
        assert handler.can_handle(field_info) is True

    def test_can_handle_list_int(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=list[int], default_factory=list)
        assert handler.can_handle(field_info) is True

    def test_can_handle_list_float(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=list[float], default_factory=list)
        assert handler.can_handle(field_info) is True

    def test_can_handle_set_str(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=set[str], default_factory=set)
        assert handler.can_handle(field_info) is True

    def test_cannot_handle_list_basemodel(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=list[SampleModel], default_factory=list)
        assert handler.can_handle(field_info) is False

    def test_cannot_handle_str(self):
        handler = CollectionHandler()
        field_info = FieldInfo(annotation=str, default="")
        assert handler.can_handle(field_info) is False


# Test FallbackHandler
class TestFallbackHandler:
    def test_can_handle_anything(self):
        handler = FallbackHandler()
        # Should handle any type
        assert handler.can_handle(FieldInfo(annotation=str, default="")) is True
        assert handler.can_handle(FieldInfo(annotation=int, default=0)) is True
        assert handler.can_handle(FieldInfo(annotation=list, default_factory=list)) is True

    def test_priority_is_lowest(self):
        handler = FallbackHandler()
        assert handler.priority == -1000
