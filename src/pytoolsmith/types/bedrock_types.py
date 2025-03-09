from dataclasses import asdict, dataclass
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

    def to_dict(self):
        return asdict(self)


@dataclass
class AwsBedrockConverseToolConfig:
    """What gets passed into Bedrock to configure the tools available to the LLM"""

    tools: list[AwsBedrockToolSpecListObject]

    def to_dict(self):
        return {
            "tools": [tool.to_dict() for tool in self.tools]
        }
