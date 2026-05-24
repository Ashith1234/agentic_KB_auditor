from collections import Counter
from datetime import datetime
from typing import Any, Dict, List, Optional


class SourceConflictResolver:
    """
    Resolves conflicts when multiple trusted sources return different claims.

    Resolution priority order
    -------------------------
    1. Remove failed scraper sources  (scraper_working = False)
    2. Remove invalid data            (schema_valid = False OR content_length < 100)
    3. Prefer official / internal source type
    4. Prefer higher trust_score
    5. Prefer latest last_updated date
    6. Prefer source with valid schema
    7. If still unresolvable → SOURCE_CONFLICT → manager review

    Return format
    -------------
    {
        "status":               str,    # AGREEMENT | RESOLVED_BY_* | SOURCE_CONFLICT | NO_SOURCES
        "final_claim":          str | None,
        "winning_source":       dict | None,
        "needs_manager_review": bool,
        "reason":               str,
        "conflicting_sources":  list   # populated when status == SOURCE_CONFLICT
    }
    """

    # Trust gap required to auto-resolve in favour of the higher-scored source
    TRUST_GAP_THRESHOLD = 0.20

    # Minimum content length to consider a source's data valid
    MIN_CONTENT_LENGTH = 100

    def resolve(self, source_claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        source_claims format
        --------------------
        [
            {
                "source_name":    "Official Pricing Page",
                "source_url":     "data/trusted_sources/mock_pricing_source_1.html",
                "claim":          "₹1499",
                "trust_score":    0.95,
                "source_type":    "official",          # official | internal | internal_old
                "last_updated":   "2026-05-20",
                "scraper_working": True,
                "schema_valid":   True,
                "content_length": 420,
            }
        ]
        """

        if not source_claims:
            return self._result(
                status="NO_SOURCES",
                final_claim=None,
                winning_source=None,
                needs_review=True,
                reason="No trusted sources were available.",
            )

        # ── Step 1: Remove failed scrapers ────────────────────────────────────
        working = [s for s in source_claims if s.get("scraper_working", True)]

        if not working:
            return self._result(
                status="NO_WORKING_SOURCES",
                final_claim=None,
                winning_source=None,
                needs_review=True,
                reason="All trusted sources failed scraping.",
            )

        # ── Step 2: Remove invalid data ───────────────────────────────────────
        valid = [
            s for s in working
            if s.get("schema_valid", True)
            and s.get("content_length", self.MIN_CONTENT_LENGTH) >= self.MIN_CONTENT_LENGTH
        ]

        if not valid:
            return self._result(
                status="NO_VALID_DATA",
                final_claim=None,
                winning_source=None,
                needs_review=True,
                reason=(
                    "All working sources returned invalid data "
                    "(schema invalid or content too short)."
                ),
            )

        # ── Step 3: Check agreement among valid sources ───────────────────────
        claim_counts = Counter(s["claim"] for s in valid)
        if len(claim_counts) == 1:
            return self._result(
                status="AGREEMENT",
                final_claim=valid[0]["claim"],
                winning_source=valid[0],
                needs_review=False,
                reason="All valid trusted sources agree.",
            )

        # ── Steps 4-6: Rank by official type → trust_score → recency → schema ─
        ranked = sorted(
            valid,
            key=lambda s: (
                self._source_type_rank(s.get("source_type", "")),
                s.get("trust_score", 0.0),
                s.get("last_updated", ""),
                int(s.get("schema_valid", True)),
            ),
            reverse=True,
        )

        top    = ranked[0]
        second = ranked[1]

        trust_gap = top.get("trust_score", 0.0) - second.get("trust_score", 0.0)

        # Official source with meaningful trust gap → auto-resolve
        if top.get("source_type") == "official" and trust_gap >= self.TRUST_GAP_THRESHOLD:
            return self._result(
                status="RESOLVED_BY_OFFICIAL_SOURCE",
                final_claim=top["claim"],
                winning_source=top,
                needs_review=False,
                reason=(
                    f"Selected claim from '{top['source_name']}' — official source "
                    f"with trust score {top.get('trust_score', 0):.2f} "
                    f"(gap: {trust_gap:.2f})."
                ),
            )

        # Non-official but clear trust-score gap → auto-resolve
        if trust_gap >= self.TRUST_GAP_THRESHOLD:
            return self._result(
                status="RESOLVED_BY_TRUST_SCORE",
                final_claim=top["claim"],
                winning_source=top,
                needs_review=False,
                reason=(
                    f"Selected claim from '{top['source_name']}' — "
                    f"highest trust score {top.get('trust_score', 0):.2f} "
                    f"(gap: {trust_gap:.2f})."
                ),
            )

        # ── Step 7: Cannot auto-resolve → escalate ───────────────────────────
        return self._result(
            status="SOURCE_CONFLICT",
            final_claim=None,
            winning_source=None,
            needs_review=True,
            reason=(
                "Trusted sources disagree and automatic resolution is unsafe. "
                "Trust scores are too close (gap < 0.20) and no source is "
                "clearly authoritative."
            ),
            conflicting_sources=ranked,
        )

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _source_type_rank(source_type: str) -> int:
        """Higher = preferred."""
        return {"official": 3, "internal": 2, "internal_old": 1}.get(source_type, 0)

    @staticmethod
    def _result(
        *,
        status: str,
        final_claim: Optional[str],
        winning_source: Optional[Dict],
        needs_review: bool,
        reason: str,
        conflicting_sources: Optional[List] = None,
    ) -> Dict[str, Any]:
        return {
            "status":               status,
            "final_claim":          final_claim,
            "winning_source":       winning_source,
            "needs_manager_review": needs_review,
            "reason":               reason,
            "conflicting_sources":  conflicting_sources or [],
        }
