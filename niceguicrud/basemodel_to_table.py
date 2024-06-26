from typing import Optional, Sequence

from pydantic import BaseModel


def basemodel_to_columns(
    bm: type[BaseModel],
    exclude: set[str] = set(),
    include: Optional[set[str]] = None,
) -> list[dict]:
    """Given a pydantic BaseModel type (class derived from BaseModel) return
    columns in list of dict format to be used with nicegui `ui.table`

    Args:
        bm: pydantic BaseModel type
        exclude: set of fields to be excluded
        include: set of fields to be included, None if all fields should be
            included (if not specifically excluded with the exclude argument)

    Returns:
        list of dict with column information for nicegui (name, label, field)
    """
    columns = []
    for fieldname, fieldinfo in bm.model_fields.items():
        if fieldname in exclude:
            continue
        if include is not None and fieldname not in include:
            continue
        if not fieldinfo.exclude:
            columns.append(
                dict(name=fieldname, label=fieldinfo.title or fieldname, field=fieldname)
            )
    return columns


def basemodellist_to_rows(
    bmlist: Sequence[BaseModel],
    exclude: set[str] = set(),
    include: Optional[set[str]] = None,
) -> list[dict]:
    rows = []
    for bm in bmlist:
        rr = bm.model_dump(include=include, exclude=exclude, context=dict(gui=True))
        rows.append(rr)
    return rows


def basemodellist_to_rows_and_cols(
    bmlist: Sequence[BaseModel],
    exclude: set[str] = set(),
    include: Optional[set[str]] = None,
) -> tuple[list[dict], list[dict]]:
    if not bmlist:
        return [], []
    columns = basemodel_to_columns(bmlist[0].__class__, exclude, include)
    rows = basemodellist_to_rows(bmlist, exclude, include)
    return rows, columns
