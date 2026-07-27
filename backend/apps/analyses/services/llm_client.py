import json
import logging
import time
from typing import Any

from django.conf import settings
from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)


class LLMClientError(Exception):
    """Base exception for all LLM client errors."""


class LLMConfigurationError(LLMClientError):
    """Raised when required Gemini configuration is missing or invalid."""


class LLMRequestError(LLMClientError):
    """Raised when the Gemini API request cannot be completed."""


class LLMResponseError(LLMClientError):
    """Raised when Gemini returns an invalid or empty response."""


IDEA_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "idea_summary": {
            "type": "string",
        },
        "target_customer": {
            "type": "string",
        },
        "problem_statement": {
            "type": "string",
        },
        "value_proposition": {
            "type": "string",
        },
        "risky_assumptions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "mom_test_questions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "moscow": {
            "type": "object",
            "properties": {
                "must": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "should": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "could": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "wont": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
            },
            "required": [
                "must",
                "should",
                "could",
                "wont",
            ],
            "additionalProperties": False,
        },
        "validation_roadmap": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "evidence_to_collect": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "final_recommendation": {
            "type": "string",
        },
    },
    "required": [
        "idea_summary",
        "target_customer",
        "problem_statement",
        "value_proposition",
        "risky_assumptions",
        "mom_test_questions",
        "moscow",
        "validation_roadmap",
        "evidence_to_collect",
        "final_recommendation",
    ],
    "additionalProperties": False,
}

INTERVIEW_EVIDENCE_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "supporting_evidence": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "contradicting_evidence": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "repeated_needs": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "new_risky_assumptions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "next_validation_steps": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "supporting_evidence",
        "contradicting_evidence",
        "repeated_needs",
        "new_risky_assumptions",
        "next_validation_steps",
    ],
    "additionalProperties": False,
}

MOM_TEST_QUESTIONS_SCHEMA = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                    },
                    "question": {
                        "type": "string",
                    },
                },
                "required": [
                    "category",
                    "question",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "questions",
    ],
    "additionalProperties": False,
}

def _get_client() -> genai.Client:
    api_key = getattr(settings, "GEMINI_API_KEY", "")

    if not api_key:
        raise LLMConfigurationError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=120_000,
        ),
    )


def _build_contents(prompt: str, idea_text: str) -> str:
    clean_prompt = prompt.strip()
    clean_idea_text = idea_text.strip()

    if not clean_prompt:
        raise LLMConfigurationError(
            "The analysis prompt cannot be empty."
        )

    if not clean_idea_text:
        raise LLMRequestError(
            "Idea text cannot be empty."
        )

    return f"""
{clean_prompt}

Analiz edilecek iş fikri:

{clean_idea_text}
""".strip()

def _normalize_result(result: dict) -> dict:
    moscow = result.get("moscow")

    if not isinstance(moscow, dict):
        return result

    key_mapping = {
        "must_have": "must",
        "should_have": "should",
        "could_have": "could",
        "wont_have": "wont",
    }

    normalized_moscow = {}

    for key, value in moscow.items():
        normalized_key = key_mapping.get(key, key)
        normalized_moscow[normalized_key] = value

    result["moscow"] = normalized_moscow

    return result


def _parse_response(response: Any) -> dict:
    response_text = getattr(response, "text", None)

    if not response_text:
        raise LLMResponseError(
            "Gemini returned an empty response."
        )

    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as exc:
        logger.exception(
            "Gemini response could not be parsed as JSON."
        )
        raise LLMResponseError(
            "Gemini returned invalid JSON."
        ) from exc

    if not isinstance(result, dict):
        raise LLMResponseError(
            "Gemini response must be a JSON object."
        )

    return _normalize_result(result)


def call_llm(prompt: str, idea_text: str) -> dict:
    client = _get_client()

    contents = _build_contents(
        prompt=prompt,
        idea_text=idea_text,
    )

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    max_output_tokens=2048,
                ),
            )

            return _parse_response(response)

        except errors.ClientError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code in (401, 403):
                logger.exception(
                    "Gemini API authentication failed."
                )
                raise LLMConfigurationError(
                    "Gemini API authentication failed."
                ) from exc

            if status_code == 429:
                logger.exception(
                    "Gemini API usage limit was reached."
                )
                raise LLMRequestError(
                    "Gemini usage limit has been reached. "
                    "Please try again later."
                ) from exc

            logger.exception(
                "Gemini rejected the request."
            )
            raise LLMRequestError(
                "The Gemini request was rejected."
            ) from exc

        except errors.ServerError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code == 504 and attempt < max_attempts:
                wait_seconds = 2 ** attempt

                logger.warning(
                    "Gemini request timed out. "
                    "Retrying in %s seconds. Attempt %s/%s.",
                    wait_seconds,
                    attempt,
                    max_attempts,
                )

                time.sleep(wait_seconds)
                continue

            logger.exception(
                "Gemini API server error."
            )
            raise LLMRequestError(
                "The AI analysis service is temporarily unavailable."
            ) from exc

        except LLMClientError:
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini API error."
            )
            raise LLMRequestError(
                "An unexpected AI service error occurred."
            ) from exc

    raise LLMRequestError(
        "The AI analysis service could not complete the request."
    )

def call_interview_analysis_llm(prompt: str) -> dict:
    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise LLMConfigurationError(
            "The interview analysis prompt cannot be empty."
        )

    client = _get_client()
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=clean_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_json_schema=INTERVIEW_EVIDENCE_ANALYSIS_SCHEMA,
                    max_output_tokens=2048,
                ),
            )

            result = _parse_response(response)

            required_fields = [
                "supporting_evidence",
                "contradicting_evidence",
                "repeated_needs",
                "new_risky_assumptions",
                "next_validation_steps",
            ]

            for field in required_fields:
                if not isinstance(result.get(field), list):
                    raise LLMResponseError(
                        f"Gemini response field '{field}' must be a list."
                    )

            if not result["next_validation_steps"]:
                result["next_validation_steps"] = [
                    "Mevcut bulguları doğrulamak için yeni müşteri görüşmeleri yap."
                ]

            return result

        except errors.ClientError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code in (401, 403):
                logger.exception(
                    "Gemini API authentication failed."
                )
                raise LLMConfigurationError(
                    "Gemini API authentication failed."
                ) from exc

            if status_code == 429:
                logger.exception(
                    "Gemini API usage limit was reached."
                )
                raise LLMRequestError(
                    "Gemini usage limit has been reached. "
                    "Please try again later."
                ) from exc

            logger.exception(
                "Gemini rejected the interview analysis request."
            )
            raise LLMRequestError(
                "The Gemini interview analysis request was rejected."
            ) from exc

        except errors.ServerError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code == 504 and attempt < max_attempts:
                wait_seconds = 2 ** attempt

                logger.warning(
                    "Gemini interview analysis request timed out. "
                    "Retrying in %s seconds. Attempt %s/%s.",
                    wait_seconds,
                    attempt,
                    max_attempts,
                )

                time.sleep(wait_seconds)
                continue

            logger.exception(
                "Gemini API server error during interview analysis."
            )
            raise LLMRequestError(
                "The AI interview analysis service is temporarily unavailable."
            ) from exc

        except LLMClientError:
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini interview analysis error."
            )
            raise LLMRequestError(
                "An unexpected AI service error occurred."
            ) from exc

    raise LLMRequestError(
        "The AI interview analysis service could not complete the request."
    )

def call_mom_test_llm(prompt: str) -> dict:
    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise LLMConfigurationError(
            "The Mom Test prompt cannot be empty."
        )

    client = _get_client()
    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=clean_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_json_schema=MOM_TEST_QUESTIONS_SCHEMA,
                    max_output_tokens=2048,
                ),
            )

            result = _parse_response(response)

            questions = result.get("questions")

            if not isinstance(questions, list):
                raise LLMResponseError(
                    "Gemini response field 'questions' must be a list."
                )

            if not questions:
                raise LLMResponseError(
                    "Gemini returned no Mom Test questions."
                )

            for question in questions:
                if not isinstance(question, dict):
                    raise LLMResponseError(
                        "Each question must be an object."
                    )

                if (
                    not isinstance(
                        question.get("category"),
                        str,
                    )
                    or not isinstance(
                        question.get("question"),
                        str,
                    )
                ):
                    raise LLMResponseError(
                        "Each question must contain 'category' and 'question'."
                    )

            return result

        except errors.ClientError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code in (401, 403):
                logger.exception(
                    "Gemini API authentication failed."
                )
                raise LLMConfigurationError(
                    "Gemini API authentication failed."
                ) from exc

            if status_code == 429:
                logger.exception(
                    "Gemini API usage limit was reached."
                )
                raise LLMRequestError(
                    "Gemini usage limit has been reached. "
                    "Please try again later."
                ) from exc

            logger.exception(
                "Gemini rejected the Mom Test request."
            )
            raise LLMRequestError(
                "The Gemini Mom Test request was rejected."
            ) from exc

        except errors.ServerError as exc:
            status_code = getattr(exc, "status_code", None)

            if status_code == 504 and attempt < max_attempts:
                wait_seconds = 2 ** attempt

                logger.warning(
                    "Gemini Mom Test request timed out. "
                    "Retrying in %s seconds. Attempt %s/%s.",
                    wait_seconds,
                    attempt,
                    max_attempts,
                )

                time.sleep(wait_seconds)
                continue

            logger.exception(
                "Gemini API server error during Mom Test generation."
            )
            raise LLMRequestError(
                "The AI Mom Test service is temporarily unavailable."
            ) from exc

        except LLMClientError:
            raise

        except Exception as exc:
            logger.exception(
                "Unexpected Gemini Mom Test error."
            )
            raise LLMRequestError(
                "An unexpected AI service error occurred."
            ) from exc

    raise LLMRequestError(
        "The AI Mom Test service could not complete the request."
    )