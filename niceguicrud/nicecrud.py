import collections.abc
import html
import logging
import re
import typing
from functools import partial
from types import UnionType
from typing import Awaitable, Callable, Generic, Literal, Optional, Type, TypeVar, Union

import annotated_types
import httpx
from nicegui import events, ui
from pydantic import BaseModel, Field, ValidationError
from pydantic.fields import FieldInfo

from .basemodel_to_table import basemodellist_to_rows_and_cols
from .show_error import show_error

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class FieldOptions(BaseModel, title="Options that can be set in each Field in json_schema_extra"):
    """Options that can be set in each Field in json_schema_extra"""

    step: Optional[float] = Field(default=None, title="Step size for numeric Fields")
    input_type: Optional[Literal["slider", "number", "select", "multiselect"]] = Field(default=None)
    selections: dict[str, str] | None = Field(
        default=None, title="selections for input_type=select"
    )
    readonly: Optional[bool] = Field(default=None)
    exclude: Optional[bool] = Field(default=None)


def NiceCRUDField(
    *args, title: str | None = None, nicecrud_options: FieldOptions | None = None, **kwargs
):
    json_schema_extra = nicecrud_options.model_dump() if nicecrud_options is not None else None
    if "json_schema_extra" in kwargs:
        log.warning("Use json_schema_extra *or* nicecrud_options with NiceCRUDField")
        json_schema_extra = kwargs["json_schema_extra"] | json_schema_extra or dict()
    return Field(*args, **kwargs, title=title, json_schema_extra=json_schema_extra)


class NiceCRUDConfig(BaseModel, title="Options for a NiceCRUD instance", validate_assignment=True):
    """General nicecrud config. This is put in a BaseModel objects so it is
    easier to use the editor to manage options"""

    id_field: str = ""
    id_label: Optional[str] = None
    no_data_label: str = "No data given"
    search_input_label: Optional[str] = None
    heading: str | None = None
    add_button_text: str = "Add new item"
    delete_button_text: str = "Delete selected items"
    new_item_dialog_heading: Optional[str] = None
    update_item_dialog_heading: Optional[str] = None
    additional_exclude: list[str] = Field(
        default_factory=list,
        description="fields that should be excluded from the CRUD application"
        "additionally to those excluded in pydantic",
    )
    class_heading: str = Field(
        default="text-xl font-bold", description="CSS (tailwind) classes for headings"
    )
    class_subheading: str = Field(
        default="text-lg font-bold", description="CSS (tailwind) classes for subheadings"
    )
    class_card: str = Field(default="dark:bg-slate-900 bg-slate-200")
    class_card_selected: str = Field(default="dark:bg-slate-800 bg-slate-100")
    class_card_header: str = Field(default="dark:bg-slate-700 bg-slate-50")
    column_count: int | None = Field(
        default=None,
        description="Number of columns to be used for the settings card, default None calculates it from the number of inputs",
    )

    def update(self, data: dict):
        for k, v in data.items():
            setattr(self, k, v)


# NiceCRUD can be used with any pydantic BaseModel. T is the generic type
# that is a placeholder for the specific model
T = TypeVar("T", bound=BaseModel)


class FieldHelperMixin(Generic[T]):
    """Mixin class to provide field functions to be used in NiceCRUD and NiceCRUDCard alike"""

    config: NiceCRUDConfig
    basemodeltype: Type[T]
    included_fields: list[tuple[str, FieldInfo]]

    def __init__(self) -> None:
        self.get_included_fields()

    def is_excluded(self, field_name: str, field_info: FieldInfo) -> bool:
        """Checks if a given field should be excluded from the card"""
        if not hasattr(self, "config") or not (isinstance(getattr(self, "config"), NiceCRUDConfig)):
            raise AttributeError("config not found")
        field_exclude = False
        extra = field_info.json_schema_extra
        if extra is not None and isinstance(extra, dict):
            field_exclude = extra.get("exclude", False) or False
            if not isinstance(field_exclude, bool):
                log.error(f"exclude can only be bool, you provided {type(field_exclude)}")
                field_exclude = False
        return field_info.exclude or field_name in self.config.additional_exclude or field_exclude

    def get_included_fields(self):
        """Get a list of fields to be included in the card"""
        self.included_fields = []
        for field_name, field_info in self.basemodeltype.model_fields.items():
            if not self.is_excluded(field_name=field_name, field_info=field_info):
                self.included_fields.append((field_name, field_info))

    @property
    def column_count(self):
        return self.config.column_count or max((int(len(self.included_fields) / 4), 1))

    @property
    def included_field_names(self):
        return [x[0] for x in self.included_fields]

    def field_exists(self, field_name: str):
        return field_name in self.basemodeltype.model_fields.keys()


class NiceCRUDCard(FieldHelperMixin, Generic[T]):
    """One card with inputs for one BaseModel object

    This is separate, so that it can be used stand alone.

    Attributes:
        item: The BaseModel object
        config: NiceCRUDConfig
        id_editable: sets if the config.id_field should be editable or not
        select_options: awaitable coroutine taking the field_name and one BaseModel object,
            returning the dictionary with the select options for that field
    """

    def __init__(
        self,
        item: T,
        select_options: Optional[Callable[[str, T], Awaitable[dict]]] = None,
        config: NiceCRUDConfig = NiceCRUDConfig(),
        id_editable: bool = True,
        on_change_extra: Optional[Callable[[str, T], None]] = None,
        on_validation_result: Callable[[bool], None] = lambda _: None,
        **kwargs,
    ):
        self.item: T = item
        self.config = config
        self.config.update(kwargs)
        self.id_editable = id_editable
        self.errormsg = dict(msg="", visible=False)
        self.select_options: Callable[[str, T], Awaitable[dict]]
        if select_options is not None:
            self.select_options = select_options
        else:

            async def default_select_options(field_name: str, obj: T):
                return dict()

            self.select_options = default_select_options
        self.on_change_extra = on_change_extra
        self.on_validation_result = on_validation_result
        self.subitem_dialog = None
        self.basemodeltype = type(item)
        super().__init__()
        # As create_card needs to be async, use timer to run it in the nicegui
        # asyncio event loop
        ui.timer(0, self.create_card, once=True)

    def onchange(self, value, attr: str = "", refresh: bool = False):
        """Called on every change of an input, tries to validate the BaseModel"""
        if hasattr(value, "value"):
            value = value.value
        log.debug(f"{attr=} {value=} {type(value)=}")
        try:
            self.errormsg["msg"] = ""
            self.errormsg["visible"] = False
            # Ensure, that integer remains integer
            if not isinstance(getattr(self.item, attr), bool) and isinstance(
                getattr(self.item, attr), int
            ):
                value = None if value is None else int(value)
            setattr(self.item, attr, value)
            val_result = True
        except ValidationError as e:
            self.errormsg["msg"] = e.errors()[0]["msg"]
            self.errormsg["msg"] = re.sub(r"^Value error, ", "", self.errormsg["msg"])
            self.errormsg["msg"] = re.sub(
                r"^Input should be a valid string",
                str(e.errors()[0]["loc"]).replace("(", "").replace(")", "").replace(",", "")
                + ": not a string",
                self.errormsg["msg"],
            )
            self.errormsg["visible"] = True
            val_result = False
        if self.on_change_extra is not None:
            self.on_change_extra(attr, self.item)
        self.on_validation_result(val_result)
        if refresh:
            self.create_card.refresh()  # pyright: ignore

    @ui.refreshable
    async def create_card(self):
        # with ui.column().classes("w-full"):
        grid_class = "gap-1 gap-x-6 w-full items-center"
        columns = "minmax(100px,max-content) 1fr " * self.column_count
        with ui.grid(columns=columns).classes(grid_class):
            for field_name, field_info in self.included_fields:
                if field_name == self.config.id_field and not self.id_editable:
                    continue
                await self.get_input(field_name, field_info)
        errlabel, errrow = show_error("")
        errlabel.bind_text_from(self.errormsg, "msg")
        errrow.bind_visibility_from(self.errormsg, "visible").classes("w-full")

    @staticmethod
    def get_min_max_from_field_info(
        field_info: FieldInfo,
    ) -> tuple[Optional[float], Optional[float]]:
        _min, _max = None, None
        for m in field_info.metadata:
            if isinstance(m, annotated_types.Gt):
                _min = m.gt + 0  # type: ignore
            elif isinstance(m, annotated_types.Ge):
                _min = m.ge + 0  # type: ignore
            elif isinstance(m, annotated_types.Lt):
                _max = m.lt - 0  # type: ignore
            elif isinstance(m, annotated_types.Le):
                _max = m.le + 0  # type: ignore
        return _max, _min

    async def get_input(self, field_name: str, field_info: FieldInfo):
        """From the field_info, derive the appropriate NiceGUI input element"""
        typ = field_info.annotation
        curval = getattr(self.item, field_name)
        validation = partial(self.onchange, attr=field_name)
        validation_refresh = partial(self.onchange, attr=field_name, refresh=True)
        with ui.label((field_info.title or field_name) + ":"):
            if field_info.description is not None:
                with ui.tooltip():
                    ui.html(field_info.description)
            else:
                pass
        _max, _min = self.get_min_max_from_field_info(field_info)
        # Metadata in json_schema_extra
        _step = None
        _input_type = None
        _readonly = False
        _selections = None
        extra = field_info.json_schema_extra
        if extra:
            assert isinstance(extra, dict)
            _step = extra.get("step")
            _input_type = extra.get("input_type")
            _readonly = extra.get("readonly", False)
            _selections = extra.get("selections")
        _optional = False
        # Generate the UI elements
        ele = None
        if typing.get_origin(typ) in {Union, UnionType}:
            # Optional Fields
            if len(typing.get_args(typ)) > 1 and typing.get_args(typ)[1] == type(None):
                typ = typing.get_args(typ)[0]
                _optional = True
            # Literal[BaseModel1, BaseModel2]
            elif all([issubclass(x, BaseModel) for x in typing.get_args(typ)]):
                _input_type = "basemodelswitcher"
        log.debug(f"{field_name=} {_input_type=} {typ=} {typing.get_origin(typ)=} ")
        if _input_type in ("select", "multiselect"):
            if _selections is not None:
                assert isinstance(_selections, dict)
                select_options_dict: dict[str, str] = _selections  # type: ignore
            else:
                select_options_dict = await self.select_options(field_name, self.item)
            if len(select_options_dict) == 0 and curval:
                select_options_dict = {curval: curval}
            log.debug(f"{field_name=}: selections = {select_options_dict}")
            log.debug(f"{field_name=}: {typing.get_origin(typ)=}")
            if (
                _input_type != "multiselect"
                and curval not in select_options_dict
                and len(select_options_dict) > 0
            ):
                curval = next(iter(select_options_dict.keys()))

            def list_to_dictval(x: list):
                return validation(dict.fromkeys(x))

            ele = ui.select(
                options=select_options_dict,
                value=curval if typing.get_origin(typ) is not dict else list(curval.keys()),  # type: ignore
                validation=validation if typing.get_origin(typ) is not dict else list_to_dictval,
                multiple=_input_type == "multiselect",
            ).props("use-chips" if _input_type == "multiselect" else "")
        elif _input_type == "basemodelswitcher":
            typemapper = {x.__name__: x for x in typing.get_args(typ)}
            selections = {
                x.__name__: x.model_config.get("title", x.__name__) for x in typing.get_args((typ))
            }
            log.debug(f"{field_name=}: selections = {selections}")
            if curval.__class__.__name__ not in selections and len(selections) > 0:
                log.warning(f"{curval.__class__.__name__=}: not found in selections")
                curval = next(iter(selections.keys()))

            with ui.row().classes("items-center justify-shrink w-full flex-nowrap"):
                # This is needed, to bin it to the label object
                label = dict(label=str(curval.model_dump(context=dict(gui=True))))
                # This is used to store settings for each BaseModel type
                stordict = dict()

                def handle_base_model_switch():
                    """Submodel is selected. Check if class changed to change to dialog later"""
                    nonlocal curval
                    if curval.__class__.__name__ != selecta.value:
                        # Save the settings for the current class for later use
                        stordict[curval.__class__.__name__] = curval.model_dump()
                        # Create a new object and make sure, that it is stored within main item
                        # Restore data from previous edits if possible
                        opts = stordict.get(selecta.value or "", dict())
                        # Load settings of previously selected class
                        curval = typemapper.get(selecta.value)(**opts)  # pyright: ignore
                        # Create a new object of the newly selected class
                        setattr(self.item, field_name, curval)
                        label["label"] = str(curval.model_dump(context=dict(gui=True)))

                selecta = ui.select(
                    options=selections,
                    value=curval.__class__.__name__,
                    on_change=lambda: handle_base_model_switch(),
                )
                lab = ui.label().classes("hidden").bind_text(label, "label")

                ele = (
                    ui.button(
                        icon="edit",
                        on_click=lambda: self.handle_edit_subitem(
                            getattr(self.item, field_name), lab
                        ),
                    )
                    .props("flat round")
                    .classes("text-lightprimary dark:primary")
                )
        elif typ is None:
            log.error(f"no type found for {self.item}")
            ui.label("ERROR")
        elif typ is str:
            # String Inputs
            ele = ui.input(
                value=curval, validation=validation, placeholder=field_info.description or ""
            )
            if _optional:
                ele.props("clearable")
        elif typ in (int, float):
            # Number inputs
            if _input_type == "number" or _input_type is None or _min is None or _max is None:
                ele = ui.number(
                    value=curval,
                    validation=validation,
                    min=_min,
                    max=_max,
                    step=_step,  # type: ignore
                )
                if _optional:
                    ele.props("clearable")
            elif _input_type == "slider":
                # slider is only available when min and max where set (see condition for number)
                ui.slider(
                    value=curval,
                    on_change=validation,
                    min=_min,
                    max=_max,
                    step=_step,  # type: ignore
                ).props("label-always").classes("my-4")
        elif typing.get_origin(typ) == Literal:
            ele = ui.select(
                [x for x in typing.get_args(typ)],
                value=curval,
                validation=validation_refresh,
            )
        elif typ is bool:
            ele = ui.switch(value=curval, on_change=validation_refresh)
        elif typ == BaseModel or (isinstance(typ, type) and issubclass(typ, BaseModel)):
            with ui.row().classes("items-center justify-shrink w-full flex-nowrap"):
                lab = ui.label(str(curval.model_dump(context=dict(gui=True)))).classes(
                    "text-slate-500"
                )
                clickfun = partial(self.handle_edit_subitem, curval, lab)
                ele = (
                    ui.button(icon="edit", on_click=clickfun)
                    .props("flat round")
                    .classes("text-lightprimary dark:primary")
                )
        elif typing.get_origin(typ) in (list, set) and typing.get_args(typ)[0] is str:
            ele = ui.input(value=",".join(curval), validation=lambda v: validation(v.split(",")))
        elif typing.get_origin(typ) is list and issubclass(typing.get_args(typ)[0], (int, float)):
            ele = ui.input(
                value=",".join(map(str, curval)), validation=lambda v: validation(v.split(","))
            )
        else:
            log.warning(f"Unknown input for {field_name=} of {typ=}")
            ele = ui.input(value="ERROR", validation=validation)
        if (_readonly and ele is not None) or (
            ele is not None and field_name == self.config.id_field and not self.id_editable
        ):
            ele.disable()

    def handle_edit_subitem(self, curval: BaseModel, lab: ui.label):
        log.debug(f"handle_edit_subitem {curval.model_dump(context=dict(gui=True))}")
        self.get_subitem_dialog(curval)
        if self.subitem_dialog is None:
            log.error(f"Dialog for {curval} will not open")
            return
        self.subitem_dialog.open()
        self.subitem_dialog.on(
            "before-hide", lambda: lab.set_text(str(curval.model_dump(context=dict(gui=True))))
        )

    def get_subitem_dialog(self, item: BaseModel):
        log.debug("get_subitem_dialog")
        with ui.dialog() as self.subitem_dialog, ui.card():
            title = item.model_config.get("title")
            if title is not None:
                ui.label(title).classes("text-lg")
            with ui.row():
                NiceCRUDCard(item=item, config=self.config)


class NiceCRUD(FieldHelperMixin[T], Generic[T]):
    """NiceGUI implementation of a CRUD application: CreateReplaceUpdateDelete

    Usage:
        Create a list of your pydantic.BaseModel objects.
        The BaseModel class has to be configured to validate_assignment:
        `model_dict = ConfigDict(validate_assignment=True)`

        Inherit from this class to adapt to your usecase. Overload the methods
        `create`, `update` and `delete`. These methods should return None and
        raise KeyError if the id_field of the updated or deleted item cannot be
        found.
    """

    def __init__(
        self,
        basemodeltype: Optional[Type[T]] = None,
        basemodels: list[T] = [],
        id_field: Optional[str] = None,
        config: NiceCRUDConfig | dict = NiceCRUDConfig(),
        **kwargs,  # Config parameters can be given by keyword arguments as well
    ):
        self.basemodeltype = basemodeltype or self.infer_basemodeltype(basemodels)
        if isinstance(config, dict):
            config = NiceCRUDConfig(**config, **kwargs)
        self.config: NiceCRUDConfig = config
        self.config.update(kwargs)
        if id_field is not None:
            self.config.id_field = id_field
        self.basemodels = basemodels
        super().__init__()
        self.rows: list[dict] = []
        self.columns: list[dict] = []
        self.assert_id_field_in_model()
        self.create_rows_and_cols()
        self.item_dialog: ui.dialog
        self.button_row: ui.row
        self.table: ui.table
        self.add_resize_trigger()
        self.get_button_row()
        self.show_table()  # type: ignore

    @classmethod
    def infer_basemodeltype(cls, basemodels: list[T] | dict[str, T]) -> Type[T]:
        x = cls.getfirst(basemodels)
        return type(x)

    @staticmethod
    def getfirst(basemodels: list[T] | dict[str, T]) -> T:
        if isinstance(basemodels, list):
            return basemodels[0]
        elif isinstance(basemodels, dict):
            return next(iter(basemodels.values()))
        else:
            raise KeyError("No basemodels given")

    def add_resize_trigger(self):
        """When the width of the browser window is reduced, the event "smaller"
        is emitted, "bigger" otherwise"""
        # TODO: Make the resize trigger in nicecrud more specific so it
        # triggers when the table is not visible in full.
        # https://www.javascripttutorial.net/dom/css/check-if-an-element-is-visible-in-the-viewport/
        ui.add_head_html("""
        <script>
            let previousWidth = window.innerWidth;
            window.addEventListener('resize', function() {
            var currentWidth = window.innerWidth;
            if (currentWidth < 400 && previousWidth >= 400) {
                console.log("Smaller")
                emitEvent("smaller");
            }
            if (currentWidth > 400 && previousWidth <= 400) {
                console.log("Bigger")
                emitEvent("bigger");
            }
            previousWidth = currentWidth;
            });
        </script>
        """)

    def assert_id_field_in_model(self):
        if self.config.id_field not in self.basemodeltype.model_fields.keys():
            raise KeyError(f"id field {self.config.id_field} not in basemodel")
        if not self.basemodeltype.model_config.get("validate_assignment"):
            log.info(
                f"Set validate_assignment for {self.basemodeltype.__name__} for nicecrud validation"
            )
            self.basemodeltype.model_config["validate_assignment"] = True

    @classmethod
    async def from_http_request(
        cls,
        url: str = "http://localhost:8000/something/",
        headers: dict[str, str] | None = None,
        basemodeltype: type[BaseModel] = BaseModel,
        config: NiceCRUDConfig = NiceCRUDConfig(),
        **kwargs,
    ):
        log.debug(f"Create CRUD application site from {url=}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=httpx.Headers(headers), follow_redirects=True)
        listofdicts = response.json()
        if not isinstance(listofdicts, list):
            ui.notify(f"Invalid response from {url}", color="negative")
            return None
        try:
            basemodels = [basemodeltype(**data) for data in listofdicts]
        except ValidationError as e:
            ui.notify(f"Invalid data from {url}", color="negative")
            log.error(f"ValidationError: {str(e)}")
            return None
        res = cls(basemodeltype=basemodeltype, basemodels=basemodels, config=config, **kwargs)  # pyright: ignore[reportArgumentType]
        return res

    @property
    def id_label(self):
        if self.config.id_label is not None:
            return self.config.id_label
        if self.config.id_field is None:
            return "ID:"
        id_title = self.basemodeltype.model_fields[self.config.id_field].title
        if id_title is not None:
            return id_title + ":"
        title = self.basemodeltype.model_config.get("title")
        if title is not None:
            return title + " ID:"
        return "ID:"

    def create_rows_and_cols(self):
        """Create the list of dicts self.rows and self.columns that are used for nicegui table"""
        rows, columns = basemodellist_to_rows_and_cols(self.basemodels)
        columns = [
            c | dict(sortable=True)
            for c in columns
            if c["name"] != self.config.id_field and c["name"] in self.included_field_names
        ]
        for r in rows:
            r["obj_id"] = (
                self.id_label + " <b>" + html.escape(str(r[self.config.id_field])) + "</b>"
            )
            for k, v in r.items():
                # loop over the fields in each row
                if not v and v != 0:
                    r[k] = "No value set"
        self.rows = rows
        self.columns = columns

    def get_by_id(self, id) -> Optional[T]:
        for m in self.basemodels:
            if getattr(m, self.config.id_field) == id:
                return m
        return None

    @property
    def defaults_given(self):
        for _, v in self.basemodeltype.model_fields.items():
            if v.exclude:
                continue
            if v.is_required():
                return False
        return True

    async def handle_create(self):
        """Add button was pressed"""
        try:
            self.get_item_dialog()
            self.item_dialog.open()
        except NotImplementedError as e:
            log.error(str(e))
            ui.notify(str(e), color="negative")

    async def save_create(self, model: T):
        """Save button in item_dialog was pressed"""
        try:
            await self.create(model)
            model_id = getattr(model, self.config.id_field)
        except KeyError as e:
            log.error(f"An error occurred while adding the model: {model}")
            ui.notify("Error adding model: " + str(e), color="negative")
        else:
            log.debug(f"Added {model_id=}")
            ui.notify(
                f"Added {self.basemodeltype.model_config.get('title')} with new ID: {model_id}"
            )
        finally:
            self.create_rows_and_cols()
            self.item_dialog.close()
            self.show_table.refresh()

    async def handle_update(self, e: events.GenericEventArguments) -> None:
        """Edit icon was pressed

        Args:
            e: Event argument with the row information passed from javascript
        """
        obj_id: str = e.args[self.config.id_field]
        log.debug(f"edit row with {obj_id=}")
        model = self.get_by_id(obj_id)
        if model is None:
            log.error(f"Error, could not find {obj_id=}")
            return
        try:
            self.get_item_dialog(model)
            self.item_dialog.open()
        except NotImplementedError as er:
            ui.notify(
                f"The {self.basemodeltype.__name__} objects have not template", color="negative"
            )
            log.error(str(er))

    async def save_update(self, model: T):
        """Save button in item_dialog was pressed"""
        try:
            await self.update(model)
        except KeyError as e:
            log.error(f"An error occurred while updating the model: {model}: {str(e)}")
            ui.notify(f"Error deleting: {str(e)}", color="negative")
        else:
            obj_id: str = getattr(model, self.config.id_field)
            title = self.basemodeltype.model_config.get("title") or self.config.id_label
            log.debug(f"Updated {obj_id=}")
            ui.notify(f"Updated {title} {obj_id}")
        finally:
            self.create_rows_and_cols()
            self.item_dialog.close()
            self.show_table.refresh()

    async def handle_delete(self, e: events.GenericEventArguments) -> None:
        """Delete icon was pressed

        Args:
            e: Event argument with the row information passed from javascript
        """
        obj_id: str = e.args[self.config.id_field]
        log.debug(f"delete row with {obj_id=}")
        try:
            await self.delete(obj_id)
        except KeyError as er:
            log.error(f"Deletion operation failed for object with id: {obj_id} {str(er)}")
            ui.notify(f"Error deleting: {str(er)}", color="negative")
        else:
            title = self.basemodeltype.model_config.get("title")
            ui.notify(f"Deleted {title} {obj_id}")
        finally:
            self.create_rows_and_cols()
            self.show_table.refresh()

    async def handle_delete_selected(self) -> None:
        """Delete selected icon was pressed"""
        ndel = len(self.table.selected)
        error = False
        for x in self.table.selected:
            obj_id = x.get(self.config.id_field)
            if obj_id is None:
                continue
            try:
                await self.delete(obj_id)
            except KeyError as e:
                log.error(f"delete row with {obj_id=} failed")
                ui.notify(f"Error deleting: {str(e)}", color="negative")
                error = True
                break
            else:
                log.debug(f"delete row with {obj_id=}")
        if not error:
            ui.notify(f"{ndel} deleted")
        self.create_rows_and_cols()
        self.show_table.refresh()

    async def create(self, model: T):
        """Add an item: Extend or this method and include database commands"""
        if getattr(model, self.config.id_field) in [
            getattr(m, self.config.id_field) for m in self.basemodels
        ]:
            raise KeyError(
                f"{self.basemodeltype.model_config.get('title', self.basemodeltype.__name__)}"
                f"({self.config.id_label}={getattr(model, self.config.id_field)}) already exists"
            )
        self.basemodels.append(model)

    async def update(self, model: T):
        """Update an item: Extend or overwrite this method and include database commands"""
        exists = False
        for m in self.basemodels:
            if getattr(m, self.config.id_field) == getattr(model, self.config.id_field):
                if exists:
                    raise KeyError(
                        f"{self.basemodeltype.model_config.get('title', self.basemodeltype.__name__)}"
                        f"({self.config.id_label}={getattr(model, self.config.id_field)}) has duplicates"
                    )
                exists = True
                for field, value in model.model_dump().items():
                    setattr(m, field, value)
        if not exists:
            raise KeyError(
                f"{self.basemodeltype.model_config.get('title', self.basemodeltype.__name__)}"
                f"({self.config.id_label}={getattr(model, self.config.id_field)}) does not exist"
            )

    async def delete(self, obj_id):
        """Delete item: Extend or overwrite this method and include database commands"""
        exists = False
        for b in self.basemodels:
            if getattr(b, self.config.id_field) == obj_id:
                exists = True
                self.basemodels.remove(b)
                break
        if not exists:
            raise KeyError(
                f"{self.basemodeltype.model_config.get('title', self.basemodeltype.__name__)}"
                f"({self.config.id_label}={obj_id}) does not exist"
            )

    async def select_options(self, field_name: str, obj: T) -> dict:
        """Get the select options for a field: Extend / Overwrite this method
        and include database commands

        By default, this just gives all the different occurrences in the list
        """
        log.debug(f"Getting default select_options for {field_name=}")
        options = dict()
        if not self.field_exists(field_name):
            log.error(
                f"Trying to get select options for {field_name=}, non-exist on {self.basemodeltype}"
            )
            return dict()
        for m in self.basemodels:
            if not isinstance(getattr(m, field_name), collections.abc.Hashable):
                if isinstance(getattr(m, field_name), (dict, list)):
                    for choice in getattr(m, field_name):
                        options[choice] = choice
                else:
                    log.warning(
                        f"No select options can be determined for non-hashable type {self.basemodeltype}"
                    )
                    options = dict()
            else:
                options[getattr(m, field_name)] = getattr(m, field_name)
        return options

    def on_change_extra(self, field_name: str, obj: T) -> None:
        """Extra callback that is triggered when field_name str was changed in
        the input Overwrite this method and include some changes to the
        object"""
        return

    @ui.refreshable
    def show_table(self):
        """Show the grid of elements"""
        with ui.card().classes("w-full sm:w-full"):
            if self.config.heading:
                ui.label(self.config.heading).classes(self.config.class_heading)
            search_input = ui.input(
                label=self.config.search_input_label
                or ("Search " + (self.basemodeltype.model_config.get("title") or "table"))
            ).classes("card-content w-full")
            self.table = (
                ui.table(
                    columns=self.columns,
                    rows=self.rows,
                    row_key="obj_id",
                    selection="multiple",
                )
                .props("grid")
                .props(f"no-data-label='{self.config.no_data_label}'")
                .classes("w-full")
            ).bind_filter_from(search_input, "value")

        self.table.add_slot(
            "item",
            r"""<q-card bordered flat :class=" """
            f"props.selected ?  '{self.config.class_card_selected}' : '{self.config.class_card}'"
            r""" "
                class="sm:w-[calc(50%-20px)] w-full m-2 relative">
                <div class="absolute top-0 right-0 z-10">
                    <q-btn class="mr-2 mt-2 z-10" size="sm" color="primary" round dense icon="delete"
                        @click="() => $parent.$emit('delete', props.row)"
                    />
                    <q-btn class="mr-2 mt-2 z-10" size="sm" color="primary" round dense icon="edit"
                        @click="() => $parent.$emit('edit', props.row)"
                    />
                </div>
                <q-card-section class="z-1 """
            + self.config.class_card_header
            + r""" ">
                <q-checkbox dense v-model="props.selected">
                    <span v-html="props.row.obj_id"></span>
                </q-checkbox>
                </q-card-section> 
                <q-card-section>
                    <div class="flex flex-row p-0 m-1 w-full gap-y-1">
                    <div class="p-2 border-l-2" v-for="col in props.cols.filter(col => col.name !== 'obj_id')" :key="col.obj_id" >
                        <q-item-label caption class="text-[#444444] dark:text-[#BBBBBB]">{{ col.label }}</q-item-label>
                        <q-item-label >{{ col.value }}</q-item-label>
                    </div>
                    </div>
                </q-card-section>
            </q-card>
            """,
        )

        self.table.on("delete", self.handle_delete)
        self.table.on("edit", self.handle_update)
        # if False:
        #     ui.on("smaller", lambda: self.table.props("grid"))
        #     ui.on("bigger", lambda: self.table.props(remove="grid"))

    def get_button_row(self):
        with ui.row() as self.button_row:
            ui.button(text=self.config.add_button_text, icon="add", on_click=self.handle_create)
            ui.button(
                text=self.config.delete_button_text,
                icon="delete",
                on_click=self.handle_delete_selected,
            )

    @property
    def new_item_dialog_heading(self):
        if self.config.new_item_dialog_heading is not None:
            return self.config.new_item_dialog_heading
        title = self.basemodeltype.model_config.get("title")
        if title is not None:
            return "Add " + title
        else:
            return "Add item"

    @property
    def update_item_dialog_heading(self):
        if self.config.update_item_dialog_heading is not None:
            return self.config.update_item_dialog_heading
        title = self.basemodeltype.model_config.get("title")
        if title is not None:
            return "Update " + title
        else:
            return "Update item"

    def get_item_dialog(self, item: T | None = None):
        if self.column_count > 1:
            props = "full-width"
        else:
            props = ""
        with ui.dialog().props(props) as self.item_dialog, ui.card().classes("w-full"):
            if item is None:
                edit = False
                ui.label(self.new_item_dialog_heading).classes(self.config.class_subheading)
                if self.defaults_given:
                    item = self.basemodeltype()
                elif len(self.basemodels) > 0:
                    log.debug(
                        f"model {self.basemodeltype} does not contain defaults for"
                        "all attributes, choose first element as reference"
                    )
                    item = self.basemodels[0].model_copy(deep=True)
                    if isinstance(getattr(item, self.config.id_field), str):
                        setattr(
                            item,
                            self.config.id_field,
                            "New "
                            + (self.basemodeltype.model_config.get("title", "item") or "item"),
                        )
                else:
                    raise NotImplementedError(f"No template for {self.basemodeltype.__name__}")

                async def save_action():
                    if item is None:
                        raise TypeError(f"Item {item} is non-existent")
                    await self.save_create(item)
            else:
                edit = True
                ui.label(
                    self.update_item_dialog_heading + " " + str(getattr(item, self.config.id_field))
                ).classes(self.config.class_subheading)

                async def save_action():
                    await self.save_update(item)

            # Card with all input elements
            val_result = dict(val_result=True)
            with ui.row().classes("w-full"):
                NiceCRUDCard(
                    item,
                    self.select_options,
                    config=self.config,
                    id_editable=not edit,
                    on_change_extra=self.on_change_extra,
                    on_validation_result=lambda x: val_result.update(dict(val_result=x)),
                )

            # Save and Cancel buttons
            with ui.row().classes("w-full justify-end"):
                with ui.grid(columns=2).classes("inline-grid"):
                    ui.button(
                        "Cancel",
                        icon="cancel",
                        on_click=self.item_dialog.close,
                        color=None,
                    ).classes("w-full bg-disabled")
                    ui.button(
                        "Save",
                        icon="check_circle",
                        on_click=save_action,
                    ).classes("w-full").bind_enabled_from(val_result, "val_result")
