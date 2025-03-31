# PyToolsmith

A lightweight Python library that simplifies the process of exposing functions as tools for Large Language Models.

### Status

![Tests](https://github.com/zachrobo1/PyToolsmith/actions/workflows/linting-and-tests.yml/badge.svg)
![PyPI - Version](https://img.shields.io/pypi/v/pytoolsmith)
[![codecov](https://codecov.io/gh/zachrobo1/PyToolsmith/graph/badge.svg?token=5SQEOF1TV2)](https://codecov.io/gh/zachrobo1/PyToolsmith)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

LLM Tooling (or function calling) is a powerful way to connect LLMs to the real world. However, defining tool
definitions can be cumbersome, as it requires defining both the tool function, and a JSON schema that describes the
tool. Additionally, in some cases, you may want to control certain parameters passed into tools rather than have the LLM
decide what to pass in. PyToolsmith aims to solve this by providing a simple API to define tools from function
definitions and automatically generate the JSON schema to pass to the LLM.

### Features

- [x] Generates JSON schemas directly from your function definitions.
- [x] Parses Google-style docstrings to describe your tools in the schema.
- [x] Pass the same tools into different LLM providers with a simple method call.
- [x] Define custom type mappings to extend functionality.

### Supported Provider Interfaces

- Anthropic
- AWS Bedrock
- OpenAI

### Included Type Support

Part of being able to define schemas is mapping certain types to a JSON-compatible format. As such, PyToolsmith allows
you to define custom type maps to be used to generate the JSON schema. However, it comes out-of-the-box with support
for:

1. Standard based objects `str`, `int`, `float`, `bool`, etc.
2. UUIDs

### Usage

Simply define a tool definition as such:

```python
from pytoolsmith import ToolDefinition


# 1. Define your function
def get_user_by_id(user_id: str, tenant_id: str) -> dict:
    """
    This a tool that gets a user by its ID.
   
    Args:
       user_id: The user to search for.
       tenant_id: The tenant to search inside of
       
    Returns: A dictionary representing the user.
    """
    # Your tool logic here.
    return {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "user_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890"
    }


# 2. Make a tool definition, calling out the injected parameter.
tool_definition = ToolDefinition(
    function=get_user_by_id,
    injected_parameters=["tenant_id"],
    # You can also define a message that can be sent to the user here.
    # Use mustache template syntax to inject parameter values into the message.
    user_message="Looking up a user using id {{user_id}}."
)

# 3. Get a schema representing the tool automatically
schema = tool_definition.build_json_schema()

# 4. Get a tool definition ready to pass directly into LLM calls. 
# Note that the LLM does not have the context for the controlled parameter.
schema.to_openai()
schema.to_anthropic()
schema.to_bedrock()

# Bedrock Output:
# {
#     "name": "get_user_by_id",
#     "inputSchema": {
#         "json": {
#             "type": "object",
#             "properties": {
#                 "user_id": {
#                     "type": "string",
#                     "description": "The user to search for.",
#                 }
#             },
#             "required": ["my_param"],
#         }
#     },
#     "description": "This a tool that gets a user by its ID. "
#                    "Returns: A dictionary representing the user.",
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

When you implement your LLM call, you can use the tool library to get the tool list, and call it directly.

```python
# ^ continuing from above
from anthropic import Anthropic
from anthropic.types import MessageParam, TextBlockParam

from pytoolsmith import ToolDefinition

client = Anthropic()

hardset_parameters = {"tenant_id": "1234"}

# Get the tool name and parameters from the LLM call
llm_result = client.messages.create(
    system="You are a helpful assistant who can look up users by their ID.",
    tools=tool_library.to_anthropic(),
    model="claude-3-7-sonnet-latest",
    messages=[
        MessageParam(
            role="user",
            content=[TextBlockParam(text="Can you help me look up my account? My id is 5678", type="text")],
        )
    ],
    max_tokens=100,
)

llm_set_params, tool_name = parse_llm_result(llm_result)
# `llm_set_params` would be like: {"user_id": "5678"}
# This was decided by the LLM and passed back as something to call.

tool: ToolDefinition = tool_library.get_tool_from_name(tool_name)

user_message = tool.format_message_for_call(llm_parameters=llm_set_params, hardset_parameters=hardset_parameters)
# The user message will be `Looking up a user using id 5678.`
tool_result = tool.call_tool(
    llm_parameters=llm_set_params,
    hardset_parameters=hardset_parameters,
)
# Result is ready to be passed back to the next LLM call.
# The user message will be `Looking up a user using id 5678.`
```

Additionally, you can control the serialization parameters:

```python
from bson import ObjectId
from pytoolsmith import pytoolsmith_config

pytoolsmith_config.update_type_map({ObjectId: "string"})


# Now you can define the following function as a tool:
def get_object_by_id(object_id: ObjectId) -> dict:
    ...
```

### Additional Configuration

**Library Subsetting**
<br>
Sometimes you may not want to pass all of your tools to the LLM.
Subsetting allows you to select a smaller set of tools to pass in- either individually or by tagging them with
a `tool_group` parameter on your ToolDefinitions.

To use, call the `subset()` method on a ToolLibrary instance to get a smaller library generated. Additionally, you can
use `exclude()` to get the opposite effect.

**Batch Tool**
<br>
When using Claude 3.7, Anthropic suggests adding
a [Batch Tool](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview#parallel-tool-use) to be able to
call multiple tools at once. To use within PyToolsmith, set `include_batch_tool=True` when creating your tool library.
You can also set a custom serialization function to load the LLM's arguments into function called from the batch tool
with
`pytoolsmith_config.set_batch_tool_serializer(custom_serializer)`.

**Vendor-Specific Options**
<br>
If needed, additional OpenAPI spec can be passed into a `ToolDefinition` constructor with the `additional_parameters`
parameter.

The following client-specific configuration options are also available as options on the `to_<provider>` methods:

- [OpenAI Strict Mode](https://platform.openai.com/docs/guides/function-calling#strict-mode) with `strict_model=True`
- [Anthropic Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) with
  `use_cache_control=True`

## Future Plans

- [ ] Support for tuples as fixed-length lists
- [ ] Extendable serialization support (for LLM messages -> function inputs and vise versa)

### A Note

I was heavily inspired by FastAPI's batteries-included ability
to [create automatic OpenAPI specs](https://fastapi.tiangolo.com/reference/openapi/docs/) for web applications. Having a
single source of truth for your API docs defined as code speeds up development and reduces the chance of errors - why
not apply
that to LLM interfaces? 🤠


