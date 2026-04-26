import pytest
from agents.implementations.version_agent import VersionAgent

def test_version_agent():
    agent = VersionAgent()
    data = {"query": "test", "context": {}}
    signals = agent.analyze(data)
    
    assert isinstance(signals, list)
    # Since it's a stub, it should be empty for now
    assert len(signals) == 0
