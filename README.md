# PyToolsmith

A lightweight Python library that simplifies the process of exposing functions as tools for Large Language Models.

### Status

[![codecov](https://codecov.io/gh/zachrobo1/PyToolsmith/graph/badge.svg?token=5SQEOF1TV2)](https://codecov.io/gh/zachrobo1/PyToolsmith)

## About

LLM Tooling (or function calling) is a powerful way to connect LLMs to the real world. However, defining tool
definitions can be cumbersome, as it requires defining both the tool function, and

Out-of-the-box support for:

1. Pydantic models
2. UUIDs

### Usage:

Simply define a tool definition as such:

```python
from pytoolsmith import ToolDefinition


# 1. Define your function
def my_tool(my_param: str) -> str:
    return f"I did a search for {my_param}!"


# 2. Make a tool definition
tool_definition = ToolDefinition(function=my_tool)

# 3. Get the schema out!
tool_definition.build_json_schema().to_openai()
# Output: TBD

```

Additionally, you can use the `ToolLibrary` class to make it easy to pass in a list of tools directly to your LLM call.

```python
# ^ continuing from above
from pytoolsmith import ToolLibrary

# Make a library:
tool_library = ToolLibrary()
tool_library.add_tool(tool_definition)



```

## Future Work

3. Build out library
    - How do we specify which params are injectable on a library level? Ideally type hint..
    - How are we going to handle serialization for loading function
        - Library level? Would be good to re-use serializers. Or could do it per-tool
        - Could we potentially take advantage of the `Config` on pydantic models.



