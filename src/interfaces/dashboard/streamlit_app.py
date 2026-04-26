import streamlit as st
import sys
import os
import json
import time
import random
from datetime import datetime, timedelta

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic KB Auditor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark premium theme */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0a14 0%, #111128 60%, #0d0d20 100%);
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 35, 0.95);
        border-right: 1px solid rgba(99,102,241,0.2);
    }
    [data-testid="stHeader"] {background: transparent;}

    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(30, 30, 60, 0.6);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 14px;
        padding: 1rem 1.5rem;
        backdrop-filter: blur(12px);
    }

    /* Section headers */
    h1 { color: #a78bfa !important; }
    h2 { color: #818cf8 !important; }
    h3 { color: #94a3b8 !important; }

    /* Divider */
    hr { border-color: rgba(99,102,241,0.2) !important; }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .badge-green  { background: rgba(34,197,94,0.15);  color: #4ade80; border: 1px solid rgba(34,197,94,0.3); }
    .badge-yellow { background: rgba(234,179,8,0.15);  color: #facc15; border: 1px solid rgba(234,179,8,0.3); }
    .badge-red    { background: rgba(239,68,68,0.15);  color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
    .badge-blue   { background: rgba(99,102,241,0.15); color: #818cf8; border: 1px solid rgba(99,102,241,0.3); }

    /* Signal card */
    .signal-card {
        background: rgba(25, 25, 55, 0.7);
        border-radius: 12px;
        border-left: 4px solid #6366f1;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.7rem;
    }
    .signal-card.high   { border-left-color: #ef4444; }
    .signal-card.medium { border-left-color: #f59e0b; }
    .signal-card.low    { border-left-color: #22c55e; }

    /* Progress bar */
    .stProgress > div > div > div { background: linear-gradient(90deg, #6366f1, #a78bfa); }

    /* Scrollable code area */
    .log-box {
        background: rgba(5,5,20,0.85);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 10px;
        padding: 1rem;
        font-family: monospace;
        font-size: 0.78rem;
        height: 220px;
        overflow-y: auto;
        color: #94a3b8;
    }
</style>
""", unsafe_allow_html=True)

# Add src to path
sys.path.append(os.path.abspath("src"))

from application.orchestrator.pipeline import AuditPipeline
from agents.implementations.supervisor_agent import SupervisorAgent
from agents.implementations.version_agent import VersionAgent
from agents.implementations.duplicate_agent import DuplicateAgent
from agents.implementations.coverage_agent import CoverageAgent
from agents.implementations.learning_agent import LearningAgent
from infrastructure.db.review_queue import ReviewQueue
from kb.loader import DocumentLoader
from kb.chunker import DocumentChunker

# ── System Initialization ──────────────────────────────────────────────────
@st.cache_resource
def get_system():
    # Initialize agents
    v_agent = VersionAgent()
    d_agent = DuplicateAgent()
    c_agent = CoverageAgent()
    l_agent = LearningAgent()
    
    supervisor = SupervisorAgent(agents=[v_agent, d_agent, c_agent])
    pipeline = AuditPipeline(supervisor)
    review_queue = ReviewQueue()
    
    return pipeline, review_queue, l_agent

pipeline, review_queue, l_agent = get_system()

# ── Helpers ──────────────────────────────────────────────────────────────────
def run_audit_cycle(query: str = "General KB Audit"):
    """Runs a live audit cycle across all documents."""
    loader = DocumentLoader("data/kb")
    docs = loader.load_documents()
    chunker = DocumentChunker()
    chunks = chunker.chunk_documents(docs)
    
    # Prepare data for pipeline
    # Convert LangChain documents to simple dicts for agents
    chunk_data = [{"content": c.page_content, "metadata": c.metadata} for c in chunks]

    
    signals = pipeline.run(query, {"chunks": chunk_data})
    
    # Run LearningAgent to propose remediations
    l_agent.analyze({"signals": signals})
    
    return signals

def health_color(score: float):
    if score >= 80: return "#4ade80"
    if score >= 55: return "#facc15"
    return "#f87171"


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 KB Auditor")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🤖 Agents", "📜 Logs", "🔄 Versions", "⚙️ Settings"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown("**System Status**")
    col_a, col_b = st.columns(2)
    col_a.markdown('<span class="badge badge-green">● API</span>', unsafe_allow_html=True)
    col_b.markdown('<span class="badge badge-green">● FAISS</span>', unsafe_allow_html=True)
    from datetime import timezone
    st.caption(f"Last sync: {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("Knowledge Base Auditor")
    st.caption("Real-time health monitoring & audit signals")
    st.markdown("---")

    # Action bar
    col_t1, col_t2 = st.columns([4, 1])
    if col_t2.button("🚀 Trigger Full Audit", use_container_width=True):
        with st.spinner("Agents are auditing documents..."):
            signals = run_audit_cycle()
            st.session_state['signals'] = signals
            st.success(f"Audit complete! Found {len(signals)} issues.")

    # Get signals from state or initialize empty
    active_signals = st.session_state.get('signals', [])
    pending_remediations = review_queue.get_pending()

    # Top metrics
    health = max(0, 100 - (len(active_signals) * 5)) # Simple health heuristic
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🩺 KB Health Score", f"{health}%", f"{'-' if health < 100 else ''}{100-health}%")
    c2.metric("📄 Active Signals",  len(active_signals), f"+{len(active_signals)}")
    c3.metric("🛠️ Suggestions",    len(pending_remediations), f"+{len(pending_remediations)}")
    c4.metric("✅ Auto-Fixed",       "0",        "0")

    st.markdown("---")

    # Health gauge
    st.markdown(f"### Health Score — <span style='color:{health_color(health)}'>{health}%</span>", unsafe_allow_html=True)
    st.progress(int(health))
    st.markdown("---")

    # Audit signals
    left, right = st.columns([3, 2])

    with left:
        st.markdown("### 🔍 Active Audit Signals")
        if not active_signals:
            st.info("No active signals found. Knowledge base is healthy!")
        else:
            for s in active_signals:
                severity_class = s.severity
                st.markdown(f"""
                <div class="signal-card {severity_class}">
                    <b>{s.signal_type.upper()}</b>
                    &nbsp;<span class="badge badge-{'red' if s.severity=='high' else 'yellow' if s.severity=='medium' else 'green'}">{s.severity.upper()}</span>
                    &nbsp;<span style="color:#64748b;font-size:0.8rem">via {s.source_agent}</span>
                    <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.9rem">{s.description}</p>
                </div>
                """, unsafe_allow_html=True)

    with right:
        st.markdown("### 📈 Remediation Summary")
        st.markdown(f"""
        <div class="signal-card low">
            <b>Auto-Fixed</b> &nbsp;<span class="badge badge-green">0</span>
            <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.88rem">Low-severity issues resolved automatically.</p>
        </div>
        <div class="signal-card medium">
            <b>Suggestions Pending</b> &nbsp;<span class="badge badge-yellow">{len(pending_remediations)}</span>
            <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.88rem">Awaiting human review in HITL queue.</p>
        </div>
        <div class="signal-card high">
            <b>Escalated</b> &nbsp;<span class="badge badge-red">0</span>
            <p style="margin:4px 0 0 0; color:#cbd5e1; font-size:0.88rem">Critical contradictions requiring manual action.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if pending_remediations:
            if st.button("📝 Review Suggestions", use_container_width=True):
                st.info("Reviewing latest suggestion: " + pending_remediations[-1]['reasoning'])


# ─────────────────────────────────────────────────────────────────────────────
# PAGE: AGENTS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🤖 Agents":
    st.title("Agent Activity")
    st.caption("Live status of all auditing agents")
    st.markdown("---")

    agents = [
        ("VersionAgent",    "Detects outdated content",        "Idle",    "3 signals",  "#22c55e"),
        ("DuplicateAgent",  "Finds duplicate/conflicting docs","Running", "1 signal",   "#6366f1"),
        ("CoverageAgent",   "Identifies missing topics",       "Idle",    "0 signals",  "#22c55e"),
        ("RetrievalAgent",  "Fetches verified information",    "Idle",    "0 signals",  "#22c55e"),
        ("ScoringAgent",    "Evaluates KB health score",       "Running", "Score: 76%", "#6366f1"),
        ("LearningAgent",   "Proposes KB updates",             "Idle",    "2 updates",  "#22c55e"),
        ("SupervisorAgent", "Aggregates all agent signals",    "Running", "4 signals",  "#6366f1"),
    ]

    for name, desc, status, output, color in agents:
        with st.container():
            col1, col2, col3, col4 = st.columns([2.5, 3, 1.5, 2])
            col1.markdown(f"**{name}**")
            col2.caption(desc)
            badge = "badge-green" if status == "Idle" else "badge-blue"
            col3.markdown(f'<span class="badge {badge}">{status}</span>', unsafe_allow_html=True)
            col4.caption(output)
        st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: LOGS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "📜 Logs":
    st.title("System Logs")
    st.caption("Structured JSON logs from all agents and the pipeline")
    st.markdown("---")

    log_path = "data/logs/system.log"
    col_filter, col_level = st.columns([3,1])
    search = col_filter.text_input("Search logs", placeholder="Filter by keyword...")
    level  = col_level.selectbox("Level", ["ALL", "INFO", "WARNING", "ERROR"])

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            lines = f.readlines()
        filtered = [
            l for l in lines
            if (not search or search.lower() in l.lower())
            and (level == "ALL" or level in l.upper())
        ]
        st.code("".join(filtered[-50:]) if filtered else "No matching log entries.", language="log")
    else:
        # Demo logs
        demo_logs = "\n".join([
            f"2026-04-24 16:30:00 | INFO    | kb.loader:load_documents:32 - Loading documents from data/kb",
            f"2026-04-24 16:30:01 | INFO    | kb.chunker:chunk_documents:19 - Chunking 1 documents with size=500",
            f"2026-04-24 16:30:02 | INFO    | kb.chunker:chunk_documents:22 - Created 4 chunks.",
            f"2026-04-24 16:30:03 | INFO    | kb.embedder:_get_sbert_embeddings:28 - Using SBERT Embeddings",
            f"2026-04-24 16:30:05 | INFO    | kb.vector_store:create_index:19 - Creating new FAISS index",
            f"2026-04-24 16:30:05 | INFO    | kb.vector_store:save_index:27 - FAISS index saved to data/vector_store",
            f"2026-04-24 16:30:06 | INFO    | agents.base.base_agent:__init__:12 - Initializing Agent: VersionAgent",
            f"2026-04-24 16:30:06 | INFO    | agents.base.base_agent:__init__:12 - Initializing Agent: DuplicateAgent",
            f"2026-04-24 16:30:06 | INFO    | agents.base.base_agent:__init__:12 - Initializing Agent: SupervisorAgent",
            f"2026-04-24 16:30:07 | INFO    | application.orchestrator.pipeline:run:14 - Starting audit pipeline",
            f"2026-04-24 16:30:07 | INFO    | agents.implementations.supervisor_agent:analyze:14 - Supervisor starting analysis cycle.",
            f"2026-04-24 16:30:08 | INFO    | application.orchestrator.pipeline:run:18 - Pipeline completed. Generated 0 signals.",
        ])
        st.code(demo_logs, language="log")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: VERSIONS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "🔄 Versions":
    st.title("Version Control & Rollback")
    st.caption("Review and revert KB document changes")
    st.markdown("---")

    versions = [
        {"id": "v3", "article": "overview.md", "changed_by": "LearningAgent", "time": "16:31:20", "action": "Updated Python version references"},
        {"id": "v2", "article": "overview.md", "changed_by": "LearningAgent", "time": "12:15:04", "action": "Removed duplicate chunk"},
        {"id": "v1", "article": "overview.md", "changed_by": "system",        "time": "09:00:00", "action": "Initial ingestion"},
    ]

    selected = st.selectbox("Select document", ["overview.md"])

    for v in versions:
        col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 3, 2])
        col1.markdown(f"<span class='badge badge-blue'>{v['id']}</span>", unsafe_allow_html=True)
        col2.caption(v["article"])
        col3.caption(v["changed_by"])
        col4.caption(v["action"])
        if col5.button(f"Rollback to {v['id']}", key=v["id"]):
            st.success(f"Rollback to {v['id']} initiated!")
        st.markdown("---")

    st.markdown("### Diff Viewer")
    old = "The Agentic KB Auditor monitors knowledge bases using Python 2.7."
    new = "The Agentic KB Auditor monitors knowledge bases using Python 3.9+."

    import difflib
    diff = list(difflib.ndiff([old], [new]))
    st.code("\n".join(diff), language="diff")

# ─────────────────────────────────────────────────────────────────────────────
# PAGE: SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
elif page == "⚙️ Settings":
    st.title("System Settings")
    st.markdown("---")

    with st.form("settings_form"):
        st.subheader("Knowledge Base")
        chunk_size    = st.slider("Chunk Size",    100, 2000, 500)
        chunk_overlap = st.slider("Chunk Overlap", 0,   500,  50)

        st.subheader("Embedding Model")
        embed_provider = st.selectbox("Provider", ["SBERT (local)", "OpenAI"])
        if embed_provider == "OpenAI":
            st.text_input("OpenAI API Key", type="password", placeholder="sk-...")

        st.subheader("Remediation Thresholds")
        auto_fix_threshold  = st.slider("Auto-Fix below severity", 0, 100, 30)
        escalate_threshold  = st.slider("Escalate above severity", 0, 100, 80)

        st.subheader("Scheduler")
        audit_interval = st.number_input("Audit Interval (seconds)", 60, 86400, 3600)

        submitted = st.form_submit_button("💾 Save Settings")
        if submitted:
            st.success("Settings saved successfully!")
