from pyiceberg.types import IntegerType, LongType

from pyzigg.iceberg import _int_field_to_iceberg_type
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
