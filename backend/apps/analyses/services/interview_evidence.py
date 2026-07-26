from django.db import transaction

from apps.analyses.models import (
    InterviewEvidenceAnalysis,
    InterviewNote,
)

from .llm_client import call_interview_analysis_llm
from .prompts import build_interview_evidence_analysis_prompt


class InterviewNotesNotFoundError(Exception):
    """Raised when an idea has no interview notes to analyze."""


def _build_idea_text(idea) -> str:
    return f"""
Başlık: {idea.title}
Açıklama: {idea.description}
Hedef kitle: {idea.target_audience}
Problem: {idea.problem}
Çözüm: {idea.solution}
Sektör: {idea.sector}
""".strip()


def _build_interview_notes_text(
    interview_notes,
) -> str:
    note_sections = []

    for index, note in enumerate(interview_notes, start=1):
        interviewee_name = (
            note.interviewee_name.strip()
            if note.interviewee_name
            else "Belirtilmedi"
        )
        interviewee_profile = (
            note.interviewee_profile.strip()
            if note.interviewee_profile
            else "Belirtilmedi"
        )

        note_sections.append(
            f"""
Görüşme {index}
Görüşülen kişi: {interviewee_name}
Profil: {interviewee_profile}
Notlar:
{note.notes.strip()}
""".strip()
        )

    return "\n\n---\n\n".join(note_sections)


@transaction.atomic
def analyze_interview_evidence(idea) -> InterviewEvidenceAnalysis:
    interview_notes = list(
        InterviewNote.objects.filter(
            idea=idea,
        ).order_by("created_at")
    )

    if not interview_notes:
        raise InterviewNotesNotFoundError(
            "Bu fikre ait analiz edilecek görüşme notu bulunamadı."
        )

    idea_text = _build_idea_text(idea)
    interview_notes_text = _build_interview_notes_text(
        interview_notes,
    )

    prompt = build_interview_evidence_analysis_prompt(
        idea_text=idea_text,
        interview_notes_text=interview_notes_text,
    )

    result = call_interview_analysis_llm(
        prompt=prompt,
    )

    analysis = InterviewEvidenceAnalysis.objects.create(
        idea=idea,
        result=result,
        provider="gemini",
    )

    analysis.interview_notes.set(interview_notes)

    return analysis