import json
from typing import TYPE_CHECKING, Any

from .tool_definition import ToolDefinition
from .tool_parameters import ToolParameters

if TYPE_CHECKING:
    from .tool_library import ToolLibrary


def batch_tool(tool_library: "ToolLibrary",
               hardset_parameters: dict[str, Any],
               invocations: list[dict[str, Any]]) -> str:
    """
    Execute multiple tool calls simultaneously.

    Args:
        tool_library: Dictionary mapping tool names to their implementation functions
        hardset_parameters: The set of hard-set parameters to pass through.
        invocations: List of tool invocations, each containing 'name' and 'arguments'

    Returns:
        String containing all the results, separated by newlines
    """
    results = []
    for i, invocation in enumerate(invocations):
        tool_name = invocation.get("name")
        llm_parameters = json.loads(invocation.get("arguments", "{}"))

        tool = tool_library.get_tool_from_name(tool_name)

        try:
            result = str(tool.call_tool(
                llm_parameters=llm_parameters,
                hardset_parameters=hardset_parameters
            ))
            results.append(f"#{i} ({tool_name}) Result: {result}")
        except Exception as e:
            result = str(e)
        results.append(f"#{i} ({tool_name}) Result: {result}")

    return '\n'.join(results)


batch_tool_definition = ToolDefinition(function=batch_tool,
                                       injected_parameters=["tool_library",
                                                            "hardset_parameters"])

batch_tool_parameters = ToolParameters(
    name="batch_tool",
    description="Execute multiple tool calls simultaneously for improved efficiency",
    required_parameters=["invocations"],
    input_properties={
        "invocations": {
            "type": "array",
            "description": "The tool calls to execute in parallel",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the tool to invoke"
                    },
                    "arguments": {
                        "type": "string",
                        "description": "The arguments to the tool as a JSON string"
                    }
                },
                "required": ["name", "arguments"]
            }
        }
    }
)
