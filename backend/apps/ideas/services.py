import json

from django.conf import settings
from google import genai
from google.genai import types
from .rag_context import get_idea_rag_context


class RiskyAssumptionsGenerationError(Exception):
    """Raised when risky assumptions cannot be generated from the AI response."""


class GeneralEvaluationGenerationError(Exception):
    """Raised when the general evaluation cannot be generated from the AI response."""


class CompetitorAnalysisGenerationError(Exception):
    """Raised when the competitor analysis cannot be generated from the AI response."""


class InvestorPitchGenerationError(Exception):
    """Raised when the investor pitch cannot be generated from the AI response."""


GENERAL_EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "strengths": {
            "type": "array",
            "items": {"type": "string"},
        },
        "uncertainties": {
            "type": "array",
            "items": {"type": "string"},
        },
        "next_action": {"type": "string"},
    },
    "required": ["strengths", "uncertainties", "next_action"],
}


def build_general_evaluation_prompt(
    idea,
    rag_context: str = "",
) -> str:
    return (
        "Sen deneyimli bir girişim doğrulama danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. Aşağıdaki iş fikri için genel bir değerlendirme yap: "
        "tam olarak 3 güçlü yön, tam olarak 2 belirsiz/riskli nokta üret. Ayrıca fikrin sahibinin "
        "bu hafta atması gereken tek, somut ve uygulanabilir ilk aksiyonu tek cümlede yaz. "
        "Genel geçer laf kalabalığından kaçın, fikre özgü ve spesifik ol.\n\n"
        f"Fikir başlığı: {idea.title}\n"
        f"Açıklama: {idea.description}\n"
        f"Hedef kitle: {idea.target_audience}\n"
        f"Problem: {idea.problem}\n"
        f"Çözüm önerisi: {idea.solution}\n"
        f"Sektör: {idea.sector}\n\n"
        "--- RAG BAĞLAMI ---\n"
        f"{rag_context or 'İlgili bilgi tabanı içeriği bulunamadı.'}\n"
        "--- RAG BAĞLAMI SONU ---\n\n"
        "RAG bağlamını yalnızca destekleyici bilgi olarak kullan. "
        "Bağlamdaki ifadeleri doğrudan kopyalama; değerlendirmeyi iş fikrine özgü üret.\n"
    )


def generate_general_evaluation_payload(idea) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise GeneralEvaluationGenerationError("GEMINI_API_KEY is not configured.")

    rag_context, _ = get_idea_rag_context(
        idea,
        purpose=(
            "iş fikri değerlendirmesi, güçlü yönler, "
            "belirsizlikler, riskler ve sonraki aksiyon"
        ),
    )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_general_evaluation_prompt(
                idea,
                rag_context=rag_context,
            ),
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=GENERAL_EVALUATION_SCHEMA,
                max_output_tokens=1024,
            ),
        )
    except Exception as exc:
        raise GeneralEvaluationGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise GeneralEvaluationGenerationError("AI response was not valid JSON.") from exc

    if not isinstance(result, dict) or not all(
        key in result for key in ("strengths", "uncertainties", "next_action")
    ):
        raise GeneralEvaluationGenerationError("AI response was incomplete.")

    return result


COMPETITOR_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "competitors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "strengths": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "weaknesses": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["name", "description", "strengths", "weaknesses"],
            },
        },
        "market_gap": {"type": "string"},
        "differentiation": {"type": "string"},
    },
    "required": ["competitors", "market_gap", "differentiation"],
}


def build_competitor_analysis_prompt(idea) -> str:
    return (
        "Sen deneyimli bir pazar araştırması danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. Aşağıdaki iş fikri için bir rakip/pazar analizi yap: "
        "bu sektörde ve problemde faaliyet gösteren veya benzer bir ihtiyacı karşılayan tam olarak "
        "3 gerçekçi rakip/alternatif çözüm belirle (doğrudan rakip, dolaylı rakip veya mevcut manuel "
        "alternatif olabilir). Her rakip için kısa bir tanım, tam olarak 2 güçlü yön ve tam olarak "
        "2 zayıf yön yaz. Ardından genel pazardaki boşluğu (market_gap) ve bu fikrin rakiplerden "
        "somut olarak nasıl farklılaşabileceğini (differentiation) birer paragrafta özetle. "
        "Genel geçer laf kalabalığından kaçın, fikre özgü ve spesifik ol.\n\n"
        f"Fikir başlığı: {idea.title}\n"
        f"Açıklama: {idea.description}\n"
        f"Hedef kitle: {idea.target_audience}\n"
        f"Problem: {idea.problem}\n"
        f"Çözüm önerisi: {idea.solution}\n"
        f"Sektör: {idea.sector}\n"
    )


def generate_competitor_analysis_payload(idea) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise CompetitorAnalysisGenerationError("GEMINI_API_KEY is not configured.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_competitor_analysis_prompt(idea),
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=COMPETITOR_ANALYSIS_SCHEMA,
                max_output_tokens=1536,
            ),
        )
    except Exception as exc:
        raise CompetitorAnalysisGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise CompetitorAnalysisGenerationError("AI response was not valid JSON.") from exc

    if not isinstance(result, dict) or not all(
        key in result for key in ("competitors", "market_gap", "differentiation")
    ):
        raise CompetitorAnalysisGenerationError("AI response was incomplete.")

    return result


INVESTOR_PITCH_SCHEMA = {
    "type": "object",
    "properties": {
        "elevator_pitch": {"type": "string"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "bullets": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["title", "bullets"],
            },
        },
        "closing_ask": {"type": "string"},
    },
    "required": ["elevator_pitch", "slides", "closing_ask"],
}


def build_investor_pitch_prompt(idea) -> str:
    sections = [
        "Sen deneyimli bir girişim yatırım danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. Aşağıdaki iş fikri ve varsa ona ait mevcut analiz "
        "verilerini oku, bunları kendi kararınla sentezleyerek kısa ve ikna edici bir yatırımcı "
        "sunumu hazırla: tek cümlelik çarpıcı bir 'elevator_pitch'; tam olarak 6 slaytlık, sırasıyla "
        "Problem, Çözüm, Pazar Fırsatı, Doğrulama Kanıtları, Ürün/MVP, Kapanış-Talep başlıklarını "
        "taşıyan bir sunum akışı (her slaytta 2-4 madde, madde başlıkla aynı bilgiyi tekrar etmesin); "
        "ve net bir 'closing_ask' (yatırım, pilot müşteri veya mentorluk gibi ne istediğinizi tek "
        "cümlede belirt). Sağlanan doğrulama kanıtları (doğrulanmış varsayımlar, farklılaşma noktası, "
        "güçlü yönler) varsa 'Doğrulama Kanıtları' slaydında bunları somut olarak kullan; yoksa "
        "fikrin kendisinden çıkarım yap. Genel geçer laf kalabalığından kaçın, fikre özgü ve spesifik "
        "ol.\n\n"
        f"Fikir başlığı: {idea.title}\n"
        f"Açıklama: {idea.description}\n"
        f"Hedef kitle: {idea.target_audience}\n"
        f"Problem: {idea.problem}\n"
        f"Çözüm önerisi: {idea.solution}\n"
        f"Sektör: {idea.sector}\n"
    ]

    if hasattr(idea, "risky_assumptions"):
        assumptions = idea.risky_assumptions.assumptions_data.get("assumptions", [])
        validated = [a for a in assumptions if a.get("status") == "validated"]
        if validated:
            sections.append(
                "Kanıta dayalı doğrulanmış varsayımlar:\n"
                + "\n".join(f"- {a['text']}" for a in validated[:5])
            )

    if hasattr(idea, "moscow_scope_analysis"):
        must_haves = idea.moscow_scope_analysis.result.get("must_have", [])
        if must_haves:
            sections.append(
                "MVP'nin olmazsa olmaz özellikleri:\n"
                + "\n".join(f"- {m.get('title', '')}" for m in must_haves[:5] if m.get("title"))
            )

    if hasattr(idea, "competitor_analysis"):
        differentiation = idea.competitor_analysis.analysis_data.get("differentiation", "")
        if differentiation:
            sections.append(f"Rakiplerden farklılaşma noktası: {differentiation}")

    if hasattr(idea, "general_evaluation"):
        strengths = idea.general_evaluation.evaluation_data.get("strengths", [])
        if strengths:
            sections.append("Güçlü yönler:\n" + "\n".join(f"- {s}" for s in strengths[:5]))

    return "\n\n".join(sections)


def generate_investor_pitch_payload(idea) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise InvestorPitchGenerationError("GEMINI_API_KEY is not configured.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_investor_pitch_prompt(idea),
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=INVESTOR_PITCH_SCHEMA,
                max_output_tokens=2048,
            ),
        )
    except Exception as exc:
        raise InvestorPitchGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise InvestorPitchGenerationError("AI response was not valid JSON.") from exc

    if not isinstance(result, dict) or not all(
        key in result for key in ("elevator_pitch", "slides", "closing_ask")
    ):
        raise InvestorPitchGenerationError("AI response was incomplete.")

    return result


RISKY_ASSUMPTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "level": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["text", "level"],
            },
        }
    },
    "required": ["assumptions"],
}


def build_risky_assumptions_prompt(
    idea,
    rag_context: str = "",
) -> str:
    return (
        "Sen deneyimli bir girişim doğrulama danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. Aşağıdaki iş fikri için tam olarak 5 riskli varsayım üret. "
        "Her varsayım, MVP geliştirilmeden önce test edilmesi gereken, ölçülebilir ve spesifik bir hipotez "
        "olmalı (soyut ifadeler kullanma). Her varsayıma, yanlış çıkması durumunda fikre ne kadar zarar "
        "vereceğine ve şu an ne kadar belirsiz olduğuna göre \"high\", \"medium\" veya \"low\" risk seviyesi ata.\n\n"
        f"Fikir başlığı: {idea.title}\n"
        f"Açıklama: {idea.description}\n"
        f"Hedef kitle: {idea.target_audience}\n"
        f"Problem: {idea.problem}\n"
        f"Çözüm önerisi: {idea.solution}\n"
        f"Sektör: {idea.sector}\n\n"
        "--- RAG BAĞLAMI ---\n"
        f"{rag_context or 'İlgili bilgi tabanı içeriği bulunamadı.'}\n"
        "--- RAG BAĞLAMI SONU ---\n\n"
        "RAG bağlamını yalnızca destekleyici bilgi olarak kullan. "
        "Bağlamdaki ifadeleri doğrudan kopyalama; fikre özgü riskli varsayımlar üret.\n"
    )


def generate_risky_assumptions_payload(idea) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise RiskyAssumptionsGenerationError("GEMINI_API_KEY is not configured.")
    
    rag_context, _ = get_idea_rag_context(
        idea,
        purpose=(
            "riskli varsayımlar, hipotez doğrulama, "
            "müşteri problemi ve pazar riski"
        ),
    )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_risky_assumptions_prompt(
                idea,
                rag_context=rag_context,
            ),
            config=types.GenerateContentConfig(
                temperature=0.3,
                response_mime_type="application/json",
                response_schema=RISKY_ASSUMPTIONS_SCHEMA,
                max_output_tokens=1024,
            ),
        )
    except Exception as exc:
        raise RiskyAssumptionsGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RiskyAssumptionsGenerationError("AI response was not valid JSON.") from exc

    assumptions = result.get("assumptions") if isinstance(result, dict) else None
    if not isinstance(assumptions, list) or not assumptions:
        raise RiskyAssumptionsGenerationError("AI response did not contain assumptions.")

    assumptions = [{**item, "status": "untested"} for item in assumptions]

    return {"assumptions": assumptions}


ASSUMPTION_STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "assumption_updates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "enum": ["validated", "refuted", "untested"]},
                    "evidence_quote": {"type": "string"},
                },
                "required": ["status", "evidence_quote"],
            },
        },
        "new_assumptions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "level": {"type": "string", "enum": ["high", "medium", "low"]},
                },
                "required": ["text", "level"],
            },
        },
    },
    "required": ["assumption_updates", "new_assumptions"],
}


def build_assumption_status_prompt(idea, assumptions: list, interview_notes_text: str) -> str:
    if assumptions:
        assumptions_section = "\n".join(f"{i + 1}. {a['text']}" for i, a in enumerate(assumptions))
        classify_instruction = (
            "Aşağıda bu iş fikrinin riskli varsayımları numaralandırılmış olarak listelenmiştir. "
            "Görüşme notlarını oku ve HER varsayım için (numaralandırıldığı sırayla, atlamadan, "
            "tam olarak aynı sayıda madde döndürerek) durumunu belirle: "
            '"validated" (görüşmeler destekliyor), "refuted" (görüşmeler çürütüyor) veya '
            '"untested" (notlarda bu konuda yeterli bilgi yok). Her biri için notlardan kısa bir '
            "alıntı veya gerekçe yaz; kanıt yoksa \"Notlarda bu konuda bilgi yok.\" yaz."
        )
    else:
        assumptions_section = "(henüz tanımlanmış bir riskli varsayım yok)"
        classify_instruction = (
            "Bu fikir için henüz tanımlanmış bir riskli varsayım yok, bu yüzden "
            "assumption_updates listesini boş dizi olarak döndür."
        )

    return (
        "Sen deneyimli bir girişim doğrulama danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. "
        f"{classify_instruction} "
        "Ayrıca görüşme notlarından çıkan, listede olmayan yeni riskli varsayımlar varsa "
        "(en fazla 3 tane, her biri test edilebilir bir hipotez olarak) new_assumptions "
        "alanına ekle; yoksa boş dizi döndür.\n\n"
        f"Fikir başlığı: {idea.title}\n\n"
        f"Riskli varsayımlar:\n{assumptions_section}\n\n"
        f"Görüşme notları:\n{interview_notes_text}\n"
    )


def generate_assumption_status_updates(idea, assumptions: list, interview_notes_text: str) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise RiskyAssumptionsGenerationError("GEMINI_API_KEY is not configured.")

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_assumption_status_prompt(idea, assumptions, interview_notes_text),
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json",
                response_schema=ASSUMPTION_STATUS_SCHEMA,
                max_output_tokens=2048,
            ),
        )
    except Exception as exc:
        raise RiskyAssumptionsGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RiskyAssumptionsGenerationError("AI response was not valid JSON.") from exc

    updates = result.get("assumption_updates") if isinstance(result, dict) else None
    new_assumptions = result.get("new_assumptions") if isinstance(result, dict) else None

    if not isinstance(updates, list) or not isinstance(new_assumptions, list):
        raise RiskyAssumptionsGenerationError("AI response was incomplete.")
    if len(updates) != len(assumptions):
        raise RiskyAssumptionsGenerationError("AI response did not match the assumption count.")

    return {"assumption_updates": updates, "new_assumptions": new_assumptions}


def apply_interview_evidence_to_risky_assumptions(idea, interview_notes_text: str) -> dict:
    from .models import RiskyAssumptions

    existing, _ = RiskyAssumptions.objects.get_or_create(
        idea=idea,
        defaults={"assumptions_data": {"assumptions": []}},
    )
    assumptions = existing.assumptions_data.get("assumptions", [])

    result = generate_assumption_status_updates(idea, assumptions, interview_notes_text)

    updated_assumptions = [
        {**assumption, "status": update["status"], "evidence_quote": update["evidence_quote"]}
        for assumption, update in zip(assumptions, result["assumption_updates"])
    ]
    new_items = [
        {**item, "status": "untested", "evidence_quote": "Yeni tespit edilen varsayım."}
        for item in result["new_assumptions"]
    ]
    updated_assumptions.extend(new_items)

    existing.assumptions_data = {"assumptions": updated_assumptions}
    existing.save(update_fields=["assumptions_data"])

    return {
        "assumptions": updated_assumptions,
        "new_assumptions_count": len(new_items),
    }


class RoadmapGenerationError(Exception):
    """Raised when the validation roadmap cannot be generated from the AI response."""


VALIDATION_ROADMAP_PHASE_KEYS = (
    "İlk görüşmeler",
    "Test edilecek varsayımlar",
    "MVP öncelikleri",
    "Başarı metrikleri",
    "Sonraki karar noktaları",
)

VALIDATION_ROADMAP_SCHEMA = {
    "type": "object",
    "properties": {
        "roadmap_type": {"type": "string"},
        "idea_title": {"type": "string"},
        "phases": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "week": {"type": "integer"},
                    "title": {"type": "string"},
                    **{key: {"type": "array", "items": {"type": "string"}} for key in VALIDATION_ROADMAP_PHASE_KEYS},
                },
                "required": ["week", "title", *VALIDATION_ROADMAP_PHASE_KEYS],
            },
        },
    },
    "required": ["roadmap_type", "idea_title", "phases"],
}


def build_validation_roadmap_prompt(
    idea,
    rag_context: str = "",
):
    return (
        "Sen deneyimli bir girişim doğrulama danışmanısın. SADECE geçerli JSON döndür, "
        "markdown veya ek açıklama ekleme. Aşağıdaki iş fikri için 3 haftalık, aşamalı bir doğrulama "
        "yol haritası üret. Her hafta şu tam alanları içermeli: "
        '"İlk görüşmeler", "Test edilecek varsayımlar", "MVP öncelikleri", '
        '"Başarı metrikleri", "Sonraki karar noktaları" (her biri 2 maddelik bir dizi). '
        "Yol haritası fikre özgü, somut ve uygulanabilir olsun; genel geçer ifadelerden kaçın.\n\n"
        f"Fikir başlığı: {idea.title}\n"
        f"Açıklama: {idea.description}\n"
        f"Hedef kitle: {idea.target_audience}\n"
        f"Problem: {idea.problem}\n"
        f"Çözüm önerisi: {idea.solution}\n"
        f"Sektör: {idea.sector}\n\n"
        "--- RAG BAĞLAMI ---\n"
        f"{rag_context or 'İlgili bilgi tabanı içeriği bulunamadı.'}\n"
        "--- RAG BAĞLAMI SONU ---\n\n"
        "RAG bağlamını yalnızca destekleyici bilgi olarak kullan. "
        "Bağlamdaki ifadeleri doğrudan kopyalama; fikre özgü, somut ve uygulanabilir "
        "bir doğrulama yol haritası üret.\n"
    )


def generate_validation_roadmap_payload(idea) -> dict:
    api_key = getattr(settings, "GEMINI_API_KEY", "")
    if not api_key:
        raise RoadmapGenerationError("GEMINI_API_KEY is not configured.")
    
    rag_context, _ = get_idea_rag_context(
        idea,
        purpose=(
            "doğrulama yol haritası, deneyler, başarı metrikleri, "
            "müşteri görüşmeleri ve karar noktaları"
        ),
    )

    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=60_000),
    )

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=build_validation_roadmap_prompt(
                idea,
                rag_context=rag_context,
            ),
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json",
                response_schema=VALIDATION_ROADMAP_SCHEMA,
                max_output_tokens=2048,
            ),
        )
    except Exception as exc:
        raise RoadmapGenerationError("AI provider request failed.") from exc

    try:
        result = json.loads(response.text)
    except (json.JSONDecodeError, TypeError) as exc:
        raise RoadmapGenerationError("AI response was not valid JSON.") from exc

    if not isinstance(result, dict) or not result.get("phases"):
        raise RoadmapGenerationError("AI response was incomplete.")

    return result