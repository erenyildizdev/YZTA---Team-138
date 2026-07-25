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