from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.analyses.rag.retriever import (
    RetrievedChunk,
    build_rag_context,
    format_rag_context,
    retrieve_context,
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

    @patch("apps.analyses.rag.retriever.embed_query")
    def test_retrieve_context_returns_empty_list_for_blank_query(
        self,
        mock_embed_query,
    ):
        result = retrieve_context("   ")

        self.assertEqual(result, [])
        mock_embed_query.assert_not_called()

    def test_retrieve_context_raises_error_for_invalid_limit(self):
        with self.assertRaises(ValueError):
            retrieve_context(
                query="test",
                limit=0,
            )

    def _mock_result(
        self,
        *,
        chunk_id,
        source_id,
        source_title,
        distance,
        chunk_index=0,
    ):
        source = SimpleNamespace(
            title=source_title,
            source_type="youtube",
            source_url="https://youtube.com/test",
        )

        return SimpleNamespace(
            id=chunk_id,
            source_id=source_id,
            source=source,
            content=f"Chunk {chunk_id}",
            chunk_index=chunk_index,
            distance=distance,
        )

    @patch("apps.analyses.rag.retriever.embed_query")
    @patch("apps.analyses.rag.retriever.KnowledgeChunk.objects")
    def test_retrieve_context_filters_similarity_threshold(
        self,
        mock_objects,
        mock_embed_query,
    ):
        mock_embed_query.return_value = [0.1]

        queryset = MagicMock()

        queryset.__getitem__.return_value = [
            self._mock_result(
                chunk_id=1,
                source_id=1,
                source_title="Kaynak 1",
                distance=0.20,
            ),
            self._mock_result(
                chunk_id=2,
                source_id=2,
                source_title="Kaynak 2",
                distance=0.55,
            ),
        ]

        (
            mock_objects
            .select_related.return_value
            .annotate.return_value
            .order_by.return_value
        ) = queryset

        chunks = retrieve_context(
            query="test",
            limit=4,
        )

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].source_title, "Kaynak 1")
        self.assertLessEqual(chunks[0].distance, 0.40)

    @patch("apps.analyses.rag.retriever.embed_query")
    @patch("apps.analyses.rag.retriever.KnowledgeChunk.objects")
    def test_retrieve_context_limits_chunks_per_source(
        self,
        mock_objects,
        mock_embed_query,
    ):
        mock_embed_query.return_value = [0.1]

        queryset = MagicMock()

        queryset.__getitem__.return_value = [
            self._mock_result(
                chunk_id=1,
                source_id=1,
                source_title="Video A",
                distance=0.10,
                chunk_index=0,
            ),
            self._mock_result(
                chunk_id=2,
                source_id=1,
                source_title="Video A",
                distance=0.11,
                chunk_index=1,
            ),
            self._mock_result(
                chunk_id=3,
                source_id=1,
                source_title="Video A",
                distance=0.12,
                chunk_index=2,
            ),
            self._mock_result(
                chunk_id=4,
                source_id=2,
                source_title="Video B",
                distance=0.15,
            ),
        ]

        (
            mock_objects
            .select_related.return_value
            .annotate.return_value
            .order_by.return_value
        ) = queryset

        chunks = retrieve_context(
            query="test",
            limit=4,
        )

        video_a_chunks = [
            chunk
            for chunk in chunks
            if chunk.source_title == "Video A"
        ]

        self.assertEqual(len(video_a_chunks), 2)

def test_build_rag_context_returns_formatted_context(self):
    chunks = [
        RetrievedChunk(
            content="İçerik",
            source_title="Kaynak",
            source_type="youtube",
            source_url="https://example.com",
            chunk_id=1,
            chunk_index=0,
            distance=0.12,
        )
    ]

    with patch(
        "apps.analyses.rag.retriever.retrieve_context",
        return_value=chunks,
    ):
        result = build_rag_context("test")

    self.assertIn("Kaynak", result)
    self.assertIn("İçerik", result)