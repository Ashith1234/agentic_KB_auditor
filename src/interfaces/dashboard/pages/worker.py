import streamlit as st
import sys, os
sys.path.append(os.path.abspath("src"))

from feedback.feedback_handler import FeedbackHandler
from infrastructure.db.audit_logs import AuditLogsDB

_handler = FeedbackHandler()
_audit_log = AuditLogsDB()

def main():
    st.title("🧑‍💻 Worker Dashboard")
    st.caption("Query your KB, review AI responses, and submit feedback.")
    st.markdown("---")

    # ── Query Interface ──────────────────────────────────────────────
    query = st.text_input("💬 Enter your query", placeholder="e.g. What is the refund policy?")
    
    if query:
        with st.spinner("Fetching response..."):
            # In production this calls the chatbot API; here we use a stub
            response = st.session_state.get(
                f"response_{query}",
                f"[Simulated KB Response] The answer to '{query}' based on current KB content."
            )
            st.session_state[f"response_{query}"] = response

        st.markdown("#### 📄 Response")
        st.info(response)

        # ── Feedback ──────────────────────────────────────────────────
        st.markdown("#### 🗳️ Was this answer correct?")
        col_like, col_dislike = st.columns(2)

        with col_like:
            if st.button("👍 Looks Good", use_container_width=True, key="like_btn"):
                _handler.handle_feedback(
                    query=query, response=response,
                    f_type="GOOD", reason="NONE", confidence=1.0
                )
                st.success("✅ Positive feedback recorded. Great!")

        with col_dislike:
            show_reason = st.session_state.get("show_reason", False)
            if st.button("👎 Something's Wrong", use_container_width=True, key="dislike_btn"):
                st.session_state["show_reason"] = True

        if st.session_state.get("show_reason", False):
            st.markdown("##### Why was this wrong?")
            reason = st.selectbox(
                "Select reason",
                ["OUTDATED", "WRONG", "MISMATCH", "VERSION_MISMATCH", "IRRELEVANT"],
                key="dislike_reason"
            )
            if st.button("Submit Feedback", key="submit_dislike", type="primary"):
                _handler.handle_feedback(
                    query=query, response=response,
                    f_type="BAD", reason=reason, confidence=0.2
                )
                st.warning(f"⚠️ Feedback submitted: {reason}. Agent will self-correct.")
                st.session_state["show_reason"] = False

    st.markdown("---")

    # ── Recent Audit Log (my queries) ──────────────────────────────
    st.markdown("#### 📋 Recent Queries")
    logs = _audit_log.get_logs(limit=10)
    if not logs:
        st.caption("No queries logged yet.")
    else:
        for log in logs:
            with st.expander(f"🔹 {log['query'][:60]}... — {log['timestamp'][:19]}"):
                st.write(f"**Signals found:** {log['signals_count']}")
                st.write(f"**Confidence:** {log['confidence_score']}")
                st.write(f"**Agents:** {', '.join(log['agents_triggered'])}")

if __name__ == "__main__":
    main()

