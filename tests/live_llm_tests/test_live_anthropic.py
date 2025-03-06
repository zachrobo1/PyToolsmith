from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlockParam
from pytest import mark

from pytoolsmith import ToolLibrary


@mark.llm_test
def test_tool_library_for_anthropic(
        live_anthropic_client: Anthropic, basic_tool_library: ToolLibrary
):
    result = live_anthropic_client.messages.create(
        system="You are a helpful assistant connected to a database",
        tools=basic_tool_library.to_anthropic(),
        model="claude-3-7-sonnet-latest",
        messages=[
            MessageParam(
                role="user",
                content=[TextBlockParam(text="What can you do for me?", type="text")],
            )
        ],
        max_tokens=100,
    )
    for phrase in ["user", "ID", "name"]:
        assert phrase in result.content[0].text
