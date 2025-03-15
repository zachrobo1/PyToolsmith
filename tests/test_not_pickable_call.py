import socket

from pytoolsmith import ToolDefinition


def _non_pickleable_func(sock: socket.socket):
    print(sock.__class__.__name__)


def test_passing_in_non_copyable_object():
    """Test to ensure that a bux fix implemented in 0.1.6 works as expected."""
    tool = ToolDefinition(function=_non_pickleable_func, injected_parameters=["sock"])

    tool.call_tool({}, {"sock": socket.socket()})
