from src.ingestion.parser import parse_file

def main() -> None:
    document = parse_file("data/documents/AdityaResume.pdf")

    print(f"Document ID: {document.document_id}")
    print(f"Source: {document.source}")
    print(f"Type: {document.source_type}")
    print(f"Title: {document.title}")

    print(f"\nSections: {len(document.sections)}")
    print(f"Tables: {len(document.tables)}")

    print("\n--- TEXT ---")
    print(document.full_text()[:3000])


if __name__ == "__main__":
    main()