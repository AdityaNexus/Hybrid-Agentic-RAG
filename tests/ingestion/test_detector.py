from pathlib import Path

from src.ingestion.detector import detect_file_type


def test_pdf_detection():
    assert detect_file_type(Path("document.pdf")) == "pdf"


def test_docx_detection():
    assert detect_file_type(Path("document.docx")) == "docx"


def test_markdown_detection():
    assert detect_file_type(Path("document.md")) == "markdown"