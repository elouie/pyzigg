# pyzigg

Annotate pydantic models with explicit data-framework types, and translate
them into real schema objects for other frameworks — Apache Iceberg to
start, with Delta Lake, pyarrow, and Avro planned.

## Install

```bash
uv sync
```

## Usage

```python
from typing import Annotated

from pydantic import BaseModel
from pyzigg import UInt16, UInt32, to_iceberg_schema


class Sensor(BaseModel):
    id: Annotated[int, UInt32]
    reading_count: Annotated[int, UInt16]
    label: str


schema = to_iceberg_schema(Sensor)
print(schema)
# table {
#   1: id: required long
#   2: reading_count: required int
#   3: label: required string
# }
```

Iceberg has no unsigned or 16-bit integer type, so `pyzigg` maps by
value-range safety: `Int16`, `UInt16`, `Int32`, and plain `int` all become
Iceberg's 32-bit `int`, while `UInt32` widens to Iceberg's 64-bit `long`
since its max value (4294967295) overflows a 32-bit signed integer.

A field's Iceberg `required` flag mirrors pydantic's own
`FieldInfo.is_required()`: a field is required unless it has a default
(including an explicit `None` default). Note that in pydantic v2, a bare
`Optional[int]` with no default is still required — only assigning it a
default makes it optional.

Passing a model with a field type that has no mapping (nested `BaseModel`s,
`list`, `dict`, non-`Optional` `Union`s) raises
`pyzigg.UnsupportedTypeError`, naming the offending field.

## Roadmap / non-goals (v1)

- No Delta Lake, pyarrow, or Avro converters yet.
- No nested/complex types (lists, dicts, nested models, non-`Optional`
  unions) — these raise rather than being silently coerced.
- No runtime value-bounds validation (e.g. rejecting `70000` for a
  `UInt16` field) — v1 is schema-level translation only.
- No CLI.
- No Iceberg catalog/table integration — only an in-memory
  `pyiceberg.schema.Schema` is produced.

## Development

```bash
uv sync --dev
uv run pytest
uv run ruff check .
uv run ruff format .
```
