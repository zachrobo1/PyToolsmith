import os
from typing import Literal
import uuid

from anthropic import Anthropic
import boto3
from dotenv import load_dotenv
from openai import OpenAI
import pytest

from pytoolsmith import ToolDefinition, ToolLibrary

load_dotenv()


@pytest.fixture
def basic_tool_library() -> ToolLibrary:
    """Returns a tool library with a few tools."""

    def get_users_name_from_id(user_id: uuid.UUID, fields_to_include: list[Literal[
        "first_name", "last_name", "email", "phone"]] | None = None) -> str:
        """
        Searches the database for a user's full name.
        Args:
            user_id: The ID of the user whose name we want to look up.
            fields_to_include: A list of fields to include in the response. 
            Can set to `null` to return all fields.

        Returns: The user's information that was specified.

        """
        return "Zach Cloud"

    user_lookup_tool = ToolDefinition(
        function=get_users_name_from_id,
        user_message="Looking up user(s)..."
    )

    library = ToolLibrary(include_batch_tool=True)
    library.add_tool(user_lookup_tool)

    return library


@pytest.fixture
def live_anthropic_client():
    return Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )


@pytest.fixture
def live_openai_client():
    return OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


@pytest.fixture
def live_bedrock_client():
    return boto3.client(
        "bedrock-runtime",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_KEY"),
        region_name=os.environ.get("AWS_REGION", "us-east-1"),
    )
