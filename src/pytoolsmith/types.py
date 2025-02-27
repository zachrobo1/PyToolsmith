from enum import StrEnum, auto
from typing import Literal

from pydantic import Field, PrivateAttr, BaseModel


class AwsBedrockMessageRole(StrEnum):
    USER = auto()
    ASSISTANT = auto()


class AwsBedrockTextBlock(BaseModel):
    text: str

    _user_facing_text: str | None = PrivateAttr(None)
    """If there's text that should be shown to the user rather than the system's reasoning, store it here."""

    @property
    def user_facing_text(self):
        """Returns text to be displayed to the user"""
        return self._user_facing_text or self.text

    def set_user_facing_text(self, text: str):
        self._user_facing_text = text


class AwsBedrockToolUseObject(BaseModel):
    toolUseId: str
    """The ID to correlate to a tool result"""
    name: str
    """The name of the tool to use"""
    input: dict
    """The parameters to pass into the tool"""


class AwsBedrockToolResultObject(BaseModel):
    toolUseId: str

    content: list[
        AwsBedrockTextBlock
    ]  # TODO: add additional content types that can be passed as a response

    status: Literal["success", "error"]


class AwsBedrockToolUseBlock(BaseModel):
    toolUse: AwsBedrockToolUseObject


class AwsBedrockToolResultBlock(BaseModel):
    toolResult: AwsBedrockToolResultObject


class AwsBedrockMessage(BaseModel):
    role: AwsBedrockMessageRole
    content: list[
        AwsBedrockToolUseBlock | AwsBedrockToolResultBlock | AwsBedrockTextBlock | dict
        ]


class AwsBedrockStopReason(StrEnum):
    END_TURN = auto()
    TOOL_USE = auto()
    MAX_TOKENS = auto()
    STOP_SEQUENCE = auto()
    GUARDRAIL_INTERVENED = auto()
    CONTENT_FILTERED = auto()


class AwsBedrockUsage(BaseModel):
    inputTokens: int
    outputTokens: int
    totalTokens: int


class AwsBedrockToolInputSchema(BaseModel):
    """Defines the JSON-schema compliant input schema for a tool to be used by bedrock"""

    type: Literal["object"]
    properties: dict[str, dict]
    """The json schema explaining the inputs to the function"""
    required: list[str]
    """List of required inputs to the tool"""


class AwsBedrockToolSchemaJson(BaseModel):
    """Bedrock insists that we have this intermediate step :)"""

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


class AwsBedrockConverseResponseOutput(BaseModel):
    """Note: only includes the fields we use"""

    message: AwsBedrockMessage


class AwsBedrockConverseToolConfig(BaseModel):
    tools: list[AwsBedrockToolSpecListObject]


class AwsBedrockConverseRequest(BaseModel):
    """
    Data sent to AWS Bedrock to converse with the model.

    Note: only includes the fields we use
    """

    modelId: str
    messages: list[AwsBedrockMessage]
    system: list[dict] = Field([], description="""Used to set system prompts""")
    inferenceConfig: dict = Field({})
    additionalModelRequestFields: dict = Field({})
    toolConfig: AwsBedrockConverseToolConfig | None = Field(None)

    def to_api_request_dict(self) -> dict:
        """
        Returns a dictionary that can be sent to the Bedrock API. Use this over the
        `dict()` method to remove unset fields that would crash the request.
        """
        d = self.dict()
        if self.toolConfig is None:
            d.pop("toolConfig")
        return d


class AwsBedrockConverseResponse(BaseModel):
    """
    Data returned from AWS Bedrock after conversing with the model.

    Note: only includes the fields we use
    """

    output: AwsBedrockConverseResponseOutput
    stopReason: AwsBedrockStopReason
    usage: AwsBedrockUsage
