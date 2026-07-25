from django.test import TestCase

from apps.analyses.rag.retriever import (
    RetrievedChunk,
    build_rag_context,
    format_rag_context,
)


class RagRetrieverTests(TestCase):
    def test_build_rag_context_returns_empty_string_for_empty_query(self):
        result = build_rag_context("")

        self.assertEqual(result, "")

    def test_format_rag_context_returns_empty_string_for_empty_chunks(self):
        result = format_rag_context([])

        self.assertEqual(result, "")

    def test_format_rag_context_includes_source_metadata(self):
        chunks = [
            RetrievedChunk(
                content="Test kaynak içeriği",
                source_title="Test Kaynağı",
                source_type="pdf",
                source_url="https://example.com/test.pdf",
                chunk_id=1,
                chunk_index=0,
                distance=0.15,
            )
        ]

        result = format_rag_context(chunks)

        self.assertIn("Test Kaynağı", result)
        self.assertIn("pdf", result)
        self.assertIn("https://example.com/test.pdf", result)
        self.assertIn("Test kaynak içeriği", result)