from unittest.mock import patch

from django.test import TestCase

from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.analyses.rag.ingestion import ingest_text


class TextIngestionTests(TestCase):
    @patch(
        "apps.analyses.rag.ingestion.text_ingestion.embed_document",
        return_value=[0.1] * 768,
    )
    def test_generic_text_source_is_chunked_embedded_and_persisted(
        self,
        mock_embed_document,
    ):
        source = ingest_text(
            title="  Açık Lisanslı Doğrulama Rehberi  ",
            text="Müşterinin geçmiş davranışlarını sor. " * 80,
            source_url="https://example.com/validation-guide",
        )

        self.assertEqual(source.title, "Açık Lisanslı Doğrulama Rehberi")
        self.assertEqual(source.source_type, "text")
        self.assertGreater(source.chunks.count(), 0)
        self.assertEqual(
            mock_embed_document.call_count,
            source.chunks.count(),
        )
        self.assertEqual(KnowledgeSource.objects.count(), 1)
        self.assertEqual(
            KnowledgeChunk.objects.filter(source=source).count(),
            source.chunks.count(),
        )

    @patch("apps.analyses.rag.ingestion.text_ingestion.embed_document")
    def test_empty_text_is_rejected_without_writing_source(
        self,
        mock_embed_document,
    ):
        with self.assertRaisesMessage(
            ValueError,
            "Source text cannot be empty.",
        ):
            ingest_text(title="Kaynak", text="   ")

        self.assertFalse(KnowledgeSource.objects.exists())
        mock_embed_document.assert_not_called()
