from typing import Any

from pydantic import BaseModel

from .types.anthropic_types import (
    AnthropicToolParam,
    AnthropicCacheControlParam,
    AnthropicInputSchema,
)
from .types.bedrock_types import (
    AwsBedrockToolParam,
    AwsBedrockToolSchemaJson,
    AwsBedrockToolInputSchema,
)


class ToolParameters(BaseModel):
    """Parameters extracted from the tool definition."""

    input_properties: dict[str, Any]
    required_parameters: list[str]
    name: str
    description: str

    def to_bedrock(self) -> AwsBedrockToolParam:
        """Returns a Bedrock-compatible tool definition."""
        return AwsBedrockToolParam(
            name=self.name,
            inputSchema=AwsBedrockToolSchemaJson(
                json=AwsBedrockToolInputSchema(
                    type="object",
                    properties=self.input_properties,
                    required=self.required_parameters,
                )
            ),
            description=self.description,
        )

    def to_anthropic(self, use_cache_control: bool = False):
        return AnthropicToolParam(
            name=self.name,
            description=self.description,
            cache_control=AnthropicCacheControlParam(type="ephemeral")
            if use_cache_control
            else None,
            input_schema=AnthropicInputSchema(
                type="object", properties=self.input_properties
            ),
        )

    def to_openai(self):
        raise NotImplementedError
