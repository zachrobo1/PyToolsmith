# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from dataclasses import dataclass
from typing import Literal


@dataclass
class AnthropicCacheControlParam:
    type: Literal["ephemeral"]


@dataclass
class AnthropicInputSchema:
    type: Literal["object"]
    required: list[str]
    properties: dict
    """The input properties"""


@dataclass
class AnthropicToolParam:
    input_schema: AnthropicInputSchema
    name: str
    description: str
    cache_control: AnthropicCacheControlParam | None = None
