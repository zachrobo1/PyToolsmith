from copy import deepcopy
import datetime
from types import NoneType
from typing import Literal
import uuid

_ACCEPTED_TYPES = Literal[
    "string", "integer", "null", "object", "array", "boolean", "number"
]

_DEFAULT_TYPE_MAP: dict[type, _ACCEPTED_TYPES] = {
    str: "string",
    int: "integer",
    float: "number",
    dict: "object",
    list: "array",
    bool: "boolean",
    NoneType: "null",
    datetime.datetime: "string",
    uuid.UUID: "string",
}
"""Default type map to use"""

_DEFAULT_FORMAT_MAP: dict[type, str] = {
    datetime.datetime: "date-time",
    uuid.UUID: "uuid",
}
"""Default format map to use."""

_TYPE_MAP = deepcopy(_DEFAULT_TYPE_MAP)
_FORMAT_MAP = deepcopy(_DEFAULT_FORMAT_MAP)


def update_type_map(types_to_update: dict[type, _ACCEPTED_TYPES]):
    """
    Adds additional types to the type map, which maps parameter inputs to JSON schema 
    specs.
    Can be used to overwrite parameters as well as set new ones.

    Args:
        types_to_update: A dictionary of types to set

    Examples: Can pass in {ObjectID: "string"} to be able to handle functions that 
    required ObjectIDs in them.

    Returns: None

    """
    _TYPE_MAP.update(types_to_update)


def update_format_map(format_types_to_update: dict[type, str]):
    """
    Adds additional types to the format map, which maps types to the `format` parameter 
    on the definition.
    Can be used to overwrite parameters as well as set new ones.

    Args:
        format_types_to_update: A dictionary of types to set
        
    Returns: None

    """
    _FORMAT_MAP.update(format_types_to_update)


def reset_type_map():
    """Resets the type map to the default configuration."""
    global _TYPE_MAP
    _TYPE_MAP = deepcopy(_DEFAULT_TYPE_MAP)


def reset_format_map():
    """Resets the format map to the default configuration."""
    global _FORMAT_MAP
    _FORMAT_MAP = deepcopy(_DEFAULT_FORMAT_MAP)


def get_type_map():
    """Returns the type map as it is currently configured."""
    return _TYPE_MAP


def get_format_map():
    """Returns the format map as it is currently configured."""
    return _FORMAT_MAP
