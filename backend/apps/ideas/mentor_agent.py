from django.conf import settings
from google import genai
from google.genai import errors, types

from apps.analyses.services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
)

from .models import CompetitorAnalysis, GeneralEvaluation, InvestorPitch, RiskyAssumptions, ValidationRoadmap
from .services import (
    CompetitorAnalysisGenerationError,
    GeneralEvaluationGenerationError,
    InvestorPitchGenerationError,
    RiskyAssumptionsGenerationError,
    RoadmapGenerationError,
    apply_interview_evidence_to_risky_assumptions,
    generate_competitor_analysis_payload,
    generate_general_evaluation_payload,
    generate_investor_pitch_payload,
    generate_risky_assumptions_payload,
    generate_validation_roadmap_payload,
)


class MentorAgentError(Exception):
    """Raised when the mentor agent cannot complete a chat turn."""


def _get_client() -> genai.Client:
    api_key = getattr(settings, "GEMINI_API_KEY", "")

    if not api_key:
        raise MentorAgentError("GEMINI_API_KEY is not configured.")

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )


def _tool_update_target_audience(idea, args: dict) -> dict:
    new_value = str(args.get("new_target_audience") or "").strip()
    if not new_value:
        raise ValueError("new_target_audience boş olamaz.")
    idea.target_audience = new_value
    idea.save(update_fields=["target_audience"])
    return {"target_audience": new_value}


def _tool_regenerate_validation_roadmap(idea, args: dict) -> dict:
    try:
        payload = generate_validation_roadmap_payload(idea)
    except RoadmapGenerationError as exc:
        raise ValueError(str(exc)) from exc

    ValidationRoadmap.objects.update_or_create(
        idea=idea,
        defaults={"roadmap_data": payload},
    )
    return {"phase_count": len(payload.get("phases", []))}


def _tool_regenerate_moscow_scope(idea, args: dict) -> dict:
    analysis = generate_moscow_scope(idea)
    result = analysis.result
    return {
        "must_have": [item["title"] for item in result.get("must_have", [])],
        "should_have": [item["title"] for item in result.get("should_have", [])],
        "could_have": [item["title"] for item in result.get("could_have", [])],
        "wont_have": [item["title"] for item in result.get("wont_have", [])],
    }


def _tool_generate_mom_test_questions(idea, args: dict) -> dict:
    count = int(args.get("question_count") or 10)
    count = max(8, min(10, count))
    questions = generate_mom_test_questions(idea, question_count=count)
    return {"questions": [q["question"] for q in questions]}


def _tool_regenerate_risky_assumptions(idea, args: dict) -> dict:
    try:
        payload = generate_risky_assumptions_payload(idea)
    except RiskyAssumptionsGenerationError as exc:
        raise ValueError(str(exc)) from exc

    RiskyAssumptions.objects.update_or_create(
        idea=idea,
        defaults={"assumptions_data": payload},
    )
    return {
        "assumptions": [
            f"[{item['level']}] {item['text']}" for item in payload["assumptions"]
        ]
    }


def _tool_regenerate_general_evaluation(idea, args: dict) -> dict:
    try:
        payload = generate_general_evaluation_payload(idea)
    except GeneralEvaluationGenerationError as exc:
        raise ValueError(str(exc)) from exc

    GeneralEvaluation.objects.update_or_create(
        idea=idea,
        defaults={"evaluation_data": payload},
    )
    return payload


def _tool_regenerate_competitor_analysis(idea, args: dict) -> dict:
    try:
        payload = generate_competitor_analysis_payload(idea)
    except CompetitorAnalysisGenerationError as exc:
        raise ValueError(str(exc)) from exc

    CompetitorAnalysis.objects.update_or_create(
        idea=idea,
        defaults={"analysis_data": payload},
    )
    return {
        "competitors": [c["name"] for c in payload["competitors"]],
        "differentiation": payload["differentiation"],
    }


def _tool_generate_investor_pitch(idea, args: dict) -> dict:
    try:
        payload = generate_investor_pitch_payload(idea)
    except InvestorPitchGenerationError as exc:
        raise ValueError(str(exc)) from exc

    InvestorPitch.objects.update_or_create(
        idea=idea,
        defaults={"pitch_data": payload},
    )
    return {
        "elevator_pitch": payload["elevator_pitch"],
        "slide_titles": [s["title"] for s in payload["slides"]],
        "closing_ask": payload["closing_ask"],
    }


def _tool_save_interview_note(idea, args: dict) -> dict:
    from apps.analyses.models import InterviewNote

    notes = str(args.get("notes") or "").strip()
    if len(notes) < 10:
        raise ValueError(
            "Görüşme notu çok kısa görünüyor. Görüşmede konuşulanları biraz daha "
            "detaylandırıp tekrar gönderir misin?"
        )

    interviewee_name = str(args.get("interviewee_name") or "").strip()[:255]
    interviewee_profile = str(args.get("interviewee_profile") or "").strip()[:500]

    note = InterviewNote.objects.create(
        idea=idea,
        interviewee_name=interviewee_name,
        interviewee_profile=interviewee_profile,
        notes=notes[:10_000],
    )
    return {
        "note_id": note.id,
        "interviewee_name": interviewee_name or "Belirtilmedi",
    }


def _tool_analyze_interview_evidence(idea, args: dict) -> dict:
    from apps.analyses.models import InterviewNote

    notes = list(InterviewNote.objects.filter(idea=idea).order_by("created_at"))
    if not notes:
        raise ValueError(
            "Bu fikir için henüz görüşme notu eklenmemiş. Önce en az bir müşteri "
            "görüşmesi notu ekle, sonra tekrar dener misin?"
        )

    interview_notes_text = "\n\n---\n\n".join(
        f"Görüşme {index} ({note.interviewee_name.strip() or 'Belirtilmedi'}):\n{note.notes.strip()}"
        for index, note in enumerate(notes, start=1)
    )

    try:
        result = apply_interview_evidence_to_risky_assumptions(idea, interview_notes_text)
    except RiskyAssumptionsGenerationError as exc:
        raise ValueError(str(exc)) from exc

    assumptions = result["assumptions"]
    return {
        "interview_count": len(notes),
        "validated_count": sum(1 for a in assumptions if a["status"] == "validated"),
        "refuted_count": sum(1 for a in assumptions if a["status"] == "refuted"),
        "untested_count": sum(1 for a in assumptions if a["status"] == "untested"),
        "new_assumptions_count": result["new_assumptions_count"],
        "assumptions": [
            f"[{a['status']}] {a['text']} — {a.get('evidence_quote', '')}" for a in assumptions
        ],
    }


TOOL_HANDLERS = {
    "update_target_audience": _tool_update_target_audience,
    "regenerate_validation_roadmap": _tool_regenerate_validation_roadmap,
    "regenerate_moscow_scope": _tool_regenerate_moscow_scope,
    "generate_mom_test_questions": _tool_generate_mom_test_questions,
    "regenerate_risky_assumptions": _tool_regenerate_risky_assumptions,
    "regenerate_general_evaluation": _tool_regenerate_general_evaluation,
    "regenerate_competitor_analysis": _tool_regenerate_competitor_analysis,
    "generate_investor_pitch": _tool_generate_investor_pitch,
    "save_interview_note": _tool_save_interview_note,
    "analyze_interview_evidence": _tool_analyze_interview_evidence,
}

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="update_target_audience",
        description="Fikrin hedef kitlesini kullanıcının belirttiği yeni tanımla günceller.",
        parameters={
            "type": "object",
            "properties": {
                "new_target_audience": {
                    "type": "string",
                    "description": "Yeni hedef kitle tanımı.",
                }
            },
            "required": ["new_target_audience"],
        },
    ),
    types.FunctionDeclaration(
        name="regenerate_validation_roadmap",
        description="Fikrin haftalık/aşamalı doğrulama yol haritasını yeniden oluşturur.",
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="regenerate_moscow_scope",
        description="Fikrin MVP kapsamını (Must/Should/Could/Won't Have) yeniden değerlendirir.",
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="generate_mom_test_questions",
        description="Müşteri görüşmesi için geçmiş davranışa dayalı Mom Test sorularını üretir.",
        parameters={
            "type": "object",
            "properties": {
                "question_count": {
                    "type": "integer",
                    "description": "8 ile 10 arasında üretilecek soru sayısı.",
                }
            },
        },
    ),
    types.FunctionDeclaration(
        name="regenerate_risky_assumptions",
        description="Fikrin riskli varsayımlarını (test edilmesi gereken hipotezleri) yeniden değerlendirir.",
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="regenerate_general_evaluation",
        description="Fikrin genel değerlendirmesini (güçlü yönler, belirsiz noktalar, ilk aksiyon) yeniden oluşturur.",
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="regenerate_competitor_analysis",
        description=(
            "Fikrin rakip/pazar analizini (olası rakipler, güçlü-zayıf yönleri, pazar boşluğu ve "
            "farklılaşma noktası) yeniden oluşturur."
        ),
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="generate_investor_pitch",
        description=(
            "Fikrin var olan tüm analiz verilerini (riskli varsayımlar, MVP kapsamı, rakip analizi, "
            "genel değerlendirme) okuyup kısa bir 'elevator pitch', 6 slaytlık bir yatırımcı sunumu "
            "akışı ve net bir kapanış talebi (ask) üretir. Kullanıcı 'sunumumu hazırla', 'pitch "
            "oluştur' veya benzeri bir şey isterse bu aracı kullan."
        ),
        parameters={"type": "object", "properties": {}},
    ),
    types.FunctionDeclaration(
        name="save_interview_note",
        description=(
            "Kullanıcı bir müşteri görüşmesinin notunu veya özetini doğrudan sohbete "
            "serbest metin olarak yapıştırırsa (bir form doldurmadan), bu notu kalıcı "
            "olarak kaydeder. Notu kaydettikten sonra kanıtları değerlendirmek istersen "
            "aynı yanıtta analyze_interview_evidence aracını da çağırabilirsin."
        ),
        parameters={
            "type": "object",
            "properties": {
                "notes": {
                    "type": "string",
                    "description": "Görüşmede konuşulanların serbest metin özeti.",
                },
                "interviewee_name": {
                    "type": "string",
                    "description": "Görüşülen kişinin adı (biliniyorsa).",
                },
                "interviewee_profile": {
                    "type": "string",
                    "description": "Görüşülen kişinin profili/rolü (biliniyorsa).",
                },
            },
            "required": ["notes"],
        },
    ),
    types.FunctionDeclaration(
        name="analyze_interview_evidence",
        description=(
            "Fikre eklenmiş müşteri görüşme notlarını okuyup mevcut riskli varsayımların "
            "her birinin doğrulandı/çürütüldü/test edilmedi durumunu günceller ve notlardan "
            "çıkan yeni riskli varsayımları ekler. Kullanıcı 'görüşme notlarını analiz et', "
            "'kanıtları değerlendir' veya benzeri bir şey isterse bu aracı kullan."
        ),
        parameters={"type": "object", "properties": {}},
    ),
]

SYSTEM_INSTRUCTION_TEMPLATE = """Sen FikirLab uygulamasında bir girişim doğrulama danışmanısın.
Kullanıcının aşağıdaki iş fikri üzerinde onunla birlikte çalışıyorsun:

- Başlık: {title}
- Açıklama: {description}
- Hedef kitle: {target_audience}
- Problem: {problem}
- Çözüm önerisi: {solution}
- Sektör: {sector}

Kullanıcı bir güncelleme isterse elindeki araçlardan uygun olanı çağır. Araç çağırmadan önce
gereksiz açıklama yapma. Bir araç sonucu liste (sorular, özellikler vb.) içeriyorsa bu listeyi
özetlemek yerine kullanıcıya olduğu gibi göster. Araç sonucu döndükten sonra en fazla birkaç
cümlelik, Türkçe, net bir kapanış mesajı ver. Kullanıcının isteği elindeki araçlardan hiçbiriyle
karşılanamıyorsa bunu dürüstçe belirt ve araç çağırma. Bir turda gerekmedikçe birden fazla araç
çağırma — TEK İSTİSNA: kullanıcı bir görüşme notunu/özetini doğrudan sohbete yapıştırırsa, önce
save_interview_note ile notu kaydet, ardından aynı yanıtta analyze_interview_evidence aracını
çağırarak kanıtları hemen değerlendir.
"""


def run_mentor_chat(idea, message: str, history: list[dict] | None = None) -> dict:
    client = _get_client()

    tool = types.Tool(function_declarations=TOOL_DECLARATIONS)
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION_TEMPLATE.format(
            title=idea.title,
            description=idea.description,
            target_audience=idea.target_audience,
            problem=idea.problem,
            solution=idea.solution,
            sector=idea.sector,
        ),
        tools=[tool],
        temperature=0.3,
        max_output_tokens=1024,
    )

    contents: list[types.Content] = []
    for turn in (history or [])[-6:]:
        role = "model" if turn.get("role") == "assistant" else "user"
        text = str(turn.get("content", "")).strip()
        if text:
            contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    actions: list[dict] = []
    max_rounds = 3

    for _ in range(max_rounds):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=contents,
                config=config,
            )
        except errors.ClientError as exc:
            raise MentorAgentError("Gemini isteği reddedildi.") from exc
        except errors.ServerError as exc:
            raise MentorAgentError("Yapay zeka servisi şu anda kullanılamıyor.") from exc

        calls = response.function_calls or []

        if not calls:
            reply = (response.text or "").strip() or "Anladım, şu an için ek bir işlem yapmadım."
            return {"reply": reply, "actions": actions}

        contents.append(response.candidates[0].content)

        response_parts = []
        for call in calls:
            handler = TOOL_HANDLERS.get(call.name)

            if handler is None:
                result = {"error": f"Bilinmeyen araç: {call.name}"}
                status = "error"
            else:
                try:
                    result = handler(idea, dict(call.args or {}))
                    status = "success"
                except (MoscowGenerationError, ValueError) as exc:
                    result = {"error": str(exc)}
                    status = "error"
                except Exception:
                    result = {"error": "Beklenmeyen bir hata oluştu."}
                    status = "error"

            actions.append({"tool": call.name, "status": status, "result": result})
            response_parts.append(
                types.Part(
                    function_response=types.FunctionResponse(
                        name=call.name,
                        response=result,
                    )
                )
            )

        contents.append(types.Content(role="user", parts=response_parts))

    return {
        "reply": "İsteğini işleme alırken beklenenden fazla adım gerekti, lütfen tekrar dener misin?",
        "actions": actions,
    }
