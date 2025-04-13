from collections.abc import Callable

from pytoolsmith import ToolDefinition


def test_streaming_function_behavior():
    """Tests a pattern to pass in a handler to emit messages for a specific tool."""

    data = [
        "This is message 1.",
        "Now, I'm going to do some other work...",
        "Now, I'm doing more things.",
        "Yes, I've thought about it. This is my final answer!"
    ]

    def mock_streaming_func(msg_handler: Callable[[str], None]) -> str:
        """
        Test the tool streamer.
        Args:
            msg_handler: The message handler to yield messages to.
    
        Returns: The final result
    
        """

        def _streamer():
            yield from data

        for msg in _streamer():
            msg_handler(msg)

        return data[-1]

    tool = ToolDefinition(function=mock_streaming_func,
                          injected_parameters=["msg_handler"])

    collected_msgs = []

    def _collect_msg(msg: str):
        collected_msgs.append(msg)

    result = tool.call_tool(
        llm_parameters={},
        hardset_parameters={"msg_handler": _collect_msg},
        include_message=False
    )

    assert result == data[-1]
    assert collected_msgs == data
