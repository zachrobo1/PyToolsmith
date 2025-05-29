"""
This tool helps Anthropic LLMs perform batch calls. See
https://github.com/anthropics/anthropic-cookbook/blob/main/tool_use/parallel_tools_claude_3_7_sonnet.ipynb
for more information.
"""
import types
from typing import TYPE_CHECKING, Any, Union, Generator

from .pytoolsmith_config.batch_runner import get_batch_runner
from .pytoolsmith_config.serialization import serialize_batch_tool_args
from .tool_definition import ToolDefinition
from .tool_parameters import ToolParameters

if TYPE_CHECKING:
    from .tool_library import ToolLibrary


def batch_tool(tool_library: "ToolLibrary",
               hardset_parameters: dict[str, Any],
               invocations: list[dict[str, Any]]) -> str:
    """
    Execute multiple tool calls simultaneously.
    Supports tools returning strings or generators.

    Args:
        tool_library: Dictionary mapping tool names to their implementation functions
        hardset_parameters: The set of hard-set parameters to pass through.
        invocations: List of tool invocations, each containing 'name' and 'arguments'

    Returns:
        String containing all the results, separated by newlines.
        Each tool's output is clearly demarcated.
        Generator outputs are streamed with part indicators.
    """
    batch_runner = get_batch_runner()
    funcs_to_call = []

    for i, invocation in enumerate(invocations):
        # Create a factory function that returns the actual function with proper closure
        def invocation_func_factory(idx: int, inv: dict[str, Any]):
            def func() -> str:
                tool_name = inv.get("name")
                if not tool_name:
                    return f"#{idx} (Unknown Tool) Error: Invocation missing 'name'."

                llm_parameters_str = inv.get("arguments", "{}")
                try:
                    llm_parameters = serialize_batch_tool_args(llm_parameters_str)
                except Exception as e:
                    return f"#{idx} ({tool_name}) Error: Could not parse arguments '{llm_parameters_str}': {e}"

                try:
                    tool = tool_library.get_tool_from_name(tool_name)
                except Exception as e:  # e.g., tool not found
                    return f"#{idx} ({tool_name}) Error: {e}"

                invocation_output_lines: list[str] = []
                base_prefix = f"#{idx} ({tool_name})"

                try:
                    # This call might return a string, another type, or a generator
                    tool_call_result: Union[str, Generator[Any, None, None], Any] = tool.call_tool(
                        llm_parameters=llm_parameters,
                        hardset_parameters=hardset_parameters
                    )

                    if isinstance(tool_call_result, types.GeneratorType):
                        stream_had_items = False
                        try:
                            for item_idx, item_content in enumerate(tool_call_result):
                                invocation_output_lines.append(
                                    f"{base_prefix} Stream Result {item_idx}: {str(item_content)}"
                                )
                                stream_had_items = True
                            if not stream_had_items:
                                invocation_output_lines.append(f"{base_prefix} Stream (empty)")
                        except Exception as e_stream_iter:
                            # Error occurred during generator iteration
                            # Add error message after any successfully streamed parts
                            invocation_output_lines.append(
                                f"{base_prefix} Stream Error: {str(e_stream_iter)}"
                            )
                    else:
                        # Static result (not a generator)
                        invocation_output_lines.append(
                            f"{base_prefix} Result: {str(tool_call_result)}"
                        )

                except Exception as e_tool_call:
                    # Error in tool.call_tool() itself, or if result_or_generator was not as expected
                    # This error message becomes the sole output for this invocation
                    invocation_output_lines = [
                        f"{base_prefix} Result (note: errored): {str(e_tool_call)}"
                    ]

                return '\n'.join(invocation_output_lines)

            return func

        funcs_to_call.append(invocation_func_factory(i, invocation))

    # batch_runner executes each func, each func returns a (potentially multi-line) string.
    # These strings are then joined by newlines.
    all_results = batch_runner(funcs_to_call)
    return '\n'.join(filter(None, all_results))  # Filter out empty strings if a func returns one


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
