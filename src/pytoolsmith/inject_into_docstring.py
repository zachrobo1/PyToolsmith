from functools import wraps
import inspect


def inject_into_docstring(variable_pairs: dict[str, str]):
    """
    A decorator that substitutes variables in a docstring with the provided values.
    Useful to inject descriptions into a docstring at runtime.

    Args:
        variable_pairs: A dictionary of variable names and the values to inject
    Returns:
        A decorator function that will modify the docstring of the decorated function.
    """

    for var, value in variable_pairs.items():
        if not isinstance(value, str):
            raise TypeError(f"Expected a string value for {var}, but got {type(value)}")
        if not isinstance(var, str):
            raise TypeError(
                f"Expected a string variable name for {var}, but got {type(var)}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Get the original docstring
        docstring = inspect.getdoc(func) or ""

        # Replace the placeholder with the provided description
        for var, value in variable_pairs.items():
            docstring = docstring.replace("{{" + var + "}}", value)

        # Set the new docstring
        wrapper.__doc__ = docstring

        return wrapper

    return decorator
