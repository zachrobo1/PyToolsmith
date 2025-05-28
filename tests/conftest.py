from pydantic import BaseModel
from pydantic.v1 import BaseModel as BaseModelV1
import pytest

from pytoolsmith import pytoolsmith_config


@pytest.fixture(autouse=True)
def reset_config():
    """Resets the configuration between tests."""
    pytoolsmith_config.reset_type_map()
    pytoolsmith_config.reset_format_map()
    yield
    pytoolsmith_config.reset_type_map()
    pytoolsmith_config.reset_format_map()


@pytest.fixture
def pydantic_company_model() -> type[BaseModel]:
    """Returns the pydantic company model for testing."""

    class Address(BaseModel):
        street: str
        city: str
        zip_code: str

    class User(BaseModel):
        name: str
        address: Address  # ← uses Address once

    class Company(BaseModel):
        name: str
        headquarters: Address  # ← uses Address a second time → triggers $ref
        employees: list[User]

    return Company


@pytest.fixture
def pydantic_company_model_v1() -> type[BaseModelV1]:
    """Returns the pydantic company model (v1 version) for testing."""

    class Address(BaseModelV1):
        street: str
        city: str
        zip_code: str

    class User(BaseModelV1):
        name: str
        address: Address  # ← uses Address once

    class Company(BaseModelV1):
        name: str
        headquarters: Address  # ← uses Address a second time → triggers $ref
        employees: list[User]

    return Company
