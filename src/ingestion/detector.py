from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".pdf":"pdf",
    ".docx":"docx",
    ".txt":"txt",
    ".md":"markdown",
    ".html":"html",
    ".htm":"html",
}


def detect_file_type(path: str | Path) -> str | None:
    extension = Path(path).suffix.lower()

    try:
        return SUPPORTED_EXTENSIONS[extension]
    except KeyError:
        raise ValueError(
            f"unsupported file extension: {extension}"
        )
