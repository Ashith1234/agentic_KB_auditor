import sqlite3
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = "data/scraper_monitor.db"

# ── Thresholds ─────────────────────────────────────────────────────────────────
SLOW_RESPONSE_MS        = 5_000    # > 5 s → slow source warning
MIN_CONTENT_LENGTH      = 100      # < 100 chars → invalid scrape
MAX_CONSECUTIVE_FAIL    = 3        # >= 3 → manager review required
STALE_DAYS              = 7        # last_success older than 7 days → stale warning
HIGH_CHANGE_RATIO       = 0.50     # > 50 % content change → data_changed flag
MAX_MISSING_KEYWORDS    = 2        # > 2 missing expected keywords → flag


class ScraperMonitor:
    """
    Monitors scraper health and data quality for every trusted source.

    Key metrics tracked
    -------------------
    Failure metrics     : http_status_code, response_time_ms, error_message,
                          selector_failed, consecutive_failures,
                          last_success_time, last_failure_time, scraper_working
    Data-change metrics : content_hash, previous_content_hash,
                          content_change_ratio, data_changed,
                          keyword_missing_count, numeric_value_changed
    Validity metrics    : content_length, schema_valid
    Review flag         : needs_manager_review

    Thresholds (for Rajan)
    ----------------------
    http_status_code != 200        → source failed
    response_time_ms > 5 000       → slow source warning
    content_length  < 100          → invalid scrape
    selector_failed = True         → HTML structure changed
    consecutive_failures >= 3      → manager review required
    last_success_time older 7 days → stale source warning
    content_change_ratio > 0.50    → significant data drift
    keyword_missing_count > 2      → expected content missing
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ── Schema ─────────────────────────────────────────────────────────────────

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # ── trusted_sources table ─────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trusted_sources (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name       TEXT    NOT NULL,
                    source_url        TEXT    NOT NULL UNIQUE,
                    category          TEXT,
                    source_type       TEXT,
                    trust_score       REAL    DEFAULT 0.5,
                    expected_keywords TEXT,
                    expected_schema   TEXT,
                    is_active         INTEGER DEFAULT 1,
                    created_at        TEXT
                )
            """)

            # ── scraper_monitor table ─────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scraper_monitor (
                    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url             TEXT    NOT NULL,
                    source_name            TEXT,
                    category               TEXT,

                    -- Failure / health metrics
                    http_status_code       INTEGER,
                    response_time_ms       INTEGER,
                    last_success_time      TEXT,
                    last_failure_time      TEXT,
                    consecutive_failures   INTEGER DEFAULT 0,
                    error_message          TEXT,
                    selector_failed        INTEGER DEFAULT 0,
                    scraper_working        INTEGER DEFAULT 1,

                    -- Data size / content metrics
                    content_length         INTEGER,
                    content_hash           TEXT,
                    previous_content_hash  TEXT,
                    content_change_ratio   REAL    DEFAULT 0.0,

                    -- Data change / drift metrics
                    keyword_missing_count  INTEGER DEFAULT 0,
                    numeric_value_changed  INTEGER DEFAULT 0,
                    data_changed           INTEGER DEFAULT 0,

                    -- Validity metrics
                    schema_valid           INTEGER DEFAULT 1,

                    -- Review flag
                    needs_manager_review   INTEGER DEFAULT 0,

                    checked_at             TEXT,

                    UNIQUE(source_url)
                )
            """)
            conn.commit()

    # ── Public API ─────────────────────────────────────────────────────────────

    def record_check(self, data: Dict[str, Any]) -> None:
        """
        Upsert a monitoring record for one source URL.

        Expected keys in `data`
        -----------------------
        source_url             (required)
        source_name            optional
        category               optional
        http_status_code       int
        response_time_ms       int
        content                str  — full scraped text (used to derive hash/length)
        error_message          str
        selector_failed        bool
        expected_keywords      list[str]  — for keyword_missing_count
        numeric_value_changed  bool
        schema_valid           bool
        """
        url              = data["source_url"]
        now              = datetime.utcnow().isoformat()
        status_code      = data.get("http_status_code", 0)
        response_time    = data.get("response_time_ms", 0)
        content          = data.get("content", "")
        error_msg        = data.get("error_message", "")
        selector_failed  = int(bool(data.get("selector_failed", False)))
        numeric_changed  = int(bool(data.get("numeric_value_changed", False)))
        schema_valid     = int(bool(data.get("schema_valid", True)))

        content_length   = len(content)
        current_hash     = self._hash(content)

        # ── Fetch previous record ─────────────────────────────────────────────
        prev = self._get_record(url)
        previous_hash        = prev["content_hash"]          if prev else None
        previous_failures    = prev["consecutive_failures"]  if prev else 0
        prev_success_time    = prev["last_success_time"]     if prev else None

        # ── Derive content_change_ratio ───────────────────────────────────────
        change_ratio = self._compute_change_ratio(
            prev["content_length"] if prev else 0, content_length
        )

        # ── Keyword check ─────────────────────────────────────────────────────
        expected_keywords    = data.get("expected_keywords", [])
        keyword_missing_count = sum(
            1 for kw in expected_keywords
            if kw.lower() not in content.lower()
        )

        # ── scraper_working determination ─────────────────────────────────────
        scraper_working = int(
            status_code == 200
            and content_length >= MIN_CONTENT_LENGTH
            and not selector_failed
            and not error_msg
        )

        # ── data_changed flag ─────────────────────────────────────────────────
        data_changed = int(
            (previous_hash is not None and current_hash != previous_hash)
            and change_ratio > HIGH_CHANGE_RATIO
        )

        # ── success / failure times ───────────────────────────────────────────
        if scraper_working:
            last_success_time  = now
            last_failure_time  = prev["last_failure_time"] if prev else None
            consecutive_failures = 0
        else:
            last_success_time  = prev_success_time
            last_failure_time  = now
            consecutive_failures = previous_failures + 1

        # ── needs_manager_review ──────────────────────────────────────────────
        needs_review = int(
            consecutive_failures >= MAX_CONSECUTIVE_FAIL
            or data_changed
            or keyword_missing_count > MAX_MISSING_KEYWORDS
            or numeric_changed
        )

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO scraper_monitor (
                    source_url, source_name, category,
                    http_status_code, response_time_ms,
                    last_success_time, last_failure_time,
                    consecutive_failures, error_message,
                    selector_failed, scraper_working,
                    content_length, content_hash, previous_content_hash,
                    content_change_ratio,
                    keyword_missing_count, numeric_value_changed, data_changed,
                    schema_valid, needs_manager_review,
                    checked_at
                ) VALUES (
                    :source_url, :source_name, :category,
                    :http_status_code, :response_time_ms,
                    :last_success_time, :last_failure_time,
                    :consecutive_failures, :error_message,
                    :selector_failed, :scraper_working,
                    :content_length, :content_hash, :previous_content_hash,
                    :content_change_ratio,
                    :keyword_missing_count, :numeric_value_changed, :data_changed,
                    :schema_valid, :needs_manager_review,
                    :checked_at
                )
                ON CONFLICT(source_url) DO UPDATE SET
                    source_name            = excluded.source_name,
                    category               = excluded.category,
                    http_status_code       = excluded.http_status_code,
                    response_time_ms       = excluded.response_time_ms,
                    last_success_time      = excluded.last_success_time,
                    last_failure_time      = excluded.last_failure_time,
                    consecutive_failures   = excluded.consecutive_failures,
                    error_message          = excluded.error_message,
                    selector_failed        = excluded.selector_failed,
                    scraper_working        = excluded.scraper_working,
                    content_length         = excluded.content_length,
                    previous_content_hash  = scraper_monitor.content_hash,
                    content_hash           = excluded.content_hash,
                    content_change_ratio   = excluded.content_change_ratio,
                    keyword_missing_count  = excluded.keyword_missing_count,
                    numeric_value_changed  = excluded.numeric_value_changed,
                    data_changed           = excluded.data_changed,
                    schema_valid           = excluded.schema_valid,
                    needs_manager_review   = excluded.needs_manager_review,
                    checked_at             = excluded.checked_at
            """, {
                "source_url":            url,
                "source_name":           data.get("source_name", ""),
                "category":              data.get("category", ""),
                "http_status_code":      status_code,
                "response_time_ms":      response_time,
                "last_success_time":     last_success_time,
                "last_failure_time":     last_failure_time,
                "consecutive_failures":  consecutive_failures,
                "error_message":         error_msg,
                "selector_failed":       selector_failed,
                "scraper_working":       scraper_working,
                "content_length":        content_length,
                "content_hash":          current_hash,
                "previous_content_hash": previous_hash,
                "content_change_ratio":  round(change_ratio, 4),
                "keyword_missing_count": keyword_missing_count,
                "numeric_value_changed": numeric_changed,
                "data_changed":          data_changed,
                "schema_valid":          schema_valid,
                "needs_manager_review":  needs_review,
                "checked_at":            now,
            })
            conn.commit()

    def get_all_sources(self) -> List[Dict[str, Any]]:
        """Return all monitored source records as a list of dicts."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM scraper_monitor ORDER BY checked_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_sources_needing_review(self) -> List[Dict[str, Any]]:
        """Return only sources flagged for manager review."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM scraper_monitor WHERE needs_manager_review = 1"
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear_failure(self, source_url: str) -> None:
        """Clear all failure / review flags for a source after manager resolves it."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE scraper_monitor SET
                    last_failure_time    = NULL,
                    consecutive_failures = 0,
                    error_message        = '',
                    selector_failed      = 0,
                    data_changed         = 0,
                    numeric_value_changed = 0,
                    needs_manager_review = 0
                WHERE source_url = ?
            """, (source_url,))
            conn.commit()

    def get_summary_stats(self) -> Dict[str, int]:
        """Quick KPI counts for the Manager Dashboard header."""
        with sqlite3.connect(self.db_path) as conn:
            total    = conn.execute("SELECT COUNT(*) FROM scraper_monitor").fetchone()[0]
            working  = conn.execute("SELECT COUNT(*) FROM scraper_monitor WHERE scraper_working = 1").fetchone()[0]
            review   = conn.execute("SELECT COUNT(*) FROM scraper_monitor WHERE needs_manager_review = 1").fetchone()[0]
            changed  = conn.execute("SELECT COUNT(*) FROM scraper_monitor WHERE data_changed = 1").fetchone()[0]
        return {
            "total_sources":         total,
            "working_sources":       working,
            "failed_sources":        total - working,
            "needs_review":          review,
            "data_changed_sources":  changed,
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()

    @staticmethod
    def _compute_change_ratio(old_len: int, new_len: int) -> float:
        """Proportion of content length that changed (simple heuristic)."""
        if old_len == 0 and new_len == 0:
            return 0.0
        if old_len == 0:
            return 1.0
        return abs(new_len - old_len) / max(old_len, new_len)

    def _get_record(self, source_url: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM scraper_monitor WHERE source_url = ?", (source_url,)
            ).fetchone()
            return dict(row) if row else None
