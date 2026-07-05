# Sprint 1 Backlog Dağıtma Mantığı

## Genel Yaklaşım

Sprint 1 backlog’u oluşturulurken öncelik, ürünün tüm özelliklerini geliştirmekten ziyade projenin temel altyapısını kurmaya ve sonraki sprintlerde geliştirilecek ana modüller için sağlam bir başlangıç oluşturmaya verilmiştir.

Bu sprintte takım olarak önce ürün fikri, hedef kitle, problem, çözüm ve MVP kapsamı netleştirilmiştir. Daha sonra bu kapsam doğrultusunda teknik olarak ilk geliştirilmesi gereken işler belirlenmiş ve Sprint Board üzerine eklenmiştir.

Backlog dağıtımında temel amaç; Sprint 1 sonunda ürünün temel backend altyapısının hazır hale gelmesi, kullanıcı ve fikir yönetimi süreçlerinin başlatılması ve Sprint 2’de frontend entegrasyonu ile AI analiz akışına geçilebilmesidir.

---

## Önceliklendirme Mantığı

Backlog maddeleri aşağıdaki kriterlere göre önceliklendirilmiştir:

- Ürünün temel akışını başlatmak için gerekli olması
- Sonraki sprintlerde geliştirilecek modüllere altyapı sağlaması
- Takımın mevcut teknik yetkinlikleriyle Sprint 1 içerisinde tamamlanabilir olması
- MVP kapsamına doğrudan katkı sağlaması
- Bağımlılık oluşturan temel işlerden biri olması

Bu nedenle Sprint 1’de öncelik; kullanıcı yönetimi, fikir yönetimi, backend mimarisi, veritabanı model taslağı ve proje dokümantasyonu üzerine verilmiştir.

---

## Sprint 1’e Alınan İşler

Sprint 1’e alınan başlıca işler:

| İş | Öncelik | Gerekçe | Durum |
| -- | ------- | ------- | ----- |
| Proje fikrinin netleştirilmesi | Yüksek | Ürünün problem, çözüm ve hedef kitlesinin belirlenmesi gerekiyordu. | Tamamlandı |
| Takım rollerinin belirlenmesi | Yüksek | Scrum sürecinin sağlıklı ilerleyebilmesi için rol dağılımı gerekliydi. | Tamamlandı |
| Product Backlog oluşturulması | Yüksek | Sprint planlaması ve görev takibi için ana backlog gerekliydi. | Tamamlandı |
| Sprint Board oluşturulması | Yüksek | Görevlerin takip edilebilir olması için board yapısı gerekliydi. | Tamamlandı |
| Lokal geliştirme ortamının kurulması | Yüksek | Ekip üyelerinin projeyi çalıştırabilmesi için gerekliydi. | Tamamlandı |
| Django backend mimarisinin kurulması | Yüksek | Ürünün teknik temelini oluşturduğu için önceliklendirildi. | Tamamlandı |
| Temel veritabanı model taslağının hazırlanması | Yüksek | Fikir ve kullanıcı yönetimi için veri yapısının belirlenmesi gerekiyordu. | Tamamlandı |
| Kullanıcı kayıt/giriş endpointlerinin yazılması | Yüksek | Kullanıcı bazlı fikir yönetimi için kimlik doğrulama altyapısı gerekliydi. | Tamamlandı |
| Fikir CRUD endpointlerinin yazılması | Yüksek | Ürünün temel akışı, kullanıcının fikir ekleyip yönetebilmesine dayanıyordu. | Tamamlandı |
| Django admin panelinin aktif hale getirilmesi | Orta | Geliştirme sürecinde temel veri yönetimi ve kontrol için gerekliydi. | Tamamlandı |
| RAG kaynak araştırmasının başlatılması | Orta | AI analiz kalitesini artırmak için sonraki sprintlere hazırlık yapılması gerekiyordu. | Devam Ediyor |
| Frontend teknoloji seçimi ve proje iskeleti | Orta | Sprint 2’de frontend entegrasyonuna geçilebilmesi için ön hazırlık gerekliydi. | Devam Ediyor |
| Sprint 1 dokümantasyonunun hazırlanması | Yüksek | Sprint sonunda proje yönetimi çıktılarının GitHub üzerinde belgelenmesi gerekiyordu. | Devam Ediyor |

---

## Sprint 1’e Alınmayan / Sonraki Sprintlere Bırakılan İşler

Bazı işler ürün için önemli olsa da Sprint 1 kapsamına alınmamıştır. Bunun sebebi, önce temel backend altyapısının ve ürün kapsamının netleştirilmesi gerektiğidir.

Sprint 2 ve Sprint 3’e bırakılan başlıca işler:

| İş | Planlanan Sprint | Gerekçe |
| -- | ---------------- | ------- |
| Kayıt ve giriş ekranlarının frontend tarafında geliştirilmesi | Sprint 2 | Backend endpointleri tamamlandıktan sonra frontend entegrasyonu yapılacaktır. |
| Fikir ekleme ve listeleme ekranlarının geliştirilmesi | Sprint 2 | Fikir CRUD endpointleri hazırlandıktan sonra arayüz geliştirmesi yapılacaktır. |
| AI destekli temel fikir analizi | Sprint 2 | Önce fikir giriş akışının ve backend yapısının oturması hedeflenmiştir. |
| Riskli varsayım analizi | Sprint 2 | Temel AI analiz akışından sonra geliştirilecektir. |
| Mom Test prensiplerine uygun soru üretimi | Sprint 2 | AI analiz çıktılarıyla birlikte ele alınacaktır. |
| MoSCoW yöntemiyle MVP önceliklendirme | Sprint 2 | Fikir analizi ve varsayım analizi sonrası anlamlı hale gelecektir. |
| Doğrulama yol haritası oluşturma | Sprint 3 | Önce analiz ve önceliklendirme modüllerinin tamamlanması gerekmektedir. |
| Görüşme notu analizi | Sprint 3 | Kullanıcıdan alınacak doğrulama verileri üzerinden geliştirilecektir. |
| Final validasyon raporu | Sprint 3 | Önce analiz, görüşme ve yol haritası çıktılarının tamamlanması gerekmektedir. |
| RAG destekli bilgi katmanı entegrasyonu | Sprint 1-3 | Araştırma Sprint 1’de başlamış olup entegrasyon ilerleyen sprintlerde tamamlanacaktır. |
| Deploy çalışması | Sprint 3 | Ürün daha kararlı hale geldikten sonra ele alınacaktır. |

---

## Sprint Board Kullanımı

Sprint 1 sürecinde görevler GitHub Projects üzerinde takip edilmiştir. Board üzerinde işler aşağıdaki kolonlarla yönetilmiştir:

- Todo
- In Progress
- In Review
- Done

Sprint başlangıcında görevler çoğunlukla Todo kolonunda yer almıştır. Geliştirme süreci ilerledikçe backend mimarisi, kullanıcı/fikir yönetimi endpointleri ve proje dokümantasyonu gibi işler ilgili durumlarına göre güncellenmiştir.

Sprint sonunda tamamlanan işler Done kolonuna taşınmış, devam eden RAG araştırması, frontend teknoloji seçimi ve Sprint 1 dokümantasyonu gibi işler In Progress durumunda bırakılmıştır.

---

## Backlog Dağıtım Sonucu

Sprint 1 sonunda backlog dağıtımı, projenin temel teknik altyapısını kurmaya ve sonraki sprintlerde ürün özelliklerinin geliştirilebilmesine zemin hazırlamaya odaklanmıştır.

Bu yaklaşım sayesinde:

- Ürün fikri ve MVP kapsamı netleşmiştir.
- Backend mimarisi oluşturulmuştur.
- Kullanıcı ve fikir yönetimi için temel endpointler geliştirilmiştir.
- Sprint 2’de frontend entegrasyonu ve AI analiz akışı için gerekli altyapı hazırlanmıştır.
- RAG destekli bilgi katmanı için araştırma süreci başlatılmıştır.

Sprint 2’de backlog daha küçük issue’lara bölünerek frontend entegrasyonu, AI analiz akışı ve RAG araştırmasının ilerletilmesi üzerine yoğunlaşılacaktır.
