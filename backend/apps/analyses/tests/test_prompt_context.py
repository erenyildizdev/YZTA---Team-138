from django.test import SimpleTestCase

from apps.analyses.rag.prompt_context import build_optional_rag_section


class OptionalRagPromptSectionTests(SimpleTestCase):
    def test_none_context_is_omitted(self):
        self.assertEqual(
            build_optional_rag_section(None, guidance="Kural"),
            "",
        )

    def test_whitespace_context_is_omitted(self):
        self.assertEqual(
            build_optional_rag_section("   ", guidance="Kural"),
            "",
        )

    def test_nonempty_context_includes_context_and_guidance(self):
        section = build_optional_rag_section(
            "  Kaynak içeriği  ",
            guidance="Kaynağı doğrudan kopyalama.",
        )

        self.assertIn("--- RAG BAĞLAMI ---", section)
        self.assertIn("Kaynak içeriği", section)
        self.assertIn("Kaynağı doğrudan kopyalama.", section)
