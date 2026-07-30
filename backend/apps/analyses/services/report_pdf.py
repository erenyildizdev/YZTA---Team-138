import json
import re
import threading
import unicodedata
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.text import slugify
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


FONT_DIRECTORY = Path("/usr/share/fonts/truetype/dejavu")
REGULAR_FONT_PATH = FONT_DIRECTORY / "DejaVuSans.ttf"
BOLD_FONT_PATH = FONT_DIRECTORY / "DejaVuSans-Bold.ttf"
REGULAR_FONT_NAME = "FikirLabDejaVuSans"
BOLD_FONT_NAME = "FikirLabDejaVuSansBold"

ROADMAP_SECTION_KEYS = (
    ("İlk görüşmeler", "İlk Görüşmeler"),
    ("Test edilecek varsayımlar", "Test Edilecek Varsayımlar"),
    ("MVP öncelikleri", "MVP Öncelikleri"),
    ("Başarı metrikleri", "Başarı Metrikleri"),
    ("Sonraki karar noktaları", "Sonraki Karar Noktaları"),
)

MISSING_SECTION_MESSAGES = {
    "risky_assumptions": (
        "Bu fikir için henüz riskli varsayım analizi oluşturulmadı."
    ),
    "mom_test": (
        "Bu fikir için henüz müşteri görüşme soruları oluşturulmadı."
    ),
    "moscow": "Bu fikir için henüz MVP kapsamı oluşturulmadı.",
    "roadmap": (
        "Bu fikir için henüz bir doğrulama yol haritası oluşturulmadı."
    ),
    "general_evaluation": (
        "Bu fikir için henüz genel değerlendirme oluşturulmadı."
    ),
    "competitor_analysis": (
        "Bu fikir için henüz rakip/pazar analizi oluşturulmadı."
    ),
    "investor_pitch": (
        "Bu fikir için henüz yatırımcı sunumu oluşturulmadı."
    ),
}

_CONTROL_CHARACTERS = re.compile(
    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"
)
_RESERVED_FILENAMES = {
    "aux",
    "con",
    "nul",
    "prn",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}
_FONT_REGISTRATION_LOCK = threading.Lock()


class ReportPdfConfigurationError(RuntimeError):
    """Raised when the deterministic PDF runtime is not configured."""


def _register_fonts():
    with _FONT_REGISTRATION_LOCK:
        registered_fonts = set(pdfmetrics.getRegisteredFontNames())
        if {
            REGULAR_FONT_NAME,
            BOLD_FONT_NAME,
        }.issubset(registered_fonts):
            return

        missing_paths = [
            path
            for path in (REGULAR_FONT_PATH, BOLD_FONT_PATH)
            if not path.is_file()
        ]
        if missing_paths:
            raise ReportPdfConfigurationError(
                "Required DejaVu Sans PDF fonts are not installed."
            )

        if REGULAR_FONT_NAME not in registered_fonts:
            pdfmetrics.registerFont(
                TTFont(REGULAR_FONT_NAME, str(REGULAR_FONT_PATH))
            )
        if BOLD_FONT_NAME not in registered_fonts:
            pdfmetrics.registerFont(
                TTFont(BOLD_FONT_NAME, str(BOLD_FONT_PATH))
            )
        pdfmetrics.registerFontFamily(
            REGULAR_FONT_NAME,
            normal=REGULAR_FONT_NAME,
            bold=BOLD_FONT_NAME,
            italic=REGULAR_FONT_NAME,
            boldItalic=BOLD_FONT_NAME,
        )


def _plain_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    elif isinstance(value, (int, float, bool)):
        text = str(value)
    else:
        try:
            text = json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
            )
        except (TypeError, ValueError):
            text = str(value)

    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return _CONTROL_CHARACTERS.sub(" ", text).strip()


def _paragraph_text(value, fallback="Bilgi bulunmuyor."):
    text = _plain_text(value) or fallback
    return "<br/>".join(escape(line) for line in text.split("\n"))


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _as_list(value):
    return value if isinstance(value, list) else []


def _nonempty_items(value):
    if isinstance(value, list):
        return [
            item
            for item in value
            if _plain_text(item)
        ]
    return [value] if _plain_text(value) else []


def _related_json(idea, relation_name, field_name, default):
    try:
        related_object = getattr(idea, relation_name)
    except ObjectDoesNotExist:
        return default
    return getattr(related_object, field_name, default)


def collect_report_data(idea):
    """Collect the report's canonical persisted data without generating it."""
    return {
        "idea": {
            "id": idea.pk,
            "title": idea.title,
            "description": idea.description,
            "problem": idea.problem,
            "target_audience": idea.target_audience,
            "solution": idea.solution,
            "sector": idea.sector,
            "created_at": idea.created_at,
            "sources": _as_list(idea.rag_sources),
        },
        "risky_assumptions": _as_dict(
            _related_json(
                idea,
                "risky_assumptions",
                "assumptions_data",
                {},
            )
        ),
        "mom_test": _as_list(
            _related_json(
                idea,
                "mom_test_questions_analysis",
                "questions",
                [],
            )
        ),
        "moscow": _as_dict(
            _related_json(
                idea,
                "moscow_scope_analysis",
                "result",
                {},
            )
        ),
        "roadmap": _as_dict(
            _related_json(
                idea,
                "validation_roadmap",
                "roadmap_data",
                {},
            )
        ),
        "general_evaluation": _as_dict(
            _related_json(
                idea,
                "general_evaluation",
                "evaluation_data",
                {},
            )
        ),
        "competitor_analysis": _as_dict(
            _related_json(
                idea,
                "competitor_analysis",
                "analysis_data",
                {},
            )
        ),
        "investor_pitch": _as_dict(
            _related_json(
                idea,
                "investor_pitch",
                "pitch_data",
                {},
            )
        ),
    }


def build_report_filename(idea):
    idea_id = getattr(idea, "pk", None) or "rapor"
    safe_slug = slugify(_plain_text(getattr(idea, "title", "")))
    safe_slug = re.sub(r"[^a-z0-9-]+", "-", safe_slug.lower())
    safe_slug = re.sub(r"-{2,}", "-", safe_slug).strip(" .-_")

    if (
        not safe_slug
        or safe_slug.split(".", 1)[0] in _RESERVED_FILENAMES
    ):
        safe_slug = f"fikir-{idea_id}"

    safe_slug = safe_slug[:80].rstrip(" .-_")
    if not safe_slug:
        safe_slug = f"fikir-{idea_id}"

    return f"fikirlab-{safe_slug}-raporu.pdf"


def _styles():
    body = ParagraphStyle(
        "ReportBody",
        fontName=REGULAR_FONT_NAME,
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#27313F"),
        spaceAfter=5,
        splitLongWords=True,
        allowWidows=0,
        allowOrphans=0,
    )
    return {
        "brand": ParagraphStyle(
            "ReportBrand",
            parent=body,
            fontName=BOLD_FONT_NAME,
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4F46E5"),
            uppercase=True,
            spaceAfter=3,
        ),
        "document_title": ParagraphStyle(
            "ReportDocumentTitle",
            parent=body,
            fontName=BOLD_FONT_NAME,
            fontSize=23,
            leading=28,
            textColor=colors.HexColor("#111827"),
            spaceAfter=5,
        ),
        "idea_title": ParagraphStyle(
            "ReportIdeaTitle",
            parent=body,
            fontName=BOLD_FONT_NAME,
            fontSize=18,
            leading=23,
            textColor=colors.HexColor("#1F2937"),
            spaceAfter=5,
        ),
        "metadata": ParagraphStyle(
            "ReportMetadata",
            parent=body,
            fontSize=8.5,
            leading=11,
            textColor=colors.HexColor("#6B7280"),
            spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "ReportSection",
            parent=body,
            fontName=BOLD_FONT_NAME,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#111827"),
            spaceBefore=11,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "subsection": ParagraphStyle(
            "ReportSubsection",
            parent=body,
            fontName=BOLD_FONT_NAME,
            fontSize=10.5,
            leading=14,
            textColor=colors.HexColor("#1F2937"),
            spaceBefore=5,
            spaceAfter=3,
            keepWithNext=True,
        ),
        "body": body,
        "muted": ParagraphStyle(
            "ReportMuted",
            parent=body,
            fontSize=8.7,
            leading=12,
            textColor=colors.HexColor("#6B7280"),
        ),
        "placeholder": ParagraphStyle(
            "ReportPlaceholder",
            parent=body,
            fontSize=9,
            leading=12.5,
            textColor=colors.HexColor("#6B7280"),
            backColor=colors.HexColor("#F3F4F6"),
            borderColor=colors.HexColor("#E5E7EB"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=5,
        ),
        "card": ParagraphStyle(
            "ReportCard",
            parent=body,
            backColor=colors.HexColor("#F8FAFC"),
            borderColor=colors.HexColor("#E5E7EB"),
            borderWidth=0.5,
            borderPadding=6,
            spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "ReportBullet",
            parent=body,
            leftIndent=11,
            firstLineIndent=0,
            bulletIndent=0,
            bulletFontName=REGULAR_FONT_NAME,
            bulletFontSize=8,
            spaceAfter=3,
        ),
        "numbered": ParagraphStyle(
            "ReportNumbered",
            parent=body,
            leftIndent=13,
            firstLineIndent=-13,
            spaceAfter=5,
        ),
        "centered": ParagraphStyle(
            "ReportCentered",
            parent=body,
            alignment=TA_CENTER,
        ),
    }


def _add_section(story, styles, title):
    story.append(Paragraph(escape(title), styles["section"]))


def _add_subsection(story, styles, title):
    story.append(Paragraph(escape(title), styles["subsection"]))


def _add_paragraph(story, styles, value, style="body", fallback=None):
    story.append(
        Paragraph(
            _paragraph_text(
                value,
                fallback if fallback is not None else "Bilgi bulunmuyor.",
            ),
            styles[style],
        )
    )


def _add_labeled_paragraph(
    story,
    styles,
    label,
    value,
    *,
    style="body",
    fallback="Bilgi bulunmuyor.",
):
    story.append(
        Paragraph(
            (
                f"<b>{escape(label)}:</b> "
                f"{_paragraph_text(value, fallback)}"
            ),
            styles[style],
        )
    )


def _add_bullets(story, styles, value, empty_message):
    items = _nonempty_items(value)
    if not items:
        _add_paragraph(
            story,
            styles,
            empty_message,
            style="muted",
        )
        return

    for item in items:
        story.append(
            Paragraph(
                _paragraph_text(item),
                styles["bullet"],
                bulletText="•",
            )
        )


def _format_analysis_date(value):
    if value is None:
        value = timezone.now()
    try:
        if timezone.is_aware(value):
            value = timezone.localtime(value)
        return value.strftime("%d.%m.%Y")
    except (AttributeError, TypeError, ValueError):
        return timezone.localtime(timezone.now()).strftime("%d.%m.%Y")


def _append_idea_summary(story, styles, idea_data):
    _add_section(story, styles, "Fikir Özeti")
    _add_paragraph(story, styles, idea_data.get("description"))
    if _plain_text(idea_data.get("sector")):
        _add_labeled_paragraph(
            story,
            styles,
            "Sektör",
            idea_data.get("sector"),
            style="muted",
        )
    if _plain_text(idea_data.get("solution")):
        _add_labeled_paragraph(
            story,
            styles,
            "Çözüm",
            idea_data.get("solution"),
        )

    _add_section(story, styles, "Problem ve Hedef Kitle")
    _add_labeled_paragraph(
        story,
        styles,
        "Problem",
        idea_data.get("problem"),
        style="card",
    )
    _add_labeled_paragraph(
        story,
        styles,
        "Hedef Kitle",
        idea_data.get("target_audience"),
        style="card",
    )


def _append_risky_assumptions(story, styles, data):
    _add_section(story, styles, "Riskli Varsayımlar")
    assumptions = _as_list(data.get("assumptions"))
    if not assumptions:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["risky_assumptions"],
            style="placeholder",
        )
        return

    risk_labels = {
        "high": "Yüksek Risk",
        "medium": "Orta Risk",
        "low": "Düşük Risk",
    }
    status_labels = {
        "validated": "Doğrulandı",
        "refuted": "Çürütüldü",
        "untested": "Test Edilmedi",
    }

    for index, raw_assumption in enumerate(assumptions, start=1):
        assumption = _as_dict(raw_assumption)
        text = (
            assumption.get("text")
            if assumption
            else raw_assumption
        )
        risk_label = risk_labels.get(
            _plain_text(assumption.get("level")).lower(),
            "Risk Seviyesi Belirtilmedi",
        )
        status_label = status_labels.get(
            _plain_text(assumption.get("status")).lower(),
            "Test Durumu Belirtilmedi",
        )
        _add_subsection(
            story,
            styles,
            f"{index}. {risk_label} · {status_label}",
        )
        _add_paragraph(story, styles, text, style="card")
        if _plain_text(assumption.get("evidence_quote")):
            _add_labeled_paragraph(
                story,
                styles,
                "Kanıt",
                assumption.get("evidence_quote"),
                style="muted",
            )


def _append_mom_test(story, styles, questions):
    _add_section(story, styles, "Müşteri Görüşme Soruları")
    if not questions:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["mom_test"],
            style="placeholder",
        )
        return

    for index, raw_question in enumerate(questions, start=1):
        question = _as_dict(raw_question)
        question_text = (
            question.get("question")
            if question
            else raw_question
        )
        story.append(
            Paragraph(
                (
                    f"<b>{index}.</b> "
                    f"{_paragraph_text(question_text)}"
                ),
                styles["numbered"],
            )
        )
        if _plain_text(question.get("category")):
            _add_labeled_paragraph(
                story,
                styles,
                "Kategori",
                question.get("category"),
                style="muted",
            )


def _append_moscow(story, styles, data):
    _add_section(story, styles, "MVP Kapsamı (MoSCoW)")
    categories = (
        ("must_have", "Must Have"),
        ("should_have", "Should Have"),
        ("could_have", "Could Have"),
        ("wont_have", "Won’t Have"),
    )
    has_content = bool(
        _plain_text(data.get("summary"))
        or any(_as_list(data.get(key)) for key, _ in categories)
    )
    if not has_content:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["moscow"],
            style="placeholder",
        )
        return

    if _plain_text(data.get("summary")):
        _add_labeled_paragraph(
            story,
            styles,
            "Genel MVP Özeti",
            data.get("summary"),
            style="card",
        )

    for key, label in categories:
        _add_subsection(story, styles, label)
        items = _as_list(data.get(key))
        if not items:
            _add_paragraph(
                story,
                styles,
                "Bu kategoride kayıtlı madde yok.",
                style="muted",
            )
            continue

        for raw_item in items:
            item = _as_dict(raw_item)
            if item:
                title = _paragraph_text(
                    item.get("title"),
                    "Başlıksız madde",
                )
                reason = _paragraph_text(
                    item.get("reason"),
                    "Gerekçe belirtilmedi.",
                )
                story.append(
                    Paragraph(
                        f"<b>{title}</b><br/>{reason}",
                        styles["card"],
                    )
                )
            else:
                _add_paragraph(
                    story,
                    styles,
                    raw_item,
                    style="card",
                )


def _append_roadmap(story, styles, data):
    _add_section(story, styles, "Doğrulama Yol Haritası")
    phases = _as_list(data.get("phases"))
    if not phases:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["roadmap"],
            style="placeholder",
        )
        return

    roadmap_type = _plain_text(data.get("roadmap_type")).lower()
    for index, raw_phase in enumerate(phases, start=1):
        phase = _as_dict(raw_phase)
        order = phase.get("week", phase.get("phase", index))
        default_label = (
            f"Hafta {order}"
            if roadmap_type == "weekly"
            else f"Aşama {order}"
        )
        title = _plain_text(phase.get("title")) or default_label
        _add_subsection(
            story,
            styles,
            f"{index}. {title} ({default_label})",
        )

        for key, label in ROADMAP_SECTION_KEYS:
            _add_labeled_paragraph(
                story,
                styles,
                label,
                "",
                style="subsection",
                fallback="",
            )
            _add_bullets(
                story,
                styles,
                phase.get(key),
                "Bu alt bölüm için kayıtlı madde yok.",
            )


def _append_general_evaluation(story, styles, data):
    _add_section(story, styles, "Genel Değerlendirme")
    has_content = bool(
        _as_list(data.get("strengths"))
        or _as_list(data.get("uncertainties"))
        or _plain_text(data.get("next_action"))
    )
    if not has_content:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["general_evaluation"],
            style="placeholder",
        )
        return

    _add_subsection(story, styles, "Güçlü Yönler")
    _add_bullets(
        story,
        styles,
        data.get("strengths"),
        "Güçlü yön kaydedilmedi.",
    )
    _add_subsection(story, styles, "Belirsiz Noktalar")
    _add_bullets(
        story,
        styles,
        data.get("uncertainties"),
        "Belirsiz nokta kaydedilmedi.",
    )
    _add_subsection(story, styles, "İlk Yapılacak Aksiyon")
    _add_paragraph(
        story,
        styles,
        data.get("next_action"),
        style="card",
    )


def _append_competitor_analysis(story, styles, data):
    _add_section(story, styles, "Rakip / Pazar Analizi")
    competitors = _as_list(data.get("competitors"))
    has_content = bool(
        competitors
        or _plain_text(data.get("market_gap"))
        or _plain_text(data.get("differentiation"))
    )
    if not has_content:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["competitor_analysis"],
            style="placeholder",
        )
        return

    for index, raw_competitor in enumerate(competitors, start=1):
        competitor = _as_dict(raw_competitor)
        if not competitor:
            _add_subsection(story, styles, f"{index}. Rakip")
            _add_paragraph(
                story,
                styles,
                raw_competitor,
                style="card",
            )
            continue

        name = _plain_text(competitor.get("name")) or f"Rakip {index}"
        _add_subsection(story, styles, f"{index}. {name}")
        _add_paragraph(
            story,
            styles,
            competitor.get("description"),
            style="card",
        )
        _add_labeled_paragraph(
            story,
            styles,
            "Güçlü Yönler",
            "",
            style="subsection",
            fallback="",
        )
        _add_bullets(
            story,
            styles,
            competitor.get("strengths"),
            "Güçlü yön kaydedilmedi.",
        )
        _add_labeled_paragraph(
            story,
            styles,
            "Zayıf Yönler",
            "",
            style="subsection",
            fallback="",
        )
        _add_bullets(
            story,
            styles,
            competitor.get("weaknesses"),
            "Zayıf yön kaydedilmedi.",
        )

    if _plain_text(data.get("market_gap")):
        _add_subsection(story, styles, "Pazar Boşluğu")
        _add_paragraph(
            story,
            styles,
            data.get("market_gap"),
            style="card",
        )
    if _plain_text(data.get("differentiation")):
        _add_subsection(story, styles, "Farklılaşma Noktası")
        _add_paragraph(
            story,
            styles,
            data.get("differentiation"),
            style="card",
        )


def _append_investor_pitch(story, styles, data):
    _add_section(story, styles, "Yatırımcı Sunumu")
    slides = _as_list(data.get("slides"))
    has_content = bool(
        _plain_text(data.get("elevator_pitch"))
        or slides
        or _plain_text(data.get("closing_ask"))
    )
    if not has_content:
        _add_paragraph(
            story,
            styles,
            MISSING_SECTION_MESSAGES["investor_pitch"],
            style="placeholder",
        )
        return

    if _plain_text(data.get("elevator_pitch")):
        _add_subsection(story, styles, "Elevator Pitch")
        _add_paragraph(
            story,
            styles,
            data.get("elevator_pitch"),
            style="card",
        )

    for index, raw_slide in enumerate(slides, start=1):
        slide = _as_dict(raw_slide)
        if slide:
            title = _plain_text(slide.get("title")) or f"Slayt {index}"
            _add_subsection(
                story,
                styles,
                f"{index}. {title}",
            )
            _add_bullets(
                story,
                styles,
                slide.get("bullets"),
                "Bu slayt için kayıtlı madde yok.",
            )
        else:
            _add_subsection(story, styles, f"Slayt {index}")
            _add_paragraph(
                story,
                styles,
                raw_slide,
                style="card",
            )

    if _plain_text(data.get("closing_ask")):
        _add_subsection(story, styles, "Kapanış / Talep")
        _add_paragraph(
            story,
            styles,
            data.get("closing_ask"),
            style="card",
        )


def _append_sources(story, styles, sources):
    unique_sources = []
    seen = set()
    for raw_source in sources:
        source = _as_dict(raw_source)
        if source:
            identity = (
                _plain_text(source.get("source_url"))
                or _plain_text(source.get("title"))
            )
        else:
            identity = _plain_text(raw_source)
        if not identity or identity in seen:
            continue
        seen.add(identity)
        unique_sources.append(raw_source)

    if not unique_sources:
        return

    _add_section(story, styles, "Kullanılan Kaynaklar")
    _add_paragraph(
        story,
        styles,
        (
            "Bu analiz hazırlanırken aşağıdaki eğitim içerikleri "
            "referans alınmıştır."
        ),
        style="muted",
    )
    for index, raw_source in enumerate(unique_sources, start=1):
        source = _as_dict(raw_source)
        if source:
            title = source.get("title") or f"Kaynak {index}"
            _add_subsection(
                story,
                styles,
                f"{index}. {_plain_text(title)}",
            )
            if _plain_text(source.get("source_url")):
                _add_labeled_paragraph(
                    story,
                    styles,
                    "Bağlantı",
                    source.get("source_url"),
                    style="muted",
                )
        else:
            _add_subsection(story, styles, f"Kaynak {index}")
            _add_paragraph(
                story,
                styles,
                raw_source,
                style="muted",
            )


def build_report_pdf(idea):
    _register_fonts()
    report_data = collect_report_data(idea)
    idea_data = report_data["idea"]
    styles = _styles()
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        pageCompression=True,
        initialFontName=REGULAR_FONT_NAME,
        initialFontSize=9.5,
        initialLeading=13,
    )

    idea_title = _plain_text(idea_data.get("title")) or "Başlıksız Fikir"
    report_title = f"{idea_title} — Doğrulama Raporu"

    def draw_page_frame(canvas, doc):
        canvas.saveState()
        canvas.setTitle(report_title)
        canvas.setAuthor("FikirLab")
        canvas.setCreator("FikirLab ReportLab PDF Service")
        canvas.setSubject("Fikir doğrulama ve analiz raporu")

        canvas.setFont(BOLD_FONT_NAME, 8)
        canvas.setFillColor(colors.HexColor("#4B5563"))
        canvas.drawString(
            18 * mm,
            A4[1] - 12 * mm,
            "FikirLab · Doğrulama Raporu",
        )
        canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
        canvas.setLineWidth(0.5)
        canvas.line(
            18 * mm,
            A4[1] - 14 * mm,
            A4[0] - 18 * mm,
            A4[1] - 14 * mm,
        )

        canvas.setFont(REGULAR_FONT_NAME, 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawRightString(
            A4[0] - 18 * mm,
            10 * mm,
            f"Sayfa {doc.page}",
        )
        canvas.restoreState()

    story = [
        Paragraph("FikirLab", styles["brand"]),
        Paragraph("Doğrulama Raporu", styles["document_title"]),
        Paragraph(_paragraph_text(idea_title), styles["idea_title"]),
        Paragraph(
            (
                f"Analiz tarihi: "
                f"{_format_analysis_date(idea_data.get('created_at'))}"
                f" &nbsp;&nbsp;·&nbsp;&nbsp; "
                f"Fikir ID: {_paragraph_text(idea_data.get('id'), '—')}"
            ),
            styles["metadata"],
        ),
        Spacer(1, 4),
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=colors.HexColor("#D1D5DB"),
            spaceBefore=3,
            spaceAfter=3,
        ),
    ]

    _append_idea_summary(story, styles, idea_data)
    _append_risky_assumptions(
        story,
        styles,
        report_data["risky_assumptions"],
    )
    _append_mom_test(story, styles, report_data["mom_test"])
    _append_moscow(story, styles, report_data["moscow"])
    _append_roadmap(story, styles, report_data["roadmap"])
    _append_general_evaluation(
        story,
        styles,
        report_data["general_evaluation"],
    )
    _append_competitor_analysis(
        story,
        styles,
        report_data["competitor_analysis"],
    )
    _append_investor_pitch(
        story,
        styles,
        report_data["investor_pitch"],
    )
    _append_sources(story, styles, idea_data["sources"])

    document.build(
        story,
        onFirstPage=draw_page_frame,
        onLaterPages=draw_page_frame,
    )
    return buffer.getvalue()
