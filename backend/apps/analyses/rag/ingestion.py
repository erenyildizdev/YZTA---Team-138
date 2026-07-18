from django.db import transaction

from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.analyses.rag.chunker import split_text
from apps.analyses.rag.embedding_service import embed_document


@transaction.atomic
def ingest_text(
    *,
    title: str,
    text: str,
    source_url: str | None = None,
) -> KnowledgeSource:
    clean_title = title.strip()
    clean_text = text.strip()

    if not clean_title:
        raise ValueError("Source title cannot be empty.")

    if not clean_text:
        raise ValueError("Source text cannot be empty.")

    source = KnowledgeSource.objects.create(
        title=clean_title,
        source_type="text",
        source_url=source_url,
    )

    chunks = split_text(
        clean_text,
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunk_objects = []

    for index, chunk_text in enumerate(chunks):
        embedding = embed_document(chunk_text)

        chunk_objects.append(
            KnowledgeChunk(
                source=source,
                content=chunk_text,
                chunk_index=index,
                embedding=embedding,
            )
        )

    KnowledgeChunk.objects.bulk_create(chunk_objects)

    return source