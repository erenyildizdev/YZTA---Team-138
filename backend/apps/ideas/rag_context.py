import logging
from typing import Any

from apps.analyses.rag.retriever import (
    format_rag_context,
    retrieve_context,
)

logger = logging.getLogger(__name__)


def build_idea_rag_query(
    idea: Any,
    purpose: str = "",
) -> str:
    parts = [
        getattr(idea, "title", ""),
        getattr(idea, "description", ""),
        getattr(idea, "target_audience", ""),
        getattr(idea, "problem", ""),
        getattr(idea, "solution", ""),
        getattr(idea, "sector", ""),
        purpose,
    ]

    return " ".join(
        part.strip()
        for part in parts
        if isinstance(part, str) and part.strip()
    )


def serialize_rag_sources(chunks: list[Any]) -> list[dict]:
    return [
        {
            "title": chunk.source_title,
            "source_type": chunk.source_type,
            "source_url": chunk.source_url,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "distance": chunk.distance,
        }
        for chunk in chunks
    ]


def get_idea_rag_context(
    idea: Any,
    *,
    purpose: str = "",
    limit: int = 4,
    save_sources: bool = True,
) -> tuple[str, list[dict]]:
    query = build_idea_rag_query(
        idea,
        purpose=purpose,
    )

    if not query:
        return "", []

    try:
        chunks = retrieve_context(
            query=query,
            limit=limit,
        )
    except Exception:
        logger.exception(
            "RAG context could not be retrieved for idea_id=%s.",
            getattr(idea, "id", None),
        )
        return "", []

    rag_context = format_rag_context(chunks)
    sources = serialize_rag_sources(chunks)

    if save_sources:
        existing_sources = (
            idea.rag_sources
            if isinstance(idea.rag_sources, list)
            else []
        )

        merged_sources: dict[str, dict] = {}

        for source in [*existing_sources, *sources]:
            chunk_id = source.get("chunk_id")

            if chunk_id is not None:
                key = f"chunk:{chunk_id}"
            else:
                key = (
                    f"url:{source.get('source_url', '')}"
                    f":index:{source.get('chunk_index', '')}"
                    f":title:{source.get('title', '')}"
                )

            merged_sources[key] = source

        idea.rag_sources = list(merged_sources.values())
        idea.save(update_fields=["rag_sources"])

    return rag_context, sources