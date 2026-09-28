"""Exceptions raised by pyzigg's schema converters."""


class UnsupportedTypeError(TypeError):
    """Raised when a pydantic field's type has no known target-framework mapping."""

    def __init__(self, field_name: str, field_type: object) -> None:
        self.field_name = field_name
        self.field_type = field_type
        super().__init__(f"Field {field_name!r} has unsupported type {field_type!r}")
