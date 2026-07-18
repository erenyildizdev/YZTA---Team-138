from dataclasses import dataclass

from pgvector.django import CosineDistance

from apps.analyses.models import KnowledgeChunk
from apps.analyses.rag.embedding_service import embed_query


@dataclass
class RetrievedChunk:
    content: str
    source_title: str
    distance: float


def retrieve_context(
    query: str,
    limit: int = 4,
) -> list[RetrievedChunk]:
    clean_query = query.strip()

    if not clean_query:
        return []

    if limit <= 0:
        raise ValueError("Limit must be greater than zero.")

    query_embedding = embed_query(clean_query)

    results = (
        KnowledgeChunk.objects
        .select_related("source")
        .annotate(
            distance=CosineDistance(
                "embedding",
                query_embedding,
            )
        )
        .order_by("distance")[:limit]
    )

    return [
        RetrievedChunk(
            content=result.content,
            source_title=result.source.title,
            distance=float(result.distance),
        )
        for result in results
    ]


def build_rag_context(
    query: str,
    limit: int = 4,
) -> str:
    chunks = retrieve_context(
        query=query,
        limit=limit,
    )

    if not chunks:
        return ""

    sections = []

    for index, chunk in enumerate(chunks, start=1):
        sections.append(
            (
                f"Kaynak {index}: {chunk.source_title}\n"
                f"İçerik:\n{chunk.content}"
            )
        )

    return "\n\n".join(sections)