from pyzigg.exceptions import UnsupportedTypeError


def test_unsupported_type_error_is_a_type_error():
    assert issubclass(UnsupportedTypeError, TypeError)


def test_unsupported_type_error_message_names_field_and_type():
    error = UnsupportedTypeError("weird_field", list[int])
    assert "weird_field" in str(error)
    assert "list[int]" in str(error)
    assert error.field_name == "weird_field"
    assert error.field_type == list[int]
