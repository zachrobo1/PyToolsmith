from typing import Any

from src.pytoolsmith.tool_definition import ToolDefinition


class ToolLibrary:

    def __init__(self, injectable_parameters: list[str]):
        self._injectable_parameters = injectable_parameters
        self._tools: dict[str, ToolDefinition] = {}

    def add_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        self._tools[tool.name] = tool

    # def call_tool(self, tool_name: str, llm_parameters: dict[str, Any], injected_parameters: dict[str, Any]):
    #     if tool_name not in self._tools:
    #         raise ValueError(f"No such tool: {tool_name}")
    #
    #     return self._tools[tool_name].call_tool(llm_parameters, injected_parameters)


def test_func(a: int, b: bool) -> int:
    """
    A test function to test.
    Args:
        a: An int
        b: A bool

    Returns: Sum of int and bool ha ha ha

    """
    return a + int(b)


if __name__ == "__main__":
    library = ToolLibrary(injectable_parameters=["t_id", "user_id"])
    tool = ToolDefinition(function=test_func)

    library.add_tool(tool)
