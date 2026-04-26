import sys
import os

# Scripts run from project root; add src/ to path so bare package names resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.logger import logger
from processing.ingestion import IngestionPipeline
from kb.embedder import Embedder
from kb.vector_store import VectorStoreManager
from kb.search import KBExplorer
from agents.implementations.version_agent import VersionAgent
from agents.implementations.duplicate_agent import DuplicateAgent
from agents.implementations.coverage_agent import CoverageAgent
from agents.implementations.scoring_agent import ScoringAgent
from agents.implementations.supervisor_agent import SupervisorAgent
from application.orchestrator.pipeline import AuditPipeline
from remediation.engine import RemediationEngine

def main():
    logger.info("=" * 60)
    logger.info("  Agentic KB Auditor — Starting Full Pipeline")
    logger.info("=" * 60)

    # ── Phase 1: Ingestion ─────────────────────────────────────
    logger.info("[1/4] Running KB Ingestion...")
    ingestion = IngestionPipeline(kb_path="data/kb")
    chunks = ingestion.run()

    if not chunks:
        logger.warning("No documents found in data/kb/. Add .txt, .pdf, or .md files.")
        return

    # ── Phase 2: Embedding & Indexing ──────────────────────────
    logger.info("[2/4] Creating Embeddings & FAISS Index...")
    embedder = Embedder()
    embedding_func = embedder.get_embedding_function()

    vs_manager = VectorStoreManager(embedding_func)
    vector_store = vs_manager.create_index(chunks)

    # ── Phase 3: Test Search ───────────────────────────────────
    logger.info("[3/4] Running Semantic Search Test...")
    explorer = KBExplorer(vector_store)
    query = "What is the Agentic KB Auditor?"
    results = explorer.search(query, k=3)

    print("\n── Search Results ──────────────────────────────────────")
    for i, r in enumerate(results, 1):
        print(f"\n[{i}] {r.page_content[:200]}...")
        print(f"    Source: {r.metadata.get('source', 'unknown')}")
    print("────────────────────────────────────────────────────────\n")

    # ── Phase 4: Run Audit Agents ──────────────────────────────
    logger.info("[4/4] Running Audit Agent Pipeline...")
    agents = [
        VersionAgent(),
        DuplicateAgent(),
        CoverageAgent(),
        ScoringAgent(),
    ]
    supervisor = SupervisorAgent(agents=agents)
    pipeline   = AuditPipeline(supervisor=supervisor)

    signals = pipeline.run(query=query, context={"chunks": len(chunks)})

    remediator = RemediationEngine()
    for signal in signals:
        remediator.process_signal(signal)

    logger.info("=" * 60)
    logger.info(f"  Pipeline complete. Signals generated: {len(signals)}")
    logger.info("  Run the dashboard: streamlit run src/interfaces/dashboard/streamlit_app.py")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
