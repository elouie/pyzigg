"""Convert annotated pydantic models into Apache Iceberg schemas."""

from pydantic.fields import FieldInfo
from pyiceberg.types import BooleanType, DoubleType, IcebergType, IntegerType, LongType, StringType

from pyzigg.exceptions import UnsupportedTypeError
from pyzigg.types import Int16, Int32, UInt16, UInt32

_INT_MARKER_TO_ICEBERG_TYPE = {
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


def _python_type_to_iceberg_type(field_name: str, annotation: type, metadata: tuple[object, ...]) -> IcebergType:
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
