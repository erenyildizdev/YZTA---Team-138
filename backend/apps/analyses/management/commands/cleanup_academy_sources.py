import re
from urllib.parse import parse_qs, unquote, urlsplit

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.analyses.models import KnowledgeChunk, KnowledgeSource
from apps.ideas.models import Idea


ACADEMY_VIDEO_IDS = frozenset(
    {
        "2ahypzxFlgM",
        "2e1pxGdCm2o",
        "3rP4_N_uFLc",
        "4eK1bYTIpIY",
        "6Gier_OlL5E",
        "6n8US6az1wY",
        "BB0-nnYHUZU",
        "CCoNK4A4cRQ",
        "EDxPb77TnQY",
        "InsamP2VUv8",
        "JKwUfaKkWjk",
        "Kd83g_DiRn4",
        "LsmtIR_xq98",
        "RR9D_JdyRu0",
        "S8nX6UuDD5Y",
        "WWF_zvMYP3g",
        "WYK0PZOIfSY",
        "Yo1Ze7Qqa5Y",
        "_J_CPazaC6Y",
        "_fjRpQ6aNuY",
        "cSk9Oyu0BuY",
        "fLc6xbVjjOs",
        "krqBaECxjBA",
        "n9NSqcYMz6s",
        "oLGdLUtAElw",
        "rXJWoy7Rsew",
        "sqVQXFHviGs",
        "stBOMP50pws",
        "sxPi5_lVWkw",
        "tRYwmEvBbZQ",
        "x88__9rkMIU",
        "xGB4JXRLTEc",
        "xi0W5uN3-R4",
        "y3YUJ6hOTDQ",
    }
)

_VIDEO_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{11}$")
_YOUTUBE_BASE_HOSTS = ("youtube.com", "youtube-nocookie.com")
_SHORT_YOUTUBE_HOSTS = {"youtu.be", "www.youtu.be"}


def _is_youtube_host(hostname: str) -> bool:
    return any(
        hostname == base_host
        or hostname.endswith(f".{base_host}")
        for base_host in _YOUTUBE_BASE_HOSTS
    )


def extract_youtube_video_id(source_url: object) -> str | None:
    if not isinstance(source_url, str) or not source_url.strip():
        return None

    try:
        parsed = urlsplit(source_url.strip())
    except ValueError:
        return None

    hostname = (parsed.hostname or "").casefold().rstrip(".")
    path_parts = [
        unquote(part)
        for part in parsed.path.split("/")
        if part
    ]
    video_id = None

    if hostname in _SHORT_YOUTUBE_HOSTS and path_parts:
        video_id = path_parts[0]
    elif _is_youtube_host(hostname):
        if parsed.path.rstrip("/").casefold() == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
        elif len(path_parts) >= 2 and path_parts[0].casefold() in {
            "embed",
            "live",
            "shorts",
            "v",
        }:
            video_id = path_parts[1]

    if not isinstance(video_id, str):
        return None

    video_id = video_id.strip()
    if not _VIDEO_ID_PATTERN.fullmatch(video_id):
        return None

    return video_id


def is_academy_source_url(source_url: object) -> bool:
    return extract_youtube_video_id(source_url) in ACADEMY_VIDEO_IDS


def filter_academy_references(
    rag_sources: object,
    *,
    target_chunk_ids: set[str],
) -> tuple[object, int]:
    def is_target_reference(source: object) -> bool:
        if not isinstance(source, dict):
            return False

        chunk_id = source.get("chunk_id")
        is_target_chunk = (
            chunk_id is not None
            and str(chunk_id) in target_chunk_ids
        )
        return is_target_chunk or is_academy_source_url(
            source.get("source_url")
        )

    if isinstance(rag_sources, dict):
        if is_target_reference(rag_sources):
            return [], 1
        return rag_sources, 0

    if not isinstance(rag_sources, list):
        return rag_sources, 0

    retained_sources = []
    removed_count = 0

    for source in rag_sources:
        if is_target_reference(source):
            removed_count += 1
        else:
            retained_sources.append(source)

    return retained_sources, removed_count


class Command(BaseCommand):
    help = (
        "Remove only the retired Academy YouTube sources, their chunks and "
        "embeddings, and matching Idea.rag_sources references."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report matching records without changing the database.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        source_queryset = (
            KnowledgeSource.objects
            .exclude(source_url__isnull=True)
            .exclude(source_url="")
            .only("id", "source_url")
        )

        def matching_source_ids(source_rows):
            return {
                source.id
                for source in source_rows
                if is_academy_source_url(source.source_url)
            }

        def chunk_ids_for(source_ids):
            return set(
                KnowledgeChunk.objects.filter(
                    source_id__in=source_ids
                ).values_list("id", flat=True)
            )

        def collect_idea_updates(ideas, chunk_ids):
            updates: list[tuple[Idea, object]] = []
            reference_count = 0
            chunk_id_strings = {
                str(chunk_id) for chunk_id in chunk_ids
            }

            for idea in ideas:
                filtered_sources, removed_count = (
                    filter_academy_references(
                        idea.rag_sources,
                        target_chunk_ids=chunk_id_strings,
                    )
                )
                if removed_count:
                    updates.append((idea, filtered_sources))
                    reference_count += removed_count

            return updates, reference_count

        if dry_run:
            target_source_ids = matching_source_ids(source_queryset)
            target_chunk_ids = chunk_ids_for(target_source_ids)
            idea_updates, removed_reference_count = (
                collect_idea_updates(
                    Idea.objects.only("id", "rag_sources"),
                    target_chunk_ids,
                )
            )
        else:
            with transaction.atomic():
                candidate_source_ids = matching_source_ids(
                    source_queryset
                )
                locked_source_rows = (
                    source_queryset.select_for_update().filter(
                        id__in=candidate_source_ids
                    )
                )
                target_source_ids = matching_source_ids(
                    locked_source_rows
                )
                target_chunk_ids = chunk_ids_for(target_source_ids)

                candidate_idea_updates, _ = collect_idea_updates(
                    Idea.objects.only("id", "rag_sources"),
                    target_chunk_ids,
                )
                candidate_idea_ids = [
                    idea.id for idea, _ in candidate_idea_updates
                ]
                idea_updates, removed_reference_count = (
                    collect_idea_updates(
                        Idea.objects.select_for_update()
                        .filter(id__in=candidate_idea_ids)
                        .only("id", "rag_sources"),
                        target_chunk_ids,
                    )
                )

                for idea, filtered_sources in idea_updates:
                    idea.rag_sources = filtered_sources
                    idea.save(update_fields=["rag_sources"])

                if target_source_ids:
                    KnowledgeSource.objects.filter(
                        id__in=target_source_ids
                    ).delete()

        summary = (
            f"sources={len(target_source_ids)}, "
            f"chunks={len(target_chunk_ids)}, "
            f"idea_references={removed_reference_count}, "
            f"ideas_updated={len(idea_updates)}"
        )
        if dry_run:
            self.stdout.write(f"Dry run; no changes made: {summary}")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Academy cleanup completed: {summary}")
            )
