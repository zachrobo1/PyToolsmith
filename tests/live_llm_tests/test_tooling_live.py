from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlockParam
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pytest import mark

from pytoolsmith import ToolLibrary

_SYS_MESSAGE = "You are a helpful assistant connected to a database."
_USER_MESSAGE = "What do you need to look up someone? What can you return for me?"

PHRASES = ["user", "id", "name", "email", "phone"]


@mark.llm_test
@mark.parametrize("cache_control", [False, True])
def test_tool_library_for_anthropic(
        live_anthropic_client: Anthropic, basic_tool_library: ToolLibrary, cache_control
):
    result = live_anthropic_client.messages.create(
        system=_SYS_MESSAGE,
        tools=basic_tool_library.to_anthropic(use_cache_control=cache_control),
        model="claude-3-7-sonnet-latest",
        messages=[
            MessageParam(
                role="user",
                content=[TextBlockParam(text=_USER_MESSAGE, type="text")],
            )
        ],
        max_tokens=100,
    )
    for phrase in PHRASES:
        assert phrase in result.content[0].text.lower()


@mark.llm_test
@mark.parametrize("strict_mode", [True, False])
def test_tool_library_for_openai(
        live_openai_client: OpenAI, basic_tool_library: ToolLibrary, strict_mode: bool
):
    result = live_openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            ChatCompletionSystemMessageParam(role="system", content=_SYS_MESSAGE),
            ChatCompletionUserMessageParam(role="user", content=_USER_MESSAGE)
        ],
        tools=basic_tool_library.to_openai(strict_mode=strict_mode),
        max_completion_tokens=100,
    )
    for phrase in PHRASES:
        assert phrase in result.choices[0].message.content.lower()


@mark.llm_test
def test_tool_library_for_bedrock(live_bedrock_client, basic_tool_library: ToolLibrary):
    result = live_bedrock_client.converse(
        system=[{"text": _SYS_MESSAGE}],
        toolConfig=basic_tool_library.to_bedrock(),
        modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        messages=[
            MessageParam(
                role="user",
                content=[{"text": _USER_MESSAGE}],
            )
        ],
        inferenceConfig={"maxTokens": 100},
    )["output"]["message"]
    for phrase in PHRASES:
        assert phrase in result["content"][0]["text"].lower()
