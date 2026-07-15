import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings
from django.db import transaction
from rest_framework import serializers

from apps.analyses.models import MoscowScopeAnalysis
from apps.analyses.serializers import MoscowScopeResultSerializer

PROMPT_VERSION = "moscow-v1"
CATEGORY_FIELDS = ("must_have", "should_have", "could_have", "wont_have")


class MoscowGenerationError(Exception):
    """Raised when an LLM response cannot safely produce a valid scope."""


class MoscowClient(Protocol):
    provider: str
    model_name: str

    def complete(self, prompt: str) -> Any: ...


@dataclass
class OpenAICompatibleClient:
    api_url: str
    api_key: str
    model_name: str
    provider: str = "openai-compatible"

    @classmethod
    def from_settings(cls):
        if not settings.AI_API_KEY or not settings.AI_MODEL_NAME:
            raise MoscowGenerationError("AI provider is not configured.")
        return cls(
            api_url=settings.AI_API_URL,
            api_key=settings.AI_API_KEY,
            model_name=settings.AI_MODEL_NAME,
            provider=settings.AI_PROVIDER,
        )

    def complete(self, prompt: str) -> str:
        payload = json.dumps(
            {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0.2,
            }
        ).encode()
        request = Request(
            self.api_url,
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=45) as response:  # nosec: configured provider URL
                body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
        except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise MoscowGenerationError("AI provider request failed.") from exc


def build_moscow_prompt(idea) -> str:
    return f"""Deneyimli bir ürün yöneticisi ve MVP danışmanı gibi davran.
Aşağıdaki iş fikrini yalnızca verilen bilgilerle değerlendir:
- Başlık: {idea.title}
- Açıklama / çözülen problem ve değer önerisi: {idea.description}
- Hedef kullanıcı: {idea.target_audience}

Toplam 8-12 somut ürün özelliği üret ve Must Have, Should Have, Could Have ve Won't Have
kategorilerine ayır. Must Have yalnızca temel değeri sunmak için zorunlu özellikleri; Should Have
önemli fakat ilk sürüm için mutlak zorunlu olmayanları; Could Have deneyimi geliştiren fakat
ertelenebilecekleri içersin. Won't Have kötü veya gereksiz demek değildir; mevcut MVP kapsamına
bilinçli olarak alınmayacak özellikleri içersin.

Aynı özellik iki kategoride bulunmasın. Soyut ifadeler yerine uygulanabilir fonksiyonlar üret;
"yapay zeka", "güvenlik" veya "iyi kullanıcı deneyimi" gibi ifadeleri tek başına kullanma.
Her özellik için 3-100 karakterlik kısa title ve 10-500 karakterlik 1-2 cümlelik reason yaz.
10-1000 karakterlik bir summary yaz. Dört kategori de boş olmasın.
Yalnızca şu alanları içeren geçerli JSON döndür; markdown, code fence veya açıklama ekleme:
{{"summary":"...","must_have":[{{"title":"...","reason":"..."}}],
"should_have":[{{"title":"...","reason":"..."}}],
"could_have":[{{"title":"...","reason":"..."}}],
"wont_have":[{{"title":"...","reason":"..."}}]}}"""


def _parse_json(data: Any) -> dict:
    if isinstance(data, dict):
        return data
    if not isinstance(data, str):
        raise MoscowGenerationError("AI response is not JSON.")
    value = data.strip()
    if value.startswith("```"):
        lines = value.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        value = "\n".join(lines).strip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise MoscowGenerationError("AI response contains malformed JSON.") from exc
    if not isinstance(parsed, dict):
        raise MoscowGenerationError("AI response must be a JSON object.")
    return parsed


def normalize_moscow_result(data: Any) -> dict:
    parsed = _parse_json(data)
    normalized = dict(parsed)
    if isinstance(normalized.get("summary"), str):
        normalized["summary"] = " ".join(normalized["summary"].split())
    for category in CATEGORY_FIELDS:
        items = normalized.get(category)
        if isinstance(items, list):
            normalized[category] = [
                {
                    key: " ".join(value.split()) if isinstance(value, str) else value
                    for key, value in item.items()
                }
                if isinstance(item, dict) else item
                for item in items
            ]
    return normalized


def parse_and_validate_moscow_result(data: Any) -> dict:
    normalized = normalize_moscow_result(data)
    serializer = MoscowScopeResultSerializer(data=normalized)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as exc:
        raise MoscowGenerationError("AI response failed MoSCoW validation.") from exc
    return dict(serializer.validated_data)


@transaction.atomic
def save_moscow_analysis(idea, result: dict, *, provider: str = "", model_name: str = ""):
    analysis, _ = MoscowScopeAnalysis.objects.update_or_create(
        idea=idea,
        defaults={
            "result": result,
            "prompt_version": PROMPT_VERSION,
            "provider": provider,
            "model_name": model_name,
        },
    )
    return analysis


def generate_moscow_scope(idea, client: MoscowClient | None = None):
    client = client or OpenAICompatibleClient.from_settings()
    prompt = build_moscow_prompt(idea)
    last_error = None
    for _attempt in range(2):
        try:
            try:
                response = client.complete(prompt)
            except MoscowGenerationError:
                raise
            except Exception as exc:
                raise MoscowGenerationError("AI provider request failed.") from exc
            result = parse_and_validate_moscow_result(response)
            return save_moscow_analysis(
                idea,
                result,
                provider=getattr(client, "provider", ""),
                model_name=getattr(client, "model_name", ""),
            )
        except MoscowGenerationError as exc:
            last_error = exc
    raise MoscowGenerationError("Unable to generate a valid MoSCoW scope.") from last_error
