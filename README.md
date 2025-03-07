# PyToolsmith

A lightweight Python library that simplifies the process of exposing functions as tools for Large Language Models.

### Status

[![codecov](https://codecov.io/gh/zachrobo1/PyToolsmith/graph/badge.svg?token=5SQEOF1TV2)](https://codecov.io/gh/zachrobo1/PyToolsmith)

## What is this?

LLM Tooling (or function calling) is a powerful way to connect LLMs to the real world. However, defining tool
definitions can be cumbersome, as it requires defining both the tool function, and a JSON schema that describes the
tool. Additionally, in some cases, you may want to control certain parameters passed into tools rather than have the LLM
decide what to pass in. PyToolsmith aims to solve this by providing a simple API to define tools from function
definitions and automatically generate the JSON schema to pass to the LLM.

### Supported Providers

- Anthropic
- AWS Bedrock
- OpenAI (coming soon)

### Type support

Part of being able to define schemas is mapping certain types to a JSON-compatible format. As such, PyToolsmith allows
you to define custom type maps to be used to generate the JSON schema. However, it comes out-of-the-box with support
for:

1. Standard based objects `str`, `int`, `float`, `bool`, etc.
2. UUIDs
3. Pydantic models

### Usage

Simply define a tool definition as such:

```python
from pytoolsmith import ToolDefinition


# 1. Define your function
def my_tool(my_param: str | None, my_controlled_param: str = "hello") -> str:
    """
    This a tool that formats a specific string with parameters.
   
    Args:
       my_param: A parameter controlled by the LLM
       my_controlled_param: A parameter controlled by the application.
       
    Returns: A formatted string.
    """
    return f"I did a search for {my_param} with controlled parameter {my_controlled_param}!"


# 2. Make a tool definition, calling out the injected parameter.
tool_definition = ToolDefinition(function=my_tool, injected_parameters=["my_controlled_param"])

# 3. Get a schema representing the tool automatically
schema = tool_definition.build_json_schema()

# 4. Get a tool definition ready to pass directly into LLM calls. 
# Note that the LLM does not have the context for the controlled parameter.
schema.to_openai()
schema.to_anthropic()
schema.to_bedrock()

# Bedrock Output:
# {
#     "name": "my_tool",
#     "inputSchema": {
#         "json": {
#             "type": "object",
#             "properties": {
#                 "my_param": {
#                     "anyOf": [{"type": "string"}, {"type": "null"}],
#                     "description": "A parameter controlled by the LLM",
#                 }
#             },
#             "required": ["my_param"],
#         }
#     },
#     "description": "This a tool that formats a specific string with parameters. Returns: A formatted string.",
# }

```

Additionally, you can use the `ToolLibrary` class to make it easy to pass in a list of tools directly to your LLM call.

```python
# ^ continuing from above
from pytoolsmith import ToolLibrary

# Make a library:
tool_library = ToolLibrary()
tool_library.add_tool(tool_definition)
tool_library.add_tool(other_tool_definition)

# Get a tool list ready to pass directly into LLM calls.
tool_library.to_openai()
tool_library.to_anthropic()
tool_library.to_bedrock()
# All of these are a list that can be passed in directly to your LLM call.


```

Additionally, you can control the serialization parameters:

```python
from bson import ObjectId
from pytoolsmith import pytoolsmith_config

pytoolsmith_config.update_type_map({ObjectId: "string"})
```

## Future Work

- Live LLM test for OpenAI
- Add support for calling tools & returning results directly from the library
    - Include serialization of LLM inputs to function input types
- Support installations requiring pydantic v1
- Publish on PyPI 🤠


