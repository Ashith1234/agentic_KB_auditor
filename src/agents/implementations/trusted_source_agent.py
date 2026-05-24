import csv
import os
import time
from typing import Any, Dict, List

from agents.base.base_agent import BaseAgent
from agents.implementations.source_conflict_resolver import SourceConflictResolver
from domain.entities.audit_signal import AuditSignal
from infrastructure.db.scraper_monitor import ScraperMonitor


class TrustedSourceAgent(BaseAgent):
    """
    Validates KB answers against manager-approved authoritative sources.

    Pipeline
    --------
    1. Load trusted_sources.csv
    2. Scrape / read each source file
    3. Record scraper health metrics via ScraperMonitor
    4. Run data-validity checks (presence, length, schema, keywords)
    5. Pass valid source claims to SourceConflictResolver
    6. Return AuditSignal(s) describing the outcome

    Data Validity Checks
    --------------------
    presence_check      — content is not empty
    length_check        — content_length >= 100 chars
    schema_check        — required CSV fields are present
    type_check          — trust_score is a valid float in [0, 1]
    freshness_check     — last_updated field is present (not null)
    keyword_check       — expected_keywords appear in content
    trust_score_check   — trust_score >= 0.50
    scraper_health_check— scraper_working = True
    conflict_check      — other trusted sources do not strongly disagree
    """

    SOURCES_CSV   = "data/trusted_sources/trusted_sources.csv"
    MIN_LENGTH    = 100
    MIN_TRUST     = 0.50

    def __init__(self):
        super().__init__(name="TrustedSourceAgent")
        self._monitor  = ScraperMonitor()
        self._resolver = SourceConflictResolver()

    # ── Public interface ───────────────────────────────────────────────────────

    def analyze(self, data: Dict[str, Any]) -> List[AuditSignal]:
        """
        Parameters
        ----------
        data : dict with at least:
            query    — the user question being validated
            category — optional filter (e.g. "pricing", "api")

        Returns
        -------
        List[AuditSignal]
        """
        query    = data.get("query", "")
        category = data.get("category", None)

        sources   = self._load_sources(category)
        claims    = []
        signals   = []

        for src in sources:
            raw = self._scrape_source(src)

            # --- Record scraper metrics ---
            self._monitor.record_check({
                "source_url":          src["source_url"],
                "source_name":         src["source_name"],
                "category":            src.get("category", ""),
                "http_status_code":    raw["http_status_code"],
                "response_time_ms":    raw["response_time_ms"],
                "content":             raw["content"],
                "error_message":       raw["error_message"],
                "selector_failed":     raw["selector_failed"],
                "expected_keywords":   self._parse_keywords(src.get("expected_keywords", "")),
                "numeric_value_changed": False,
                "schema_valid":        self._schema_valid(src, raw["content"]),
            })

            # --- Data validity checks ---
            validity = self._run_validity_checks(src, raw)
            if not validity["is_valid"]:
                signals.append(AuditSignal(
                    signal_type  = "INVALID_SOURCE_DATA",
                    severity     = "medium",
                    description  = (
                        f"Source '{src['source_name']}' failed validity checks: "
                        f"{validity['failed_checks']}. "
                        f"Invalid data will not be used for answer validation."
                    ),
                    source_agent = self.name,
                ))
                continue

            # --- Build claim entry for conflict resolver ---
            claim_text = self._extract_claim(raw["content"], query)
            claims.append({
                "source_name":    src["source_name"],
                "source_url":     src["source_url"],
                "claim":          claim_text,
                "trust_score":    float(src.get("trust_score", 0.5)),
                "source_type":    src.get("source_type", ""),
                "last_updated":   src.get("last_updated", ""),
                "scraper_working": raw["scraper_working"],
                "schema_valid":   validity["schema_valid"],
                "content_length": len(raw["content"]),
            })

        # --- Conflict resolution ---
        if claims:
            result  = self._resolver.resolve(claims)
            signals += self._signals_from_resolution(result, query)

        return signals

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _load_sources(self, category: str = None) -> List[Dict[str, str]]:
        """Read trusted_sources.csv and optionally filter by category."""
        sources = []
        if not os.path.exists(self.SOURCES_CSV):
            return sources
        with open(self.SOURCES_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("is_active", "1") == "0":
                    continue
                if category and row.get("category", "") != category:
                    continue
                sources.append(row)
        return sources

    def _scrape_source(self, src: Dict[str, str]) -> Dict[str, Any]:
        """
        Read a local HTML/text source file (mock scraper).
        In production this would be an HTTP request.
        """
        url   = src["source_url"]
        start = time.time()
        result = {
            "http_status_code": 200,
            "response_time_ms": 0,
            "content":          "",
            "error_message":    "",
            "selector_failed":  False,
            "scraper_working":  True,
        }
        try:
            if not os.path.exists(url):
                raise FileNotFoundError(f"Source file not found: {url}")
            with open(url, "r", encoding="utf-8", errors="replace") as f:
                result["content"] = f.read()
        except Exception as exc:
            result["http_status_code"] = 0
            result["error_message"]    = str(exc)
            result["scraper_working"]  = False
        finally:
            result["response_time_ms"] = int((time.time() - start) * 1000)
        return result

    def _run_validity_checks(
        self, src: Dict[str, str], raw: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run all data-validity checks.

        Checks
        ------
        presence_check      — content is not empty
        length_check        — content_length >= 100
        schema_check        — required CSV fields exist
        type_check          — trust_score is a valid float
        freshness_check     — last_updated is not null
        keyword_check       — expected keywords present in content
        trust_score_check   — trust_score >= 0.50
        scraper_health_check— scraper_working = True
        """
        content       = raw.get("content", "")
        failed_checks = []

        # presence_check
        if not content.strip():
            failed_checks.append("presence_check")

        # length_check
        if len(content) < self.MIN_LENGTH:
            failed_checks.append("length_check")

        # schema_check (required CSV columns)
        for field in ("source_name", "source_url", "trust_score"):
            if not src.get(field):
                failed_checks.append(f"schema_check:{field}")

        # type_check
        try:
            ts = float(src.get("trust_score", 0))
            if not (0.0 <= ts <= 1.0):
                failed_checks.append("type_check:trust_score_range")
        except (ValueError, TypeError):
            failed_checks.append("type_check:trust_score_not_float")

        # freshness_check
        if not src.get("last_updated", "").strip():
            failed_checks.append("freshness_check")

        # keyword_check
        keywords = self._parse_keywords(src.get("expected_keywords", ""))
        missing  = [kw for kw in keywords if kw.lower() not in content.lower()]
        if missing:
            failed_checks.append(f"keyword_check:{missing}")

        # trust_score_check
        try:
            if float(src.get("trust_score", 0)) < self.MIN_TRUST:
                failed_checks.append("trust_score_check")
        except (ValueError, TypeError):
            pass

        # scraper_health_check
        if not raw.get("scraper_working", False):
            failed_checks.append("scraper_health_check")

        schema_valid = "schema_check" not in " ".join(failed_checks)

        return {
            "is_valid":      len(failed_checks) == 0,
            "failed_checks": failed_checks,
            "schema_valid":  schema_valid,
        }

    def _schema_valid(self, src: Dict[str, str], content: str) -> bool:
        """Quick schema check used for the monitor record."""
        required = ("source_name", "source_url", "trust_score")
        return all(src.get(f) for f in required) and len(content) >= self.MIN_LENGTH

    def _extract_claim(self, content: str, query: str) -> str:
        """
        Extract the relevant claim from scraped content.
        In production, an LLM would be used here.
        For now: return first 300 chars of content as the claim.
        """
        return content.strip()[:300] if content.strip() else "[no content]"

    @staticmethod
    def _parse_keywords(raw: str) -> List[str]:
        """Parse pipe-separated keywords from the CSV field."""
        if not raw:
            return []
        return [kw.strip() for kw in raw.split("|") if kw.strip()]

    def _signals_from_resolution(
        self, result: Dict[str, Any], query: str
    ) -> List[AuditSignal]:
        """Convert a resolver result into AuditSignal(s)."""
        status  = result["status"]
        signals = []

        if status == "AGREEMENT":
            signals.append(AuditSignal(
                signal_type  = "SOURCE_AGREEMENT",
                severity     = "low",
                description  = (
                    f"All trusted sources agree for query '{query[:80]}'. "
                    f"Claim: {result['final_claim'][:120]}. {result['reason']}"
                ),
                source_agent = self.name,
            ))

        elif status.startswith("RESOLVED_BY"):
            ws = result.get("winning_source") or {}
            signals.append(AuditSignal(
                signal_type  = "SOURCE_RESOLVED",
                severity     = "low",
                description  = (
                    f"Conflict resolved for query '{query[:80]}'. "
                    f"Winner: {ws.get('source_name', 'unknown')} "
                    f"(trust={ws.get('trust_score', 'n/a')}). "
                    f"Claim: {result['final_claim'][:120]}. {result['reason']}"
                ),
                source_agent = self.name,
            ))

        elif status == "SOURCE_CONFLICT":
            signals.append(AuditSignal(
                signal_type  = "SOURCE_CONFLICT",
                severity     = "high",
                description  = (
                    f"Unresolved source conflict for query '{query[:80]}'. "
                    f"{result['reason']} — escalated to manager review."
                ),
                source_agent = self.name,
            ))

        elif status in ("NO_SOURCES", "NO_WORKING_SOURCES", "NO_VALID_DATA"):
            signals.append(AuditSignal(
                signal_type  = "SOURCE_UNAVAILABLE",
                severity     = "high",
                description  = (
                    f"No usable sources for query '{query[:80]}'. "
                    f"Status: {status}. {result['reason']}"
                ),
                source_agent = self.name,
            ))

        return signals
