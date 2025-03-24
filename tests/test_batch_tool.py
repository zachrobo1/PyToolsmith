import json

from pytoolsmith import ToolDefinition, ToolLibrary, pytoolsmith_config


def test_batch_tool():
    def square(x: int) -> str:
        return str(x * x)

    def errors() -> str:
        raise ValueError("This is an error")

    used_json_strs = []

    def custom_serializer(json_str: str) -> dict:
        nonlocal used_json_strs
        used_json_strs.append(json_str)
        return json.loads(json_str)

    pytoolsmith_config.set_batch_tool_serializer(custom_serializer)

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

    result, call_message_1 = tool_to_call.call_tool(
        llm_params, {}, include_message=True)
    assert result == ("#0 (square) Result: 4\n#1 (square) Result: 9\n"
                      "#2 (errors) Result (note: errored): This is an error")

    # Should be twice as `include_message` will also use the function.
    assert used_json_strs == [
        '{"x": 2}',
        '{"x": 3}',
        '{}',
        '{"x": 2}',
        '{"x": 3}',
        '{}'
    ]

    call_message_2 = tool_to_call.format_message_for_call(llm_params, {})
    for msg in [call_message_1, call_message_2]:
        assert msg == "Squaring 2\nSquaring 3"
