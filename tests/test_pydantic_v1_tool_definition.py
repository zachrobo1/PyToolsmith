from pydantic.v1 import BaseModel

from pytoolsmith import ToolDefinition, ToolParameters


class PersonInfoPydanticV1(BaseModel):
    first_name: str | None
    last_name: str | None = None


class Address(BaseModel):
    street: str
    city: str
    zip_code: str


class User(BaseModel):
    name: str
    address: Address  # ← uses Address once


class Company(BaseModel):
    name: str
    headquarters: Address  # ← uses Address a second time → triggers $ref
    employees: list[User]


def _list_of_items_func(model_list: list[PersonInfoPydanticV1]):
    print(f"BaseModel len: {len(model_list)}")
    return ""


def test_build_tool_for_list_of_items():
    """Tests to ensure that a v1 pydantic model serializes as expected."""
    tool = ToolDefinition(function=_list_of_items_func)

    result = tool.build_json_schema()

    assert (
            result ==
            ToolParameters(
                name="_list_of_items_func",
                input_properties={
                    "model_list": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "title": "PersonInfoPydanticV1",
                            "properties": {
                                "first_name": {
                                    "title": "First Name",
                                    "type": "string"
                                },
                                "last_name": {
                                    "title": "Last Name",
                                    "type": "string",
                                },
                            },
                        },
                    },
                },
                required_parameters=["model_list"],
                description="",
            )

    )


def test_tool_with_complex_type_pydantic_v1():
    def tool_with_complex_input(company: Company):
        return f"Hello {company.name}!"

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
                    '$ref': '#/$defs/Address'
                },
                'employees': {
                    'items': {
                        '$ref': '#/$defs/User'
                    },
                    'title': 'Employees',
                    'type': 'array'
                }
            },
            'required': ['name', 'headquarters', 'employees'],
            'title': 'Company'
        },
        '$defs': {
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
                    'address': {'$ref': '#/$defs/Address'}},
                'required': ['name', 'address'],
                'title': 'User',
                'type': 'object'
            }
        },
    }
