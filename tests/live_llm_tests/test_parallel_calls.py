from typing import cast

from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    ThinkingConfigEnabledParam,
    ToolUseBlock,
)
from pytest import mark

from pytoolsmith import ToolLibrary

_SYS_MESSAGE = ("You are a helpful assistant connected to a database. "
                "You can look up multiple people at once.")


@mark.llm_test
def test_batch_tool_for_anthropic(
        live_anthropic_client: Anthropic, basic_tool_library: ToolLibrary
):
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
