from typing import Any


def remove_keys(obj: Any, keys_to_remove: list[str]) -> Any:
    """
    Recursively remove keys from dictionaries.

    Args:
        obj: The object to process, typically a dict or a list containing dicts
        keys_to_remove: A list of keys to remove from the object recursively.

    Returns:
        The object with all keys removed at any nesting level
    """
    if isinstance(obj, dict):
        new_dict = {k: remove_keys(v, keys_to_remove) for k, v in obj.items()
                    if k not in keys_to_remove}
        return new_dict
    elif isinstance(obj, list):
        return [remove_keys(item, keys_to_remove) for item in obj]
    else:
        return obj
