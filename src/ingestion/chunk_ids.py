from hashlib import sha256


def create_chunk_id(
    document_id: str,
    chunk_index: int,
    text: str,
) -> str:
    payload = f"{document_id}:{chunk_index}:{text}".encode("utf-8")

    return sha256(payload).hexdigest()