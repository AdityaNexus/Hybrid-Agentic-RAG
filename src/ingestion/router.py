from pathlib import Path


SUPPORTED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "text",
    ".md": "markdown",
    ".html": "html",
    ".htm": "html",
}


def detect_source(source: str) -> str:
    if not source:
        raise ValueError("Source cannot be empty.")

    if source.startswith(("http://", "https://")):
        return "url"

    path = Path(source)

    if not path.exists():
        raise FileNotFoundError(source)

    if not path.is_file():
        raise ValueError(f"Not a file: {source}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return SUPPORTED_EXTENSIONS[extension]