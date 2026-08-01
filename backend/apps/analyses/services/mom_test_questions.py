from apps.analyses.services.llm_client import (
    LLMClientError,
    LLMResponseError,
    call_mom_test_llm,
)
from apps.analyses.services.prompts import (
    build_mom_test_questions_prompt,
)

from apps.ideas.rag_context import get_idea_rag_context

QUESTION_TEMPLATES = (
    {
        "category": "problem_context",
        "question": "Bu problemle en son ne zaman karşılaştınız?",
    },
    {
        "category": "recent_example",
        "question": "En son yaşadığınız durumu baştan sona anlatabilir misiniz?",
    },
    {
        "category": "past_behavior",
        "question": "O durumda ilk olarak ne yaptınız?",
    },
    {
        "category": "frequency",
        "question": "Son bir ay içinde bu problem kaç kez tekrarlandı?",
    },
    {
        "category": "current_alternatives",
        "question": "Şu anda bu problemi çözmek için hangi yöntemleri veya araçları kullanıyorsunuz?",
    },
    {
        "category": "attempted_solutions",
        "question": "Daha önce hangi çözümleri denediniz ve sonuç ne oldu?",
    },
    {
        "category": "dissatisfaction",
        "question": "Mevcut çözümünüzün en çok hangi kısmı sizi zorluyor?",
    },
    {
        "category": "cost_and_effort",
        "question": "Bu problemi çözmek size ne kadar zaman, para veya emek harcatıyor?",
    },
    {
        "category": "decision_process",
        "question": "Yeni bir çözüm ararken kararı kim veriyor ve hangi ölçütlere bakılıyor?",
    },
    {
        "category": "commitment_signal",
        "question": "Bu problemi çözmek için yakın zamanda attığınız somut bir adım oldu mu?",
    },
)


def generate_mom_test_questions(idea, question_count=10):
    if question_count < 8 or question_count > len(QUESTION_TEMPLATES):
        raise ValueError(
            "question_count must be between 8 and 10."
        )
        
    rag_context, _ = get_idea_rag_context(
        idea,
        purpose=(
            "Mom Test müşteri görüşmeleri, geçmiş davranışlar, "
            "problem doğrulama ve kullanıcı içgörüsü"
        ),
    )
    
    prompt = build_mom_test_questions_prompt(
        idea=idea,
        question_count=question_count,
        rag_context=rag_context,
    )

    try:
        result = call_mom_test_llm(prompt)
        questions = result.get("questions", [])

        if len(questions) != question_count:
            raise LLMResponseError(
                "Gemini returned an unexpected number of "
                "Mom Test questions."
            )

        categories = []
        normalized_questions = []

        for item in questions:
            category = item["category"].strip()
            question = item["question"].strip()

            if not category or not question:
                raise LLMResponseError(
                    "Mom Test questions cannot contain "
                    "empty fields."
                )

            categories.append(category)
            normalized_questions.append(
                {
                    "category": category,
                    "question": question,
                }
            )

        if len(set(categories)) != len(categories):
            raise LLMResponseError(
                "Mom Test question categories must be unique."
            )

        question_texts = [
            item["question"]
            for item in normalized_questions
        ]

        if len(set(question_texts)) != len(question_texts):
            raise LLMResponseError(
                "Mom Test questions must be unique."
            )

        return normalized_questions

    except LLMClientError:
        return [
            dict(question)
            for question in QUESTION_TEMPLATES[:question_count]
        ]
