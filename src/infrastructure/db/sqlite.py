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
