from collections import defaultdict
from dataclasses import asdict

from .batch_tool import batch_tool_definition, batch_tool_parameters
from .tool_definition import ToolDefinition
from .types.bedrock_types import (
    AwsBedrockConverseToolConfig,
    AwsBedrockToolSpecListObject,
)


class ToolLibrary:

    def __init__(self, include_batch_tool: bool = False):
        """
        Args:
            include_batch_tool: If true, will include the batch tool used to make
                parallel tool calls with Claude 3.7.
        """
        self._tools: dict[str, ToolDefinition] = {}
        self._tool_groups: dict[str, list[str]] = defaultdict(list)
        """Map of groups to the tool names inside of them."""
        self._include_batch_tool = include_batch_tool

    def add_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        tool.set_tool_library(self)

        self._tools[tool.name] = tool

        if tool.tool_group:
            self._tool_groups[tool.tool_group].append(tool.name)

    def get_tool_from_name(self, name: str) -> ToolDefinition:
        if self._include_batch_tool and name == "batch_tool":
            batch_tool_definition.set_tool_library(self)
            return batch_tool_definition

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
        tools_params = [
            batch_tool_parameters
        ] if self._include_batch_tool else []

        tools_params.extend([
            t.build_json_schema() for t in self._tools.values()
        ])

        ret_dict = []
        last_i = len(tools_params) - 1
        for i, p in enumerate(tools_params):
            ret_dict.append(asdict(
                p.to_anthropic(use_cache_control=use_cache_control and i == last_i)))

        return ret_dict

    def to_bedrock(self) -> dict:
        batch_tool_addition = [
            AwsBedrockToolSpecListObject(toolSpec=batch_tool_parameters.to_bedrock(
                as_dict=True))
        ] if self._include_batch_tool else []
        bedrock_config = AwsBedrockConverseToolConfig(
            tools=[
                      AwsBedrockToolSpecListObject(
                          toolSpec=t.build_json_schema().to_bedrock(as_dict=True)
                      )
                      for t in self._tools.values()
                  ] + batch_tool_addition
        )
        return asdict(bedrock_config)

    def subset(self, names: list[str] | None = None,
               groups: list[str] | None = None) -> "ToolLibrary":
        """
        Returns a subset of tools as a new tool library.
        Uses a `or` condition to filter the tools- i.e. any tool that either has a name
        in the list or is in a specified group.
        Will shadow the original library in terms of having the batch tool.
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

        subset = ToolLibrary(include_batch_tool=self._include_batch_tool)
        for name in all_accepted_tool_names:
            subset.add_tool(self.get_tool_from_name(name))
        return subset

    def exclude(self, names: list[str] | None = None,
                groups: list[str] | None = None) -> "ToolLibrary":
        """
        Returns a subset of tools as a new tool library by excluding the specified 
        tools / groups. Uses a `or` condition to filter the tools- i.e. any tool that 
        either has a name in the list or is in a specified group is removed.
        Will shadow the original library in terms of having the batch tool.
        """

        # Start with the full set of tool names, then remove there
        all_accepted_tool_names = set(self.get_all_tool_names())

        names_to_remove = set(names or [])

        for group in groups or []:
            names_to_remove.update(self.get_tool_names_in_group(group))

        for name in names_to_remove:
            if name in all_accepted_tool_names:
                all_accepted_tool_names.remove(name)

        subset = ToolLibrary(include_batch_tool=self._include_batch_tool)
        for name in all_accepted_tool_names:
            subset.add_tool(self.get_tool_from_name(name))
        return subset
