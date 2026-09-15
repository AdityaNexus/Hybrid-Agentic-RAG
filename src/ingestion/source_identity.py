from pathlib import Path

from src.ingestion.router import detect_source
from src.ingestion.source_fingerprint import fingerprint_file, fingerprint_url


def get_source_fingerprint(source:str)->tuple[str,str]:

    source_type  = detect_source(source)

    if source_type == "url":
        return source_type, fingerprint_url(source)

    return (
        source_type,
        fingerprint_file(
            Path(source)
        )
    )