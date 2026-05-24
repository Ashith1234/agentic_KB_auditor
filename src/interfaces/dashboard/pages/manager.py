import streamlit as st
import sys, os
sys.path.append(os.path.abspath("src"))

from infrastructure.db.audit_logs import AuditLogsDB
from infrastructure.db.review_queue import ReviewQueue
from infrastructure.db.feedback_db import FeedbackDB
from infrastructure.memory.semantic_store import SemanticStore
from infrastructure.db.scraper_monitor import ScraperMonitor

_audit_log = AuditLogsDB()
_queue     = ReviewQueue()
_feedback_db = FeedbackDB()
_semantic  = SemanticStore()
_scraper   = ScraperMonitor()

# ── Badge helpers ─────────────────────────────────────────────────────────────

def _badge(text: str, colour: str) -> str:
    """Return an inline HTML badge."""
    palette = {
        "green":  ("rgba(34,197,94,0.15)",  "#4ade80", "rgba(34,197,94,0.3)"),
        "red":    ("rgba(239,68,68,0.15)",   "#f87171", "rgba(239,68,68,0.3)"),
        "yellow": ("rgba(234,179,8,0.15)",   "#facc15", "rgba(234,179,8,0.3)"),
        "blue":   ("rgba(99,102,241,0.15)",  "#818cf8", "rgba(99,102,241,0.3)"),
        "purple": ("rgba(168,85,247,0.15)",  "#c084fc", "rgba(168,85,247,0.3)"),
    }
    bg, fg, border = palette.get(colour, palette["blue"])
    return (
        f'<span style="display:inline-block;padding:2px 10px;border-radius:999px;'
        f'font-size:0.72rem;font-weight:600;background:{bg};color:{fg};'
        f'border:1px solid {border}">{text}</span>'
    )

def _bool_badge(value, true_label="Yes", false_label="No",
                true_colour="green", false_colour="red") -> str:
    return _badge(true_label, true_colour) if value else _badge(false_label, false_colour)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.title("🧑‍💼 Manager Dashboard")
    st.caption("System-wide control: monitor failures, approve changes, rollback.")
    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 1 ── Live KPIs
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### 📊 Live System Stats")

    stats      = _audit_log.get_stats()
    feedbacks  = _feedback_db.get_feedbacks()
    bad_count  = sum(1 for f in feedbacks if f.get("feedback_type") == "BAD")
    pending    = _queue.get_pending()
    mon_stats  = _scraper.get_summary_stats()

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("🔍 Total Queries",      stats["total_queries"])
    c2.metric("🚨 Total Signals",      stats["total_signals"])
    c3.metric("👎 Bad Feedback",       bad_count)
    c4.metric("⏳ Pending Approvals",  len(pending))
    c5.metric("🌐 Sources Monitored",  mon_stats["total_sources"])
    c6.metric("⚠️ Needs Review",       mon_stats["needs_review"],
              delta=f'{mon_stats["needs_review"]} sources',
              delta_color="inverse")

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 2 ── Approval Queue
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### ⏳ Pending Approval Queue")
    if not pending:
        st.success("✅ No pending approvals. System is clean.")
    else:
        reviewer = st.text_input("Your name (Reviewer)", value="manager",
                                 key="reviewer_name")
        for item in pending:
            with st.container():
                col_info, col_approve, col_reject = st.columns([5, 1, 1])
                with col_info:
                    st.markdown(
                        f"**`{item['item_type']}`** — _{item['reasoning']}_"
                    )
                    st.caption(
                        f"Submitted by: {item['submitted_by']} "
                        f"at {item['created_at'][:19]}"
                    )
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

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 3 ── Trusted Source Monitoring Table
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### 🌐 Trusted Source Monitoring Table")
    st.caption(
        "Columns: HTTP Status · Response Time · Content Length · "
        "Content Change Ratio · Schema Valid · Selector Failed · "
        "Consecutive Failures · Last Success · Last Failure · "
        "Needs Review · Error Message"
    )

    sources = _scraper.get_all_sources()

    if not sources:
        st.info(
            "No sources have been monitored yet. "
            "Run an audit or trigger TrustedSourceAgent to populate this table."
        )
    else:
        # ── Filter bar ───────────────────────────────────────────────────────
        col_f1, col_f2 = st.columns([2, 1])
        search_url  = col_f1.text_input("🔎 Filter by source name / URL",
                                        placeholder="type to filter…",
                                        key="monitor_search")
        only_review = col_f2.checkbox("⚠️ Show only 'Needs Review'",
                                      key="monitor_review_only")

        filtered = [
            s for s in sources
            if (not search_url or search_url.lower() in
                (s.get("source_url", "") + s.get("source_name", "")).lower())
            and (not only_review or s.get("needs_manager_review"))
        ]

        if not filtered:
            st.caption("No sources match the current filter.")
        else:
            for s in filtered:
                working      = bool(s.get("scraper_working", 1))
                schema_ok    = bool(s.get("schema_valid", 1))
                sel_failed   = bool(s.get("selector_failed", 0))
                data_changed = bool(s.get("data_changed", 0))
                needs_review = bool(s.get("needs_manager_review", 0))
                http_code    = s.get("http_status_code") or "—"
                resp_ms      = s.get("response_time_ms")
                c_len        = s.get("content_length") or 0
                c_ratio      = s.get("content_change_ratio") or 0.0
                consec_fail  = s.get("consecutive_failures", 0)
                last_ok      = (s.get("last_success_time") or "Never")[:19]
                last_fail    = (s.get("last_failure_time") or "—")[:19]
                err_msg      = s.get("error_message") or "None"
                checked_at   = (s.get("checked_at") or "—")[:19]

                # Determine border colour
                if needs_review:
                    border_colour = "#ef4444"   # red
                elif data_changed:
                    border_colour = "#f59e0b"   # amber
                elif not working:
                    border_colour = "#f59e0b"
                else:
                    border_colour = "#22c55e"   # green

                # ── Card ─────────────────────────────────────────────────────
                st.markdown(
                    f"""
                    <div style="
                        background:rgba(25,25,55,0.7);
                        border-radius:12px;
                        border-left:4px solid {border_colour};
                        padding:0.8rem 1.2rem;
                        margin-bottom:0.7rem;
                    ">
                      <b>{s.get('source_name','—')}</b>
                      &nbsp;
                      <span style="color:#64748b;font-size:0.8rem">
                        {s.get('source_url','—')}
                      </span>
                      &nbsp;&nbsp;
                      {_badge('✅ Working', 'green') if working else _badge('❌ Failed', 'red')}
                      &nbsp;
                      {'⚠️ ' + _badge('Needs Review', 'red') if needs_review else ''}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                row1, row2, row3, row4 = st.columns(4), st.columns(4), \
                                          st.columns(4), st.columns(4)

                # Row 1 — network / timing
                row1[0].metric("🌐 HTTP Status",
                               http_code,
                               delta="OK" if http_code == 200 else "FAIL",
                               delta_color="normal" if http_code == 200 else "inverse")
                row1[1].metric("⏱ Response (ms)",
                               f"{resp_ms} ms" if resp_ms is not None else "—",
                               delta="Slow ⚠️" if (resp_ms or 0) > 5000 else "Fast ✅",
                               delta_color="inverse" if (resp_ms or 0) > 5000 else "normal")
                row1[2].metric("📄 Content Length",
                               f"{c_len} chars",
                               delta="Too short ⚠️" if c_len < 100 else "OK",
                               delta_color="inverse" if c_len < 100 else "normal")
                row1[3].metric("🔄 Change Ratio",
                               f"{c_ratio:.1%}",
                               delta="High drift ⚠️" if c_ratio > 0.5 else "Stable",
                               delta_color="inverse" if c_ratio > 0.5 else "normal")

                # Row 2 — health flags
                row2[0].markdown("**Schema Valid**")
                row2[0].markdown(
                    _bool_badge(schema_ok, "✅ Valid", "❌ Invalid"),
                    unsafe_allow_html=True,
                )
                row2[1].markdown("**Selector Failed**")
                row2[1].markdown(
                    _bool_badge(not sel_failed, "✅ OK", "❌ Failed",
                                "green", "red"),
                    unsafe_allow_html=True,
                )
                row2[2].markdown("**Data Changed**")
                row2[2].markdown(
                    _bool_badge(not data_changed, "✅ Stable", "⚠️ Changed",
                                "green", "yellow"),
                    unsafe_allow_html=True,
                )
                row2[3].metric("🔁 Consec. Failures", consec_fail,
                               delta="Review ⚠️" if consec_fail >= 3 else "OK",
                               delta_color="inverse" if consec_fail >= 3 else "normal")

                # Row 3 — times + error
                row3[0].markdown(f"**✅ Last Success:** `{last_ok}`")
                row3[1].markdown(f"**❌ Last Failure:** `{last_fail}`")
                row3[2].markdown(f"**🕐 Checked At:** `{checked_at}`")
                row3[3].markdown(
                    f"**⚠️ Error:** "
                    f"`{err_msg[:60]}{'…' if len(err_msg) > 60 else ''}`"
                )

                # ── Clear button ─────────────────────────────────────────────
                if needs_review or not working or data_changed:
                    btn_col, _ = st.columns([1, 5])
                    if btn_col.button(
                        "🔧 Clear Issue",
                        key=f"clear_{s['source_url']}",
                        help="Acknowledge and reset monitoring flags",
                    ):
                        _scraper.clear_failure(s["source_url"])
                        st.success(
                            f"Monitoring flags cleared for {s['source_url']}"
                        )
                        st.rerun()

                st.divider()

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 4 ── Source Conflict Alert Panel
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### ⚠️ Source Conflict Alerts")
    st.caption(
        "Queries where trusted sources disagree and automatic resolution was unsafe."
    )

    # Pull real SOURCE_CONFLICT signals from audit log
    all_logs = _audit_log.get_logs(limit=200)
    conflict_logs = [
        log for log in all_logs
        if "SOURCE_CONFLICT" in str(log.get("signals_count", ""))
        or "SOURCE_CONFLICT" in str(log.get("response", ""))
    ]

    # ── Demo conflict panel (always visible so Rajan can see the UI) ──────────
    st.markdown(
        """
        <div style="
            background:rgba(239,68,68,0.08);
            border:1px solid rgba(239,68,68,0.35);
            border-radius:12px;
            padding:1rem 1.4rem;
            margin-bottom:1rem;
        ">
          <h4 style="color:#f87171;margin:0 0 0.5rem 0">
            ⚠️ Source Conflict Detected &nbsp;
            <span style="font-size:0.75rem;color:#94a3b8;font-weight:400">
              [Demo — replace with live signals]
            </span>
          </h4>
          <p style="margin:0 0 0.3rem 0">
            <b>Query:</b> What is the monthly API call limit?
          </p>
          <p style="margin:0 0 0.3rem 0">
            <b>Source A</b> (Official Limits Page, trust&nbsp;0.95) says:
            <code>10 000 API calls/month</code>
          </p>
          <p style="margin:0 0 0.3rem 0">
            <b>Source B</b> (Enterprise Docs Page, trust&nbsp;0.95) says:
            <code>50 000 API calls/month</code>
          </p>
          <p style="margin:0 0 0.8rem 0;color:#94a3b8;font-size:0.88rem">
            <b>Reason:</b> Trusted sources disagree and trust scores are too close
            (gap &lt; 0.20). Automatic resolution is unsafe.
          </p>
          <p style="margin:0;color:#facc15;font-size:0.88rem">
            <b>Action:</b> Manager must select the correct source below.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    demo_col1, demo_col2 = st.columns(2)
    with demo_col1:
        if st.button(
            "✅ Use Source A — 10 000 calls/month",
            key="demo_conflict_a",
            use_container_width=True,
        ):
            st.success("Resolved: 10 000 API calls/month (Source A selected)")

    with demo_col2:
        if st.button(
            "✅ Use Source B — 50 000 calls/month",
            key="demo_conflict_b",
            use_container_width=True,
        ):
            st.success("Resolved: 50 000 API calls/month (Source B selected)")

    # ── Live conflict signals (if any) ────────────────────────────────────────
    if conflict_logs:
        st.markdown("#### Live Conflict Signals from Audit Log")
        for idx, conflict in enumerate(conflict_logs):
            with st.expander(
                f"⚠️ Conflict — {conflict.get('query', 'Unknown')[:70]} "
                f"| {conflict.get('timestamp', '')[:19]}"
            ):
                st.warning("⚠️ Source Conflict Detected")
                st.markdown(f"**Query:** {conflict.get('query', '—')}")
                st.markdown(f"**Signals found:** {conflict.get('signals_count', '—')}")
                st.markdown(
                    "**Action Required:** Manager must select the correct source."
                )
                c1, c2 = st.columns(2)
                if c1.button("Select Source 1", key=f"live_src1_{idx}"):
                    st.success("Resolved using Source 1")
                if c2.button("Select Source 2", key=f"live_src2_{idx}"):
                    st.success("Resolved using Source 2")

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 5 ── All User Feedback
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### 📋 All User Feedback")
    all_feedbacks = _feedback_db.get_feedbacks()
    if not all_feedbacks:
        st.caption("No feedback submitted yet.")
    else:
        for fb in all_feedbacks[:20]:
            badge = "🟢" if fb.get("feedback_type") == "GOOD" else "🔴"
            st.markdown(
                f"{badge} **{fb.get('feedback_type')}** — _{fb.get('reason')}_ "
                f"| `{fb.get('query', '')[:50]}` "
                f"| {fb.get('timestamp', '')[:19]}"
            )

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 6 ── Semantic Patterns (Learned)
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### 🧠 Learned Patterns (Semantic Memory)")
    patterns = _semantic.get_patterns()
    if not patterns:
        st.caption("No patterns detected yet. Run an audit first.")
    else:
        for p in patterns[:10]:
            st.markdown(
                f"- `{p['pattern']}` — seen **{p['frequency']}** time(s) "
                f"_(last: {p['timestamp'][:19]})_"
            )

    st.markdown("---")

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 7 ── Full Audit Log Stream
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown("### 📡 Live Audit Log Stream")
    logs = _audit_log.get_logs(limit=50)
    if not logs:
        st.caption("No audit logs yet.")
    else:
        for log in logs:
            with st.expander(
                f"🔹 {log['query'][:70]} | {log['timestamp'][:19]}"
            ):
                col_a, col_b = st.columns(2)
                col_a.write(f"**Signals:** {log['signals_count']}")
                col_b.write(f"**Confidence:** {log['confidence_score']}")
                st.write(f"**Agents:** {', '.join(log['agents_triggered'])}")
                st.write(f"**Response preview:** {log['response'][:150]}")


if __name__ == "__main__":
    main()
