import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class YouTubeVideoMetadata:
    video_id: str
    title: str
    channel: str
    webpage_url: str
    duration_seconds: float | None


def parse_youtube_info(
    file_path: str | Path,
) -> YouTubeVideoMetadata:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Video metadata dosyası bulunamadı: {path}"
        )

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    video_id = data.get("id")
    title = data.get("title")
    channel = (
        data.get("channel")
        or data.get("uploader")
        or "Bilinmeyen kanal"
    )
    webpage_url = (
        data.get("webpage_url")
        or data.get("original_url")
    )
    duration = data.get("duration")

    if not video_id:
        raise ValueError("Metadata içinde video id bulunamadı.")

    if not title:
        raise ValueError("Metadata içinde video başlığı bulunamadı.")

    if not webpage_url:
        webpage_url = (
            f"https://www.youtube.com/watch?v={video_id}"
        )

    if not isinstance(duration, (int, float)):
        duration = None

    return YouTubeVideoMetadata(
        video_id=str(video_id),
        title=str(title),
        channel=str(channel),
        webpage_url=str(webpage_url),
        duration_seconds=float(duration) if duration is not None else None,
    )