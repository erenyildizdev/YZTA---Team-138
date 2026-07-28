from dataclasses import dataclass

from pgvector.django import CosineDistance

from apps.analyses.models import KnowledgeChunk
from apps.analyses.rag.embedding_service import embed_query


SIMILARITY_THRESHOLD = 0.40
MAX_CHUNKS_PER_SOURCE = 2


@dataclass
class RetrievedChunk:
    content: str
    source_title: str
    source_type: str
    source_url: str | None
    chunk_id: int
    chunk_index: int
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

    # Eşik ve kaynak tekrarı filtrelerinden sonra yeterli sayıda sonuç
    # kalabilmesi için veritabanından biraz daha fazla aday çekiyoruz.
    candidate_limit = limit * 3

    results = (
        KnowledgeChunk.objects
        .select_related("source")
        .annotate(
            distance=CosineDistance(
                "embedding",
                query_embedding,
            )
        )
        .order_by("distance")[:candidate_limit]
    )

    retrieved_chunks: list[RetrievedChunk] = []
    source_chunk_counts: dict[int, int] = {}

    for result in results:
        distance = float(result.distance)

        # Cosine distance küçüldükçe benzerlik artar.
        if distance > SIMILARITY_THRESHOLD:
            continue

        source_id = result.source_id
        current_source_count = source_chunk_counts.get(source_id, 0)

        # Aynı kaynaktan çok fazla chunk dönmesini engeller.
        if current_source_count >= MAX_CHUNKS_PER_SOURCE:
            continue

        retrieved_chunks.append(
            RetrievedChunk(
                content=result.content,
                source_title=result.source.title,
                source_type=result.source.source_type,
                source_url=result.source.source_url,
                chunk_id=result.id,
                chunk_index=result.chunk_index,
                distance=distance,
            )
        )

        source_chunk_counts[source_id] = current_source_count + 1

        if len(retrieved_chunks) >= limit:
            break

    return retrieved_chunks


def format_rag_context(
    chunks: list[RetrievedChunk],
) -> str:
    if not chunks:
        return ""

    sections: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        source_url_line = ""

        if chunk.source_url:
            source_url_line = f"Bağlantı: {chunk.source_url}\n"

        sections.append(
            (
                f"Kaynak {index}: {chunk.source_title}\n"
                f"Kaynak türü: {chunk.source_type}\n"
                f"{source_url_line}"
                f"İçerik:\n{chunk.content}"
            )
        )

    return "\n\n".join(sections)


def build_rag_context(
    query: str,
    limit: int = 4,
) -> str:
    chunks = retrieve_context(
        query=query,
        limit=limit,
    )

    return format_rag_context(chunks)