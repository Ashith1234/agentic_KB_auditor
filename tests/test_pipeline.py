import pytest
from unittest.mock import MagicMock
from application.orchestrator.pipeline import AuditPipeline
from agents.implementations.supervisor_agent import SupervisorAgent
from agents.implementations.version_agent import VersionAgent
from agents.implementations.duplicate_agent import DuplicateAgent

def test_pipeline_runs():
    version_agent = VersionAgent()
    duplicate_agent = DuplicateAgent()
    supervisor = SupervisorAgent(agents=[version_agent, duplicate_agent])
    pipeline = AuditPipeline(supervisor=supervisor)
    
    signals = pipeline.run(
        query="What is the Agentic KB Auditor?",
        context={"docs": ["sample doc"]}
    )
    
    assert isinstance(signals, list)
