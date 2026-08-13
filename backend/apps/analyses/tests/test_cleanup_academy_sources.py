from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from apps.analyses.management.commands.cleanup_academy_sources import (
    extract_youtube_video_id,
    is_academy_source_url,
)
from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.ideas.models import Idea


class AcademySourceCleanupTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="cleanup-owner",
            email="cleanup-owner@example.com",
            password="StrongPass123!",
        )
        self.academy_source = KnowledgeSource.objects.create(
            title="Fikir Doğrulama 1",
            source_type="youtube",
            source_url=(
                "https://www.youtube.com/watch?v=xi0W5uN3-R4&t=1s"
            ),
        )
        self.academy_chunk = KnowledgeChunk.objects.create(
            source=self.academy_source,
            content="Kaldırılacak Akademi içeriği",
            chunk_index=0,
            embedding=[0.1] * 768,
        )
        self.unrelated_source = KnowledgeSource.objects.create(
            title="Fikir Doğrulama 1",
            source_type="youtube",
            source_url="https://www.youtube.com/watch?v=Z9Y8X7W6V5U",
        )
        self.unrelated_chunk = KnowledgeChunk.objects.create(
            source=self.unrelated_source,
            content="Korunacak bağımsız içerik",
            chunk_index=0,
            embedding=[0.2] * 768,
        )
        self.unrelated_reference = {
            "title": self.unrelated_source.title,
            "source_type": "youtube",
            "source_url": self.unrelated_source.source_url,
            "chunk_id": self.unrelated_chunk.id,
            "chunk_index": 0,
            "distance": 0.1,
        }
        self.chunk_only_reference = {
            "title": "Chunk kimliğiyle eşleşen eski referans",
            "source_type": "documentation",
            "source_url": "https://example.com/stale-reference",
            "chunk_id": self.academy_chunk.id,
            "chunk_index": 0,
            "distance": 0.3,
        }
        self.idea = Idea.objects.create(
            user=self.user,
            title="Cleanup Test Idea",
            description="Cleanup kapsamını doğrulayan iş fikri.",
            target_audience="Girişimciler",
            problem="Yanlış kaynakların silinme riski",
            solution="Exact allowlist kullanmak",
            sector="SaaS",
            rag_sources=[
                {
                    "title": self.academy_source.title,
                    "source_type": "youtube",
                    "source_url": self.academy_source.source_url,
                    "chunk_id": self.academy_chunk.id,
                    "chunk_index": 0,
                    "distance": 0.1,
                },
                {
                    "title": "Eski Akademi referansı",
                    "source_type": "youtube",
                    "source_url": "https://youtu.be/6n8US6az1wY",
                    "chunk_id": 999999,
                    "chunk_index": 0,
                    "distance": 0.2,
                },
                self.chunk_only_reference,
                self.unrelated_reference,
            ],
        )
        self.original_rag_sources = list(self.idea.rag_sources)

    def run_cleanup(self, *args):
        stdout = StringIO()
        call_command("cleanup_academy_sources", *args, stdout=stdout)
        return stdout.getvalue()

    def test_cleanup_removes_only_allowlisted_sources_and_references(self):
        output = self.run_cleanup()

        self.assertFalse(
            KnowledgeSource.objects.filter(pk=self.academy_source.pk).exists()
        )
        self.assertFalse(
            KnowledgeChunk.objects.filter(pk=self.academy_chunk.pk).exists()
        )
        self.assertTrue(
            KnowledgeSource.objects.filter(pk=self.unrelated_source.pk).exists()
        )
        self.assertTrue(
            KnowledgeChunk.objects.filter(pk=self.unrelated_chunk.pk).exists()
        )
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.rag_sources, [self.unrelated_reference])
        self.assertIn("sources=1", output)
        self.assertIn("chunks=1", output)
        self.assertIn("idea_references=3", output)
        self.assertIn("ideas_updated=1", output)

    def test_cleanup_is_idempotent(self):
        self.run_cleanup()

        second_output = self.run_cleanup()

        self.assertIn("sources=0", second_output)
        self.assertIn("chunks=0", second_output)
        self.assertIn("idea_references=0", second_output)
        self.assertIn("ideas_updated=0", second_output)
        self.assertTrue(
            KnowledgeSource.objects.filter(pk=self.unrelated_source.pk).exists()
        )
        self.assertTrue(
            KnowledgeChunk.objects.filter(pk=self.unrelated_chunk.pk).exists()
        )
        self.idea.refresh_from_db()
        self.assertEqual(self.idea.rag_sources, [self.unrelated_reference])

    def test_dry_run_reports_matches_without_changing_database(self):
        with CaptureQueriesContext(connection) as captured_queries:
            output = self.run_cleanup("--dry-run")

        self.assertIn("Dry run; no changes made", output)
        self.assertNotIn(
            "FOR UPDATE",
            "\n".join(
                query["sql"].upper()
                for query in captured_queries.captured_queries
            ),
        )
        self.assertTrue(
            KnowledgeSource.objects.filter(pk=self.academy_source.pk).exists()
        )
        self.assertTrue(
            KnowledgeChunk.objects.filter(pk=self.academy_chunk.pk).exists()
        )
        self.idea.refresh_from_db()
        self.assertEqual(
            self.idea.rag_sources,
            self.original_rag_sources,
        )

    def test_cleanup_handles_single_dict_reference_shape(self):
        dict_shaped_idea = Idea.objects.create(
            user=self.user,
            title="Legacy JSON Shape",
            description="Eski JSON biçimini doğrulayan fikir.",
            target_audience="Girişimciler",
            problem="Kaynak alanı liste değil",
            solution="Güvenli cleanup",
            sector="SaaS",
            rag_sources={
                "title": "Eski Akademi referansı",
                "source_type": "youtube",
                "source_url": "https://youtu.be/6n8US6az1wY",
                "chunk_id": 999999,
            },
        )

        self.run_cleanup()

        dict_shaped_idea.refresh_from_db()
        self.assertEqual(dict_shaped_idea.rag_sources, [])

    def test_cleanup_rolls_back_reference_updates_when_delete_fails(self):
        with (
            patch(
                "django.db.models.query.QuerySet.delete",
                side_effect=RuntimeError("forced delete failure"),
            ),
            self.assertRaisesMessage(
                RuntimeError,
                "forced delete failure",
            ),
        ):
            self.run_cleanup()

        self.assertTrue(
            KnowledgeSource.objects.filter(pk=self.academy_source.pk).exists()
        )
        self.assertTrue(
            KnowledgeChunk.objects.filter(pk=self.academy_chunk.pk).exists()
        )
        self.idea.refresh_from_db()
        self.assertEqual(
            self.idea.rag_sources,
            self.original_rag_sources,
        )


class AcademySourceUrlIdentificationTests(TestCase):
    def test_supported_youtube_urls_extract_exact_video_id(self):
        self.assertEqual(
            extract_youtube_video_id(
                "https://www.youtube.com/watch?v=xi0W5uN3-R4&t=10"
            ),
            "xi0W5uN3-R4",
        )
        self.assertEqual(
            extract_youtube_video_id("https://youtu.be/6n8US6az1wY"),
            "6n8US6az1wY",
        )
        self.assertEqual(
            extract_youtube_video_id(
                "https://tr.youtube.com./v/xi0W5uN3-R4"
            ),
            "xi0W5uN3-R4",
        )
        self.assertEqual(
            extract_youtube_video_id(
                "https://www.youtube-nocookie.com/embed/"
                "xi0W5uN3%2DR4"
            ),
            "xi0W5uN3-R4",
        )

    def test_lookalike_host_and_unrelated_video_are_not_targets(self):
        self.assertFalse(
            is_academy_source_url(
                "https://www.youtube.com.evil.example/"
                "watch?v=xi0W5uN3-R4"
            )
        )
        self.assertFalse(
            is_academy_source_url(
                "https://www.youtube.com/watch?v=Z9Y8X7W6V5U"
            )
        )
        self.assertIsNone(extract_youtube_video_id("not a URL"))
        self.assertIsNone(extract_youtube_video_id(None))
