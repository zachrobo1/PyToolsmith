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

    def to_openai(self):
        return [t.build_json_schema().to_openai() for t in self._tools.values()]

    def to_anthropic(self, use_cache_control: bool = False):
        return [
            t.build_json_schema().to_anthropic(use_cache_control=use_cache_control)
            for t in self._tools.values()
        ]

    def to_bedrock(self) -> AwsBedrockConverseToolConfig:
        return AwsBedrockConverseToolConfig(
            tools=[
                AwsBedrockToolSpecListObject(
                    toolSpec=t.build_json_schema().to_bedrock()
                )
                for t in self._tools.values()
            ]
        )

    # def call_tool(self, tool_name: str, llm_parameters: dict[str, Any], injected_parameters: dict[str, Any]):
    #     if tool_name not in self._tools:
    #         raise ValueError(f"No such tool: {tool_name}")
    #
    #     return self._tools[tool_name].call_tool(llm_parameters, injected_parameters)
