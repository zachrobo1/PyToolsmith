from collections import defaultdict
from dataclasses import asdict

from .tool_definition import ToolDefinition
from .types.bedrock_types import (
    AwsBedrockConverseToolConfig,
    AwsBedrockToolSpecListObject,
)


class ToolLibrary:

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
        self._tool_groups: dict[str, list[str]] = defaultdict(list)
        """Map of groups to the tool names inside of them."""

    def add_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        self._tools[tool.name] = tool

        if tool.tool_group:
            self._tool_groups[tool.tool_group].append(tool.name)

    def get_tool_from_name(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise ValueError(f"Tool not found: {name}")
        return self._tools[name]

    def get_tool_names_in_group(self, group: str) -> list[str]:
        """Gets the names of all the tools in the group"""
        if group not in self._tool_groups:
            raise ValueError(f"Group not found: {group}")
        return self._tool_groups[group]

    def get_all_tool_names(self) -> list[str]:
        """Returns a list of the names of all the tools in the library."""
        return list(self._tools.keys())

    def get_all_tool_group_names(self) -> list[str]:
        """Returns a list of the names of all the tools in the library."""
        return list(self._tool_groups.keys())

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

    def subset(self, names: list[str] | None = None,
               groups: list[str] | None = None) -> "ToolLibrary":
        """
        Returns a subset of tools as a new tool library.
        Uses a `or` condition to filter the tools- i.e. any tool that either has a name
        in the list or is in a specified group..\
        """
        names = names or []

        all_accepted_tool_names = set(names)
        if groups:
            for group in groups:
                all_accepted_tool_names.update(self.get_tool_names_in_group(group))

        if not all(name in self._tools for name in all_accepted_tool_names):
            raise ValueError(
                f"Not all tools in {', '.join(all_accepted_tool_names)} are in the "
                f"library."
            )

        subset = ToolLibrary()
        for name in all_accepted_tool_names:
            subset.add_tool(self.get_tool_from_name(name))
        return subset
