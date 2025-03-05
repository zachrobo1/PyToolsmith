from src.pytoolsmith import ToolDefinition, ToolLibrary


def _func_to_test_1():
    return None


def _func_to_test_2():
    return None


def test_get_tool_from_name(self):
    tool_1 = ToolDefinition(function=self._func_to_test_1)
    tool_2 = ToolDefinition(function=self._func_to_test_2)
    tool_library = ToolLibrary(tools=[tool_1, tool_2])
    self.assertEqual(tool_1, tool_library.get_tool_from_name("_func_to_test_1"))
    self.assertEqual(tool_2, tool_library.get_tool_from_name("_func_to_test_2"))
