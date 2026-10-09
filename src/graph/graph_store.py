from pathlib import Path
from typing import Any

import kuzu

from src.config.settings import settings


class GraphStore:
    def __init__(
        self,
        database_path: str | None = None,
    ) -> None:
        path = (
            Path(database_path)
            if database_path
            else Path(settings.graph_dir) / "graph.kuzu"
        )
        path.parent.mkdir(parents=True, exist_ok=True)

        self.database = kuzu.Database(str(path))
        self.connection = kuzu.Connection(self.database)

        self._initialize_schema()

    def _initialize_schema(self) -> None:
        statements = [
            """
            CREATE NODE TABLE IF NOT EXISTS Document(
                id STRING PRIMARY KEY,
                source STRING,
                title STRING
            )
            """,
            """
            CREATE NODE TABLE IF NOT EXISTS Chunk(
                id STRING PRIMARY KEY,
                document_id STRING,
                text STRING
            )
            """,
            """
            CREATE NODE TABLE IF NOT EXISTS Entity(
                id STRING PRIMARY KEY,
                name STRING,
                entity_type STRING
            )
            """,
            """
            CREATE REL TABLE IF NOT EXISTS CONTAINS(
                FROM Document TO Chunk
            )
            """,
            """
            CREATE REL TABLE IF NOT EXISTS MENTIONS(
                FROM Chunk TO Entity
            )
            """,
            """
            CREATE REL TABLE IF NOT EXISTS RELATED_TO(
                FROM Entity TO Entity,
                relationship STRING,
                chunk_id STRING
)
            """,
        ]

        for statement in statements:
            self.connection.execute(statement)

    def add_document(
        self,
        document_id: str,
        source: str,
        title: str | None,
    ) -> None:
        self.connection.execute(
            """
            MERGE (d:Document {id: $id})
            SET d.source = $source,
                d.title = $title
            """,
            {
                "id": document_id,
                "source": source,
                "title": title or "",
            },
        )

    def add_chunk(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
    ) -> None:
        self.connection.execute(
            """
            MERGE (c:Chunk {id: $id})
            SET c.document_id = $document_id,
                c.text = $text
            """,
            {
                "id": chunk_id,
                "document_id": document_id,
                "text": text,
            },
        )

        self.connection.execute(
            """
            MATCH (d:Document {id: $document_id}),
                  (c:Chunk {id: $chunk_id})
            MERGE (d)-[:CONTAINS]->(c)
            """,
            {
                "document_id": document_id,
                "chunk_id": chunk_id,
            },
        )

    def add_entity(
        self,
        entity_id: str,
        name: str,
        entity_type: str,
    ) -> None:
        self.connection.execute(
            """
            MERGE (e:Entity {id: $id})
            SET e.name = $name,
                e.entity_type = $entity_type
            """,
            {
                "id": entity_id,
                "name": name,
                "entity_type": entity_type,
            },
        )

    def add_mention(
        self,
        chunk_id: str,
        entity_id: str,
    ) -> None:
        self.connection.execute(
            """
            MATCH (c:Chunk {id: $chunk_id}),
                  (e:Entity {id: $entity_id})
            MERGE (c)-[:MENTIONS]->(e)
            """,
            {
                "chunk_id": chunk_id,
                "entity_id": entity_id,
            },
        )
        
    def add_relationship(
        self,
        source_id : str,
        relationship : str,
        target_id : str,
        chunk_id : str,
    )->None:
        self.connection.execute(
        """
        MATCH (source:Entity {id: $source_id}),
              (target:Entity {id: $target_id})
        MERGE (source)-[r:RELATED_TO]->(target)
        SET r.relationship = $relationship,
            r.chunk_id = $chunk_id
        """,
        {
            "source_id": source_id,
            "target_id": target_id,
            "relationship": relationship,
            "chunk_id": chunk_id,
        },
    )
    
    def find_entity(self, name: str) -> list[dict]:
        result = self.connection.execute(
            """
            MATCH (e:Entity)
            WHERE lower(e.name) = lower($name)
            RETURN e.id, e.name, e.entity_type
            """,
            {
                "name": name,
            },
        )

        return [
            {
                "id": row[0],
                "name": row[1],
                "entity_type": row[2],
            }
            for row in result.get_all()
        ]

    def close(self) -> None:
        self.connection.close()