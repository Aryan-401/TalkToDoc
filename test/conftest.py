import pytest
from agent_store import Agents


@pytest.fixture
def agent_class():
    return Agents()
