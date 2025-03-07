import os
import uuid

import boto3
import pytest
from anthropic import Anthropic
from dotenv import load_dotenv

from pytoolsmith import ToolDefinition, ToolLibrary

load_dotenv()


@pytest.fixture
def basic_tool_library() -> ToolLibrary:
    """Returns a tool library with a few tools."""

    def get_users_name_from_id(user_id: uuid.UUID) -> str:
        """
        Searches the database for a user's full name.
        Args:
            user_id: The ID of the user whose name we want to look up.

        Returns: The first and last name of the user.

        """
        print(user_id)
        return "Zach Cloud"

    user_lookup_tool = ToolDefinition(function=get_users_name_from_id)

    library = ToolLibrary()
    library.add_tool(user_lookup_tool)

    return library


@pytest.fixture
def live_anthropic_client():
    return Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )


@pytest.fixture
def live_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
