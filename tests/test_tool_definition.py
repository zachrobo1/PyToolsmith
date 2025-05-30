from dataclasses import asdict
from datetime import datetime
from enum import StrEnum, auto
from typing import Literal
import uuid

from bson import ObjectId
from pydantic import BaseModel
import pytest

from pytoolsmith import ToolDefinition, ToolParameters, pytoolsmith_config


class PersonInfo(BaseModel):
    first_name: str
    last_name: str | None = None


class TestEnum(StrEnum):
    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = auto()


BASE_TENANT_ID = uuid.uuid4()


def mock_function_database_lookup(
        tenant_id: uuid.UUID,
        entity_id: uuid.UUID,
        latest: bool,
        k: int = 10,
        optional_dict: dict[str, str] | None = None,
) -> list[str]:
    """
    Mocks a database query.
    Args:
        entity_id: The entity ID
        latest: If it's latest or not.
        k: Number to return. Include some other text, that will overflow
        to the next line. This is a pretty long line that should be wrapped.
        optional_dict: Optional dictionary to use, just for funsies.


    Returns: A list of strings

    """
    assert isinstance(tenant_id, uuid.UUID)
    assert isinstance(entity_id, uuid.UUID)
    assert isinstance(latest, bool)
    assert isinstance(k, int)
    assert optional_dict is None or isinstance(optional_dict, dict)

    return ["a", "b"]


def test_build_tool_parameter():
    tool = ToolDefinition(
        function=mock_function_database_lookup,
        injected_parameters=["tenant_id"],
        additional_parameters={"k": {"minimum": 1}},
    )

    assert tool.name == "mock_function_database_lookup"

    result = tool.build_json_schema()
    assert (
            ToolParameters(
                name="mock_function_database_lookup",
                description="Mocks a database query. Returns: A list of strings",
                input_properties={
                    "entity_id": {
                        "type": "string",
                        "format": "uuid",
                        "description": "The entity ID",
                    },
                    "latest": {
                        "type": "boolean",
                        "description": "If it's latest or not.",
                    },
                    "k": {
                        "type": "integer",
                        "description": "Number to return. Include some other text, "
                                       "that will overflow to the "
                                       "next line. This is a pretty long line that "
                                       "should be wrapped.",
                        "default": 10,
                        "minimum": 1,
                    },
                    "optional_dict": {
                        "anyOf": [{"type": "object"}, {"type": "null"}],
                        "description": "Optional dictionary to use, just for funsies.",
                        "default": "null",
                    },
                },
                required_parameters=["entity_id", "latest"],
            )
            == result
    )


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
        f"The 2nd person's name is {contact_info_2.first_name} "
        f"{contact_info_2.last_name}"
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

    assert asdict(exp) == asdict(result)


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
            )
            == result
    )


def _breaking_function(id_: ObjectId) -> str:
    return id_.binary.decode()


def test_breaking_tool():
    """
    Tests to make sure that when an invalid parameter type is set, it raises an error.
    """
    assert ObjectId not in pytoolsmith_config.get_type_map()

    with pytest.raises(ValueError):
        ToolDefinition(function=_breaking_function)


def test_calling_tool():
    """
    Tests calling the tool to make sure it works.
    In the future, can expand to ensure serialization works as expected.
    """
    injected_params = {
        "tenant_id": "1234"
    }
    llm_params = {
        "db_name": "psql_db",
        "sql": "SELECT * FROM table_name"
    }

    def checking_function(tenant_id: str, db_name: str, sql: str):
        assert tenant_id == "1234"
        assert db_name == "psql_db"
        assert sql == "SELECT * FROM table_name"
        return True

    tool = ToolDefinition(function=checking_function, injected_parameters=["tenant_id"],
                          user_message="Checking function using command: `{{sql}}`")

    res_no_message = tool.call_tool(
        llm_parameters=llm_params,
        hardset_parameters=injected_params
    )
    assert res_no_message is True

    res_w_message = tool.call_tool(
        llm_parameters=llm_params,
        hardset_parameters=injected_params,
        include_message=True
    )
    assert ((True,
             "Checking function using command: `SELECT * FROM table_name`") ==
            res_w_message)


def test_build_tool_with_template_variables():
    """
    Tests that variables can be injected into the docstring when building the schema.
    """

    def function_with_template(
            param1: str,
            param2: int,
    ) -> str:
        """
        A function with template variables in the docstring. {{VALUE}}

        Args:
            param1: A parameter with {{VARIABLE}} in description
            param2: Another parameter with value {{VALUE}}

        Returns: A string
        """
        return f"{param1} {param2}"

    tool = ToolDefinition(function=function_with_template)

    # Test with no variables (should leave templates as-is)
    schema_no_vars = tool.build_json_schema()
    assert "{{VARIABLE}}" in schema_no_vars.input_properties["param1"]["description"]
    assert "{{VALUE}}" in schema_no_vars.input_properties["param2"]["description"]

    # Test with variables substituted
    schema_with_vars = tool.build_json_schema(
        schema_vals={"VARIABLE": "substituted", "VALUE": "42"}
    )

    # Check that variables were properly substituted
    assert "42" in schema_with_vars.description
    assert "substituted" in schema_with_vars.input_properties["param1"]["description"]
    assert "42" in schema_with_vars.input_properties["param2"]["description"]
    assert "{{VALUE}}" not in schema_with_vars.description
    assert "{{VARIABLE}}" not in schema_with_vars.input_properties["param1"][
        "description"]
    assert "{{VALUE}}" not in schema_with_vars.input_properties["param2"]["description"]

    # Check that function description also gets substituted
    assert "template variables" in schema_with_vars.description


def test_reformat_pydantic_definitions():
    """
    Test that definitions are collected from nested locations and moved to top level
    """

    # Input object with definitions scattered throughout
    input_data = {
        "name": "test_schema",
        "definitions": {
            "TopLevel": {"type": "object"}
        },
        "nested": {
            "definitions": {
                "NestedModel": {"type": "string"}
            },
            "data": {
                "$ref": "#/definitions/NestedModel"
            }
        },
        "deep": {
            "very": {
                "definitions": {
                    "DeepModel": {"type": "number"}
                }
            }
        }
    }

    # Expected output with all definitions at top level
    expected_output = {
        "name": "test_schema",
        "nested": {
            "data": {
                "$ref": "#/definitions/NestedModel"
            }
        },
        "deep": {
            "very": {}
        },
        "definitions": {
            "TopLevel": {"type": "object"},
            "NestedModel": {"type": "string"},
            "DeepModel": {"type": "number"}
        }
    }

    result = ToolDefinition._reformat_pydantic_definitions(
        input_data,
    )
    assert result == expected_output


def test_tool_with_complex_type_pydantic_v2(pydantic_company_model):
    def tool_with_complex_input(company: pydantic_company_model):
        return f"Hello {getattr(company, 'name')}!"

    tool = ToolDefinition(function=tool_with_complex_input)

    schema = tool.build_json_schema()

    assert schema.input_properties == {
        'company': {
            'type': 'object',
            'properties': {
                'name': {
                    'title': 'Name',
                    'type': 'string'
                },
                'headquarters': {
                    '$ref': '#/definitions/Address'
                },
                'employees': {
                    'items': {
                        '$ref': '#/definitions/User'
                    },
                    'title': 'Employees',
                    'type': 'array'
                }
            },
            'required': ['name', 'headquarters', 'employees'],
            'title': 'Company'
        },
        'definitions': {
            'Address': {
                'properties': {
                    'street': {'title': 'Street', 'type': 'string'},
                    'city': {'title': 'City', 'type': 'string'},
                    'zip_code': {'title': 'Zip Code', 'type': 'string'}},
                'required': ['street', 'city', 'zip_code'],
                'title': 'Address',
                'type': 'object'
            },
            'User': {
                'properties': {
                    'name': {'title': 'Name', 'type': 'string'},
                    'address': {'$ref': '#/definitions/Address'}},
                'required': ['name', 'address'],
                'title': 'User',
                'type': 'object'
            }
        },
    }
