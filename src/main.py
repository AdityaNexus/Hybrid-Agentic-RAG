from src.ingestion.ingest import ingest


def main() -> None:
    result = ingest("data/documents/AdityaResume.pdf")

    print(f"Document: {result.document.title}")
    print(f"Document ID: {result.document.document_id}")

    print(f"\nChunks: {len(result.chunks)}")

    for chunk in result.chunks[:5]:
        print("\n---")
        print(f"ID: {chunk.chunk_id}")
        print(f"Index: {chunk.chunk_index}")
        print(f"Tokens: {chunk.token_count}")
        print(f"Page: {chunk.page_number}")
        print(chunk.text[:500])


if __name__ == "__main__":
    main()