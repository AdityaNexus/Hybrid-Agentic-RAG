import sqlite3
from pathlib import Path
from dataclasses import dataclass


@dataclass(slots=True)
class DocumentRecord:
    source: str
    source_type: str
    content_hash: str
    document_id: str


class DocumentRegistry:
    def __init__(
        self,
        database_path: str = "data/state/documents.db",
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
            CREATE TABLE IF NOT EXISTS documents (
                source TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                document_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.connection.commit()

    def get(
        self,
        source: str,
    ) -> DocumentRecord | None:
        cursor = self.connection.execute(
            """
            SELECT
                source,
                source_type,
                content_hash,
                document_id
            FROM documents
            WHERE source = ?
            """,
            (source,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return DocumentRecord(
            source=row[0],
            source_type=row[1],
            content_hash=row[2],
            document_id=row[3],
        )

    def upsert(
        self,
        record: DocumentRecord,
    ) -> None:
        self.connection.execute(
            """
            INSERT INTO documents (
                source,
                source_type,
                content_hash,
                document_id
            )
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source)
            DO UPDATE SET
                source_type = excluded.source_type,
                content_hash = excluded.content_hash,
                document_id = excluded.document_id,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                record.source,
                record.source_type,
                record.content_hash,
                record.document_id,
            ),
        )

        self.connection.commit()

    def close(self) -> None:
        self.connection.close()