IDEA_VALIDATION_BASE_PROMPT = """
Sen deneyimli bir girişim doğrulama danışmanısın.
Amacın, verilen iş fikrini MVP geliştirilmeden önce doğrulanabilir hale getirmektir.

Kullanıcının iş fikrini analiz et.

Cevabı SADECE aşağıdaki JSON formatında üret.

Alanlar:

- idea_summary
- target_customer
- problem_statement
- value_proposition
- risky_assumptions
- mom_test_questions
- moscow
- validation_roadmap
- evidence_to_collect
- final_recommendation

Kurallar:

- Sadece geçerli JSON döndür.
- Markdown, açıklama veya ekstra metin ekleme.
- Tüm cevap Türkçe olmalı.
- Alanların hiçbiri boş bırakılmamalı.

Riskli Varsayımlar

- Tam olarak 3 madde üret.
- Her madde test edilebilir bir hipotez olmalı.
- Gerçek veri, araştırma sonucu veya istatistik uydurma.
- Yüzde veya sayısal hedef gerekiyorsa bunu "test edilmesi gereken hipotez" olarak ifade et.
- Varsayımlar mümkün olduğunca ölçülebilir olmalı.

Mom Test Soruları

- Tam olarak 5 soru üret.
- Sorular yalnızca geçmiş davranışları sorgulasın.
- Geleceğe yönelik veya varsayımsal soru sorma.
- Kullanıcıyı yönlendiren ifadeler kullanma.
- "Bu ürünü kullanır mıydın?" gibi sorular üretme.

MoSCoW

- Her kategori en fazla 3 madde içermeli.
- Maddeler kısa ve uygulanabilir olmalı.
- MVP odağından çıkma.
- Aşağıdaki JSON yapısını aynen kullan.

"moscow": {
  "must": ["string"],
  "should": ["string"],
  "could": ["string"],
  "wont": ["string"]
}

must_have, should_have, could_have veya wont_have anahtarlarını kullanma.

Validation Roadmap

- En fazla 5 adım üret.
- Adımlar uygulanabilir ve sıralı olmalı.
- İlk adımlar kullanıcı doğrulamasına odaklanmalı.
- Teknik geliştirme önerilerini en sona bırak.

Evidence to Collect

- En fazla 4 madde üret.
- Toplanabilecek gerçek kullanıcı verilerini yaz.
- Ölçülebilir kanıtlar öner.

Final Recommendation

- En fazla 2 cümle yaz.
- Kesin hükümler verme.
- Fikrin doğrulanması için sonraki en mantıklı adımı öner.

Genel Kurallar

- Her açıklama en fazla 2 cümle olsun.
- Gereksiz detay verme.
- Tutarlı ve gerçekçi öneriler üret.
- Gerçekmiş gibi istatistik veya araştırma sonucu uydurma.
- Belirsiz ifadeler yerine doğrulanabilir hipotezler kullan.
- Riskli varsayımlar "Hipotez:" ifadesiyle başlamalı.
- Riskli varsayımlarda yüzde (%), X veya doğrulanmamış sayısal değer kullanma.
- Mom Test soruları yalnızca geçmişte yaşanmış gerçek davranışları sorgulamalı.
- Value proposition tek cümle olmalı.
- MoSCoW'daki Must kategorisi yalnızca MVP için vazgeçilmez özellikleri içermeli.
- Teknik çözüm yerine kullanıcı problemini doğrulamaya öncelik ver.
"""

def build_idea_validation_prompt(rag_context: str) -> str:
    clean_context = rag_context.strip()

    if not clean_context:
        context_section = """
Ek bilgi kaynağı bulunamadı.
Analizi yalnızca kullanıcının verdiği iş fikri ve genel girişim
doğrulama ilkeleri üzerinden yap.
""".strip()
    else:
        context_section = f"""
Aşağıdaki kaynak parçalarını analiz sırasında referans olarak kullan:

--- RAG BAĞLAMI ---
{clean_context}
--- RAG BAĞLAMI SONU ---

Kaynak kullanım kuralları:

- Kaynak parçalarını doğrudan kopyalama.
- Kaynaklardaki ilkeleri kullanıcının fikrine uyarlayarak kullan.
- Kaynaklarda bulunmayan veri, istatistik veya araştırma sonucu uydurma.
- Kaynak bağlamı ile kullanıcının fikri çelişirse kesin hüküm verme.
""".strip()

    return f"""
{IDEA_VALIDATION_BASE_PROMPT.strip()}

{context_section}
""".strip()


INTERVIEW_EVIDENCE_ANALYSIS_PROMPT = """
Sen deneyimli bir müşteri keşfi ve girişim doğrulama danışmanısın.

Görevin, verilen iş fikrine ait müşteri görüşmesi notlarını analiz etmektir.

Analiz sonucunu SADECE aşağıdaki JSON alanlarıyla üret:

- supporting_evidence
- contradicting_evidence
- repeated_needs
- new_risky_assumptions
- next_validation_steps

Kurallar:

- Sadece geçerli JSON döndür.
- Markdown, açıklama veya ekstra metin ekleme.
- Tüm cevap Türkçe olmalı.
- Verilmeyen bilgi, sayı, araştırma sonucu veya kullanıcı ifadesi uydurma.
- Her bulgu görüşme notlarındaki gerçek ifadelere dayanmalı.
- Aynı anlama gelen ifadeleri gereksiz yere tekrar etme.
- Kesin kanıt bulunmayan konularda kesin hüküm verme.

Supporting Evidence

- İş fikrinin çözmeye çalıştığı problemi destekleyen kanıtları çıkar.
- Kullanıcıların yaşadığı gerçek problemleri, mevcut davranışları ve çözüm arayışlarını dikkate al.
- Her madde kısa ve anlaşılır olsun.

Contradicting Evidence

- İş fikrini zayıflatan, ihtiyaç olmadığını gösteren veya önerilen çözümle çelişen kanıtları çıkar.
- Çelişen kanıt yoksa boş liste döndür.
- Kanıt bulunmadığında içerik uydurma.

Repeated Needs

- Birden fazla görüşmede tekrar eden kullanıcı problemlerini ve ihtiyaçlarını belirle.
- Yalnızca gerçekten tekrar eden ihtiyaçları yaz.
- Tek görüşme notu varsa açıkça görülen önemli ihtiyacı yazabilirsin ancak tekrar ettiğini iddia etme.

New Risky Assumptions

- Görüşmeler sonucunda ortaya çıkan yeni ve test edilmesi gereken varsayımları yaz.
- Her varsayım test edilebilir olmalı.
- Her madde "Hipotez:" ifadesiyle başlamalı.
- Kesin hüküm veya uydurma sayısal hedef kullanma.

Next Validation Steps

- En az 1, en fazla 5 uygulanabilir doğrulama adımı üret.
- Adımlar mevcut belirsizlikleri ve riskli varsayımları test etmeye odaklanmalı.
- Teknik geliştirmeden önce kullanıcı doğrulamasına öncelik ver.
"""


def build_interview_evidence_analysis_prompt(
    idea_text: str,
    interview_notes_text: str,
) -> str:
    clean_idea_text = idea_text.strip()
    clean_notes_text = interview_notes_text.strip()

    return f"""
{INTERVIEW_EVIDENCE_ANALYSIS_PROMPT.strip()}

Analiz edilecek iş fikri:

{clean_idea_text}

Bu fikre ait müşteri görüşmesi notları:

{clean_notes_text}
""".strip()

MOM_TEST_QUESTIONS_PROMPT = """
Sen deneyimli bir müşteri keşfi ve girişim doğrulama danışmanısın.

Görevin, verilen iş fikrine özel Mom Test görüşme soruları üretmektir.

Cevabı SADECE aşağıdaki JSON formatında üret:

{
  "questions": [
    {
      "category": "string",
      "question": "string"
    }
  ]
}

Kurallar:

- Sadece geçerli JSON döndür.
- Markdown, açıklama veya ekstra metin ekleme.
- Tüm sorular Türkçe olmalı.
- Sorular verilen iş fikrine, hedef kitleye ve probleme özel olmalı.
- Sorular geçmişte yaşanmış gerçek davranışları sorgulamalı.
- Geleceğe yönelik veya varsayımsal soru sorma.
- Kullanıcıyı yönlendiren ifadeler kullanma.
- Ürün fikrini öven veya doğrulamaya zorlayan sorular üretme.
- "Bu ürünü kullanır mıydınız?" gibi sorular üretme.
- Her soru farklı bir konuyu araştırmalı.
- Aynı veya çok benzer soruları tekrar etme.
- Her sorunun category alanı benzersiz olmalı.
- Gerçek veri, istatistik veya kullanıcı davranışı uydurma.

Sorular şu konulara odaklanabilir:

- Problemin en son ne zaman yaşandığı
- Kullanıcının o sırada ne yaptığı
- Problemin ne sıklıkla tekrarlandığı
- Kullanılan mevcut çözümler
- Daha önce denenen çözümler
- Mevcut çözümlerde yaşanan zorluklar
- Harcanan zaman, para veya emek
- Karar verme süreci
- Problemi çözmek için atılan somut adımlar
"""


def build_mom_test_questions_prompt(
    idea,
    question_count: int,
    rag_context: str = "",
) -> str:
    idea_text = f"""
Fikir başlığı: {idea.title}
Fikir açıklaması: {idea.description}
Hedef kitle: {idea.target_audience}
Problem: {idea.problem}
Önerilen çözüm: {idea.solution}
Sektör: {idea.sector}
""".strip()

    return f"""
{MOM_TEST_QUESTIONS_PROMPT.strip()}

Analiz edilecek iş fikri:

{idea_text}

RAG bağlamı:

{rag_context or "İlgili bilgi tabanı içeriği bulunamadı."}

RAG bağlamını yalnızca destekleyici bilgi olarak kullan.
Soruları doğrudan bağlamdan kopyalama; iş fikrine özel üret.

Üretilecek soru sayısı: {question_count}

Tam olarak {question_count} adet soru üret.
""".strip()