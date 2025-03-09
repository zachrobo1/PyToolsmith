from pydantic.v1 import BaseModel

from pytoolsmith import ToolDefinition, ToolParameters


class PersonInfoPydanticV1(BaseModel):
    first_name: str | None
    last_name: str | None = None


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
