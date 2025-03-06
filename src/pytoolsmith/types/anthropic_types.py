# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import BaseModel
from typing_extensions import Literal


class AnthropicCacheControlParam(BaseModel):
    type: Literal["ephemeral"]


class AnthropicInputSchema(BaseModel):
    type: Literal["object"]

    properties: dict
    """The input properties"""


class AnthropicToolParam(BaseModel):
    input_schema: AnthropicInputSchema

    name: str

    cache_control: AnthropicCacheControlParam | None = None

    description: str
