from dataclasses import asdict

from .tool_definition import ToolDefinition
from .types.bedrock_types import (
    AwsBedrockConverseToolConfig,
    AwsBedrockToolSpecListObject,
)


class ToolLibrary:

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def add_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        self._tools[tool.name] = tool

    def get_tool_from_name(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(f"Tool not found: {name}")

    def get_all_tool_names(self) -> list[str]:
        """Returns a list of the names of all the tools in the library."""
        return list(self._tools.keys())

    def get_tool_descriptions(self) -> dict[str, str]:
        """
        Returns a mapping tool names with the descriptions of the tool in the library.
        """
        return {
            name: tool.build_json_schema().description
            for name, tool in self._tools.items()
        }

    def to_openai(self, *, strict_mode=True):
        return [
            asdict(t.build_json_schema().to_openai(strict_mode=strict_mode))
            for t in self._tools.values()
        ]

    def to_anthropic(self, *, use_cache_control: bool = False):
        return [
            asdict(
                t.build_json_schema().to_anthropic(use_cache_control=use_cache_control))
            for t in self._tools.values()
        ]

    def to_bedrock(self) -> dict:
        bedrock_config = AwsBedrockConverseToolConfig(
            tools=[
                AwsBedrockToolSpecListObject(
                    toolSpec=t.build_json_schema().to_bedrock(as_dict=True)
                )
                for t in self._tools.values()
            ]
        )
        return asdict(bedrock_config)

    def subset(self, names: list[str]) -> "ToolLibrary":
        """Returns a subset of tools as a new tool library."""

        if not all(name in self._tools for name in names):
            raise ValueError(f"Not all tools in {names} are in the library.")

        subset = ToolLibrary()
        for name in names:
            subset.add_tool(self.get_tool_from_name(name))
        return subset
