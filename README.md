# AI Destekli Fikir Doğrulama Asistanı

## Takım İsmi

TEAM - 138

---

## Takım Üyeleri ve Rolleri

| İsim             | Rol           |
| ---------------- | ------------- |
| Eren Yıldız      | Scrum Master  |
| Sema Yeşilkaya   | Product Owner |
| Semiha Çıtırkı   | Developer     |
| Mücahit Ayyıldız | Developer     |
| Berker Öner      | Developer     |

---

## Ürün İsmi

AI Destekli Fikir Doğrulama Asistanı

---

## Ürün Açıklaması

Bu proje, girişimci adaylarının iş fikirlerini doğrulamasına yardımcı olan AI destekli bir fikir doğrulama panelidir.

Kullanıcı iş fikrini sisteme girer. Sistem bu fikri analiz eder, en riskli varsayımları belirler, müşteri görüşmeleri için doğru sorular üretir, MVP kapsamını daraltır ve kullanıcıya adım adım doğrulama yol haritası sunar.

Bu ürünün amacı, girişimci adaylarının fikirlerini doğrudan ürüne dönüştürmeden önce daha sistemli, ölçülebilir ve kanıta dayalı şekilde doğrulamalarına yardımcı olmaktır.

---

## Ürün Vizyonu

AI Destekli Fikir Doğrulama Asistanı'nın vizyonu, girişimci adaylarının iş fikirlerini yalnızca sezgisel kararlarla değil, sistemli analizler, müşteri içgörüleri ve doğrulama adımlarıyla test edebilecekleri erişilebilir bir karar destek platformu sunmaktır.

Ürün; kullanıcıların fikirlerini daha erken aşamada değerlendirmesine, en riskli varsayımları fark etmesine, doğru müşteri görüşmeleri yapmasına ve MVP kapsamını daha gerçekçi şekilde belirlemesine yardımcı olmayı hedefler.

---

## Problem

Girişimci adayları ve erken aşama ekipler, iş fikirlerini hayata geçirmeden önce çoğu zaman sistemli bir doğrulama süreci yürütememektedir. Fikirler genellikle kişisel sezgilere, çevreden alınan yüzeysel geri bildirimlere veya doğrudan ürün geliştirme isteğine dayanarak ilerlemektedir.

Bu durum; yanlış varsayımlar üzerine ürün geliştirilmesine, müşteri ihtiyacının yeterince anlaşılmamasına, MVP kapsamının gereğinden fazla büyümesine ve zaman/kaynak kaybına neden olmaktadır.

Bu proje kapsamında odaklanılan temel problem; kullanıcıların iş fikirlerindeki en riskli varsayımları belirlemekte, doğru müşteri görüşme soruları hazırlamakta ve fikirlerini kanıta dayalı şekilde doğrulamakta zorlanmalarıdır.

---

## Çözüm

AI Destekli Fikir Doğrulama Asistanı, girişimci adaylarının iş fikirlerini daha sistemli ve kanıta dayalı şekilde değerlendirebilmesi için geliştirilmiş bir doğrulama panelidir.

Kullanıcı iş fikrini sisteme girdikten sonra uygulama, fikri yalnızca genel olarak yorumlamakla kalmaz; fikrin arkasındaki temel varsayımları, potansiyel riskleri, hedef kitleyi ve MVP kapsamını analiz eder.

Sistem; kullanıcıya riskli varsayımlarını gösterir, müşteri görüşmeleri için yönlendirici sorular üretir, MoSCoW yöntemiyle MVP kapsamını daraltmaya yardımcı olur ve doğrulama sürecinde izlenebilecek adımları bir yol haritası halinde sunar.

Bu sayede kullanıcı, fikrini doğrudan geliştirmeye başlamadan önce hangi varsayımları test etmesi gerektiğini, kimlerle görüşmesi gerektiğini ve ilk MVP kapsamında nelere odaklanması gerektiğini daha net görebilir.

---

## Hedef Kitle

AI Destekli Fikir Doğrulama Asistanı'nın ana hedef kitlesi, iş fikrini hayata geçirmeden önce fikrinin uygulanabilirliğini ve müşteri ihtiyacını doğrulamak isteyen erken aşama girişimci adaylarıdır.

Ürün özellikle MVP geliştirme sürecine başlamadan önce hangi varsayımların test edilmesi gerektiğini görmek isteyen bireyler ve küçük ekipler için tasarlanmıştır.

İkincil hedef kitle olarak üniversite öğrencileri, bootcamp ve hackathon katılımcıları, girişimcilik programlarında yer alan ekipler ve proje fikrini daha sistemli bir doğrulama sürecinden geçirmek isteyen kullanıcılar hedeflenmektedir.

---

## Ürün Özellikleri

### Tamamlanan MVP Özellikleri

- Kullanıcı kayıt ve giriş işlemlerinin gerçekleştirilmesi
- JWT tabanlı kullanıcı kimlik doğrulama altyapısının sağlanması
- Kullanıcının yeni bir iş fikrini sisteme ekleyebilmesi
- Kullanıcının kendisine ait iş fikirlerini listeleyebilmesi
- Kullanıcının fikir detaylarını görüntüleyebilmesi
- Kullanıcının eklediği iş fikirlerini güncelleyebilmesi ve silebilmesi
- Girilen iş fikrinin backend tarafında yapay zekâ destekli olarak analiz edilebilmesi
- Kullanıcının hedef kitlesiyle gerçekleştireceği görüşmeler için Mom Test prensiplerine uygun sorular üretilmesi
- İş fikrinin MVP kapsamının MoSCoW yöntemiyle önceliklendirilmesi
- Doğrulama yol haritası üretim servisinin backend tarafında hazırlanması
- Girişimcilik ve fikir doğrulama içeriklerinin kullanılabilmesi için başlangıç seviyesinde RAG retrieval altyapısının hazırlanması
- MoSCoW kapsam analizlerinin veritabanında saklanması ve analiz endpointlerinde kullanıcı sahipliği kontrollerinin gerçekleştirilmesi
- Analiz endpointleri için doğrulama, yetkilendirme ve temel backend testlerinin hazırlanması

### Son Sprint Kapsamındaki Çalışmalar

- Backend tarafından oluşturulan analiz sonuçlarının dashboard kullanıcı arayüzüne entegre edilmesi
- Fikir gönderme, analiz başlatma ve sonuç görüntüleme adımlarının uçtan uca bir kullanıcı akışında birleştirilmesi
- Sprint 2 kapsamında geliştirilen analiz modüllerinin frontend ekranlarında gösterilmesi
- Uçtan uca MVP akışına yönelik temel test senaryolarının hazırlanması
- Kullanıcının daha önce oluşturduğu fikirleri ve analiz sonuçlarını arayüz üzerinden görüntüleyebilmesi
- Ürünün teslim edilebilir ve deploy edilebilir hale getirilmesi
- Son ürün kontrollerinin, hata düzeltmelerinin ve demo hazırlıklarının tamamlanması

### MVP Sonrasında Geliştirilebilecek Özellikler

- Kullanıcının müşteri görüşme notlarını sisteme ekleyebilmesi
- Görüşme notlarından kanıt, içgörü ve tekrar eden problem analizi yapılması
- Kullanıcı geri bildirimlerine göre fikir varsayımlarının güncellenmesi
- Fikrin doğrulama seviyesini gösteren kapsamlı final validasyon raporu oluşturulması
- Analiz sonuçlarının PDF veya paylaşılabilir rapor olarak dışa aktarılması
- Kullanıcıya doğrulama sürecindeki ilerlemesini gösteren takip sistemi sunulması
- RAG bilgi tabanının daha fazla açık kaynak girişimcilik içeriğiyle genişletilmesi

---

## Product Backlog

Product Backlog, ürünün geliştirme sürecinde ihtiyaç duyulan özellikleri ve teknik çalışmaları göstermektedir. İşlerin ayrıntılı takibi GitHub Issues, Milestone ve Project Board üzerinden gerçekleştirilmektedir.

| ID | Backlog Item | Öncelik | Sprint | Durum |
| --- | --- | --- | --- | --- |
| PB-01 | Kullanıcı kayıt ve giriş işlemleri için backend endpointlerinin geliştirilmesi | Yüksek | Sprint 1 | Tamamlandı |
| PB-02 | JWT tabanlı kimlik doğrulama altyapısının hazırlanması | Yüksek | Sprint 1 | Tamamlandı |
| PB-03 | Kullanıcının iş fikri ekleyebilmesi için backend endpointlerinin geliştirilmesi | Yüksek | Sprint 1 | Tamamlandı |
| PB-04 | Kullanıcının kendi fikirlerini listeleyebilmesi ve detaylarını görüntüleyebilmesi | Yüksek | Sprint 1 | Tamamlandı |
| PB-05 | Kullanıcının eklediği fikirleri güncelleyebilmesi ve silebilmesi | Orta | Sprint 1 | Tamamlandı |
| PB-06 | Django Admin üzerinden temel veri yönetiminin sağlanması | Orta | Sprint 1 | Tamamlandı |
| PB-07 | Docker ve PostgreSQL tabanlı geliştirme ortamının hazırlanması | Yüksek | Sprint 1 | Tamamlandı |
| PB-08 | Kullanıcının iş fikrini sisteme gönderebilmesini sağlayan fikir gönderme akışının geliştirilmesi | Yüksek | Sprint 2 | Tamamlandı |
| PB-09 | İş fikirlerinin doğrulanması için yapay zekâ analiz servisinin geliştirilmesi | Yüksek | Sprint 2 | Backend tamamlandı, frontend entegrasyonu Son Sprint'e aktarıldı |
| PB-10 | Mom Test prensiplerine uygun müşteri görüşme sorularının üretilmesi | Yüksek | Sprint 2 | Tamamlandı |
| PB-11 | MVP kapsamının MoSCoW yöntemiyle önceliklendirilmesi | Yüksek | Sprint 2 | Tamamlandı |
| PB-12 | Kullanıcıya fikir doğrulama yol haritası oluşturulması | Yüksek | Sprint 2 | Tamamlandı |
| PB-13 | Girişimcilik içerikleri için başlangıç RAG retrieval altyapısının hazırlanması | Orta | Sprint 2 | Tamamlandı |
| PB-14 | Analiz sonuçlarının dashboard kullanıcı arayüzüne entegre edilmesi | Yüksek | Son Sprint | Son Sprint'e Aktarıldı |
| PB-15 | Fikir gönderme, analiz başlatma ve sonuç görüntüleme adımlarının uçtan uca birleştirilmesi | Yüksek | Son Sprint | Planlandı |
| PB-16 | MVP kullanıcı akışına yönelik temel test senaryolarının hazırlanması | Yüksek | Son Sprint | Planlandı |
| PB-17 | Kullanıcının önceki fikirlerini ve analiz sonuçlarını arayüz üzerinden görüntüleyebilmesi | Orta | Son Sprint | Planlandı |
| PB-18 | Ürünün deploy edilebilir hale getirilmesi | Yüksek | Son Sprint | Planlandı |
| PB-19 | Son ürün kontrollerinin, hata düzeltmelerinin ve demo hazırlıklarının tamamlanması | Yüksek | Son Sprint | Planlandı |
| PB-20 | Kullanıcının müşteri görüşme notlarını sisteme ekleyebilmesi | Orta | MVP Sonrası | Planlandı |
| PB-21 | Görüşme notlarından kanıt ve içgörü analizi yapılması | Orta | MVP Sonrası | Planlandı |
| PB-22 | Kapsamlı final validasyon raporunun oluşturulması | Orta | MVP Sonrası | Planlandı |
| PB-23 | Analiz sonuçlarının PDF veya paylaşılabilir rapor olarak dışa aktarılması | Düşük | MVP Sonrası | Planlandı |

Sprint 2 sonunda backend ve yapay zekâ ağırlıklı analiz özelliklerinin büyük bölümü tamamlanmıştır. Frontend entegrasyonu, uçtan uca kullanıcı akışı, test çalışmaları ve ürünün deploy edilebilir hale getirilmesi Son Sprint'in öncelikli backlog maddeleri olarak belirlenmiştir.
---

## Product Backlog URL

Product Backlog; GitHub Issues, Milestone ve GitHub Projects kullanılarak takip edilmektedir.

Backlog maddelerinin öncelikleri, sprint atamaları, sorumluları ve güncel durumları Project Board üzerinden görüntülenebilir.

URL: <https://github.com/users/erenylldz/projects/2>

---

## Sprint Board URL

Bootcamp süresince planlanan ve geliştirilen çalışmalar GitHub Projects üzerinde takip edilmektedir.

Board üzerinde görevler aşağıdaki durumlara göre yönetilmektedir:

- `Backlog`: Henüz sprint kapsamına alınmamış çalışmalar
- `To Do`: İlgili sprintte yapılması planlanan çalışmalar
- `In Progress`: Geliştirmesi devam eden çalışmalar
- `Done`: Geliştirmesi ve kontrolleri tamamlanan çalışmalar

Tamamlanamayan işler ilgili issue'lara açıklayıcı yorumlar eklenerek sonraki sprintlere aktarılmaktadır. Tamamlanan çalışmalar ise pull request ve test süreçlerinin ardından `Done` durumuna taşınmaktadır.

URL: <https://github.com/users/erenylldz/projects/2>

---

## Kullanılan Teknolojiler

Projenin backend, frontend, yapay zekâ ve geliştirme ortamında kullanılan temel teknolojiler aşağıdaki tabloda gösterilmiştir.

| Alan | Teknoloji / Yaklaşım |
| --- | --- |
| Frontend | React |
| Frontend Geliştirme Aracı | Vite |
| Arayüz ve Stil | Tailwind CSS |
| Backend | Django |
| REST API | Django REST Framework |
| Veritabanı | PostgreSQL |
| Kimlik Doğrulama | JWT ve Django REST Framework SimpleJWT |
| Admin Panel | Django Admin |
| Containerization | Docker ve Docker Compose |
| Yapay Zekâ | OpenAI uyumlu LLM API |
| RAG | Girişimcilik ve fikir doğrulama kaynakları üzerinden retrieval pipeline |
| Test | Django Test Framework |
| Versiyon Kontrolü | Git ve GitHub |
| Proje Yönetimi | GitHub Issues, Milestones ve GitHub Projects |
| Dokümantasyon | Markdown |
| Deployment | Son Sprint kapsamında hazırlanacaktır |

### Teknik Yaklaşım

Backend tarafında modüler ve sürdürülebilir bir yapı oluşturmak amacıyla Django uygulamaları sorumluluklarına göre ayrılmıştır. Kullanıcı işlemleri `users`, iş fikri işlemleri `ideas`, yapay zekâ destekli doğrulama işlemleri ise `analyses` uygulaması üzerinden yönetilmektedir.

API geliştirme süreçlerinde Django REST Framework kullanılmakta, kullanıcı kimlik doğrulama işlemleri JWT tabanlı olarak gerçekleştirilmektedir. Veritabanı olarak ilişkisel veri yapısına uygun olması nedeniyle PostgreSQL tercih edilmiştir.

Yapay zekâ analiz işlemleri doğrudan view katmanında yürütülmek yerine servis katmanı üzerinden gerçekleştirilmektedir. Bu yapı sayesinde LLM bağlantısı, prompt yönetimi, yanıt doğrulama, normalizasyon ve hata yönetimi gibi işlemlerin API katmanından ayrılması hedeflenmiştir.

Frontend tarafında React ve Vite kullanılmaktadır. Kullanıcı arayüzünün geliştirilmesinde Tailwind CSS tercih edilmiştir. Frontend ile backend arasındaki iletişim REST API endpointleri üzerinden sağlanmaktadır.

Projenin farklı geliştirme ortamlarında tutarlı biçimde çalıştırılabilmesi için Docker ve Docker Compose kullanılmaktadır. PostgreSQL veritabanı ve Django backend servisi container yapısı içerisinde çalışacak şekilde yapılandırılmıştır.

---

## Proje Yapısı

Proje; Django tabanlı backend, React tabanlı frontend, yapay zekâ analiz servisleri, RAG altyapısı ve sprint dokümantasyonlarından oluşmaktadır.

```text
.
├── backend/
│   ├── apps/
│   │   ├── analyses/
│   │   │   ├── rag/                 # RAG kaynakları ve retrieval işlemleri
│   │   │   ├── services/            # AI analiz ve doğrulama servisleri
│   │   │   ├── tests/               # Analiz modüllerine ait testler
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # Analiz sonuçlarına ait veri modelleri
│   │   │   ├── serializers.py       # Analiz API serializer'ları
│   │   │   ├── urls.py              # Analiz endpoint tanımları
│   │   │   └── views.py             # Analiz API view'ları
│   │   ├── ideas/
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py            # İş fikri veri modeli
│   │   │   ├── serializers.py       # Fikir API serializer'ları
│   │   │   ├── tests.py             # Fikir işlemlerine ait testler
│   │   │   ├── urls.py
│   │   │   └── views.py             # Fikir CRUD endpointleri
│   │   └── users/
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py            # Özel kullanıcı modeli
│   │       ├── serializers.py       # Kayıt ve kullanıcı serializer'ları
│   │       ├── tests.py             # Kullanıcı işlemlerine ait testler
│   │       ├── urls.py
│   │       └── views.py             # Kayıt ve kimlik doğrulama işlemleri
│   ├── config/
│   │   ├── settings.py              # Django proje ayarları
│   │   ├── urls.py                  # Ana URL yönlendirmeleri
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx              # Ana React uygulama bileşeni
│   │   │   ├── components/
│   │   │   │   ├── common/          # Ortak kullanılan bileşenler
│   │   │   │   ├── figma/           # Tasarımdan uyarlanan bileşenler
│   │   │   │   ├── layout/          # Sayfa düzeni bileşenleri
│   │   │   │   ├── mentor/          # AI mentor bileşenleri
│   │   │   │   └── ui/              # Temel arayüz bileşenleri
│   │   │   ├── data/
│   │   │   │   └── mockData.ts      # Geliştirme sürecindeki örnek veriler
│   │   │   ├── pages/
│   │   │   │   ├── AnalysisPage.tsx
│   │   │   │   ├── DashboardPage.tsx
│   │   │   │   ├── HistoryPage.tsx
│   │   │   │   ├── LoadingPage.tsx
│   │   │   │   ├── MentorPage.tsx
│   │   │   │   └── ReportPage.tsx
│   │   │   └── types/
│   │   │       └── index.ts          # TypeScript tip tanımları
│   │   ├── main.tsx                  # Frontend başlangıç noktası
│   │   └── styles/
│   │       ├── fonts.css
│   │       ├── globals.css
│   │       ├── index.css
│   │       ├── tailwind.css
│   │       └── theme.css
│   ├── guidelines/
│   │   └── Guidelines.md
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   ├── postcss.config.mjs
│   ├── vite.config.ts
│   └── README.md
├── docs/
│   ├── product/                      # Ürün kapsamı ve ürün dokümantasyonu
│   ├── sprint-1/
│   │   ├── screenshots/              # Sprint 1 ekran görüntüleri
│   │   ├── backlog-distribution.md
│   │   ├── daily-scrum.md
│   │   ├── product-status.md
│   │   ├── sprint-board.md
│   │   ├── sprint-review.md
│   │   ├── sprint-retrospective.md
│   │   ├── sprint1-demo.gif
│   │   └── sprint1-demo.webm
│   ├── sprint-2/
│   │   ├── screenshots/
│   │   │   └── sprint-board.png
│   │   └── sprint2-demo.gif
│   └── sprint-3/
├── Dockerfile                       # Django backend container tanımı
├── docker-compose.yml               # Backend ve PostgreSQL servisleri
├── .env.example                     # Ortam değişkenleri için örnek dosya
├── .gitignore
└── README.md
```

`dist/`, `node_modules/`, Python sanal ortamları, `__pycache__`, migration dosyaları ve geçici arşiv dosyaları okunabilirliği korumak amacıyla proje ağacında gösterilmemiştir.

---

## Kurulum

Proje, Django REST Framework tabanlı backend, PostgreSQL veritabanı ve React tabanlı frontend uygulamasından oluşmaktadır.

Backend ve veritabanının çalıştırılması için Docker Compose kullanılması önerilmektedir. Frontend uygulaması ise Vite geliştirme sunucusu üzerinden ayrı olarak çalıştırılmaktadır.

### Gereksinimler

Projeyi çalıştırmak için aşağıdaki araçların sistemde kurulu olması gerekir:

- Git
- Docker
- Docker Compose
- Node.js
- npm

### 1. Repoyu klonlama

```bash
git clone https://github.com/erenylldz/YZTA---Team-138.git
cd YZTA---Team-138
```

### 2. Ortam değişkenlerini hazırlama

Proje kök dizininde bulunan `.env.example` dosyası örnek alınarak `.env` dosyası oluşturulmalıdır.

```bash
cp .env.example .env
```

Oluşturulan `.env` dosyasındaki veritabanı, Django ve yapay zekâ servislerine ait değişkenler geliştirme ortamına göre düzenlenmelidir.

AI destekli analiz özellikleri için kullanılan temel ortam değişkenleri:

```env
AI_API_URL=
AI_API_KEY=
AI_PROVIDER=
AI_MODEL_NAME=
```

Gizli anahtarlar ve gerçek erişim bilgileri GitHub reposuna gönderilmemelidir.

### 3. Backend ve veritabanını çalıştırma

Proje kök dizininde aşağıdaki komut çalıştırılmalıdır:

```bash
docker compose up --build
```

Bu komut Django backend uygulamasını ve PostgreSQL veritabanını başlatır.

Servisleri arka planda çalıştırmak için:

```bash
docker compose up --build -d
```

### 4. Veritabanı migration işlemlerini çalıştırma

Container'lar çalışmaya başladıktan sonra migration işlemleri ayrı bir terminal üzerinden yürütülmelidir:

```bash
docker compose exec web python manage.py migrate
```

### 5. Admin kullanıcısı oluşturma

Django Admin panelini kullanmak için isteğe bağlı olarak superuser oluşturulabilir:

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Frontend bağımlılıklarını yükleme

Yeni bir terminal açılarak frontend klasörüne geçilmelidir:

```bash
cd frontend
npm install
```

### 7. Frontend uygulamasını çalıştırma

```bash
npm run dev
```

Vite geliştirme sunucusu başlatıldıktan sonra terminalde gösterilen bağlantı tarayıcı üzerinden açılabilir.

Frontend varsayılan olarak:

```text
http://localhost:5173/
```

Backend API varsayılan olarak:

```text
http://localhost:8000/
```

Django Admin paneli:

```text
http://localhost:8000/admin/
```

### 8. Servisleri durdurma

Docker servislerini durdurmak için proje kök dizininde:

```bash
docker compose down
```

Veritabanı volume'larını da silerek tamamen temiz bir kurulum yapmak için:

```bash
docker compose down -v
```

> `docker compose down -v` komutu PostgreSQL içerisinde saklanan yerel verileri siler. Bu nedenle yalnızca temiz bir geliştirme ortamı gerektiğinde kullanılmalıdır.

## API Kullanımı

Backend API, varsayılan olarak aşağıdaki temel adres üzerinden çalışmaktadır:

```text
http://localhost:8000/api/
```

Kimlik doğrulama gerektiren endpointlere JWT access token ile istek gönderilmelidir:

```http
Authorization: Bearer <access_token>
```

### Kimlik Doğrulama Endpointleri

| Metot | Endpoint | Açıklama | Kimlik Doğrulama |
| --- | --- | --- | --- |
| `POST` | `/api/auth/register/` | Yeni kullanıcı kaydı oluşturur. | Gerekli değil |
| `POST` | `/api/auth/login/` | Kullanıcı girişi gerçekleştirir ve JWT bilgilerini döndürür. | Gerekli değil |

### İş Fikri Endpointleri

İş fikri işlemleri Django REST Framework `DefaultRouter` ve `IdeaViewSet` üzerinden yönetilmektedir.

| Metot | Endpoint | Açıklama | Kimlik Doğrulama |
| --- | --- | --- | --- |
| `GET` | `/api/ideas/` | Kullanıcının kendisine ait iş fikirlerini listeler. | Gerekli |
| `POST` | `/api/ideas/` | Yeni bir iş fikri oluşturur. | Gerekli |
| `GET` | `/api/ideas/<idea_id>/` | Belirtilen iş fikrinin detaylarını getirir. | Gerekli |
| `PUT` | `/api/ideas/<idea_id>/` | İş fikrinin bütün alanlarını günceller. | Gerekli |
| `PATCH` | `/api/ideas/<idea_id>/` | İş fikrinin belirtilen alanlarını günceller. | Gerekli |
| `DELETE` | `/api/ideas/<idea_id>/` | İş fikrini siler. | Gerekli |

Kullanıcılar yalnızca kendilerine ait fikirler üzerinde işlem yapabilir.

### Yapay Zekâ Fikir Analizi

| Metot | Endpoint | Açıklama | Kimlik Doğrulama |
| --- | --- | --- | --- |
| `POST` | `/api/analyses/analyze/` | Gönderilen iş fikri için yapay zekâ destekli temel analiz oluşturur. | Gerekli |

Bu endpoint, iş fikrinin temel doğrulama analizinin backend tarafında gerçekleştirilmesi için kullanılmaktadır.

### Mom Test Görüşme Soruları

| Metot | Endpoint | Açıklama | Kimlik Doğrulama |
| --- | --- | --- | --- |
| `POST` | `/api/analyses/ideas/<idea_id>/mom-test-questions/` | Belirtilen fikir için Mom Test yaklaşımına uygun müşteri görüşme soruları üretir. | Gerekli |

İstek içerisinde üretilecek soru sayısı belirtilebilir:

```json
{
  "question_count": 10
}
```

`question_count` değeri 8 ile 10 arasında olmalıdır. Değer gönderilmediğinde varsayılan olarak 10 soru üretilir.

Endpoint, yalnızca giriş yapan kullanıcının kendisine ait fikirler için kullanılabilir.

### MoSCoW MVP Kapsam Analizi

| Metot | Endpoint | Açıklama | Kimlik Doğrulama |
| --- | --- | --- | --- |
| `GET` | `/api/analyses/ideas/<idea_id>/moscow-scope/` | Daha önce oluşturulmuş MoSCoW analizini getirir. | Gerekli |
| `POST` | `/api/analyses/ideas/<idea_id>/moscow-scope/` | Fikir için yeni bir MoSCoW kapsam analizi oluşturur veya mevcut analizi yeniler. | Gerekli |

`GET` isteğinde kayıtlı analiz bulunmuyorsa `404 Not Found` yanıtı döndürülür.

`POST` isteği request body gerektirmez. İlk kez oluşturulan analiz için `201 Created`, mevcut analizin yenilenmesi durumunda `200 OK` yanıtı döndürülür.

Örnek yanıt:

```json
{
  "id": 1,
  "idea_id": 5,
  "summary": "MVP temel doğrulama akışına odaklanmalıdır.",
  "must_have": [
    {
      "title": "Fikir girişi",
      "reason": "Analiz için temel fikir bilgilerinin alınması gereklidir."
    }
  ],
  "should_have": [
    {
      "title": "Analiz geçmişi",
      "reason": "Önceki sonuçlarla karşılaştırma yapılmasını kolaylaştırır."
    }
  ],
  "could_have": [
    {
      "title": "PDF çıktısı",
      "reason": "Sonucun paydaşlarla paylaşılmasını kolaylaştırır."
    }
  ],
  "wont_have": [
    {
      "title": "Ödeme sistemi",
      "reason": "İlk MVP değerini test etmek için gerekli değildir."
    }
  ],
  "prompt_version": "moscow-v1",
  "provider": "openai-compatible",
  "model_name": "configured-model"
}
```

MoSCoW endpointi yalnızca kullanıcının kendisine ait fikirler için erişilebilir. Başka bir kullanıcıya ait fikir istendiğinde kaynak bilgisi gizlenerek `404 Not Found` yanıtı döndürülür.

### Yapay Zekâ Servisi Ayarları

Yapay zekâ analiz servisleri OpenAI uyumlu chat completions altyapısını kullanmaktadır.

Gerekli ortam değişkenleri:

```env
AI_API_URL=
AI_API_KEY=
AI_PROVIDER=
AI_MODEL_NAME=
```

Gerçek API anahtarları `.env` dosyasında saklanmalı ve GitHub reposuna gönderilmemelidir.

---

## Geliştirme Ortamı

Proje geliştirme sürecinde backend ve frontend uygulamaları ayrı geliştirme sunucuları üzerinden çalıştırılmaktadır.

Backend tarafında Django ve Django REST Framework, frontend tarafında ise React, TypeScript ve Vite kullanılmaktadır. PostgreSQL veritabanı ile Django backend servisinin Docker Compose üzerinden çalıştırılması önerilmektedir.

### Backend Geliştirme Ortamı

Backend ve PostgreSQL servislerini başlatmak için proje kök dizininde:

```bash
docker compose up --build
```

Servisleri arka planda çalıştırmak için:

```bash
docker compose up --build -d
```

Django sistem kontrollerini çalıştırmak için:

```bash
docker compose exec web python manage.py check
```

Veritabanı migration işlemlerini uygulamak için:

```bash
docker compose exec web python manage.py migrate
```

Backend testlerini çalıştırmak için:

```bash
docker compose exec web python manage.py test
```

Belirli bir uygulamanın testlerini çalıştırmak için:

```bash
docker compose exec web python manage.py test apps.users
docker compose exec web python manage.py test apps.ideas
docker compose exec web python manage.py test apps.analyses
```

Backend uygulaması varsayılan olarak aşağıdaki adreste çalışır:

```text
http://localhost:8000/
```

### Docker Kullanmadan Backend Geliştirme

Backend uygulamasını Docker kullanmadan çalıştırmak için Python sanal ortamı oluşturulabilir.

```bash
python3 -m venv venv
source venv/bin/activate
```

Bağımlılıkları yüklemek için:

```bash
pip install -r backend/requirements.txt
```

Backend dizinine geçerek migration işlemlerini uygulamak ve geliştirme sunucusunu başlatmak için:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Docker kullanılmadan çalıştırıldığında PostgreSQL bağlantısı ve gerekli ortam değişkenleri lokal geliştirme ortamına uygun biçimde yapılandırılmalıdır.

### Frontend Geliştirme Ortamı

Frontend bağımlılıklarını yüklemek için:

```bash
cd frontend
npm install
```

Vite geliştirme sunucusunu başlatmak için:

```bash
npm run dev
```

Frontend uygulaması varsayılan olarak aşağıdaki adreste çalışır:

```text
http://localhost:5173/
```

Üretim için frontend build çıktısı oluşturmak için:

```bash
npm run build
```

Oluşturulan build dosyaları `frontend/dist/` klasöründe yer alır.

### Geliştirme Akışı

Yeni geliştirmeler doğrudan `main` branch üzerinde yapılmamalıdır. Her çalışma için ilgili issue üzerinden ayrı bir branch oluşturulmalı, değişiklikler commit edildikten sonra pull request açılmalıdır.

Geliştirme tamamlanmadan önce aşağıdaki kontroller gerçekleştirilmelidir:

- İlgili issue kapsamındaki gereksinimlerin karşılandığının doğrulanması
- Backend sistem kontrollerinin çalıştırılması
- İlgili backend testlerinin başarıyla tamamlanması
- Frontend build işleminin hatasız tamamlanması
- Ortam değişkenleri ve gizli anahtarların repoya eklenmediğinin kontrol edilmesi
- Project Board ve issue durumlarının güncellenmesi
---

## Sprint Dokümantasyonu

Bootcamp süreci toplam üç sprint üzerinden ilerlemektedir. Her sprint sonunda proje yönetimi süreci, ürün ilerlemesi, takım içi değerlendirmeler ve ortaya çıkan ürün artımı ilgili sprint klasörü altında dokümante edilmektedir.

Sprint dokümantasyonlarında aşağıdaki içeriklere yer verilmektedir:

- Sprint hedefi ve sprint notları
- Sprint backlog dağılımı
- Daily Scrum kayıtları
- Sprint Board güncellemeleri
- Ürün durumu ve demo kayıtları
- Sprint Review
- Sprint Retrospective
- Ekran görüntüleri ve ilerleme kanıtları

Sprint dokümantasyonlarına aşağıdaki bağlantılardan ulaşılabilir:

- [Sprint 1 Dokümantasyonu](docs/sprint-1/)
- [Sprint 2 Dokümantasyonu](docs/sprint-2/)
- [Sprint 3 Dokümantasyonu](docs/sprint-3/)

Her sprintin dokümantasyonu, ekran görüntüleri ve ürün ilerleme kayıtları ilgili sprint klasörü altında saklanmaktadır.

---

## Sprint Sonu Beklenen Dokümanlar

Her sprint sonunda proje yönetimi sürecini, takımın çalışma biçimini ve ürünün geldiği noktayı göstermek amacıyla aşağıdaki başlıklar güncellenmektedir:

- Backlog dağıtma mantığı
- Sprint hedefi ve sprint notları
- Daily Scrum notları
- Sprint Board güncellemeleri
- Ürün durumu
- Sprint Review
- Sprint Retrospective
- Tamamlanan ve sonraki sprinte aktarılan işlerin durumu
- Ürün ekran görüntüleri ve demo kayıtları

Dokümantasyon hazırlanırken GitHub Issues, Milestones, Project Board, pull request'ler ve ürün çıktıları kanıt olarak kullanılmaktadır.

Tamamlanamayan işler ilgili issue'lara açıklayıcı yorumlar eklenerek açık biçimde belirtilmekte ve gerekli olması durumunda sonraki sprinte aktarılmaktadır.

Tüm sprint dokümanları `docs/` klasörü altında, ilgili sprint dizinlerinde tutulmaktadır.

---

## Sprint 1

### Sprint Notları

Sprint 1 sürecinde öncelikli olarak proje fikri netleştirilmiş, takım rolleri belirlenmiş ve ürünün temel kapsamı oluşturulmuştur. Bu sprintte hedef, tüm özellikleri tamamlamak yerine projenin teknik temelini kurmak, backend mimarisini oluşturmak ve sonraki sprintlerde geliştirilecek AI destekli analiz akışları için uygun bir altyapı hazırlamak olmuştur.

Backend tarafında Django mimarisi kurulmuş, kullanıcı kayıt/giriş işlemleri için endpointler hazırlanmıştır. Ayrıca kullanıcıların iş fikirlerini ekleyebildiği, listeleyebildiği, detaylarını görüntüleyebildiği ve silebildiği temel fikir yönetimi endpointleri geliştirilmiştir.

Sprint 1 sonunda admin panel aktif hale getirilmiş, backend tarafındaki ilk geliştirmeler ilgili branch üzerinden GitHub reposuna aktarılmıştır. Frontend tarafında ise kullanıcı kayıt/giriş ekranları ve backend entegrasyonu Sprint 2 kapsamında ele alınacak şekilde planlanmıştır.

Buna ek olarak, ürünün girişimcilik ve fikir doğrulama süreçlerinde daha nitelikli analizler sunabilmesi için RAG destekli bilgi katmanı üzerine kaynak araştırması başlatılmıştır.

### Sprint Hedefi

Sprint 1’in temel hedefi, AI Destekli Fikir Doğrulama Asistanı projesinin ürün kapsamını netleştirmek ve geliştirme süreci için gerekli teknik altyapıyı oluşturmaktır.

Bu sprintte ürünün problem-çözüm yapısı, hedef kitlesi, temel özellikleri ve product backlog’u belirlenmiştir. Teknik tarafta ise Django tabanlı backend mimarisi kurulmuş, kullanıcı yönetimi ve fikir yönetimi için ilk endpointler geliştirilmiştir.

Sprint 1 sonunda hedeflenen ana çıktılar:

- Ürün fikrinin ve MVP kapsamının netleştirilmesi
- Takım rollerinin belirlenmesi
- GitHub repository ve proje dokümantasyon yapısının oluşturulması
- Django backend mimarisinin kurulması
- Kullanıcı kayıt/giriş endpointlerinin hazırlanması
- Fikir ekleme, listeleme, detay görüntüleme ve silme endpointlerinin geliştirilmesi
- Admin panelin aktif hale getirilmesi
- RAG destekli bilgi katmanı için kaynak araştırmasının başlatılması
- Sprint 2’de geliştirilecek frontend ve AI analiz akışları için temel planın çıkarılması

### Sprint Backlog

| ID    | İş | Sorumlu | Durum |
| ----- | -- | ------- | ----- |
| SB-01 | Proje fikrinin netleştirilmesi | Takım | Tamamlandı |
| SB-02 | Takım rollerinin belirlenmesi | Takım | Tamamlandı |
| SB-03 | Product backlog’un oluşturulması | Takım | Tamamlandı |
| SB-04 | GitHub repository yapısının hazırlanması | Eren | Tamamlandı |
| SB-05 | Django backend mimarisinin kurulması | Backend Ekibi | Tamamlandı |
| SB-06 | Kullanıcı kayıt endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-07 | Kullanıcı giriş endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-08 | Fikir ekleme endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-09 | Fikir listeleme endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-10 | Fikir detay görüntüleme endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-11 | Fikir silme endpointinin yazılması | Backend Ekibi | Tamamlandı |
| SB-12 | Django admin panelinin aktif hale getirilmesi | Backend Ekibi | Tamamlandı |
| SB-13 | Arayüz prototipi ve kullanıcı akışının incelenmesi | Takım | Devam Ediyor |
| SB-14 | RAG destekli bilgi katmanı için kaynak araştırmasının başlatılması | Takım | Devam Ediyor |
| SB-15 | Sprint 1 dokümantasyonunun hazırlanması | Eren | Devam Ediyor |

### Daily Scrum Notları

Sprint 1 sürecinde Daily Scrum görüşmeleri ağırlıklı olarak Slack Huddle üzerinden gerçekleştirilmiştir. Toplantılarda ekip üyelerinin üzerinde çalıştığı görevler, tamamlanan işler, karşılaşılan engeller ve bir sonraki adımlar değerlendirilmiştir.

Slack Huddle görüşmelerine ek olarak, ekip içi hızlı iletişim ve anlık koordinasyon için WhatsApp grubu aktif olarak kullanılmıştır. Bu sayede geliştirme sürecinde ortaya çıkan kısa sorular, görev güncellemeleri ve hızlı karar alınması gereken konular daha pratik şekilde takip edilmiştir.

Bu sprintte Daily Scrum gündemi genel olarak aşağıdaki başlıklar etrafında ilerlemiştir:

- Proje fikrinin netleştirilmesi
- Takım rollerinin belirlenmesi
- Ürün kapsamı ve MVP özelliklerinin konuşulması
- Backend mimarisinin kurulması
- Kullanıcı kayıt/giriş endpointlerinin geliştirilmesi
- Fikir ekleme, listeleme, detay görüntüleme ve silme endpointlerinin geliştirilmesi
- Admin panelin aktif hale getirilmesi
- Frontend tarafında eksik kalan kayıt/giriş ekranlarının belirlenmesi
- RAG destekli bilgi katmanı için kaynak araştırmasının başlatılması
- Sprint 1 dokümantasyonunun hazırlanması

Daily Scrum notları ve ekip içi iletişim çıktıları Sprint 1 dokümantasyonu kapsamında `docs/sprint-1/` klasörü altında ayrıca paylaşılacaktır.

### Sprint Board Güncellemeleri

Sprint 1 sürecinde görev takibi GitHub Projects üzerinden yapılmıştır. Product backlog ve sprint backlog maddeleri; yapılacaklar, devam eden işler ve tamamlanan işler olarak ayrıştırılmıştır.

Sprint board üzerinde özellikle aşağıdaki iş grupları takip edilmiştir:

- Proje fikri ve kapsam belirleme
- Takım rolleri ve görev dağılımı
- Backend mimarisinin kurulması
- Kullanıcı kayıt/giriş endpointleri
- Fikir ekleme, listeleme, detay görüntüleme ve silme endpointleri
- Admin panel kurulumu
- Frontend tarafında geliştirilecek ekranların belirlenmesi
- RAG kaynak araştırması
- Sprint 1 dokümantasyonu

Sprint 1 sonunda backend tarafındaki temel endpoint geliştirmeleri tamamlanmış, frontend entegrasyonu ve AI analiz akışları Sprint 2 kapsamına alınmıştır.

Sprint board ekran görüntüleri ve görev durumları `docs/sprint-1/` klasörü altında paylaşılacaktır.

### Ürün Durumu

Sprint 1 sonunda ürün, tam çalışan bir MVP seviyesinde değildir; ancak projenin temel teknik altyapısı ve ilk backend modülleri oluşturulmuştur.

Backend tarafında Django mimarisi kurulmuş, kullanıcı kayıt/giriş işlemleri için endpointler hazırlanmıştır. Ayrıca kullanıcıların iş fikirlerini ekleyebildiği, listeleyebildiği, detaylarını görüntüleyebildiği ve silebildiği temel fikir yönetimi endpointleri geliştirilmiştir.

Django admin paneli aktif hale getirilmiş ve temel veri yönetimi için kullanılabilir duruma getirilmiştir. Backend geliştirmeleri ilgili branch üzerinden GitHub reposuna aktarılmıştır.

Frontend tarafında arayüz ve kullanıcı akışı üzerine ön hazırlık yapılmış olup, kayıt/giriş ekranları ve backend entegrasyonu Sprint 2 kapsamında ele alınacaktır.

AI analiz akışı, riskli varsayım çıkarımı, müşteri görüşme soruları, MoSCoW önceliklendirme ve doğrulama yol haritası özellikleri sonraki sprintlerde geliştirilecek ana modüller olarak planlanmıştır.

RAG destekli bilgi katmanı için kaynak araştırması Sprint 1’de başlatılmıştır ve bu çalışmanın Sprint 3’e kadar geliştirilerek ürüne entegre edilmesi hedeflenmektedir.

![Sprint 1 Ürün Durumu](docs/sprint-1/sprint1-demo.gif)

### Sprint Review

Sprint 1 sonunda takım olarak proje fikri, ürün kapsamı, teknik mimari ve geliştirilen ilk backend çıktıları gözden geçirilmiştir.

Bu sprintte ürünün temel problem-çözüm yapısı netleştirilmiş, hedef kitle belirlenmiş ve Product Backlog oluşturulmuştur. Teknik tarafta Django tabanlı backend mimarisi kurulmuş, kullanıcı yönetimi ve fikir yönetimi için ilk endpointler geliştirilmiştir.

Sprint 1 sonunda ortaya çıkan başlıca çıktılar:

- Proje fikri ve ürün vizyonu netleştirildi.
- Takım rolleri belirlendi.
- Product Backlog ve Sprint Backlog oluşturuldu.
- GitHub repository ve proje klasör yapısı hazırlandı.
- Django backend mimarisi kuruldu.
- Kullanıcı kayıt ve giriş endpointleri geliştirildi.
- Kullanıcıların fikir ekleyebildiği, listeleyebildiği, detaylarını görüntüleyebildiği ve silebildiği endpointler geliştirildi.
- Django admin paneli aktif hale getirildi.
- Arayüz prototipi ve kullanıcı akışı üzerinden frontend geliştirme planı değerlendirildi.
- RAG destekli bilgi katmanı için kaynak araştırması başlatıldı.

Sprint Review sonucunda, Sprint 2’de frontend ekranlarının geliştirilmesi, backend ile entegrasyonun yapılması ve AI destekli temel fikir analizi akışının başlatılması öncelikli hedefler olarak belirlenmiştir..

### Sprint Retrospective

Sprint 1 sonunda takım olarak süreç, iletişim, görev dağılımı ve teknik ilerleme açısından değerlendirme yapılmıştır.

#### İyi Gidenler

- Proje fikri erken aşamada netleştirildi.
- Takım rolleri belirlendi.
- Ürün problemi, hedef kitlesi ve temel MVP kapsamı daha anlaşılır hale getirildi.
- Backend tarafında Django mimarisi kuruldu.
- Kullanıcı kayıt/giriş endpointleri geliştirildi.
- Kullanıcıların fikir ekleme, listeleme, detay görüntüleme ve silme işlemleri için temel endpointler tamamlandı.
- Django admin paneli aktif hale getirildi.
- Slack Huddle ve WhatsApp grubu üzerinden ekip içi iletişim aktif şekilde sürdürüldü.
- RAG destekli bilgi katmanı için kaynak araştırması başlatıldı.

#### Geliştirilmesi Gerekenler

- Görevlerin GitHub Issues üzerinde daha küçük ve takip edilebilir parçalara ayrılması gerekiyor.
- Sprint board güncellemelerinin daha düzenli yapılması gerekiyor.
- Daily Scrum notlarının daha sistemli şekilde dokümante edilmesi gerekiyor.
- Frontend tarafındaki teknoloji ve geliştirme planının netleştirilmesi gerekiyor.
- Backend ile frontend arasındaki veri akışının daha açık şekilde tanımlanması gerekiyor.
- AI analiz çıktılarının hangi formatta döneceği netleştirilmeli.

#### Bir Sonraki Sprint İçin Aksiyonlar

- Kayıt ve giriş ekranlarının frontend tarafında geliştirilmesi
- Fikir ekleme, listeleme ve detay görüntüleme ekranlarının backend ile entegre edilmesi
- AI destekli temel fikir analizi akışının başlatılması
- Riskli varsayım analizi için çıktı formatının belirlenmesi
- Mom Test prensiplerine uygun soru üretimi için prompt yapısının hazırlanması
- RAG kaynak araştırmasının sürdürülmesi ve kullanılabilecek veri kaynaklarının listelenmesi
- GitHub Issues ve Sprint Board kullanımının daha düzenli hale getirilmesi

---

## Sprint 2

### Sprint Notları

Sprint 2, 6 Temmuz 2026 tarihinde başlamış ve 19 Temmuz 2026 tarihinde tamamlanmıştır.

Bu sprintte, kullanıcının iş fikrini sisteme eklemesinden başlayarak fikir doğrulama analizlerine ulaşmasına kadar olan temel backend akışının geliştirilmesine odaklanılmıştır. Bu kapsamda fikir gönderme akışı, Mom Test görüşme soruları, MoSCoW tabanlı MVP kapsam analizi, doğrulama yol haritası ve başlangıç seviyesinde RAG altyapısı üzerinde çalışılmıştır.

Sprint boyunca backend ve yapay zekâ tarafında önemli ilerleme sağlanmıştır. Kullanıcının iş fikrini sisteme gönderebilmesini sağlayan fikir gönderme akışı tamamlanmış; analiz servisleri, API endpointleri, veri modelleri ve ilgili testler geliştirilmiştir.

AI analiz servisinin backend tarafı hazırlanmış ancak frontend geliştirmeleri planlanan seviyede tamamlanamadığı için analiz sonuçları kullanıcı arayüzüne bağlanamamıştır.

Frontend entegrasyonunun tamamlanamaması nedeniyle analiz sonuçlarının dashboard üzerinde gösterilmesi ve uçtan uca MVP akışına yönelik temel test senaryolarının hazırlanması Son Sprint'e aktarılmıştır.

Sprint sonunda tamamlanan, devam eden ve sonraki sprinte aktarılan işler GitHub Issues, Sprint 2 Milestone ve Project Board üzerinde güncellenmiştir.

### Sprint Hedefi

Sprint 2'nin temel hedefi, kullanıcının iş fikrini sisteme ekleyebilmesini ve bu fikir üzerinden yapay zekâ destekli doğrulama analizleri alabilmesini sağlayacak temel ürün akışını geliştirmekti.

Bu kapsamda aşağıdaki çalışmalar hedeflenmiştir:

- Kullanıcının iş fikrini sisteme gönderebilmesini sağlayan fikir gönderme akışını geliştirmek
- Kullanıcının hedef kitlesiyle yapacağı görüşmeler için Mom Test yaklaşımına uygun sorular oluşturmak
- İş fikrinin MVP kapsamını MoSCoW yöntemiyle önceliklendirmek
- Kullanıcıya uygulanabilir bir fikir doğrulama yol haritası sunmak
- Analiz süreçlerinde kullanılmak üzere başlangıç seviyesinde RAG altyapısı hazırlamak
- Yapay zekâ destekli analiz servisinin backend altyapısını geliştirmek
- Backend tarafından üretilen analiz sonuçlarını dashboard arayüzüne entegre etmek
- Sprint 2 MVP akışına yönelik temel test senaryolarını hazırlamak

Sprint sonunda fikir gönderme akışı, Mom Test, MoSCoW kapsam analizi, doğrulama yol haritası, başlangıç RAG altyapısı ve AI analiz servisinin backend geliştirmeleri tamamlanmıştır.

AI analiz servisinin backend tarafı hazır olmasına rağmen frontend tarafı tamamlanmadığı için kullanıcı arayüzü entegrasyonu gerçekleştirilememiştir. Dashboard entegrasyonu ve uçtan uca MVP test senaryoları Son Sprint'e aktarılmıştır.

### Sprint Backlog

Sprint 2 backlog'u, kullanıcının iş fikrini sisteme göndermesini ve yapay zekâ destekli doğrulama analizleri almasını sağlayacak temel ürün akışına yönelik GitHub issue'larından oluşturulmuştur.

İşlerin takibi GitHub Issues, Sprint 2 Milestone ve Project Board üzerinden gerçekleştirilmiştir.

| Issue | Çalışma | Sprint Sonu Durumu |
|---|---|---|
| #16 | Implement Idea Submission Flow | Tamamlandı. |
| #17 | Create AI Analysis Service for Idea Validation | Backend geliştirmesi tamamlandı ve issue kapatıldı. Frontend entegrasyonu #22 üzerinden takip edilmek üzere Son Sprint'e aktarıldı. |
| #18 | Generate The Mom Test Interview Questions | Tamamlandı. |
| #19 | Implement MoSCoW Based MVP Scope Module | Tamamlandı. |
| #20 | Generate Validation Roadmap Report | Tamamlandı. |
| #21 | Build Initial RAG Retrieval Pipeline | Tamamlandı. |
| #22 | Integrate Analysis Results into Dashboard UI | Frontend hazır olmadığı için tamamlanamadı. Açık bırakılarak Son Sprint'e aktarıldı. |
| #23 | Add Basic Test Scenarios for Sprint 2 MVP Flow | Uçtan uca MVP akışı tamamlanmadığı için gerçekleştirilemedi. Açık bırakılarak Son Sprint'e aktarıldı. |
| #24 | Prepare Sprint 2 Documentation and Review Notes | Sprint sonu dokümantasyon çalışmaları kapsamında yürütülmektedir. |

Sprint içerisinde toplam dokuz backlog maddesi takip edilmiştir. Bunlardan altısının teknik geliştirmeleri tamamlanmış, iki çalışma Son Sprint'e aktarılmış ve Sprint 2 dokümantasyonu sprint kapanış sürecinde hazırlanmıştır.

### Daily Scrum Notları

Sprint 2 boyunca ekip içi iletişim Slack ve WhatsApp üzerinden sürdürülmüştür. Takım üyeleri yürüttükleri çalışmalar, tamamladıkları görevler, karşılaştıkları engeller ve sonraki adımları hakkında düzenli olarak bilgi paylaşmıştır.

Daily Scrum iletişimlerinde ağırlıklı olarak aşağıdaki konular takip edilmiştir:

- Üzerinde çalışılan issue ve branch bilgileri
- Fikir gönderme akışındaki ilerlemeler
- Tamamlanan backend, frontend, AI ve RAG geliştirmeleri
- Açılan pull request'ler ve kod inceleme durumları
- Test sonuçları ve karşılaşılan teknik sorunlar
- Takım üyelerinin sonraki çalışma hedefleri
- Frontend ile backend arasındaki entegrasyon bağımlılıkları
- Sprint sonunda tamamlanamayacak işlerin belirlenmesi

Sprint sürecinde fikir gönderme akışı, Mom Test soru üretimi, MoSCoW kapsam analizi, doğrulama yol haritası ve RAG altyapısına ilişkin geliştirmeler takip edilmiştir.

Backend tarafındaki analiz servisleri hazırlanırken frontend çalışmalarının planlanan seviyede ilerlememesi, entegrasyon sürecinin önündeki temel engel olarak belirlenmiştir.

Bu engel ekip içerisinde paylaşılmış ve analiz sonuçlarının dashboard arayüzüne bağlanması ile uçtan uca MVP testlerinin Son Sprint'e aktarılmasına karar verilmiştir.

Daily Scrum kayıtları ve ekip içi ilerleme paylaşımları, sprint sürecinin takip edilebilirliğini sağlamak amacıyla Slack üzerinde tutulmuştur.

### Sprint Board Güncellemeleri

Sprint 2 boyunca işlerin durumu GitHub Project Board üzerinden takip edilmiştir. Issue'lar çalışma durumlarına göre `To Do`, `In Progress` ve `Done` sütunları arasında güncellenmiştir.

Sprint başlangıcında planlanan işler `To Do` sütununa eklenmiş, geliştirmesine başlanan görevler `In Progress` durumuna alınmış ve tamamlanan çalışmalar ilgili pull request'lerin birleştirilmesinin ardından `Done` sütununa taşınmıştır.

Sprint sonunda board üzerinde gerçekleştirilen güncellemeler aşağıdaki gibidir:

- **#16 – Implement Idea Submission Flow:** Tamamlanarak `Done` durumuna taşındı.
- **#17 – Create AI Analysis Service for Idea Validation:** Backend geliştirmesi tamamlandığı için kapatıldı. Kalan frontend bağlantısı #22 üzerinden takip edilmeye devam etmektedir.
- **#18 – Generate The Mom Test Interview Questions:** Tamamlanarak `Done` durumuna taşındı.
- **#19 – Implement MoSCoW Based MVP Scope Module:** Tamamlanarak `Done` durumuna taşındı.
- **#20 – Generate Validation Roadmap Report:** Tamamlanarak `Done` durumuna taşındı.
- **#21 – Build Initial RAG Retrieval Pipeline:** Tamamlanarak `Done` durumuna taşındı.
- **#22 – Integrate Analysis Results into Dashboard UI:** Tamamlanamadığı için açık bırakıldı, `To Do` durumuna alındı ve Son Sprint'e aktarıldı.
- **#23 – Add Basic Test Scenarios for Sprint 2 MVP Flow:** Tamamlanamadığı için açık bırakıldı, `To Do` durumuna alındı ve Son Sprint'e aktarıldı.
- **#24 – Prepare Sprint 2 Documentation and Review Notes:** Sprint kapanış sürecinde `In Progress` durumunda takip edildi.

Tamamlanamayan işlerin açıklamaları ilgili issue'lara yorum olarak eklenmiş ve milestone bilgileri `Son Sprint` olarak güncellenmiştir. Böylece Sprint 2 sonunda board, tamamlanan çalışmalar ile sonraki sprinte aktarılan işleri açık biçimde gösterecek şekilde düzenlenmiştir.

#### Sprint Board Ekran Görüntüsü

Sprint board ekran görüntüleri ve görev durumları `docs/sprint-2/` klasörü altında paylaşılmıştır.

### Ürün Durumu

![Sprint 2 Ürün Durumu](docs/sprint-2/sprint2-demo.gif)

### Sprint Review

Sprint 2 sonunda, projenin temel fikir doğrulama özelliklerinin backend ve yapay zekâ tarafında önemli ölçüde geliştirildiği görülmüştür.

Sprint kapsamında aşağıdaki çalışmalar tamamlanmıştır:

- Kullanıcının yeni bir iş fikrini sisteme ekleyebilmesini sağlayan fikir gönderme akışı geliştirilmiştir.
- Kullanıcıların hedef kitleleriyle yapacağı görüşmeler için Mom Test yaklaşımına uygun soru üretme özelliği hazırlanmıştır.
- İş fikrinin MVP kapsamını belirlemek amacıyla MoSCoW tabanlı kapsam analizi geliştirilmiştir.
- Kullanıcıya doğrulama sürecinde izleyebileceği adımları sunan doğrulama yol haritası özelliği hazırlanmıştır.
- Analiz süreçlerinde kullanılmak üzere başlangıç seviyesinde RAG retrieval altyapısı oluşturulmuştur.
- Yapay zekâ destekli analiz servisinin backend altyapısı ve ilgili API akışı hazırlanmıştır.
- Geliştirilen backend özellikleri için gerekli test ve doğrulama çalışmaları gerçekleştirilmiştir.

Sprint sonunda backend tarafındaki analiz özellikleri kullanılabilir ve test edilebilir duruma getirilmiştir. Ancak frontend geliştirmelerinin planlanan seviyede tamamlanamaması nedeniyle analiz sonuçları dashboard arayüzüne bağlanamamıştır.

Bu nedenle aşağıdaki çalışmalar Sprint 2 içerisinde tamamlanamamış ve Son Sprint'e aktarılmıştır:

- Analiz sonuçlarının dashboard kullanıcı arayüzüne entegre edilmesi
- Fikir gönderme ve analiz sonuçlarını görüntüleme adımlarını kapsayan uçtan uca MVP test senaryolarının hazırlanması

Sprint 2 sonunda ortaya çıkan ürün artımı, fikir oluşturma ve fikir doğrulama analizlerinin backend tarafında çalışan temelini oluşturmaktadır. Son Sprint'te öncelik, tamamlanan backend servislerinin frontend ile birleştirilmesi ve kullanıcı tarafından uçtan uca deneyimlenebilir bir ürün akışının oluşturulması olacaktır.

### Sprint Retrospective

Sprint 2 süreci sonunda ekip tarafından teknik ilerleme, iş dağılımı, iletişim ve tamamlanamayan çalışmalar değerlendirilmiştir.

#### İyi Giden Noktalar

- Sprint backlog'unda yer alan backend ve yapay zekâ ağırlıklı çalışmaların büyük bölümü tamamlanmıştır.
- Fikir gönderme, Mom Test, MoSCoW kapsam analizi ve doğrulama yol haritası gibi ürünün temel özellikleri geliştirilmiştir.
- Analiz işlemlerinin doğrudan view katmanında yürütülmesi yerine servis katmanları kullanılarak daha düzenli ve sürdürülebilir bir backend yapısı oluşturulmuştur.
- Geliştirilen endpointler için yetkilendirme, fikir sahipliği kontrolü, veri doğrulama ve test süreçlerine önem verilmiştir.
- Çalışmalar GitHub Issues, branch'ler, pull request'ler ve Project Board üzerinden takip edilmiştir.
- Tamamlanamayan işler gizlenmeden ilgili issue'lara açıklayıcı yorumlar eklenmiş ve Son Sprint'e aktarılmıştır.
- Ekip üyeleri kendi çalışma alanlarındaki ilerlemeleri Slack ve WhatsApp üzerinden paylaşmıştır.

#### Karşılaşılan Zorluklar

- Frontend geliştirmeleri ile backend analiz servisleri aynı hızda ilerleyememiştir.
- Frontend ekranlarının hazır olmaması, tamamlanan backend özelliklerinin kullanıcı arayüzüne bağlanmasını engellemiştir.
- Backend ve frontend arasındaki bağımlılıklar sprint başlangıcında yeterince ayrıntılı planlanmamıştır.
- Uçtan uca MVP akışı oluşturulamadığı için temel kullanıcı senaryolarının tamamı test edilememiştir.
- Bazı çalışmalar sprint sonuna yakın tamamlandığı için entegrasyon ve genel ürün kontrolü için yeterli zaman kalmamıştır.
- Takım üyelerinin geliştirdiği parçaların tek bir ürün akışında birleştirilmesi beklenenden daha fazla koordinasyon gerektirmiştir.

#### Sonraki Sprint İçin İyileştirmeler

- Son Sprint'in başında tamamlanması gereken minimum ürün akışı net biçimde belirlenecektir.
- Frontend ve backend entegrasyonu sprintin sonuna bırakılmadan ilk günlerden itibaren parça parça gerçekleştirilecektir.
- Frontend geliştirmelerinde kullanılacak API endpointleri, istek yapıları ve örnek yanıtlar ekip içerisinde açık biçimde paylaşılacaktır.
- Entegrasyon çalışmaları için sorumlu kişiler ve bağımlılıklar issue açıklamalarında belirtilecektir.
- Tamamlanan her özellik, yalnızca kendi katmanında değil, mümkün olduğunda kullanıcı akışı içerisinde de kontrol edilecektir.
- Uçtan uca test senaryoları ürün tamamen bittikten sonra değil, entegrasyon ilerledikçe hazırlanacaktır.
- Son Sprint'te yeni ve kapsamlı özellikler eklemek yerine mevcut özelliklerin birleştirilmesine, test edilmesine ve çalışır ürün haline getirilmesine öncelik verilecektir.

#### Son Sprint İçin Alınan Kararlar

- #22 kapsamında analiz sonuçları dashboard arayüzüne entegre edilecektir.
- #23 kapsamında temel MVP akışını kapsayan test senaryoları hazırlanacaktır.
- Fikir gönderme, analiz başlatma ve sonuç görüntüleme adımları tek bir kullanıcı akışında birleştirilecektir.
- Frontend ve backend arasındaki uyumsuzluklar erken aşamada tespit edilerek giderilecektir.
- Ürün tesliminden önce çalışmayan, eksik veya gereksiz özellikler belirlenerek MVP kapsamı korunacaktır.
- Dokümantasyon, demo hazırlığı ve son ürün kontrolleri sprintin son günlerine bırakılmadan paralel şekilde yürütülecektir.

---

## Sprint 3

### Sprint Notları

Belirlenecek.

### Sprint Hedefi

Belirlenecek.

### Sprint Backlog

Belirlenecek.

### Daily Scrum Notları

Belirlenecek.

### Sprint Board Güncellemeleri

Belirlenecek.

### Ürün Durumu

Belirlenecek.

### Sprint Review

Belirlenecek.

### Sprint Retrospective

Belirlenecek.

---

## Proje Teslim Bilgileri

| Teslim Kalemi | Durum        |
| ------------- | ------------ |
| GitHub reposu | Hazır        |
| Public repo   | Belirlenecek |
| Ürün demosu   | Belirlenecek |
| Canlı link    | Belirlenecek |
| Proje videosu | Belirlenecek |
| Final raporu  | Belirlenecek |

---

## Lisans

Belirlenecek.
