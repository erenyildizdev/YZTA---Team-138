import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TranscriptSegment:
    start_seconds: float
    end_seconds: float
    text: str


def clean_text(text: str) -> str:
    """Altyazı metnini temizler."""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_json3_transcript(file_path: str | Path) -> list[TranscriptSegment]:
    """
    YouTube json3 altyazısını parse eder.
    """

    path = Path(file_path)

    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    segments = []

    for event in data.get("events", []):

        segs = event.get("segs")

        if not segs:
            continue

        text = "".join(
            seg.get("utf8", "")
            for seg in segs
        )

        text = clean_text(text)

        if not text:
            continue

        start_ms = event.get("tStartMs", 0)
        duration_ms = event.get("dDurationMs", 0)

        segments.append(
            TranscriptSegment(
                start_seconds=start_ms / 1000,
                end_seconds=(start_ms + duration_ms) / 1000,
                text=text,
            )
        )

    return segments

def build_transcript_chunks(
    segments: list[TranscriptSegment],
    max_characters: int = 1000,
    overlap_segments: int = 2,
) -> list[TranscriptSegment]:
    """
    Küçük altyazı segmentlerini daha büyük ve anlamlı chunk'lara birleştirir.
    """

    if max_characters <= 0:
        raise ValueError("max_characters sıfırdan büyük olmalıdır.")

    if overlap_segments < 0:
        raise ValueError("overlap_segments negatif olamaz.")

    chunks: list[TranscriptSegment] = []
    current_segments: list[TranscriptSegment] = []
    current_length = 0

    index = 0

    while index < len(segments):
        segment = segments[index]

        additional_length = len(segment.text)

        if current_segments:
            additional_length += 1

        if (
            current_segments
            and current_length + additional_length > max_characters
        ):
            chunk_text = " ".join(
                item.text for item in current_segments
            )

            chunks.append(
                TranscriptSegment(
                    start_seconds=current_segments[0].start_seconds,
                    end_seconds=current_segments[-1].end_seconds,
                    text=chunk_text,
                )
            )

            if overlap_segments > 0:
                overlap_count = min(
                    overlap_segments,
                    max(len(current_segments) - 1, 0),
                )

                if overlap_count:
                    current_segments = current_segments[-overlap_count:]
                    current_length = sum(
                        len(item.text)
                        for item in current_segments
                    ) + max(len(current_segments) - 1, 0)
                else:
                    current_segments = []
                    current_length = 0
            else:
                current_segments = []
                current_length = 0

            continue

        current_segments.append(segment)
        current_length += additional_length
        index += 1

    if current_segments:
        chunk_text = " ".join(
            item.text for item in current_segments
        )

        chunks.append(
            TranscriptSegment(
                start_seconds=current_segments[0].start_seconds,
                end_seconds=current_segments[-1].end_seconds,
                text=chunk_text,
            )
        )

    return chunks