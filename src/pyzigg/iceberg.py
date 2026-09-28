"""Convert annotated pydantic models into Apache Iceberg schemas."""

from pyiceberg.types import IntegerType, LongType

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
