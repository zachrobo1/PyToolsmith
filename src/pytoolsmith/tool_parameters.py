from copy import deepcopy
from typing import Any

from pydantic import BaseModel

from .types.anthropic_types import (
    AnthropicCacheControlParam,
    AnthropicInputSchema,
    AnthropicToolParam,
)
from .types.bedrock_types import (
    AwsBedrockToolInputSchema,
    AwsBedrockToolParam,
    AwsBedrockToolSchemaJson,
)
from .types.openai_types import (
    OpenAIFunctionDefinition,
    OpenAIFunctionParameters,
    OpenAIToolParam,
)
from .utils import remove_keys


class ToolParameters(BaseModel):
    """Parameters extracted from the tool definition."""

    input_properties: dict[str, Any]
    required_parameters: list[str]
    name: str
    description: str

    def to_bedrock(self, as_dict: bool = True) -> AwsBedrockToolParam | dict:
        """
        Returns a Bedrock-compatible tool definition.
        `as_dict` set to True will allow you to pass it directly to Bedrock.
        """
        param = AwsBedrockToolParam(
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
        if as_dict:
            return param.model_dump(by_alias=True)
        return param

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

    def to_openai(self, *, strict_mode=True) -> OpenAIToolParam:
        """
        Strict mode has a better guarantee that the LLM will use the tool correctly. However, it removes additional
        formatting information and defaults from the LLM's context.
        """
        params = deepcopy(self.input_properties)
        if strict_mode:
            # We have to remove extra keys such as "format" from the properties...
            params = remove_keys(
                params,
                ["format", "default"]
            )
        return OpenAIToolParam(
            function=OpenAIFunctionDefinition(
                name=self.name,
                description=self.description,
                parameters=OpenAIFunctionParameters(
                    type="object",
                    additionalProperties=not strict_mode,
                    properties=params,
                    required=list(params.keys()) if strict_mode else self.required_parameters,
                ),
                strict=strict_mode,
            ),
            type="function"
        )
