import hashlib
import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CachedAnswer:
    query_hash: str
    query: str
    answer: str
    knowledge_version: str


class AnswerCache:
    def __init__(
        self,
        database_path: str = "data/cache/answers.db",
    ) -> None:

        path = Path(database_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.connection = sqlite3.connect(
            path,
            check_same_thread=False,
        )

        self._initialize()

    def _initialize(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS answers (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                knowledge_version TEXT NOT NULL,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connection.commit()

    @staticmethod
    def hash_query(query: str) -> str:
        return hashlib.sha256(
            query.strip().lower().encode("utf-8")
        ).hexdigest()

    def get(
        self,
        query: str,
        knowledge_version: str,
    ) -> CachedAnswer | None:

        query_hash = self.hash_query(query)

        cursor = self.connection.execute(
            """
            SELECT
                query_hash,
                query,
                answer,
                knowledge_version
            FROM answers
            WHERE query_hash = ?
              AND knowledge_version = ?
            """,
            (
                query_hash,
                knowledge_version,
            ),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return CachedAnswer(
            query_hash=row[0],
            query=row[1],
            answer=row[2],
            knowledge_version=row[3],
        )

    def put(
        self,
        query: str,
        answer: str,
        knowledge_version: str,
    ) -> None:

        query_hash = self.hash_query(query)

        self.connection.execute(
            """
            INSERT INTO answers (
                query_hash,
                query,
                answer,
                knowledge_version
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(query_hash)
            DO UPDATE SET
                query = excluded.query,
                answer = excluded.answer,
                knowledge_version =
                    excluded.knowledge_version,
                created_at = CURRENT_TIMESTAMP
            """,
            (
                query_hash,
                query,
                answer,
                knowledge_version,
            ),
        )

        self.connection.commit()

    def close(self) -> None:
        self.connection.close()