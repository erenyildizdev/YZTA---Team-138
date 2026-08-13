def build_optional_rag_section(
    rag_context: str | None,
    *,
    guidance: str,
) -> str:
    """Build a prompt section only when retrieval returned usable context."""
    clean_context = (rag_context or "").strip()

    if not clean_context:
        return ""

    return f"""
--- RAG BAĞLAMI ---
{clean_context}
--- RAG BAĞLAMI SONU ---

RAG bağlamını yalnızca destekleyici bilgi olarak kullan.
{guidance}
""".strip()
