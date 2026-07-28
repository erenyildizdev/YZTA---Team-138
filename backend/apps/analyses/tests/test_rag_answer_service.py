from unittest.mock import patch

from django.test import TestCase

from apps.analyses.rag.rag_answer_service import (
    RagAnswer,
    answer_with_rag,
    build_prompt,
)
from apps.analyses.rag.retriever import RetrievedChunk


class RagAnswerServiceTests(TestCase):
    def test_build_prompt_contains_question_and_context(self):
        prompt = build_prompt(
            question="MOM Test nedir?",
            rag_context="Kaynak 1\nİçerik",
        )

        self.assertIn("MOM Test nedir?", prompt)
        self.assertIn("Kaynak 1", prompt)
        self.assertIn("İçerik", prompt)
        self.assertIn("Türkçe cevap ver.", prompt)

    @patch(
        "apps.analyses.rag.rag_answer_service.call_rag_llm"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.format_rag_context"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.retrieve_context"
    )
    def test_answer_with_rag_returns_answer_and_sources(
        self,
        mock_retrieve_context,
        mock_format_rag_context,
        mock_call_rag_llm,
    ):
        chunks = [
            RetrievedChunk(
                content="Test içerik",
                source_title="Test Kaynağı",
                source_type="youtube",
                source_url="https://youtube.com/test",
                chunk_id=1,
                chunk_index=0,
                distance=0.12,
            )
        ]

        mock_retrieve_context.return_value = chunks
        mock_format_rag_context.return_value = (
            "FORMATLANMIŞ CONTEXT"
        )
        mock_call_rag_llm.return_value = "LLM cevabı"

        result = answer_with_rag(
            question="MOM Test nedir?",
            limit=4,
        )

        self.assertIsInstance(result, RagAnswer)
        self.assertEqual(result.answer, "LLM cevabı")

        self.assertEqual(len(result.sources), 1)
        self.assertEqual(
            result.sources[0].title,
            "Test Kaynağı",
        )
        self.assertEqual(
            result.sources[0].content,
            "Test içerik",
        )

    @patch(
        "apps.analyses.rag.rag_answer_service.call_rag_llm"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.format_rag_context"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.retrieve_context"
    )
    def test_answer_with_rag_calls_dependencies(
        self,
        mock_retrieve_context,
        mock_format_rag_context,
        mock_call_rag_llm,
    ):
        mock_retrieve_context.return_value = []
        mock_format_rag_context.return_value = ""
        mock_call_rag_llm.return_value = (
            "Bunu verilen kaynaklarda bulamadım."
        )

        answer_with_rag(
            question="Bilinmeyen soru",
            limit=3,
        )

        mock_retrieve_context.assert_called_once_with(
            query="Bilinmeyen soru",
            limit=3,
        )
        mock_format_rag_context.assert_called_once_with([])
        mock_call_rag_llm.assert_called_once()

    @patch(
        "apps.analyses.rag.rag_answer_service.call_rag_llm"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.format_rag_context"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.retrieve_context"
    )
    def test_prompt_contains_formatted_context(
        self,
        mock_retrieve_context,
        mock_format_rag_context,
        mock_call_rag_llm,
    ):
        mock_retrieve_context.return_value = []
        mock_format_rag_context.return_value = "TEST CONTEXT"
        mock_call_rag_llm.return_value = "cevap"

        answer_with_rag("Test sorusu")

        prompt = mock_call_rag_llm.call_args.args[0]

        self.assertIn("TEST CONTEXT", prompt)
        self.assertIn("Test sorusu", prompt)

    @patch(
        "apps.analyses.rag.rag_answer_service.call_rag_llm"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.format_rag_context"
    )
    @patch(
        "apps.analyses.rag.rag_answer_service.retrieve_context"
    )
    def test_returns_empty_sources_when_no_chunks(
        self,
        mock_retrieve_context,
        mock_format_rag_context,
        mock_call_rag_llm,
    ):
        mock_retrieve_context.return_value = []
        mock_format_rag_context.return_value = ""
        mock_call_rag_llm.return_value = (
            "Bunu verilen kaynaklarda bulamadım."
        )

        result = answer_with_rag("Test")

        self.assertEqual(result.sources, [])
        self.assertEqual(
            result.answer,
            "Bunu verilen kaynaklarda bulamadım.",
        )