from dataclasses import asdict, dataclass, field

from .tool_definition import ToolDefinition
from .types.bedrock_types import (
    AwsBedrockConverseToolConfig,
    AwsBedrockToolSpecListObject,
)


@dataclass
class ToolLibrary:
    _tools: dict[str, ToolDefinition] = field(default_factory=dict)

    def add_tool(self, tool: ToolDefinition):
        if tool.name in self._tools:
            raise ValueError(f"Duplicate tool name: {tool.name}")

        self._tools[tool.name] = tool

    def get_tool_from_name(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError:
            raise ValueError(f"Tool not found: {name}")

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
        return bedrock_config.to_dict()
