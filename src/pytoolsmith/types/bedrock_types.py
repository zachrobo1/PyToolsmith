from dataclasses import dataclass, field
from typing import Literal


@dataclass
class AwsBedrockToolInputSchema:
    """
    Defines the JSON-schema compliant input schema for a tool to be used by bedrock
    """

    type: Literal["object"]
    properties: dict[str, dict]
    """The json schema explaining the inputs to the function"""
    required: list[str]
    """List of required inputs to the tool"""
    definitions: dict
    """Any referenced definitions for bedrock."""


@dataclass
class AwsBedrockToolSchemaJson:
    # Using field to handle the alias
    json: AwsBedrockToolInputSchema
    # json as a name is reserved...


@dataclass
class AwsBedrockToolParam:
    """
    Gives Bedrock information regarding a tool, it's name, what it's used for, and how 
    to interact with it.
    """

    name: str
    inputSchema: AwsBedrockToolSchemaJson
    description: str


@dataclass
class AwsBedrockToolSpecListObject:
    """Intermediate step to pass data into Bedrock."""

    toolSpec: AwsBedrockToolParam


@dataclass
class AwsBedrockCachePointDefault:
    type: Literal["default"] = "default"


@dataclass
class AwsBedrockCachePointObject:
    cachePoint: AwsBedrockCachePointDefault = field(
        default_factory=AwsBedrockCachePointDefault
    )


@dataclass
class AwsBedrockConverseToolConfig:
    """What gets passed into Bedrock to configure the tools available to the LLM"""

    tools: list[AwsBedrockToolSpecListObject | AwsBedrockCachePointObject]
