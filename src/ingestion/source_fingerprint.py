from hashlib import sha256
from pathlib import Path


def fingerprint_file(path: str | Path) -> str:
    path = Path(path)

    digest = sha256()

    with path.open("rb") as file:
        for block in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def fingerprint_url(url: str) -> str:
    return sha256(
        url.strip().encode("utf-8")
    ).hexdigest()