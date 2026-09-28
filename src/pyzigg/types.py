"""Marker types for annotating pydantic int fields with an explicit width/signedness.

Usage:
    class Model(BaseModel):
        count: Annotated[int, UInt16]
"""


class Int16:
    """Marks an ``int`` field as a signed 16-bit integer."""


class UInt16:
    """Marks an ``int`` field as an unsigned 16-bit integer."""


class Int32:
    """Marks an ``int`` field as a signed 32-bit integer."""


class UInt32:
    """Marks an ``int`` field as an unsigned 32-bit integer."""
