import argparse
import os
import sys

# Add src to path
sys.path.append(os.path.abspath("src"))

from core.logger import logger
from agents.implementations.supervisor_agent import SupervisorAgent
from agents.implementations.version_agent import VersionAgent
from agents.implementations.duplicate_agent import DuplicateAgent
from agents.implementations.coverage_agent import CoverageAgent
from application.orchestrator.pipeline import AuditPipeline
from kb.loader import DocumentLoader
from kb.chunker import DocumentChunker

def run_manual_audit():
    logger.info("Initializing Agents for manual audit...")
    v_agent = VersionAgent()
    d_agent = DuplicateAgent()
    c_agent = CoverageAgent()
    
    supervisor = SupervisorAgent(agents=[v_agent, d_agent, c_agent])
    pipeline = AuditPipeline(supervisor)
    
    logger.info("Loading documents from data/kb...")
    loader = DocumentLoader("data/kb")
    docs = loader.load_documents()
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)
    
    chunk_data = [{"content": c.page_content, "metadata": c.metadata} for c in chunks]
    
    signals = pipeline.run("Manual CLI Audit", {"chunks": chunk_data})
    
    print("\n" + "="*30)
    print(f"AUDIT RESULTS: {len(signals)} signals generated")
    print("="*30)
    for s in signals:
        print(f"[{s.severity.upper()}] {s.signal_type.upper()}: {s.description}")
    print("="*30 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Agentic KB Auditor CLI")
    parser.add_argument("command", choices=["install", "audit", "sync"], help="Command to run")
    
    args = parser.parse_args()
    
    if args.command == "install":
        logger.info("Installing RAG Auditor Plugin...")
    elif args.command == "audit":
        run_manual_audit()
    elif args.command == "sync":
        logger.info("Syncing KB with Vector DB...")


if __name__ == "__main__":
    main()
