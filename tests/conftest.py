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
