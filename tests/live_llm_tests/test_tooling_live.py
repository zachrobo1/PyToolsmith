from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlockParam
from pytest import mark

from pytoolsmith import ToolLibrary

_SYS_MESSAGE = "You are a helpful assistant connected to a database."


@mark.llm_test
def test_tool_library_for_anthropic(
        live_anthropic_client: Anthropic, basic_tool_library: ToolLibrary
):
    result = live_anthropic_client.messages.create(
        system=_SYS_MESSAGE,
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


@mark.llm_test
def test_tool_library_for_bedrock(live_bedrock_client, basic_tool_library: ToolLibrary):
    result = live_bedrock_client.converse(
        system=[{"text": _SYS_MESSAGE}],
        toolConfig=basic_tool_library.to_bedrock(),
        modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=[
            MessageParam(
                role="user",
                content=[{"text": "What can you do for me?"}],
            )
        ],
        inferenceConfig={"maxTokens": 100},
    )["output"]["message"]
    for phrase in ["user", "ID", "name"]:
        assert phrase in result["content"][0]["text"]
