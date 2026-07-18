from apps.analyses.rag.retriever import build_rag_context

from .llm_client import call_llm
from .prompts import build_idea_validation_prompt


def analyze_idea(idea_text: str) -> dict:
    rag_context = build_rag_context(
        query=idea_text,
        limit=4,
    )

    prompt = build_idea_validation_prompt(
        rag_context=rag_context,
    )

    return call_llm(
        prompt=prompt,
        idea_text=idea_text,
    )