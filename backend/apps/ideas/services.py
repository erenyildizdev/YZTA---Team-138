import json

from django.conf import settings
from google import genai
from google.genai import types


class RiskyAssumptionsGenerationError(Exception):
    """Raised when risky assumptions cannot be generated from the AI response."""


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


def build_risky_assumptions_prompt(idea) -> str:
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
        f"Sektör: {idea.sector}\n"
    )


def generate_risky_assumptions_payload(idea) -> dict:
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
            contents=build_risky_assumptions_prompt(idea),
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

    return {"assumptions": assumptions}


def build_validation_roadmap_prompt(idea):
    return (
        "You are an expert startup validation strategist. Return ONLY valid JSON. "
        "Do not use markdown, code fences, or any explanatory text. "
        "The roadmap must be weekly or phased. Every phase/week must include these exact keys: "
        '"İlk görüşmeler", "Test edilecek varsayımlar", "MVP öncelikleri", '
        '"Başarı metrikleri", "Sonraki karar noktaları". '
        "Use arrays for each of those keys. Keep the structure parseable and consistent. "
        "Recommended top-level shape: {\"roadmap_type\": \"weekly\", \"idea_title\": ..., \"phases\": [...]}\n\n"
        f"Idea title: {idea.title}\n"
        f"Idea description: {idea.description}\n"
        f"Target audience: {idea.target_audience}\n"
    )


def generate_validation_roadmap_payload(idea):
    build_validation_roadmap_prompt(idea)

    return {
        "roadmap_type": "weekly",
        "idea_title": idea.title,
        "phases": [
            {
                "week": 1,
                "title": "Problem ve müşteri doğrulama",
                "İlk görüşmeler": [
                    "5 hedef kullanıcıyla problem görüşmesi yap",
                    "İlk müşteri segmentini netleştir",
                ],
                "Test edilecek varsayımlar": [
                    "Kullanıcılar bu problemi gerçekten yaşıyor",
                    "Çözüm arama motivasyonu yeterince yüksek",
                ],
                "MVP öncelikleri": [
                    "Tek bir ana kullanım senaryosu",
                    "Manuel doğrulama için basit kayıt akışı",
                ],
                "Başarı metrikleri": [
                    "5 görüşmede en az 3 ortak sorun ifadesi",
                    "Görüşmelerin %60'ında ödeme/deneme ilgisi",
                ],
                "Sonraki karar noktaları": [
                    "Problemin tekrarlı olup olmadığı",
                    "İkinci haftaya geçmeden önce segment daraltma gerekliliği",
                ],
            },
            {
                "week": 2,
                "title": "Çözüm ve değer önerisi doğrulama",
                "İlk görüşmeler": [
                    "İlk hafta kullanıcılarından geri dönüş al",
                    "Çözüm önerisini kısa demo ile sun",
                ],
                "Test edilecek varsayımlar": [
                    "Çözüm problemi gerçekten hafifletiyor",
                    "Kullanıcılar önerilen değeri hızlıca anlayabiliyor",
                ],
                "MVP öncelikleri": [
                    "Tek bir değer önerisi ekranı",
                    "Geri bildirim toplama formu",
                ],
                "Başarı metrikleri": [
                    "En az 3 kullanıcı çözümü anlamlı bulmalı",
                    "Geri bildirimlerin yarısı aynı faydayı işaret etmeli",
                ],
                "Sonraki karar noktaları": [
                    "Çözüm dilinin sadeleştirilmesi",
                    "MVP kapsamına ek özellik gerekip gerekmediği",
                ],
            },
            {
                "week": 3,
                "title": "MVP ve kanıt toplama",
                "İlk görüşmeler": [
                    "Erken erişim kullanıcılarıyla test görüşmeleri yap",
                    "Ürün kullanımına dair engelleri topla",
                ],
                "Test edilecek varsayımlar": [
                    "Kullanıcılar MVP'yi kullanmak ister",
                    "Ana akış tek başına yeterince değer sunar",
                ],
                "MVP öncelikleri": [
                    "Temel kayıt ve kullanım akışı",
                    "Ölçümleme ve event takibi",
                ],
                "Başarı metrikleri": [
                    "En az 3 aktif kullanım oturumu",
                    "Kullanıcıların %50'si ana akışı tamamlar",
                ],
                "Sonraki karar noktaları": [
                    "MVP'de hangi eksiklerin kritik olduğu",
                    "Ölçekleme veya pivot ihtiyacı",
                ],
            },
        ],
    }