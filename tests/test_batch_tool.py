import json
from typing import Generator

from pytoolsmith import ToolDefinition, ToolLibrary, pytoolsmith_config


def  test_batch_tool():
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


def test_batch_tool_with_multiple_generators_and_strings():
    """
    Tests the batch_tool with a mix of tools:
    - Multiple tools that return generators.
    - Tools that return simple strings.
    - Ensures results and user messages are correctly aggregated.
    """

    # 1. Define tool functions for the test
    def yield_sequential_numbers(count: int, start_from: int = 0) -> Generator[str, None, None]:
        """Yields a sequence of numbers as strings."""
        for i in range(count):
            yield f"Num: {start_from + i}"

    def yield_alphabet_chunks(prefix: str, num_chunks: int, chunk_size: int = 2) -> Generator[str, None, None]:
        """Yields chunks of alphabet letters with a prefix."""
        base_ord = ord('A')
        for i in range(num_chunks):
            chunk = "".join([chr(base_ord + (i * chunk_size) + j) for j in range(chunk_size) if (i * chunk_size) + j < 26])
            if chunk:
                yield f"{prefix}-{chunk}"

    def greet_user(name: str) -> str:
        """Returns a simple greeting string."""
        return f"Hello, {name}!"

    def report_status(status_code: int) -> str:
        """Returns a status message."""
        return f"Status reported: {status_code}"

    numbers_gen_tool = ToolDefinition(
        function=yield_sequential_numbers,
        user_message="Generating {{count}} numbers starting from {{start_from}}."
    )
    alphabet_gen_tool = ToolDefinition(
        function=yield_alphabet_chunks,
        user_message="Generating {{num_chunks}} alphabet chunks with prefix '{{prefix}}'."
    )
    greeting_tool = ToolDefinition(
        function=greet_user,
        user_message="Greeting {{name}}."
    )
    status_tool = ToolDefinition(
        function=report_status,
        user_message="Reporting status code {{status_code}}."
    )

    library = ToolLibrary(include_batch_tool=True)
    library.add_tool(numbers_gen_tool)
    library.add_tool(alphabet_gen_tool)
    library.add_tool(greeting_tool)
    library.add_tool(status_tool)

    batch_tool_instance = library.get_tool_from_name("batch_tool")

    # 5. Define the parameters for the batch_tool invocation
    llm_invocation_params = {
        "invocations": [
            {
                "name": "greet_user",
                "arguments": json.dumps({"name": "Alice"})
            },
            {
                "name": "yield_sequential_numbers",
                "arguments": json.dumps({"count": 3, "start_from": 1})
            },
            {
                "name": "yield_alphabet_chunks",
                "arguments": json.dumps({"prefix": "Alpha", "num_chunks": 2, "chunk_size": 3})
            },
            {
                "name": "report_status",
                "arguments": json.dumps({"status_code": 200})
            },
            { # Another call to a generator tool
                "name": "yield_sequential_numbers",
                "arguments": json.dumps({"count": 2, "start_from": 10})
            }
        ]
    }

    current_schema_vars = library.get_schema_vars()

    aggregated_result, aggregated_user_message = batch_tool_instance.call_tool(
        llm_parameters=llm_invocation_params,
        hardset_parameters=current_schema_vars,
        include_message=True
    )

    # 7. Define expected outcomes and assert
    expected_aggregated_result = (
        "#0 (greet_user) Result: Hello, Alice!\n"
        "#1 (yield_sequential_numbers) Stream Result 0: Num: 1\n"
        "#1 (yield_sequential_numbers) Stream Result 1: Num: 2\n"
        "#1 (yield_sequential_numbers) Stream Result 2: Num: 3\n"
        "#2 (yield_alphabet_chunks) Stream Result 0: Alpha-ABC\n"
        "#2 (yield_alphabet_chunks) Stream Result 1: Alpha-DEF\n"
        "#3 (report_status) Result: Status reported: 200\n"
        "#4 (yield_sequential_numbers) Stream Result 0: Num: 10\n"
        "#4 (yield_sequential_numbers) Stream Result 1: Num: 11"
    )

    expected_aggregated_user_message = (
        "Greeting Alice.\n"
        "Generating 3 numbers starting from 1.\n"
        "Generating 2 alphabet chunks with prefix 'Alpha'.\n"
        "Reporting status code 200.\n"
        "Generating 2 numbers starting from 10."
    )

    assert aggregated_result == expected_aggregated_result, \
        f"Aggregated result mismatch.\nExpected:\n{expected_aggregated_result}\nGot:\n{aggregated_result}"

    assert aggregated_user_message == expected_aggregated_user_message, \
        f"Aggregated user message mismatch.\nExpected:\n{expected_aggregated_user_message}\nGot:\n{aggregated_user_message}"

    formatted_user_message_direct = batch_tool_instance.format_message_for_call(
        llm_parameters=llm_invocation_params,
        hardset_parameters=current_schema_vars
    )
    assert formatted_user_message_direct == expected_aggregated_user_message, \
        f"Directly formatted user message mismatch.\nExpected:\n{expected_aggregated_user_message}\nGot:\n{formatted_user_message_direct}"

