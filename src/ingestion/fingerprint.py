from hashlib import sha256
from pathlib import Path


def calculate_file_hash(path: str | Path) -> str:
    path = Path(path)

    digest = sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()