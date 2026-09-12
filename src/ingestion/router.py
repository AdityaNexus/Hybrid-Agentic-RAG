from pathlib import Path

from src.ingestion.detector import detect_file_type

def detect_source(source:str)->str:
    if source.startswith("http://") or source.startswith("https://"):
        return "url"

    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"source path does not exist: {source}")

    if not path.is_file():
        raise ValueError(f"source path is not a file: {source}")

    return detect_file_type(source)

    