import streamlit as st
import sys, os
sys.path.append(os.path.abspath("src"))

from infrastructure.db.audit_logs import AuditLogsDB
from infrastructure.db.review_queue import ReviewQueue
from infrastructure.db.feedback_db import FeedbackDB
from infrastructure.memory.semantic_store import SemanticStore

_audit_log = AuditLogsDB()
_queue = ReviewQueue()
_feedback_db = FeedbackDB()
_semantic = SemanticStore()

def main():
    st.title("🧑‍💼 Manager Dashboard")
    st.caption("System-wide control: monitor failures, approve changes, rollback.")
    st.markdown("---")

    # ── Live KPIs ─────────────────────────────────────────────────
    st.markdown("### 📊 Live System Stats")
    stats = _audit_log.get_stats()
    feedbacks = _feedback_db.get_feedbacks()
    bad_count = sum(1 for f in feedbacks if f.get("feedback_type") == "BAD")
    pending = _queue.get_pending()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔍 Total Queries",    stats["total_queries"])
    c2.metric("🚨 Total Signals",    stats["total_signals"])
    c3.metric("👎 Bad Feedback",     bad_count)
    c4.metric("⏳ Pending Approvals", len(pending))

    st.markdown("---")

    # ── Approval Queue ────────────────────────────────────────────
    st.markdown("### ⏳ Pending Approval Queue")
    if not pending:
        st.success("✅ No pending approvals. System is clean.")
    else:
        reviewer = st.text_input("Your name (Reviewer)", value="manager", key="reviewer_name")
        for item in pending:
            with st.container():
                col_info, col_approve, col_reject = st.columns([5, 1, 1])
                with col_info:
                    st.markdown(f"**`{item['item_type']}`** — _{item['reasoning']}_")
                    st.caption(f"Submitted by: {item['submitted_by']} at {item['created_at'][:19]}")
                with col_approve:
                    if st.button("✅", key=f"approve_{item['id']}", help="Approve"):
                        _queue.approve(item["id"], reviewed_by=reviewer)
                        st.success("Approved")
                        st.rerun()
                with col_reject:
                    if st.button("❌", key=f"reject_{item['id']}", help="Reject"):
                        _queue.reject(item["id"], reviewed_by=reviewer)
                        st.warning("Rejected")
                        st.rerun()
                st.divider()

    # ── All Feedback Log ─────────────────────────────────────────
    st.markdown("### 📋 All User Feedback")
    all_feedbacks = _feedback_db.get_feedbacks()
    if not all_feedbacks:
        st.caption("No feedback submitted yet.")
    else:
        for fb in all_feedbacks[:20]:
            badge = "🟢" if fb.get("feedback_type") == "GOOD" else "🔴"
            st.markdown(
                f"{badge} **{fb.get('feedback_type')}** — _{fb.get('reason')}_ "
                f"| `{fb.get('query', '')[:50]}` | {fb.get('timestamp', '')[:19]}"
            )

    st.markdown("---")

    # ── Semantic Patterns (What the system has learned) ──────────
    st.markdown("### 🧠 Learned Patterns (Semantic Memory)")
    patterns = _semantic.get_patterns()
    if not patterns:
        st.caption("No patterns detected yet. Run an audit first.")
    else:
        for p in patterns[:10]:
            st.markdown(
                f"- `{p['pattern']}` — seen **{p['frequency']}** time(s) _(last: {p['timestamp'][:19]})_"
            )

    st.markdown("---")

    # ── Full Audit Log Stream ────────────────────────────────────
    st.markdown("### 📡 Live Audit Log Stream")
    logs = _audit_log.get_logs(limit=50)
    if not logs:
        st.caption("No audit logs yet.")
    else:
        for log in logs:
            with st.expander(f"🔹 {log['query'][:70]} | {log['timestamp'][:19]}"):
                col_a, col_b = st.columns(2)
                col_a.write(f"**Signals:** {log['signals_count']}")
                col_b.write(f"**Confidence:** {log['confidence_score']}")
                st.write(f"**Agents:** {', '.join(log['agents_triggered'])}")
                st.write(f"**Response preview:** {log['response'][:150]}")

if __name__ == "__main__":
    main()

