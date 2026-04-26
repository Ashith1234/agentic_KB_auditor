import sys
import os
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.abspath("src"))

from infrastructure.db.version_registry import VersionRegistry
from domain.entities.version import Version
from processing.consensus_checker import ConsensusChecker
from core.logger import logger

def test_versioning():
    logger.info("Testing VersionRegistry...")
    registry = VersionRegistry()
    
    # Version 1
    v1 = Version(version_id="v1", article_id="art1", content="Content V1", content_hash="h1")
    registry.register_version(v1)
    
    # Version 2
    v2 = Version(version_id="v2", article_id="art1", content="Content V2", content_hash="h2", previous_version_id="v1")
    registry.register_version(v2)
    
    latest = registry.get_latest_version("art1")
    print(f"Latest Version: {latest.version_id}, Content: {latest.content}")
    
    # Rollback
    previous = registry.rollback("art1")
    print(f"After Rollback: {previous.version_id if previous else 'None'}, Content: {previous.content if previous else 'None'}")
    
    if previous and previous.version_id == "v1":
        print("✅ Rollback successful!")
    else:
        print("❌ Rollback failed!")

def test_consensus():
    logger.info("Testing ConsensusChecker (Mocked)...")
    checker = ConsensusChecker()
    
    # Mock LLM
    checker.llm.evaluate_json = MagicMock(return_value={
        "has_consensus": True,
        "confidence": 0.95,
        "reasoning": "Majority of sources support the fact."
    })
    
    fact = "The sky is blue."
    sources = ["Source A says sky is blue", "Source B says sky is blue", "Source C says sky is green"]
    
    result = checker.check_consensus(fact, sources)
    print(f"Consensus: {result['has_consensus']}, Confidence: {result['confidence']}")
    print(f"Reasoning: {result['reasoning']}")
    
    if result['has_consensus']:
        print("✅ Consensus check passed!")
    else:
        print("❌ Consensus check failed!")

if __name__ == "__main__":
    test_versioning()
    print("-" * 30)
    test_consensus()
