from src.ingestion.chunk_ids import create_chunk_id
from src.ingestion.chunks import DocumentChunk
from src.ingestion.models import CanonicalDocument
from src.ingestion.tokenizer import estimate_tokens


DEFAULT_MAX_TOKENS = 400
DEFAULT_OVERLAP_TOKENS = 50


def chunk_document(
    document: CanonicalDocument,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
) -> list[DocumentChunk]:

    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero.")

    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative.")

    if overlap_tokens >= max_tokens:
        raise ValueError(
            "overlap_tokens must be smaller than max_tokens."
        )

    chunks: list[DocumentChunk] = []

    chunk_index = 0

    for section in document.sections:
        text = section.text.strip()

        if not text:
            continue

        words = text.split()

        start = 0

        while start < len(words):
            current_words: list[str] = []
            current_tokens = 0

            end = start

            while end < len(words):
                word = words[end]
                word_tokens = estimate_tokens(word)

                if (
                    current_words
                    and current_tokens + word_tokens > max_tokens
                ):
                    break

                current_words.append(word)
                current_tokens += word_tokens
                end += 1

            chunk_text = " ".join(current_words).strip()

            if not chunk_text:
                break

            chunk_id = create_chunk_id(
                document.document_id,
                chunk_index,
                chunk_text,
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document.document_id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                    section_id=section.section_id,
                    page_number=section.page_number,
                    token_count=current_tokens,
                    metadata={
                        "source": document.source,
                        "title": document.title,
                        "source_type": document.source_type,
                    },
                )
            )

            chunk_index += 1

            if end >= len(words):
                break

            overlap_words = min(
                overlap_tokens,
                len(current_words),
            )

            start = end - overlap_words

    return chunks