import type { ChatMessage, IdeaCard, RiskLevel } from "../types";

/* ─── Sample data ─── */
export const sampleIdeas: IdeaCard[] = [
  {
    id: "1",
    title: "Restoran Stok Yönetim Uygulaması",
    description: "Küçük ve orta ölçekli restoranlar için AI destekli stok takip ve sipariş optimizasyonu",
    sector: "F&B Teknolojisi",
    targetAudience: "Restoran sahipleri",
    status: "complete",
    date: "28 Haz 2025",
  },
  {
    id: "2",
    title: "Freelancer Proje Takip Platformu",
    description: "Bağımsız çalışanların projelerini, faturalarını ve müşteri ilişkilerini tek yerden yönetmesi",
    sector: "SaaS / Prodüktivite",
    targetAudience: "Freelancer'lar",
    status: "complete",
    date: "24 Haz 2025",
  },
  {
    id: "3",
    title: "Online Ders Takip Asistanı",
    description: "Üniversite öğrencilerinin ders, ödev ve sınav tarihlerini takip etmesi için AI asistan",
    sector: "EdTech",
    targetAudience: "Üniversite öğrencileri",
    status: "draft",
    date: "20 Haz 2025",
  },
];

export const analysisData = {
  summary:
    "Restoran Stok Yönetim Uygulaması, küçük ve orta ölçekli restoranların manuel stok takibinden kaynaklanan israf ve operasyonel verimsizliklerini çözmek için geliştirilmiş AI destekli bir SaaS çözümüdür. Hedef kullanıcılar, günlük 50–300 müşteriye hizmet veren, teknolojiye açık ancak karmaşık çözümlerden kaçınan restoran sahipleri ve şefleridir.",
  risks: [
    { id: 1, text: "Restoran sahiplerinin yeni bir yazılım benimseme motivasyonu yeterince yüksek olmayabilir.", level: "high" as RiskLevel },
    { id: 2, text: "Mevcut POS sistemleriyle entegrasyon teknik açıdan karmaşık ve maliyetli olabilir.", level: "high" as RiskLevel },
    { id: 3, text: "Aylık abonelik modeli, restoran sahiplerinin peşin ödeme alışkanlıklarıyla çelişebilir.", level: "medium" as RiskLevel },
    { id: 4, text: "AI tahminlerinin doğruluğu ilk aylarda yetersiz kalabilir ve güvensizliğe yol açabilir.", level: "medium" as RiskLevel },
    { id: 5, text: "Mobil uygulama geliştirme ve bakım maliyetleri başlangıçta yüksek olabilir.", level: "low" as RiskLevel },
  ],
  questions: [
    "Şu anda stok takibini nasıl yapıyorsunuz? Hangi araçları kullanıyorsunuz?",
    "Stok yönetimi nedeniyle ayda yaklaşık ne kadar israf yaşıyorsunuz?",
    "Yeni bir uygulama öğrenmek için ne kadar zaman ayırabilirsiniz?",
    "Mevcut POS sisteminizle entegre çalışan bir çözüm sizin için önemli mi?",
    "Bu tür bir sorun için aylık ne kadar ödeme yapmayı kabul edersiniz?",
    "En büyük stok yönetimi sorunsalınız nedir?",
  ],
  mvp: {
    mustHave: ["Günlük stok girişi ve çıkışı takibi", "Kritik stok seviyesi uyarıları", "Tedarikçi sipariş listesi oluşturma", "Basit israf raporu"],
    shouldHave: ["POS sistemi entegrasyonu", "AI tabanlı haftalık tahmin", "Mobil uygulama", "Çoklu kullanıcı desteği"],
    couldHave: ["Tedarikçi fiyat karşılaştırma", "Sezonluk talep analizi", "WhatsApp bildirim entegrasyonu", "Menü maliyet hesaplayıcı"],
    wontHave: ["Muhasebe sistemi entegrasyonu", "Franchising çoklu şube yönetimi", "Blockchain tedarik zinciri takibi"],
  },
  roadmap: [
    { step: 1, title: "Hedef kitleyi netleştir", description: "İstanbul'da 10–15 küçük restoran sahibiyle yüz yüze görüş", weeks: "Hafta 1–2" },
    { step: 2, title: "5 kullanıcıyla derinlemesine görüş", description: "Mevcut stok süreçlerini, acı noktaları ve ödeme istekliliğini anla", weeks: "Hafta 2–3" },
    { step: 3, title: "En riskli varsayımı test et", description: "Sahiplerin manuel süreçten vazgeçmeye hazır olup olmadığını doğrula", weeks: "Hafta 3–4" },
    { step: 4, title: "Basit MVP prototipi hazırla", description: "Sadece stok girişi ve uyarı özelliğiyle minimal bir web arayüzü", weeks: "Hafta 5–8" },
    { step: 5, title: "Geri bildirimlere göre fikri güncelle", description: "3 pilot restoran ile beta test, iteratif iyileştirme", weeks: "Hafta 9–12" },
  ],
  evaluation: {
    strengths: ["Net problem ve ölçülebilir israf maliyeti", "Tekrar eden gelir modeli (SaaS abonelik)", "Pazar büyük ve büyük ölçüde dijitalleşmemiş"],
    uncertainties: ["Müşteri edinme maliyeti ve kanalları belirsiz", "AI tahmin doğruluğu için yeterli veri toplanması zaman alabilir"],
    nextAction: "Bu hafta İstanbul Fatih ve Beyoğlu'nda 5 küçük restoran sahibiyle ön görüşme planla. Özellikle mevcut stok kaybı miktarını somut rakamlarla öğren.",
  },
};

export const initialMessages: ChatMessage[] = [
  {
    id: "1",
    role: "assistant",
    content: "Merhaba! Restoran Stok Yönetim Uygulaması fikrin üzerinde çalışmaya hazırım. Hedef kitleyi, MVP kapsamını, riskleri veya müşteri sorularını güncelleyebilirim.",
    timestamp: "10:30",
  },
  {
    id: "2",
    role: "user",
    content: "Hedef kitleyi sadece fine dining restoranlar olarak değiştirsek nasıl olur?",
    timestamp: "10:32",
  },
  {
    id: "3",
    role: "assistant",
    content: "Fine dining segmentinde stok değerleri çok daha yüksek (şarap, premium et), bu güçlü bir satış argümanı. Ancak bu segment Türkiye'de oldukça küçük ve yeni teknolojiyi benimsemede daha yavaş hareket ediyor.\n\nAnalizi bu hedefe göre güncelleyebilirim.",
    timestamp: "10:33",
    hasAction: true,
  },
];
