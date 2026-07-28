from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from django.test import TestCase

from apps.analyses.rag.ingestion.youtube_ingestion import (
    YouTubeIngestionResult,
    build_chunk_content,
    format_timestamp,
    ingest_youtube_video,
)


class YouTubeIngestionTests(TestCase):
    def setUp(self):
        self.metadata = SimpleNamespace(
            video_id="video-123",
            title="MOM Test Eğitimi",
            webpage_url="https://youtube.com/watch?v=video-123",
        )

        self.segments = [
            SimpleNamespace(
                text="İlk segment",
                start_seconds=0,
                end_seconds=10,
            )
        ]

        self.transcript_chunks = [
            SimpleNamespace(
                text="İlk chunk metni",
                start_seconds=5,
                end_seconds=65,
            ),
            SimpleNamespace(
                text="İkinci chunk metni",
                start_seconds=65,
                end_seconds=125,
            ),
        ]

    def test_format_timestamp_formats_seconds(self):
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(65), "01:05")
        self.assertEqual(format_timestamp(3661), "01:01:01")

    def test_format_timestamp_converts_negative_value_to_zero(self):
        result = format_timestamp(-10)

        self.assertEqual(result, "00:00")

    def test_build_chunk_content_includes_timestamps_and_text(self):
        result = build_chunk_content(
            text="Müşteriyle geçmiş davranışlar konuşulmalıdır.",
            start_seconds=65,
            end_seconds=125,
        )

        self.assertEqual(
            result,
            "[01:05 - 02:05]\n"
            "Müşteriyle geçmiş davranışlar konuşulmalıdır.",
        )

    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_youtube_info"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeSource"
    )
    def test_ingestion_skips_existing_source_with_chunks(
        self,
        mock_knowledge_source,
        mock_parse_youtube_info,
    ):
        mock_parse_youtube_info.return_value = self.metadata

        source = MagicMock()
        source.id = 10
        source.title = "Mevcut video"
        source.chunks.exists.return_value = True
        source.chunks.count.return_value = 8

        (
            mock_knowledge_source.objects
            .filter.return_value
            .first.return_value
        ) = source

        result = ingest_youtube_video(
            transcript_path="video.json3",
            info_path="video.info.json",
            skip_existing=True,
        )

        self.assertEqual(
            result,
            YouTubeIngestionResult(
                source_id=10,
                video_id="video-123",
                title="Mevcut video",
                chunk_count=8,
                created=False,
                skipped=True,
            ),
        )

        source.chunks.exists.assert_called_once_with()
        source.chunks.count.assert_called_once_with()

    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_json3_transcript"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_youtube_info"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeSource"
    )
    def test_ingestion_raises_error_when_transcript_has_no_segments(
        self,
        mock_knowledge_source,
        mock_parse_youtube_info,
        mock_parse_json3_transcript,
    ):
        mock_parse_youtube_info.return_value = self.metadata
        mock_parse_json3_transcript.return_value = []

        (
            mock_knowledge_source.objects
            .filter.return_value
            .first.return_value
        ) = None

        with self.assertRaisesMessage(
            ValueError,
            "Altyazıdan kullanılabilir segment çıkarılamadı",
        ):
            ingest_youtube_video(
                transcript_path="empty.json3",
                info_path="video.info.json",
            )

    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".build_transcript_chunks"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".parse_json3_transcript"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_youtube_info"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeSource"
    )
    def test_ingestion_raises_error_when_chunks_cannot_be_created(
        self,
        mock_knowledge_source,
        mock_parse_youtube_info,
        mock_parse_json3_transcript,
        mock_build_transcript_chunks,
    ):
        mock_parse_youtube_info.return_value = self.metadata
        mock_parse_json3_transcript.return_value = self.segments
        mock_build_transcript_chunks.return_value = []

        (
            mock_knowledge_source.objects
            .filter.return_value
            .first.return_value
        ) = None

        with self.assertRaisesMessage(
            ValueError,
            "Altyazı segmentlerinden chunk oluşturulamadı.",
        ):
            ingest_youtube_video(
                transcript_path="video.json3",
                info_path="video.info.json",
            )

    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.embed_document"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".build_transcript_chunks"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".parse_json3_transcript"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_youtube_info"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeChunk"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeSource"
    )
    def test_ingestion_creates_new_source_and_chunks(
        self,
        mock_knowledge_source,
        mock_knowledge_chunk,
        mock_parse_youtube_info,
        mock_parse_json3_transcript,
        mock_build_transcript_chunks,
        mock_embed_document,
    ):
        mock_parse_youtube_info.return_value = self.metadata
        mock_parse_json3_transcript.return_value = self.segments
        mock_build_transcript_chunks.return_value = (
            self.transcript_chunks
        )

        (
            mock_knowledge_source.objects
            .filter.return_value
            .first.return_value
        ) = None

        source = MagicMock()
        source.id = 25
        mock_knowledge_source.objects.create.return_value = source

        mock_embed_document.side_effect = [
            [0.1, 0.2],
            [0.3, 0.4],
        ]

        created_chunk_1 = MagicMock()
        created_chunk_2 = MagicMock()

        mock_knowledge_chunk.side_effect = [
            created_chunk_1,
            created_chunk_2,
        ]

        result = ingest_youtube_video(
            transcript_path="video.json3",
            info_path="video.info.json",
            max_characters=500,
            overlap_segments=1,
        )

        mock_parse_youtube_info.assert_called_once_with(
            "video.info.json"
        )
        mock_parse_json3_transcript.assert_called_once_with(
            "video.json3"
        )

        mock_build_transcript_chunks.assert_called_once_with(
            segments=self.segments,
            max_characters=500,
            overlap_segments=1,
        )

        mock_knowledge_source.objects.create.assert_called_once_with(
            title="MOM Test Eğitimi",
            source_type="youtube",
            source_url=(
                "https://youtube.com/watch?v=video-123"
            ),
        )

        self.assertEqual(
            mock_embed_document.call_args_list,
            [
                call("[00:05 - 01:05]\nİlk chunk metni"),
                call("[01:05 - 02:05]\nİkinci chunk metni"),
            ],
        )

        self.assertEqual(
            mock_knowledge_chunk.call_args_list,
            [
                call(
                    source=source,
                    content="[00:05 - 01:05]\nİlk chunk metni",
                    chunk_index=0,
                    embedding=[0.1, 0.2],
                ),
                call(
                    source=source,
                    content="[01:05 - 02:05]\nİkinci chunk metni",
                    chunk_index=1,
                    embedding=[0.3, 0.4],
                ),
            ],
        )

        (
            mock_knowledge_chunk.objects
            .bulk_create.assert_called_once_with(
                [created_chunk_1, created_chunk_2]
            )
        )

        self.assertEqual(
            result,
            YouTubeIngestionResult(
                source_id=25,
                video_id="video-123",
                title="MOM Test Eğitimi",
                chunk_count=2,
                created=True,
                skipped=False,
            ),
        )

    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.embed_document"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".build_transcript_chunks"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion"
        ".parse_json3_transcript"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.parse_youtube_info"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeChunk"
    )
    @patch(
        "apps.analyses.rag.ingestion.youtube_ingestion.KnowledgeSource"
    )
    def test_ingestion_replaces_chunks_for_existing_source(
        self,
        mock_knowledge_source,
        mock_knowledge_chunk,
        mock_parse_youtube_info,
        mock_parse_json3_transcript,
        mock_build_transcript_chunks,
        mock_embed_document,
    ):
        mock_parse_youtube_info.return_value = self.metadata
        mock_parse_json3_transcript.return_value = self.segments
        mock_build_transcript_chunks.return_value = [
            self.transcript_chunks[0]
        ]
        mock_embed_document.return_value = [0.1, 0.2]

        source = MagicMock()
        source.id = 30
        source.title = "Eski başlık"
        source.source_type = "text"

        (
            mock_knowledge_source.objects
            .filter.return_value
            .first.return_value
        ) = source

        created_chunk = MagicMock()
        mock_knowledge_chunk.return_value = created_chunk

        result = ingest_youtube_video(
            transcript_path="video.json3",
            info_path="video.info.json",
            skip_existing=False,
        )

        self.assertEqual(source.title, "MOM Test Eğitimi")
        self.assertEqual(source.source_type, "youtube")

        source.save.assert_called_once_with(
            update_fields=[
                "title",
                "source_type",
            ]
        )
        source.chunks.all.return_value.delete.assert_called_once_with()

        (
            mock_knowledge_chunk.objects
            .bulk_create.assert_called_once_with(
                [created_chunk]
            )
        )

        self.assertEqual(result.source_id, 30)
        self.assertEqual(result.chunk_count, 1)
        self.assertFalse(result.created)
        self.assertFalse(result.skipped)