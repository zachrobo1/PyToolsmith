import pytest

from pytoolsmith import ToolDefinition, ToolLibrary


def _func_to_test_1(a: str) -> str:
    return a


def _func_to_test_2(b: str) -> str:
    return b


@pytest.fixture
def filled_tool_library():
    tool_1 = ToolDefinition(function=_func_to_test_1)
    tool_2 = ToolDefinition(function=_func_to_test_2)
    tool_library = ToolLibrary()
    tool_library.add_tool(tool_1)
    tool_library.add_tool(tool_2)

    return tool_library


@pytest.mark.parametrize("method", ["to_anthropic", "to_openai", "to_bedrock"])
def test_to_x_works(filled_tool_library, method):
    """Tests each of the methods run."""
    getattr(filled_tool_library, method)()


def test_cast_library_to_anthropic(filled_tool_library):
    anthropic_result = filled_tool_library.to_anthropic()

    exp_result = [
        {
            "cache_control": None,
            "description": "",
            "input_schema": {"properties": {"a": {"type": "string"}}, "type": "object"},
            "name": "_func_to_test_1",
        },
        {
            "cache_control": None,
            "description": "",
            "input_schema": {"properties": {"b": {"type": "string"}}, "type": "object"},
            "name": "_func_to_test_2",
        },
    ]

    assert anthropic_result == exp_result


def test_get_tool_from_name(filled_tool_library):
    with pytest.raises(ValueError) as excinfo:
        filled_tool_library.get_tool_from_name("_some_other_tool")
    assert excinfo.value.args[0] == "Tool not found: _some_other_tool"

    assert filled_tool_library.get_tool_from_name("_func_to_test_1") == ToolDefinition(
        function=_func_to_test_1)
