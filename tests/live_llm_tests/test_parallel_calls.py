from collections.abc import Callable
import concurrent.futures
from typing import Any, cast

from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    ThinkingConfigEnabledParam,
    ToolUseBlock,
)
from pytest import mark

from pytoolsmith import ToolLibrary, pytoolsmith_config

_SYS_MESSAGE = ("You are a helpful assistant connected to a database. "
                "You can look up multiple people at once.")


def parallel_batch_runner(callables: list[Callable[[], Any]]) -> list[Any]:
    """
    Execute a list of callables in parallel using ThreadPoolExecutor.

    Args:
        callables: A list of callable functions with no arguments

    Returns:
        A list of results from the callables in the same order
    """
    print("Using parallel runner!")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit all callables to the executor
        future_to_index = {executor.submit(callable_func): i
                           for i, callable_func in enumerate(callables)}

        # Create a results list with the correct size
        results: list[Any | None] = [None] * len(callables)

        # As each future completes, store its result in the correct position
        for future in concurrent.futures.as_completed(future_to_index):
            index = future_to_index[future]
            try:
                results[index] = future.result()
            except Exception as exc:
                # If an exception occurs, store the exception as the result
                results[index] = exc

    return results


def test_parallel_batch_runner():
    """Test that the parallel batch runner executes functions sequentially, 
    just to make sure the other test work."""
    results = []

    def func1():
        results.append(1)
        return "one"

    def func2():
        results.append(2)
        return "two"

    def func3():
        results.append(3)
        return "three"

    callables = [func1, func2, func3]

    # Use the default batch runner
    output = parallel_batch_runner(callables)

    # Check that functions were executed in order
    assert results == [1, 2, 3]
    # Check that return values were collected correctly
    assert output == ["one", "two", "three"]


@mark.parametrize("use_batch_runner", [False, True])
@mark.llm_test
def test_batch_tool_for_anthropic(
        live_anthropic_client: Anthropic,
        basic_tool_library: ToolLibrary,
        use_batch_runner: bool
):
    if use_batch_runner:
        pytoolsmith_config.set_batch_runner(parallel_batch_runner)
    else:
        pytoolsmith_config.unset_batch_runner()

    result = live_anthropic_client.messages.create(
        system=_SYS_MESSAGE,
        tools=basic_tool_library.to_anthropic(use_cache_control=True),
        model="claude-3-7-sonnet-latest",
        messages=[
            MessageParam(
                role="user",
                content=[TextBlockParam(
                    text="Get the first name for users with IDs "
                         "123e4567-e89b-12d3-a456-426614174000 and "
                         "123e4567-e89b-12d3-a456-426614174012",
                    type="text")],
            )
        ],
        max_tokens=1025,
        temperature=1,
        thinking=ThinkingConfigEnabledParam(type="enabled", budget_tokens=1024)
    )

    tool_blocks = [bl for bl in result.content if isinstance(bl, ToolUseBlock)]
    assert len(tool_blocks) == 1
    tool_block = tool_blocks[0]
    assert tool_block.name == "batch_tool"
    exp_input = {'invocations': [
        {'name': 'get_users_name_from_id',
         'arguments': '{"user_id": "123e4567-e89b-12d3-a456-426614174000", '
                      '"fields_to_include": ["first_name"]}'},
        {'name': 'get_users_name_from_id',
         'arguments': '{"user_id": "123e4567-e89b-12d3-a456-426614174012", '
                      '"fields_to_include": ["first_name"]}'}]}

    assert exp_input == tool_block.input

    tool = basic_tool_library.get_tool_from_name(tool_block.name)

    tool_msg = tool.format_message_for_call(exp_input, {})
    assert tool_msg == "Looking up user(s)...\nLooking up user(s)..."

    tool_result = tool.call_tool(
        llm_parameters=cast(dict, tool_block.input),
        hardset_parameters={}
    )

    expected_tool_result = ("#0 (get_users_name_from_id) Result: Zach Cloud\n"
                            "#1 (get_users_name_from_id) Result: Zach Cloud")

    assert expected_tool_result == tool_result
