import json

from pytoolsmith import ToolDefinition, ToolLibrary


def test_batch_tool():
    def square(x: int) -> str:
        return str(x * x)

    def errors() -> str:
        raise ValueError("This is an error")

    square_tool = ToolDefinition(function=square, user_message="Squaring {{x}}")
    error_tool = ToolDefinition(function=errors)

    library = ToolLibrary(include_batch_tool=True)
    library.add_tool(square_tool)
    library.add_tool(error_tool)

    tool_to_call = library.get_tool_from_name("batch_tool")
    llm_params = {"invocations": [
        {"name": "square",
         "arguments": json.dumps({"x": 2})},
        {"name": "square",
         "arguments": json.dumps({"x": 3})},
        {"name": "errors",
         "arguments": "{}"}
    ]}

    result = tool_to_call.call_tool(llm_params, {})
    assert result == ("#0 (square) Result: 4\n#1 (square) Result: 9\n"
                      "#2 (errors) Result (note: errored): This is an error")

    call_message = tool_to_call.format_message_for_call(llm_params, {})
    assert call_message == "Squaring 2\nSquaring 3"
