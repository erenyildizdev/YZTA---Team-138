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
    """Return deterministic The Mom Test questions for an idea."""
    if question_count < 8 or question_count > len(QUESTION_TEMPLATES):
        raise ValueError("question_count must be between 8 and 10.")

    return [dict(question) for question in QUESTION_TEMPLATES[:question_count]]
