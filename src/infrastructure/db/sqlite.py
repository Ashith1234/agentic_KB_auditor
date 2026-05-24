import sqlite3
from typing import List, Optional
from core.logger import logger
from domain.interfaces.repository import IRepository
from domain.entities.article import Article

class SQLiteRepository(IRepository):
    """SQLite implementation of the repository pattern."""
    
    def __init__(self, db_path: str = "data/kb_audit.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    version INTEGER,
                    source TEXT
                )
            ''')

            # ── Trusted sources registry ──────────────────────────────────────
            conn.execute('''
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
            ''')

            # ── Scraper monitoring table ──────────────────────────────────────
            conn.execute('''
                CREATE TABLE IF NOT EXISTS scraper_monitor (
                    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_url             TEXT    NOT NULL,
                    source_name            TEXT,
                    category               TEXT,
                    http_status_code       INTEGER,
                    response_time_ms       INTEGER,
                    last_success_time      TEXT,
                    last_failure_time      TEXT,
                    consecutive_failures   INTEGER DEFAULT 0,
                    error_message          TEXT,
                    selector_failed        INTEGER DEFAULT 0,
                    scraper_working        INTEGER DEFAULT 1,
                    content_length         INTEGER,
                    content_hash           TEXT,
                    previous_content_hash  TEXT,
                    content_change_ratio   REAL    DEFAULT 0.0,
                    keyword_missing_count  INTEGER DEFAULT 0,
                    numeric_value_changed  INTEGER DEFAULT 0,
                    data_changed           INTEGER DEFAULT 0,
                    schema_valid           INTEGER DEFAULT 1,
                    needs_manager_review   INTEGER DEFAULT 0,
                    checked_at             TEXT,
                    UNIQUE(source_url)
                )
            ''')

    def save(self, article: Article) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO articles (id, content, version, source) VALUES (?, ?, ?, ?)",
                (article.id, article.content, article.version, article.source)
            )

    def get_by_id(self, article_id: str) -> Optional[Article]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, content, version, source FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            if row:
                return Article(id=row[0], content=row[1], version=row[2], source=row[3])
        return None

    def get_all(self) -> List[Article]:
        articles = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, content, version, source FROM articles")
            for row in cursor.fetchall():
                articles.append(Article(id=row[0], content=row[1], version=row[2], source=row[3]))
        return articles

    def delete(self, article_id: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
