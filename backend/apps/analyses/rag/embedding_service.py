import logging

from django.conf import settings
from google import genai
from google.genai import errors, types

logger = logging.getLogger(__name__)


class EmbeddingServiceError(Exception):
    """Base exception for embedding service errors."""


class EmbeddingConfigurationError(EmbeddingServiceError):
    """Raised when Gemini embedding configuration is missing."""


class EmbeddingRequestError(EmbeddingServiceError):
    """Raised when an embedding request fails."""


class EmbeddingResponseError(EmbeddingServiceError):
    """Raised when Gemini returns an invalid embedding response."""


def _get_client() -> genai.Client:
    api_key = getattr(settings, "GEMINI_API_KEY", "")

    if not api_key:
        raise EmbeddingConfigurationError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=120_000,
        ),
    )


def _embed_text(
    text: str,
    task_type: str,
) -> list[float]:
    clean_text = text.strip()

    if not clean_text:
        raise EmbeddingRequestError(
            "Embedding text cannot be empty."
        )

    client = _get_client()

    model_name = getattr(
        settings,
        "GEMINI_EMBEDDING_MODEL_NAME",
        "gemini-embedding-001",
    )

    try:
        response = client.models.embed_content(
            model=model_name,
            contents=clean_text,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=768,
            ),
        )

    except errors.ClientError as exc:
        status_code = getattr(exc, "status_code", None)

        if status_code in (401, 403):
            raise EmbeddingConfigurationError(
                "Gemini embedding authentication failed."
            ) from exc

        if status_code == 429:
            raise EmbeddingRequestError(
                "Gemini embedding usage limit has been reached."
            ) from exc

        logger.exception(
            "Gemini rejected the embedding request."
        )

        raise EmbeddingRequestError(
            "The embedding request was rejected."
        ) from exc

    except errors.ServerError as exc:
        logger.exception(
            "Gemini embedding server error."
        )

        raise EmbeddingRequestError(
            "The embedding service is temporarily unavailable."
        ) from exc

    except EmbeddingServiceError:
        raise

    except Exception as exc:
        logger.exception(
            "Unexpected Gemini embedding error."
        )

        raise EmbeddingRequestError(
            "An unexpected embedding service error occurred."
        ) from exc

    embeddings = getattr(response, "embeddings", None)

    if not embeddings:
        raise EmbeddingResponseError(
            "Gemini returned an empty embedding response."
        )

    values = getattr(embeddings[0], "values", None)

    if not values:
        raise EmbeddingResponseError(
            "Gemini returned an invalid embedding."
        )

    embedding = list(values)

    if len(embedding) != 768:
        raise EmbeddingResponseError(
            f"Expected a 768-dimensional embedding, "
            f"but received {len(embedding)} dimensions."
        )

    return embedding


def embed_document(text: str) -> list[float]:
    """
    Generates an embedding for a source document chunk.
    """

    return _embed_text(
        text=text,
        task_type="RETRIEVAL_DOCUMENT",
    )


def embed_query(text: str) -> list[float]:
    """
    Generates an embedding for a user query or business idea.
    """

    return _embed_text(
        text=text,
        task_type="RETRIEVAL_QUERY",
    )