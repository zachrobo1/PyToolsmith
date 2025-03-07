from typing import Literal

from pydantic import BaseModel


class OpenAIFunctionParameters(BaseModel):
    type: Literal["object"]
    additionalProperties: Literal[False]
    properties: dict
    required: list[str]


class OpenAIFunctionDefinition(BaseModel):
    name: str
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: str

    parameters: OpenAIFunctionParameters

    strict: bool = True
    """Whether to enable strict schema adherence when generating the function call.

    If set to true, the model will follow the exact schema defined in the
    `parameters` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. Learn more about Structured Outputs in the
    [function calling guide](docs/guides/function-calling).
    """


class OpenAIToolParam(BaseModel):
    function: OpenAIFunctionDefinition

    type: Literal["function"]
    """The type of the tool. Currently, only `function` is supported."""
