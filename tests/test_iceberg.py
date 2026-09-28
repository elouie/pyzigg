from typing import Annotated

from pydantic import BaseModel
from pyiceberg.types import BooleanType, DoubleType, IntegerType, LongType, StringType

from pyzigg.exceptions import UnsupportedTypeError
from pyzigg.iceberg import _int_field_to_iceberg_type, _is_required, _python_type_to_iceberg_type, to_iceberg_schema
from pyzigg.types import Int16, Int32, UInt16, UInt32


def test_int16_maps_to_integer_type():
    assert _int_field_to_iceberg_type((Int16,)) == IntegerType()


def test_uint16_maps_to_integer_type():
    assert _int_field_to_iceberg_type((UInt16,)) == IntegerType()


def test_int32_maps_to_integer_type():
    assert _int_field_to_iceberg_type((Int32,)) == IntegerType()


def test_uint32_maps_to_long_type():
    assert _int_field_to_iceberg_type((UInt32,)) == LongType()


def test_plain_int_with_no_marker_maps_to_integer_type():
    assert _int_field_to_iceberg_type(()) == IntegerType()


def test_str_maps_to_string_type():
    assert _python_type_to_iceberg_type("f", str, ()) == StringType()


def test_float_maps_to_double_type():
    assert _python_type_to_iceberg_type("f", float, ()) == DoubleType()


def test_bool_maps_to_boolean_type():
    assert _python_type_to_iceberg_type("f", bool, ()) == BooleanType()


def test_plain_int_dispatches_through_int_mapping():
    assert _python_type_to_iceberg_type("f", int, (UInt32,)) == LongType()


def test_list_type_is_unsupported():
    error = None
    try:
        _python_type_to_iceberg_type("items", list[int], ())
    except UnsupportedTypeError as exc:
        error = exc
    assert error is not None
    assert error.field_name == "items"


def test_dict_type_is_unsupported():
    error = None
    try:
        _python_type_to_iceberg_type("attrs", dict, ())
    except UnsupportedTypeError as exc:
        error = exc
    assert error is not None
    assert error.field_name == "attrs"


def test_nested_basemodel_is_unsupported():
    class Nested(BaseModel):
        x: int

    error = None
    try:
        _python_type_to_iceberg_type("nested", Nested, ())
    except UnsupportedTypeError as exc:
        error = exc
    assert error is not None
    assert error.field_name == "nested"


def test_non_optional_union_is_unsupported():
    error = None
    try:
        _python_type_to_iceberg_type("mixed", int | str, ())
    except UnsupportedTypeError as exc:
        error = exc
    assert error is not None
    assert error.field_name == "mixed"


def test_field_with_no_default_is_required():
    class Model(BaseModel):
        value: int

    assert _is_required(Model.model_fields["value"]) is True


def test_field_with_default_is_not_required():
    class Model(BaseModel):
        value: int = 5

    assert _is_required(Model.model_fields["value"]) is False


def test_optional_field_with_no_default_is_still_required():
    class Model(BaseModel):
        value: int | None

    assert _is_required(Model.model_fields["value"]) is True


def test_optional_field_with_explicit_none_default_is_not_required():
    class Model(BaseModel):
        value: int | None = None

    assert _is_required(Model.model_fields["value"]) is False


def test_to_iceberg_schema_end_to_end():
    class Model(BaseModel):
        id: Annotated[int, Int32]
        small: Annotated[int, UInt16]
        big: Annotated[int, UInt32]
        plain_count: int
        name: str
        score: float
        is_active: bool
        nickname: str | None = None

    schema = to_iceberg_schema(Model)
    fields = list(schema.fields)

    assert [f.name for f in fields] == [
        "id",
        "small",
        "big",
        "plain_count",
        "name",
        "score",
        "is_active",
        "nickname",
    ]
    assert [f.field_id for f in fields] == [1, 2, 3, 4, 5, 6, 7, 8]

    by_name = {f.name: f for f in fields}
    assert by_name["id"].field_type == IntegerType()
    assert by_name["small"].field_type == IntegerType()
    assert by_name["big"].field_type == LongType()
    assert by_name["plain_count"].field_type == IntegerType()
    assert by_name["name"].field_type == StringType()
    assert by_name["score"].field_type == DoubleType()
    assert by_name["is_active"].field_type == BooleanType()
    assert by_name["nickname"].field_type == StringType()

    assert by_name["id"].required is True
    assert by_name["nickname"].required is False


def test_to_iceberg_schema_raises_on_unsupported_field():
    class Model(BaseModel):
        items: list[int]

    try:
        to_iceberg_schema(Model)
        raised = False
    except UnsupportedTypeError as exc:
        raised = True
        assert exc.field_name == "items"
    assert raised
