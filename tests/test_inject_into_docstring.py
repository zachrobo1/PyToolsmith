import pytest

from pytoolsmith import ToolDefinition, ToolParameters
from pytoolsmith.inject_into_docstring import inject_into_docstring


def test_inject_into_docstring():
    """Test that the inject_into_docstring decorator correctly replaces placeholders."""
    # Define test variables
    test_vars = {
        "name": "PyToolsmith",
        "version": "1.0.0",
        "description": "A toolkit for Python developers"
    }

    # Create a function with placeholders in the docstring
    @inject_into_docstring(test_vars)
    def sample_function(_val_1: str):
        """
        This is a test function for {{name}} version {{version}}.

        {{description}}

        This placeholder {{name}} should be replaced multiple times.
        
        Args:
            _val_1: A placeholder for a value.
        
        """
        return True

    # Get the processed docstring
    docstring = sample_function.__doc__

    # Assert that all placeholders were replaced correctly
    assert "This is a test function for PyToolsmith version 1.0.0." in docstring
    assert "A toolkit for Python developers" in docstring
    assert "This placeholder PyToolsmith should be replaced multiple tim" in docstring

    assert "{{" not in docstring and "}}" not in docstring

    # Test that the function still works as expected
    assert sample_function("") is True

    # Pass the function into a tool:
    tool = ToolDefinition(function=sample_function)

    schema = tool.build_json_schema()
    exp_schema = ToolParameters(input_properties={
        '_val_1': {'type': 'string', 'description': 'A placeholder for a value.'}},
        required_parameters=['_val_1'], name='sample_function',
        description='This is a test function for PyToolsmith version 1.0.0.  '
                    'A toolkit for Python developers  This placeholder PyToolsmith '
                    'should be replaced multiple times.')

    assert schema == exp_schema


def test_inject_into_docstring_bad_variable_pairs():
    """Test that the inject_into_docstring decorator raises a TypeError."""
    # Test with non-string value
    with pytest.raises(
            TypeError,
            match="Expected a string value for count, but got <class 'int'>"):
        @inject_into_docstring({"count": 123})
        def function_with_int_value():
            """This function has {{count}} issues."""
            pass

    # Test with non-string key
    with pytest.raises(TypeError, match="Expected a string variable name for"):
        @inject_into_docstring({123: "value"})
        def function_with_int_key():
            """This function has {{123}} as a key."""
            pass
