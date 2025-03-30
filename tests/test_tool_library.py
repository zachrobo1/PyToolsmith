import pytest

from pytoolsmith import ToolDefinition, ToolLibrary


def _func_to_test_1(a: str) -> str:
    """Desc for func 1"""
    return a


def _func_to_test_2(b: str) -> str:
    """Desc for func 2"""
    return b


@pytest.fixture
def filled_tool_library():
    tool_1 = ToolDefinition(function=_func_to_test_1, tool_group="1s")
    tool_2 = ToolDefinition(function=_func_to_test_2, tool_group="2s")
    tool_library = ToolLibrary()
    tool_library.add_tool(tool_1)
    tool_library.add_tool(tool_2)

    return tool_library


@pytest.mark.parametrize("method", ["to_anthropic", "to_openai", "to_bedrock"])
def test_to_x_works(filled_tool_library, method):
    """Tests each of the methods run."""
    getattr(filled_tool_library, method)()


def test_cast_library_to_anthropic(filled_tool_library):
    """With cache control, should only set the cache control for the last tool."""
    anthropic_result = filled_tool_library.to_anthropic(use_cache_control=True)

    exp_result = [
        {
            "cache_control": None,
            "description": "Desc for func 1",
            "input_schema": {"properties": {"a": {"type": "string"}}, "type": "object",
                             "required": ["a"]},
            "name": "_func_to_test_1",
        },
        {
            "cache_control": {"type": "ephemeral"},
            "description": "Desc for func 2",
            "input_schema": {"properties": {"b": {"type": "string"}}, "type": "object",
                             "required": ["b"]},
            "name": "_func_to_test_2",
        },
    ]

    assert anthropic_result == exp_result


def test_get_tool_from_name(filled_tool_library):
    with pytest.raises(ValueError) as excinfo:
        filled_tool_library.get_tool_from_name("_some_other_tool")
    assert excinfo.value.args[0] == "Tool not found: _some_other_tool"

    exp_def = ToolDefinition(
        function=_func_to_test_1, tool_group="1s")
    exp_def.set_tool_library(filled_tool_library)

    assert filled_tool_library.get_tool_from_name("_func_to_test_1") == exp_def


def test_get_all_tool_names(filled_tool_library):
    assert set(filled_tool_library.get_all_tool_names()) == (
        {"_func_to_test_1", "_func_to_test_2"}
    )


def test_get_all_tool_group_names(filled_tool_library):
    assert set(filled_tool_library.get_all_tool_group_names()) == (
        {"1s", "2s"}
    )


def test_get_tool_descriptions(filled_tool_library):
    assert filled_tool_library.get_tool_descriptions() == (
        {"_func_to_test_1": "Desc for func 1",
         "_func_to_test_2": "Desc for func 2"}
    )


def test_subset_library(filled_tool_library):
    with pytest.raises(ValueError):
        filled_tool_library.subset(["other_func"])

    subset_library = filled_tool_library.subset(["_func_to_test_1"])
    assert subset_library.get_all_tool_names() == ["_func_to_test_1"]

    subset_library = filled_tool_library.subset(["_func_to_test_1", "_func_to_test_2"])
    assert set(subset_library.get_all_tool_names()) == set(
        filled_tool_library.get_all_tool_names())


def test_exclude_library(filled_tool_library):
    subset_library = filled_tool_library.exclude(["_func_to_test_1"])
    assert subset_library.get_all_tool_names() == ["_func_to_test_2"]

    subset_library = filled_tool_library.exclude(["_func_to_test_1", "_func_to_test_2"])
    assert subset_library.get_all_tool_names() == []


def test_subset_library_from_groups(filled_tool_library):
    with pytest.raises(ValueError):
        filled_tool_library.subset(groups=["other_group"])

    filled_tool_library.exclude(["other_func"])

    subset_library = filled_tool_library.subset(groups=["1s"])
    assert subset_library.get_all_tool_names() == ["_func_to_test_1"]
    subset_library = filled_tool_library.subset(groups=["1s", "2s"])
    assert set(subset_library.get_all_tool_names()) == set(
        filled_tool_library.get_all_tool_names())


def test_exclude_library_from_groups(filled_tool_library):
    with pytest.raises(ValueError):
        filled_tool_library.exclude(groups=["other_group"])

    subset_library = filled_tool_library.exclude(groups=["1s"])
    assert subset_library.get_all_tool_names() == ["_func_to_test_2"]
    subset_library = filled_tool_library.exclude(groups=["1s", "2s"])
    assert subset_library.get_all_tool_names() == []
