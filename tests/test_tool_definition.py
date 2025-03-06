import uuid
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal

from pydantic import BaseModel
from pytest import mark

from pytoolsmith import ToolDefinition, ToolParameters


class PersonInfo(BaseModel):
    first_name: str
    last_name: str | None = None


class TestEnum(StrEnum):
    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = auto()


BASE_TENANT_ID = uuid.uuid4()


def _get_part_work_history_test_func(
        t_id: uuid.UUID,
        ptype_id: uuid.UUID,
        latest: bool,
        k: int = 10,
        optional_dict: dict[str, str] | None = None,
) -> list[str]:
    """
    Get the latest history of work for a part type.
    Args:
        ptype_id: The part type ID
        latest: If it's latest or not.
        k: Number to return. Include some other text, that will overflow
        to the next line. This is a pretty long line that should be wrapped.
        optional_dict: Optional dictionary to use, just for funsies.


    Returns: A list of strings

    """
    assert isinstance(t_id, uuid.UUID)
    assert isinstance(ptype_id, uuid.UUID)
    assert isinstance(latest, bool)
    assert isinstance(k, int)
    assert optional_dict is None or isinstance(optional_dict, dict)

    return ["a", "b"]


def test_build_tool_parameter():
    tool = ToolDefinition(
        function=_get_part_work_history_test_func,
        injected_parameters=["t_id"],
        additional_parameters={"k": {"minimum": 1}},
    )

    assert tool.name == "_get_part_work_history_test_func"

    result = tool.build_json_schema()
    assert (
            ToolParameters(
                name="_get_part_work_history_test_func",
                description="Get the latest history of work for a part type. Returns: A list of strings",
                input_properties={
                    "ptype_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The part type ID",
                    },
                    "latest": {
                        "type": "boolean",
                        "description": "If it's latest or not.",
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number to return. Include some other text, that will overflow to the "
                                       "next line. This is a pretty long line that should be wrapped.",
                        "default": 10,
                        "minimum": 1,
                    },
                    "optional_dict": {
                        "anyOf": [{"type": "object"}, {"type": "null"}],
                        "description": "Optional dictionary to use, just for funsies.",
                        "default": "null",
                    },
                },
                required_parameters=["ptype_id", "latest"],
            )
            == result
    )


@mark.skip(reason="Not implemented yet")
def test_call_tool():
    tool = ToolDefinition(
        function=_get_part_work_history_test_func,
        injected_parameters=["t_id"],
        additional_parameters={"k": {"minimum": 1}},
    )

    # Test that the function is called
    result = tool.call_tool(
        llm_parameters={
            "ptype_id": uuid.UUID(),
            "latest": True,
            "optional_dict": {},
        },
        library_parameters={"t_id": BASE_TENANT_ID},
    )

    assert result == ["a", "b"]


def _enum_func(
        ts: datetime,
        enum_1: TestEnum,
        enum_2: TestEnum | None = None,
) -> str:
    print(f"Its {ts}")
    return str(enum_1 == enum_2)


def test_build_tool_for_enum():
    tool = ToolDefinition(function=_enum_func)

    assert (
            ToolParameters(
                name="_enum_func",
                description="",
                required_parameters=["ts", "enum_1"],
                input_properties={
                    "ts": {
                        "type": "string",
                        "format": "date-time",
                    },
                    "enum_1": {
                        "type": "string",
                        "enum": ["option_a", "option_b", "option_c"],
                    },
                    "enum_2": {
                        "anyOf": [
                            {
                                "type": "string",
                                "enum": ["option_a", "option_b", "option_c"],
                            },
                            {"type": "null"},
                        ],
                        "default": "null",
                    },
                },
            )
            == tool.build_json_schema()
    )


def _literal_func(arg_a: Literal["a", "b"], arg_b: Literal["a", "b"] | None = None):
    return str(arg_a == arg_b)


def test_build_tool_for_literal():
    tool = ToolDefinition(function=_literal_func)

    result = tool.build_json_schema()

    assert ToolParameters(
        name="_literal_func",
        input_properties={
            "arg_a": {"type": "string", "enum": ["a", "b"]},
            "arg_b": {
                "anyOf": [
                    {
                        "type": "string",
                        "enum": ["a", "b"],
                    },
                    {"type": "null"},
                ],
                "default": "null",
            },
        },
        description="",
        required_parameters=["arg_a"],
    ), result


def _pydantic_func(
        contact_info: PersonInfo,
        contact_info_2: PersonInfo | None = None,
):
    print(f"The person's name is {contact_info.first_name} {contact_info.last_name}")
    print(
        f"The 2nd person's name is {contact_info_2.first_name} {contact_info_2.last_name}"
    )
    return ""


def test_build_tool_for_pydantic_model():
    tool = ToolDefinition(function=_pydantic_func)

    result = tool.build_json_schema()

    exp = ToolParameters(
        name="_pydantic_func",
        input_properties={
            "contact_info": {
                "type": "object",
                "title": "PersonInfo",
                "required": ["first_name"],
                "properties": {
                    "first_name": {
                        "title": "First Name",
                        "type": "string",
                    },
                    "last_name": {
                        "title": "Last Name",
                        "anyOf": [
                            {
                                "type": "string",
                            },
                            {"type": "null"},
                        ],
                        "default": None,
                    },
                },
            },
            "contact_info_2": {
                "anyOf": [
                    {
                        "type": "object",
                        "title": "PersonInfo",
                        "required": ["first_name"],
                        "properties": {
                            "first_name": {
                                "title": "First Name",
                                "type": "string",
                            },
                            "last_name": {
                                "title": "Last Name",
                                "default": None,
                                "anyOf": [
                                    {
                                        "type": "string",
                                    },
                                    {"type": "null"},
                                ],
                            },
                        },
                    },
                    {"type": "null"},
                ],
                "default": "null",
            },
        },
        required_parameters=["contact_info"],
        description="",
    )

    assert exp.model_dump() == result.model_dump()


def _list_of_items_func(int_list: list[int], model_list: list[PersonInfo]):
    print(f"Int len: {len(int_list)}")
    print(f"BaseModel len: {len(model_list)}")
    return ""


def test_build_tool_for_list_of_items():
    tool = ToolDefinition(function=_list_of_items_func)

    result = tool.build_json_schema()

    assert (
            ToolParameters(
                name="_list_of_items_func",
                input_properties={
                    "int_list": {"type": "array", "items": {"type": "integer"}},
                    "model_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "title": "PersonInfo",
                            "properties": {
                                "first_name": {
                                    "title": "First Name",
                                    "type": "string",
                                },
                                "last_name": {
                                    "title": "Last Name",
                                    "anyOf": [
                                        {
                                            "type": "string",
                                        },
                                        {"type": "null"},
                                    ],
                                    "default": None,
                                },
                            },
                            "required": ["first_name"],
                        },
                    },
                },
                required_parameters=["int_list", "model_list"],
                description="",
            ).dict()
            == result.dict()
    )
