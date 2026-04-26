import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from agents.implementations.version_agent import VersionAgent
from agents.implementations.duplicate_agent import DuplicateAgent
from core.logger import logger

def test_agents():
    from unittest.mock import MagicMock
    
    # Setup dummy data
    data = {
        "chunks": [
            {
                "content": "The current version of Python is 2.7. It is highly recommended for all production systems.",
                "metadata": {"source": "old_docs.md"}
            },
            {
                "content": "Python 3.12 is the latest stable release of the Python programming language.",
                "metadata": {"source": "new_docs.md"}
            }
        ]
    }

    logger.info("Testing VersionAgent (Mocked)...")
    v_agent = VersionAgent()
    # Mock LLM response
    v_agent.llm.evaluate_json = MagicMock(side_effect=[
        {"outdated_found": True, "explanation": "Python 2.7 is end-of-life.", "severity": "high"},
        {"outdated_found": False}
    ])
    
    v_signals = v_agent.analyze(data)
    print(f"VersionAgent Signals: {len(v_signals)}")
    for s in v_signals:
        print(f" - [{s.severity}] {s.description}")

    logger.info("Testing DuplicateAgent (Mocked)...")
    d_agent = DuplicateAgent()
    # Mock LLM response for the pair
    d_agent.llm.evaluate_json = MagicMock(return_value={
        "contradiction_found": True, 
        "explanation": "Document 1 says Python 2.7 is current, while Document 2 says 3.12 is latest."
    })
    
    d_signals = d_agent.analyze(data)
    print(f"DuplicateAgent Signals: {len(d_signals)}")
    for s in d_signals:
        print(f" - [{s.severity}] {s.description}")

    # --- New Tests ---
    from agents.implementations.coverage_agent import CoverageAgent
    from agents.implementations.learning_agent import LearningAgent

    logger.info("Testing CoverageAgent (Mocked)...")
    c_agent = CoverageAgent()
    c_agent.llm.evaluate_json = MagicMock(return_value={
        "gap_found": True,
        "gap_description": "No information found on 'Python 3.13 experimental features'."
    })
    
    c_data = {"query": "What are the features of Python 3.13?", "chunks": data["chunks"]}
    c_signals = c_agent.analyze(c_data)
    print(f"CoverageAgent Signals: {len(c_signals)}")
    for s in c_signals:
        print(f" - [{s.severity}] {s.description}")

    logger.info("Testing LearningAgent (Mocked)...")
    l_agent = LearningAgent()
    l_agent.llm.evaluate_json = MagicMock(return_value={
        "action": "suggest",
        "reasoning": "Detected end-of-life version and knowledge gap. Suggesting update to latest docs."
    })
    
    # Pass signals from previous tests
    all_signals = v_signals + d_signals + c_signals
    l_agent.analyze({"signals": all_signals})
    
    pending = l_agent.review_queue.get_pending()
    print(f"LearningAgent Proposed Actions: {len(pending)}")
    for p in pending:
        print(f" - [{p['action']}] {p['reasoning']}")

if __name__ == "__main__":
    test_agents()

