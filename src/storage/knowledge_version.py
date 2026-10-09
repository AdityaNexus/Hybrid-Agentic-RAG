import hashlib

from src.storage.document_registry import DocumentRegistry


def get_knowledge_version(
    registry: DocumentRegistry,
) -> str:

    cursor = registry.connection.execute(
        """
        SELECT source, content_hash
        FROM documents
        ORDER BY source
        """
    )

    rows = cursor.fetchall()

    payload = "|".join(
        f"{source}:{content_hash}"
        for source, content_hash in rows
    )

    return hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()