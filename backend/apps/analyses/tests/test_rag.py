from unittest.mock import patch

from django.test import TestCase

from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.analyses.rag.retriever import build_rag_context, retrieve_context


class RagRetrieverTests(TestCase):
    def setUp(self):
        self.source = KnowledgeSource.objects.create(
            title="MOM Test Temel İlkeleri",
            source_type="text",
        )

        KnowledgeChunk.objects.create(
            source=self.source,
            content=(
                "Müşteri görüşmelerinde gelecekteki davranışlar yerine "
                "geçmiş davranışlar sorulmalıdır."
            ),
            chunk_index=0,
            embedding=[0.1] * 768,
        )

    @patch(
        "apps.analyses.rag.retriever.embed_query",
        return_value=[0.1] * 768,
    )
    def test_retrieve_context_returns_relevant_chunk(self, mock_embed):
        results = retrieve_context(
            query="Müşteri görüşmesinde ne sormalıyım?",
            limit=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0].source_title,
            "MOM Test Temel İlkeleri",
        )
        self.assertIn(
            "geçmiş davranışlar",
            results[0].content,
        )

    @patch(
        "apps.analyses.rag.retriever.embed_query",
        return_value=[0.1] * 768,
    )
    def test_build_rag_context_formats_source(self, mock_embed):
        context = build_rag_context(
            query="Müşteri görüşmesi",
            limit=1,
        )

        self.assertIn(
            "Kaynak 1: MOM Test Temel İlkeleri",
            context,
        )
        self.assertIn("İçerik:", context)