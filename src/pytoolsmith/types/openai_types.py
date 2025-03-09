from dataclasses import dataclass
from typing import Literal


@dataclass
class OpenAIFunctionParameters:
    type: Literal["object"]
    additionalProperties: bool
    properties: dict
    required: list[str]


@dataclass
class OpenAIFunctionDefinition:
    name: str
    """The name of the function to be called.

    Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length
    of 64.
    """

    description: str
    parameters: OpenAIFunctionParameters
    strict: bool
    """Whether to enable strict schema adherence when generating the function call.

    If set to true, the model will follow the exact schema defined in the
    `parameters` field. Only a subset of JSON Schema is supported when `strict` is
    `true`. Learn more about Structured Outputs in the
    [function calling guide](docs/guides/function-calling).
    """


@dataclass
class OpenAIToolParam:
    function: OpenAIFunctionDefinition
    type: Literal["function"]
    """The type of the tool. Currently, only `function` is supported."""
