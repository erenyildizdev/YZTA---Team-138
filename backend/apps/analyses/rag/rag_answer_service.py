from dataclasses import dataclass

from apps.analyses.rag.retriever import (
    format_rag_context,
    retrieve_context,
)
from apps.analyses.services.llm_client import call_rag_llm


@dataclass(frozen=True)
class RagSource:
    title: str
    source_type: str
    source_url: str | None
    chunk_id: int
    chunk_index: int
    distance: float
    content: str


@dataclass(frozen=True)
class RagAnswer:
    answer: str
    sources: list[RagSource]

def build_prompt(
    question: str,
    rag_context: str,
) -> str:
    return f"""
Sen girişimcilik ve ürün doğrulama konusunda uzman bir asistansın.

SADECE aşağıdaki bilgi kaynaklarını kullan.

Eğer cevap kaynaklarda yoksa
"Bunu verilen kaynaklarda bulamadım."
de.

------------------------
KAYNAKLAR

{rag_context}

------------------------

KULLANICI SORUSU

{question}

------------------------

Türkçe cevap ver.

Önce soruyu cevapla.

En sonda kullandığın kaynakları tekrar etme.

Yanıt kuralları:

- Soruyu doğrudan ve odaklı biçimde yanıtla.
- Kaynaklarda yer alsa bile soruyla doğrudan ilgili olmayan ek konulara geçme.
- Kullanıcının verdiği sınırlı veriden kesin sonuç çıkarma.
- Kanıt yetersizse "kesin olarak söylenemez", "tek başına yeterli değildir"
  veya "güçlü/zayıf bir sinyal" gibi ihtiyatlı ifadeler kullan.
- Erken ilgi, problem doğrulaması, çözüm doğrulaması ve ürün-pazar uyumunu
  birbirinden ayır.
- Kaynaklar belirli bir ayrım veya yöntem sunmuyorsa bunu açıkça belirt.
- Cevabı profesyonel, sade ve akıcı Türkçe ile yaz.
- Kaynaklardaki konuşma dili, dolgu ifadeleri ve hitapları cevaba taşıma.


""".strip()


def answer_with_rag(
    question: str,
    limit: int = 4,
) -> RagAnswer:
    chunks = retrieve_context(
        query=question,
        limit=limit,
    )

    rag_context = format_rag_context(chunks)

    prompt = build_prompt(
        question=question,
        rag_context=rag_context,
    )

    answer = call_rag_llm(prompt)

    return RagAnswer(
        answer=answer,
        sources=[
            RagSource(
                title=chunk.source_title,
                source_type=chunk.source_type,
                source_url=chunk.source_url,
                chunk_id=chunk.chunk_id,
                chunk_index=chunk.chunk_index,
                distance=chunk.distance,
                content=chunk.content,
            )
            for chunk in chunks
        ],
    )