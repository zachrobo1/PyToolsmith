import uuid

import pytoolsmith


def test_update_type_mapping():
    """Add something new, plus update the `int` type."""
    pytoolsmith.config.update_type_map({bytes: "string", int: "number"})

    type_map = pytoolsmith.config.get_type_map()

    assert type_map[bytes] == "string"
    assert type_map[int] == "number"

    pytoolsmith.config.reset_type_map()

    type_map = pytoolsmith.config.get_type_map()

    assert bytes not in type_map
    assert type_map[int] == "integer"


def test_update_format_mapping():
    """Add something new, plus update the `uuid` type."""
    pytoolsmith.config.update_format_map({bytes: "bytes", uuid.UUID: "number"})

    format_map = pytoolsmith.config.get_format_map()

    assert format_map[bytes] == "bytes"
    assert format_map[uuid.UUID] == "number"

    pytoolsmith.config.reset_format_map()

    format_map = pytoolsmith.config.get_format_map()

    assert bytes not in format_map
    assert format_map[uuid.UUID] == "uuid"
