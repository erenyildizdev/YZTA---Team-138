import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from apps.analyses.rag.ingestion.transcript_parser import (
    TranscriptSegment,
    build_transcript_chunks,
    clean_text,
    parse_json3_transcript,
)


class TranscriptParserTests(SimpleTestCase):
    def _create_json3_file(
        self,
        directory: str,
        data: dict,
    ) -> Path:
        file_path = Path(directory) / "transcript.json3"

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
            )

        return file_path

    def test_clean_text_removes_newlines_and_extra_spaces(self):
        result = clean_text(
            "  Müşteriyle\n   geçmiş davranışları konuş.  "
        )

        self.assertEqual(
            result,
            "Müşteriyle geçmiş davranışları konuş.",
        )

    def test_clean_text_returns_empty_string_for_whitespace(self):
        result = clean_text(" \n   \t ")

        self.assertEqual(result, "")

    def test_parse_json3_transcript_parses_valid_events(self):
        data = {
            "events": [
                {
                    "tStartMs": 1000,
                    "dDurationMs": 2500,
                    "segs": [
                        {"utf8": "Müşteriye "},
                        {"utf8": "gelecek planlarını sorma."},
                    ],
                },
                {
                    "tStartMs": 4000,
                    "dDurationMs": 1500,
                    "segs": [
                        {"utf8": "Geçmiş davranışları sor."},
                    ],
                },
            ]
        }

        with TemporaryDirectory() as directory:
            file_path = self._create_json3_file(
                directory,
                data,
            )

            result = parse_json3_transcript(file_path)

        self.assertEqual(
            result,
            [
                TranscriptSegment(
                    start_seconds=1.0,
                    end_seconds=3.5,
                    text="Müşteriye gelecek planlarını sorma.",
                ),
                TranscriptSegment(
                    start_seconds=4.0,
                    end_seconds=5.5,
                    text="Geçmiş davranışları sor.",
                ),
            ],
        )

    def test_parse_json3_transcript_skips_events_without_segments(
        self,
    ):
        data = {
            "events": [
                {
                    "tStartMs": 0,
                    "dDurationMs": 1000,
                },
                {
                    "tStartMs": 1000,
                    "dDurationMs": 1000,
                    "segs": [],
                },
                {
                    "tStartMs": 2000,
                    "dDurationMs": 1000,
                    "segs": [
                        {"utf8": "Geçerli içerik"},
                    ],
                },
            ]
        }

        with TemporaryDirectory() as directory:
            file_path = self._create_json3_file(
                directory,
                data,
            )

            result = parse_json3_transcript(file_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "Geçerli içerik")

    def test_parse_json3_transcript_skips_empty_text(self):
        data = {
            "events": [
                {
                    "tStartMs": 0,
                    "dDurationMs": 1000,
                    "segs": [
                        {"utf8": "   "},
                        {"utf8": "\n"},
                    ],
                }
            ]
        }

        with TemporaryDirectory() as directory:
            file_path = self._create_json3_file(
                directory,
                data,
            )

            result = parse_json3_transcript(file_path)

        self.assertEqual(result, [])

    def test_parse_json3_transcript_returns_empty_list_without_events(
        self,
    ):
        with TemporaryDirectory() as directory:
            file_path = self._create_json3_file(
                directory,
                {},
            )

            result = parse_json3_transcript(file_path)

        self.assertEqual(result, [])

    def test_parse_json3_transcript_uses_zero_for_missing_timestamps(
        self,
    ):
        data = {
            "events": [
                {
                    "segs": [
                        {"utf8": "Zaman bilgisi olmayan içerik"},
                    ]
                }
            ]
        }

        with TemporaryDirectory() as directory:
            file_path = self._create_json3_file(
                directory,
                data,
            )

            result = parse_json3_transcript(file_path)

        self.assertEqual(result[0].start_seconds, 0.0)
        self.assertEqual(result[0].end_seconds, 0.0)

    def test_build_transcript_chunks_returns_empty_list_for_no_segments(
        self,
    ):
        result = build_transcript_chunks([])

        self.assertEqual(result, [])

    def test_build_transcript_chunks_combines_segments_within_limit(
        self,
    ):
        segments = [
            TranscriptSegment(
                start_seconds=0,
                end_seconds=5,
                text="Müşteri görüşmesi",
            ),
            TranscriptSegment(
                start_seconds=5,
                end_seconds=10,
                text="geçmiş davranışlara odaklanmalıdır.",
            ),
        ]

        result = build_transcript_chunks(
            segments=segments,
            max_characters=100,
            overlap_segments=0,
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0],
            TranscriptSegment(
                start_seconds=0,
                end_seconds=10,
                text=(
                    "Müşteri görüşmesi "
                    "geçmiş davranışlara odaklanmalıdır."
                ),
            ),
        )

    def test_build_transcript_chunks_splits_segments_over_limit(
        self,
    ):
        segments = [
            TranscriptSegment(
                start_seconds=0,
                end_seconds=5,
                text="Birinci",
            ),
            TranscriptSegment(
                start_seconds=5,
                end_seconds=10,
                text="İkinci",
            ),
            TranscriptSegment(
                start_seconds=10,
                end_seconds=15,
                text="Üçüncü",
            ),
        ]

        result = build_transcript_chunks(
            segments=segments,
            max_characters=14,
            overlap_segments=0,
        )

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0],
            TranscriptSegment(
                start_seconds=0,
                end_seconds=10,
                text="Birinci İkinci",
            ),
        )

        self.assertEqual(
            result[1],
            TranscriptSegment(
                start_seconds=10,
                end_seconds=15,
                text="Üçüncü",
            ),
        )

    def test_build_transcript_chunks_applies_segment_overlap(
        self,
    ):
        segments = [
            TranscriptSegment(
                start_seconds=0,
                end_seconds=5,
                text="aaaa",
            ),
            TranscriptSegment(
                start_seconds=5,
                end_seconds=10,
                text="bbbb",
            ),
            TranscriptSegment(
                start_seconds=10,
                end_seconds=15,
                text="cccc",
            ),
        ]

        result = build_transcript_chunks(
            segments=segments,
            max_characters=9,
            overlap_segments=1,
        )

        self.assertEqual(len(result), 2)

        self.assertEqual(
            result[0],
            TranscriptSegment(
                start_seconds=0,
                end_seconds=10,
                text="aaaa bbbb",
            ),
        )

        self.assertEqual(
            result[1],
            TranscriptSegment(
                start_seconds=5,
                end_seconds=15,
                text="bbbb cccc",
            ),
        )

    def test_build_transcript_chunks_preserves_single_large_segment(
        self,
    ):
        segment = TranscriptSegment(
            start_seconds=0,
            end_seconds=20,
            text="Bu metin belirlenen karakter sınırından uzundur.",
        )

        result = build_transcript_chunks(
            segments=[segment],
            max_characters=10,
            overlap_segments=0,
        )

        self.assertEqual(result, [segment])

    def test_build_transcript_chunks_raises_error_for_zero_max_characters(
        self,
    ):
        with self.assertRaisesMessage(
            ValueError,
            "max_characters sıfırdan büyük olmalıdır.",
        ):
            build_transcript_chunks(
                segments=[],
                max_characters=0,
            )

    def test_build_transcript_chunks_raises_error_for_negative_max_characters(
        self,
    ):
        with self.assertRaisesMessage(
            ValueError,
            "max_characters sıfırdan büyük olmalıdır.",
        ):
            build_transcript_chunks(
                segments=[],
                max_characters=-1,
            )

    def test_build_transcript_chunks_raises_error_for_negative_overlap(
        self,
    ):
        with self.assertRaisesMessage(
            ValueError,
            "overlap_segments negatif olamaz.",
        ):
            build_transcript_chunks(
                segments=[],
                overlap_segments=-1,
            )

    def test_build_transcript_chunks_overlap_equal_to_chunk_size_does_not_loop(
        self,
    ):
        segments = [
            TranscriptSegment(
                start_seconds=0,
                end_seconds=5,
                text="aaaa",
            ),
            TranscriptSegment(
                start_seconds=5,
                end_seconds=10,
                text="bbbb",
            ),
            TranscriptSegment(
                start_seconds=10,
                end_seconds=15,
                text="cccc",
            ),
        ]

        result = build_transcript_chunks(
            segments=segments,
            max_characters=9,
            overlap_segments=2,
        )

        self.assertEqual(
            [chunk.text for chunk in result],
            [
                "aaaa bbbb",
                "bbbb cccc",
            ],
        )