from dataclasses import dataclass
from pathlib import Path

from django.db import transaction

from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.analyses.rag.embedding_service import embed_document
from apps.analyses.rag.ingestion.transcript_parser import (
    TranscriptSegment,
    build_transcript_chunks,
    parse_json3_transcript,
)
from apps.analyses.rag.ingestion.youtube_metadata import parse_youtube_info


@dataclass(frozen=True)
class YouTubeIngestionResult:
    source_id: int
    video_id: str
    title: str
    chunk_count: int
    created: bool
    skipped: bool = False


def format_timestamp(seconds: float) -> str:
    """Saniyeyi HH:MM:SS veya MM:SS formatına dönüştürür."""
    total_seconds = max(0, int(seconds))

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def build_chunk_content(
    text: str,
    start_seconds: float,
    end_seconds: float,
) -> str:
    start = format_timestamp(start_seconds)
    end = format_timestamp(end_seconds)

    return f"[{start} - {end}]\n{text}"


@transaction.atomic
def ingest_youtube_video(
    transcript_path: str | Path,
    info_path: str | Path,
    max_characters: int = 750,
    overlap_segments: int = 2,
    skip_existing: bool = True,
) -> YouTubeIngestionResult:
    """
    Bir YouTube videosunun altyazısını parse eder, chunk'lara ayırır,
    embedding üretir ve KnowledgeSource/KnowledgeChunk tablolarına kaydeder.

    skip_existing=True olduğunda daha önce chunk'ları oluşturulmuş videolar
    tekrar işlenmez.

    skip_existing=False olduğunda mevcut chunk'lar silinir ve yeniden üretilir.
    """
    metadata = parse_youtube_info(info_path)

    source = KnowledgeSource.objects.filter(
        source_url=metadata.webpage_url
    ).first()

    if (
        skip_existing
        and source is not None
        and source.chunks.exists()
    ):
        return YouTubeIngestionResult(
            source_id=source.id,
            video_id=metadata.video_id,
            title=source.title,
            chunk_count=source.chunks.count(),
            created=False,
            skipped=True,
        )

    segments = parse_json3_transcript(transcript_path)

    if not segments:
        raise ValueError(
            f"Altyazıdan kullanılabilir segment çıkarılamadı: "
            f"{transcript_path}"
        )

    transcript_chunks = build_transcript_chunks(
        segments=segments,
        max_characters=max_characters,
        overlap_segments=overlap_segments,
    )

    if not transcript_chunks:
        raise ValueError(
            "Altyazı segmentlerinden chunk oluşturulamadı."
        )

    created = source is None

    if source is None:
        source = KnowledgeSource.objects.create(
            title=metadata.title,
            source_type="youtube",
            source_url=metadata.webpage_url,
        )
    else:
        source.title = metadata.title
        source.source_type = "youtube"
        source.save(
            update_fields=[
                "title",
                "source_type",
            ]
        )

        source.chunks.all().delete()

    knowledge_chunks: list[KnowledgeChunk] = []

    for chunk_index, transcript_chunk in enumerate(
        transcript_chunks
    ):
        content = build_chunk_content(
            text=transcript_chunk.text,
            start_seconds=transcript_chunk.start_seconds,
            end_seconds=transcript_chunk.end_seconds,
        )

        embedding = embed_document(content)

        knowledge_chunks.append(
            KnowledgeChunk(
                source=source,
                content=content,
                chunk_index=chunk_index,
                embedding=embedding,
            )
        )

    KnowledgeChunk.objects.bulk_create(knowledge_chunks)

    return YouTubeIngestionResult(
        source_id=source.id,
        video_id=metadata.video_id,
        title=metadata.title,
        chunk_count=len(knowledge_chunks),
        created=created,
        skipped=False,
    )