"""Convert annotated pydantic models into Apache Iceberg schemas."""

import types
import typing
from typing import Any

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from pyiceberg.schema import Schema
from pyiceberg.types import BooleanType, DoubleType, IcebergType, IntegerType, LongType, NestedField, StringType

from pyzigg.exceptions import UnsupportedTypeError
from pyzigg.types import Int16, Int32, UInt16, UInt32

_INT_MARKER_TO_ICEBERG_TYPE: dict[type, IntegerType | LongType] = {
    Int16: IntegerType(),
    UInt16: IntegerType(),
    Int32: IntegerType(),
    UInt32: LongType(),
}


def _int_field_to_iceberg_type(metadata: tuple[object, ...]) -> IntegerType | LongType:
    """Map an ``int`` field's Annotated metadata to an Iceberg integer type.

    Iceberg has no unsigned or 16-bit integer type, so ``Int16``/``UInt16``/``Int32``
    (and plain, unmarked ``int``) map to the 32-bit ``IntegerType``, while ``UInt32``
    widens to the 64-bit ``LongType`` since its max value overflows a 32-bit signed int.
    """
    for marker in metadata:
        if marker in _INT_MARKER_TO_ICEBERG_TYPE:
            return _INT_MARKER_TO_ICEBERG_TYPE[marker]
    return IntegerType()


_PRIMITIVE_TYPE_TO_ICEBERG_TYPE: dict[type, IcebergType] = {
    str: StringType(),
    float: DoubleType(),
    bool: BooleanType(),
}


def _python_type_to_iceberg_type(field_name: str, annotation: Any, metadata: tuple[object, ...]) -> IcebergType:
    """Map a (non-Optional) field annotation to an Iceberg type, or raise ``UnsupportedTypeError``."""
    if annotation is int:
        return _int_field_to_iceberg_type(metadata)
    if annotation in _PRIMITIVE_TYPE_TO_ICEBERG_TYPE:
        return _PRIMITIVE_TYPE_TO_ICEBERG_TYPE[annotation]
    raise UnsupportedTypeError(field_name, annotation)


def _is_required(field_info: FieldInfo) -> bool:
    """Mirror pydantic's own notion of required: True unless a default (incl. ``None``) is set.

    Note pydantic v2 does *not* implicitly default a bare ``Optional[T]`` to ``None`` the
    way pydantic v1 did, so an ``Optional[int]`` field with no explicit default is still
    required here, matching pydantic's own validation behavior.
    """
    return field_info.is_required()


def _unwrap_optional(annotation: Any, metadata: tuple[object, ...]) -> tuple[Any, tuple[object, ...]]:
    """Strip an ``Optional[...]`` wrapper (either spelling) down to its inner type + metadata.

    A field declared as ``Optional[Annotated[int, UInt16]]`` keeps the ``Annotated`` wrapper
    nested inside the ``Optional`` in pydantic's ``FieldInfo.annotation`` rather than having it
    hoisted into ``FieldInfo.metadata`` (pydantic only does that hoist for a top-level Annotated),
    so both layers need unwrapping here. A non-Optional Union (more than one non-None arm) is
    passed through unchanged so the caller reports it as unsupported.
    """
    if typing.get_origin(annotation) not in (typing.Union, types.UnionType):
        return annotation, metadata
    non_none_args = [arg for arg in typing.get_args(annotation) if arg is not type(None)]
    if len(non_none_args) != 1:
        return annotation, metadata
    inner = non_none_args[0]
    if typing.get_origin(inner) is typing.Annotated:
        inner_args = typing.get_args(inner)
        return inner_args[0], inner_args[1:]
    return inner, metadata


def to_iceberg_schema(model: type[BaseModel]) -> Schema:
    """Convert a pydantic model class into an Apache Iceberg ``Schema``.

    Fields are assigned sequential Iceberg ``field_id``s (starting at 1) in the model's
    declaration order. See ``pyzigg.types`` for the int-width marker types, and
    ``pyzigg.exceptions.UnsupportedTypeError`` for the error raised on unmappable fields.
    """
    fields = []
    for field_id, (name, field_info) in enumerate(model.model_fields.items(), start=1):
        annotation, metadata = _unwrap_optional(field_info.annotation, tuple(field_info.metadata))
        iceberg_type = _python_type_to_iceberg_type(name, annotation, metadata)
        fields.append(
            NestedField(
                field_id=field_id,
                name=name,
                field_type=iceberg_type,
                required=_is_required(field_info),
            )
        )
    return Schema(*fields)
