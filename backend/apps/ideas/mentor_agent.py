from django.conf import settings
from google import genai
from google.genai import errors, types

from apps.analyses.services import (
    MoscowGenerationError,
    generate_mom_test_questions,
    generate_moscow_scope,
)

from .models import GeneralEvaluation, RiskyAssumptions, ValidationRoadmap
from .services import (
    GeneralEvaluationGenerationError,
    RiskyAssumptionsGenerationError,
    RoadmapGenerationError,
    generate_general_evaluation_payload,
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


TOOL_HANDLERS = {
    "update_target_audience": _tool_update_target_audience,
    "regenerate_validation_roadmap": _tool_regenerate_validation_roadmap,
    "regenerate_moscow_scope": _tool_regenerate_moscow_scope,
    "generate_mom_test_questions": _tool_generate_mom_test_questions,
    "regenerate_risky_assumptions": _tool_regenerate_risky_assumptions,
    "regenerate_general_evaluation": _tool_regenerate_general_evaluation,
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
çağırma.
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
