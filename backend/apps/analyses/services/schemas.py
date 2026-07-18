MOCK_ANALYSIS_RESPONSE = {
    "idea_summary": "",
    "target_customer": "Erken aşama girişimci adayları",
    "problem_statement": "Girişimciler fikirlerini doğrulamadan ürün geliştirmeye başlayabiliyor.",
    "value_proposition": "Kullanıcının fikrini daha sistemli ve kanıta dayalı şekilde doğrulamasına yardımcı olur.",
    "risky_assumptions": [
        "Kullanıcılar fikir doğrulama sürecinde yapay zekadan destek almak ister.",
        "Üretilen müşteri görüşme soruları sahada kullanılabilir.",
        "Kullanıcılar MVP kapsamını daraltmaya istekli olur."
    ],
    "mom_test_questions": [
        "Son kez bir iş fikrini doğrulamaya çalıştığında nasıl ilerledin?",
        "Bu süreçte en çok nerede zorlandın?",
        "Şu anda bu problemi çözmek için hangi yöntemleri kullanıyorsun?"
    ],
    "moscow": {
        "must": ["Fikir girişi", "Riskli varsayım analizi", "Müşteri görüşme soruları"],
        "should": ["Doğrulama yol haritası"],
        "could": ["Final validasyon raporu"],
        "wont": ["Tam otomatik pazar araştırması"]
    },
    "validation_roadmap": [
        "Hedef kullanıcı segmentini belirle.",
        "En riskli 3 varsayımı seç.",
        "10 müşteri görüşmesi yap.",
        "Görüşme notlarını kaydet.",
        "Toplanan kanıtlara göre fikri yeniden değerlendir."
    ],
    "evidence_to_collect": [
        "Müşteri görüşme notları",
        "Kullanıcıların mevcut çözüm yöntemleri",
        "Ödeme istekliliği sinyalleri"
    ],
    "final_recommendation": "Fikir ürüne dönüştürülmeden önce müşteri görüşmeleriyle doğrulanmalıdır."
}