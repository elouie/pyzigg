def test_public_api_exports():
    from pyzigg import Int16, Int32, UInt16, UInt32, UnsupportedTypeError, to_iceberg_schema

    assert all([Int16, Int32, UInt16, UInt32, UnsupportedTypeError, to_iceberg_schema])
