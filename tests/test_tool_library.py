from pytoolsmith import ToolDefinition, ToolLibrary


def _func_to_test_1(a: str) -> str:
    return a


def _func_to_test_2() -> str | None:
    return None


def test_get_tool_from_name():
    tool_1 = ToolDefinition(function=_func_to_test_1)
    tool_2 = ToolDefinition(function=_func_to_test_2)
    tool_library = ToolLibrary([])
    tool_library.add_tool(tool_1)
    tool_library.add_tool(tool_2)
