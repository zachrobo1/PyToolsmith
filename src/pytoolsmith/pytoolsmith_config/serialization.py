from collections.abc import Callable
import json

_BATCH_TOOL_SERIALIZER = json.loads


def set_batch_tool_serializer(serializer: Callable[[str], dict]):
    """
    Update the batch tool serializer to be a custom function.
    The function should take a JSON string and return a dictionary of the arguments
    used for the batch tool.
    """
    global _BATCH_TOOL_SERIALIZER
    _BATCH_TOOL_SERIALIZER = serializer


def serialize_batch_tool_args(arguments: str) -> dict:
    """
    Serialize the arguments for the batch tool.
    """
    return _BATCH_TOOL_SERIALIZER(arguments)
