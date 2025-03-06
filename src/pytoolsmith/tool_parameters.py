from typing import Any

from pydantic import BaseModel


class ToolParameters(BaseModel):
    """Parameters extracted from the tool definition."""

    input_properties: dict[str, Any]
    required_parameters: list[str]
    name: str
    description: str

    def to_bedrock(self):
        raise NotImplementedError

    def to_anthropic(self):
        raise NotImplementedError

    def to_openai(self):
        raise NotImplementedError
