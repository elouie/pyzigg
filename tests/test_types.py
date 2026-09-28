from typing import Annotated

import pytest
from pydantic import BaseModel

from pyzigg.types import Int16, Int32, UInt16, UInt32

MARKERS = [Int16, UInt16, Int32, UInt32]


@pytest.mark.parametrize("marker", MARKERS)
def test_marker_usable_as_annotated_metadata(marker):
    class Model(BaseModel):
        value: Annotated[int, marker]

    instance = Model(value=1)
    assert instance.value == 1
    field_metadata = Model.model_fields["value"].metadata
    assert marker in field_metadata


def test_markers_are_distinct():
    assert len({Int16, UInt16, Int32, UInt32}) == 4
