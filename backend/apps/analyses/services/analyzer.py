import logging

from apps.analyses.rag.retriever import (
    format_rag_context,
    retrieve_context,
)

from .llm_client import call_llm
from .prompts import build_idea_validation_prompt


logger = logging.getLogger(__name__)


def analyze_idea(idea_text: str) -> dict:
    try:
        retrieved_chunks = retrieve_context(
            query=idea_text,
            limit=4,
        )

        print("RETRIEVED CHUNKS COUNT:", len(retrieved_chunks))

        for chunk in retrieved_chunks:
            print(
                "SOURCE:",
                chunk.source_title,
                chunk.source_url,
                chunk.distance,
            )

    except Exception as exc:
        logger.exception("RAG kaynakları getirilirken hata oluştu.")
        print("RAG ERROR:", repr(exc))
        retrieved_chunks = []

    rag_context = format_rag_context(retrieved_chunks)

    prompt = build_idea_validation_prompt(
        rag_context=rag_context,
    )

    result = call_llm(
        prompt=prompt,
        idea_text=idea_text,
    )

    result["rag_used"] = bool(retrieved_chunks)

    result["sources"] = [
        {
            "title": chunk.source_title,
            "source_type": chunk.source_type,
            "source_url": chunk.source_url,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "distance": chunk.distance,
        }
        for chunk in retrieved_chunks
    ]

    return result