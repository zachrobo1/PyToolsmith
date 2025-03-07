from bson import ObjectId

from pytoolsmith import ToolDefinition, ToolParameters, pytoolsmith_config


def func_to_test(test_id: ObjectId) -> str:
    return test_id.binary.decode()


def test_bson_tool_definition():
    pytoolsmith_config.update_type_map({ObjectId: "string"})
    pytoolsmith_config.update_format_map(
        {ObjectId: "objectId"}
    )  # Not typical- just using to test.
    tool_def = ToolDefinition(function=func_to_test)

    schema = tool_def.build_json_schema()

    assert schema == ToolParameters(
        input_properties={"test_id": {"type": "string", "format": "objectId"}},
        required_parameters=["test_id"],
        name="func_to_test",
        description="",
    )
