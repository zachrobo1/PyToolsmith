from typing import Literal

from pydantic import BaseModel, Field


class AwsBedrockToolInputSchema(BaseModel):
    """Defines the JSON-schema compliant input schema for a tool to be used by bedrock"""

    type: Literal["object"]
    properties: dict[str, dict]
    """The json schema explaining the inputs to the function"""
    required: list[str]
    """List of required inputs to the tool"""


class AwsBedrockToolSchemaJson(BaseModel):
    json_val: AwsBedrockToolInputSchema = Field(
        alias="json"
    )  # json as a name is reserved...


class AwsBedrockToolParam(BaseModel):
    """Gives Bedrock information regarding a tool, it's name, what it's used for, and how to interact with it."""

    name: str
    inputSchema: AwsBedrockToolSchemaJson
    description: str


class AwsBedrockToolSpecListObject(BaseModel):
    """Intermediate step to pass data into Bedrock."""

    toolSpec: AwsBedrockToolParam


class AwsBedrockConverseToolConfig(BaseModel):
    """What gets passed into Bedrock to configure the tools available to the LLM"""

    tools: list[AwsBedrockToolSpecListObject]
