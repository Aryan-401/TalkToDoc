import pytest
from src.agent_store import Agents
from qdrant_docustore import QdrantLink


@pytest.fixture
def agent_class():
    return Agents()

@pytest.fixture
def link():
    return QdrantLink()
