from dataclasses import dataclass

from src.graph.graph_store import GraphStore


@dataclass(slots=True)
class GraphResult:
    entity: str
    entity_type: str
    relationship: str
    related_entity: str
    related_entity_type: str


class GraphRetriever:
    def __init__(self, store: GraphStore) -> None:
        self.store = store

    def search_entity(
        self,
        entity_name: str,
    ) -> list[GraphResult]:

        result = self.store.connection.execute(
            """
            MATCH (source:Entity)-[r:RELATED_TO]->(target:Entity)
            WHERE lower(source.name) = lower($name)
            RETURN
                source.name,
                source.entity_type,
                r.relationship,
                target.name,
                target.entity_type
            """,
            {
                "name": entity_name,
            },
        )

        rows = result.get_all()

        return [
            GraphResult(
                entity=row[0],
                entity_type=row[1],
                relationship=row[2],
                related_entity=row[3],
                related_entity_type=row[4],
            )
            for row in rows
        ]