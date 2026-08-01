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
- `Block`: Sprint sürecinde kapsamdan çıkarılan, önceliği kaldırılan veya artık tamamlanması planlanmayan çalışmalar

Tamamlanan çalışmalar pull request ve kontrol süreçlerinin ardından `Done` durumuna taşınmaktadır.

Teknik bir engel nedeniyle geçici olarak bekleyen işler `In Progress` veya ilgili issue açıklaması üzerinden takip edilmektedir. Sprint içerisinde artık yapılmamasına karar verilen, kapsamdan çıkarılan veya önceliği kaldırılan işler ise tamamlanmış gibi gösterilmeden `Block` durumuna alınmaktadır.

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

#### E-posta ve doğrulama kodu ayarları

Geliştirme ortamında varsayılan `django.core.mail.backends.console.EmailBackend`
kullanılır ve e-postalar gerçek bir SMTP sunucusuna gönderilmeden terminalde
görüntülenir. Production ortamında sağlayıcıdan bağımsız olarak
`EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend` seçilmeli ve
`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` ile
`DEFAULT_FROM_EMAIL` değerleri `.env` üzerinden yapılandırılmalıdır.

`EMAIL_USE_TLS` ve `EMAIL_USE_SSL` aynı anda `True` olamaz. Genellikle STARTTLS
için TLS, implicit TLS bağlantısı için SSL seçilir; kullanılan port SMTP
sağlayıcısının dokümantasyonuyla eşleşmelidir. SMTP parolası ve diğer gerçek
erişim bilgileri yalnız `.env` veya production secret yönetim sistemi içinde
tutulmalı, repository'ye gönderilmemelidir. Bağlantı zaman aşımı
`EMAIL_TIMEOUT` ile saniye cinsinden belirlenir.

Doğrulama ve parola sıfırlama kodlarının varsayılan politikası 10 dakika
geçerlilik, yeniden gönderimler arasında 60 saniye bekleme ve en fazla 5 yanlış
denemedir. Bu değerler sırasıyla `AUTH_CODE_TTL_MINUTES`,
`AUTH_CODE_RESEND_COOLDOWN_SECONDS` ve `AUTH_CODE_MAX_ATTEMPTS` ile
değiştirilebilir; tamamı pozitif tam sayı olmalıdır. Güvenli yapılandırma
sınırları sırasıyla 1440 dakika, 86400 saniye ve 100 denemedir; SMTP timeout
değeri en fazla 300 saniye olabilir. Geçersiz veya açıkça boş boolean
değerleri uygulama başlangıcında reddedilir.

IP tabanlı throttle'ın güvenilir istemci adresini kullanabilmesi için
`DRF_NUM_PROXIES` doğrudan bağlantıda `0` bırakılmalı; production ortamında
yalnız uygulamanın önündeki güvenilir reverse proxy sayısına ayarlanmalıdır.

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

Bu komut e-posta doğrulama alanını ve tek kullanımlık doğrulama kodu tablosunu
da mevcut verileri koruyarak uygular.

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
| `POST` | `/api/auth/register/` | Doğrulanmamış kullanıcı kaydı oluşturur ve e-posta doğrulama kodu gönderir. | Gerekli değil |
| `POST` | `/api/auth/verify-email/` | E-posta adresini altı haneli kodla doğrular. | Gerekli değil |
| `POST` | `/api/auth/resend-verification/` | Uygun hesaba yeni doğrulama kodu gönderir. | Gerekli değil |
| `POST` | `/api/auth/login/` | Doğrulanmış kullanıcı için JWT bilgilerini döndürür. | Gerekli değil |
| `POST` | `/api/auth/password-reset/request/` | Uygun hesaba parola sıfırlama kodu gönderir. | Gerekli değil |
| `POST` | `/api/auth/password-reset/confirm/` | Kod ve yeni parola ile parola sıfırlamayı tamamlar. | Gerekli değil |
| `GET` | `/api/auth/me/` | Giriş yapan kullanıcının profilini döndürür. | Gerekli |
| `PATCH` | `/api/auth/me/` | Giriş yapan kullanıcının ad ve soyadını günceller. | Gerekli |
| `POST` | `/api/auth/change-password/` | Mevcut parola ile giriş yapan kullanıcının parolasını değiştirir. | Gerekli |

Kayıt ve kod gönderme endpointleri IP başına saatte 5, kod doğrulama
endpointleri ise IP başına saatte 20 istekle sınırlandırılır. Yeniden gönderme
bekleme süresi hesap bazında ayrıca uygulanır. Birden fazla worker kullanılan
production ortamında IP throttle sayaçlarının tüm worker'larca paylaşılması
için ortak bir Django cache backend'i yapılandırılmalıdır; varsayılan local
memory cache yalnız süreç bazında koruma sağlar.

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

![Sprint 1 Board](docs/sprint-1/screenshots/sprint-board.png)

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

Sprint Review sonucunda, Sprint 2’de frontend ekranlarının geliştirilmesi, backend ile entegrasyonun yapılması ve AI destekli temel fikir analizi akışının başlatılması öncelikli hedefler olarak belirlenmiştir.

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
| #24 | Prepare Sprint 2 Documentation and Review Notes | Tamamlandı ve issue kapatıldı. |

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
- **#24 – Prepare Sprint 2 Documentation and Review Notes:** Dokümantasyon tamamlanarak `Done` durumuna taşındı ve issue kapatıldı.

Tamamlanamayan işlerin açıklamaları ilgili issue'lara yorum olarak eklenmiş ve milestone bilgileri `Son Sprint` olarak güncellenmiştir. Böylece Sprint 2 sonunda board, tamamlanan çalışmalar ile sonraki sprinte aktarılan işleri açık biçimde gösterecek şekilde düzenlenmiştir.

#### Sprint Board Ekran Görüntüsü

![Sprint 2 Board](docs/sprint-2/screenshots/sprint-board.png)

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

Sprint 3, 20 Temmuz 2026 tarihinde başlamış ve 2 Ağustos 2026 tarihinde tamamlanmıştır.

Bu sprintte temel hedef, önceki sprintlerde geliştirilen backend ve yapay zekâ modüllerini tek bir kullanıcı akışı içerisinde birleştirerek ürünü uçtan uca kullanılabilir, test edilebilir ve teslim edilebilir hale getirmek olmuştur.

Sprint 2’den aktarılan analiz sonuçlarının dashboard kullanıcı arayüzüne entegre edilmesi ve temel MVP test senaryolarının hazırlanması çalışmalarına öncelik verilmiştir. Bunun yanında fikir doğrulama modülleri tek bir doğrulama iş akışı altında birleştirilmiş; kullanıcının fikir oluşturma, analiz başlatma, sonuçları görüntüleme, müşteri görüşme notlarını kaydetme ve bu notlardan kanıta dayalı içgörüler elde etme süreçleri geliştirilmiştir.

Sprint kapsamında müşteri görüşme notları için veri modeli ve CRUD API hazırlanmış, notların frontend üzerinden eklenmesi, düzenlenmesi ve silinmesi sağlanmıştır. Görüşme notlarından kanıt ve içgörü üretme özelliği geliştirilmiş ve bu çıktılar ürünün doğrulama akışına dahil edilmiştir.

Fikir analizleri, Mom Test soruları, MoSCoW kapsam analizi, doğrulama yol haritası, görüşme kanıtları ve diğer analiz sonuçlarını bir araya getiren bütünleşik fikir doğrulama raporu hazırlanmıştır. Rapor ekranı geliştirilmiş ve doğrulama raporunun metin tabanlı PDF olarak dışa aktarılabilmesi sağlanmıştır.

Frontend tarafında analiz geçmişinin saklanması, kullanıcıya ait gerçek fikirlerin yüklenmesi, açık ve koyu tema desteği, hesap ayarları, şifre görünürlüğü, e-posta doğrulama, şifre sıfırlama ve mentor yanıtlarının Markdown biçiminde gösterilmesi gibi kullanıcı deneyimini geliştiren çalışmalar gerçekleştirilmiştir. Yüklenme, hata, boş durum ve responsive arayüz davranışları gözden geçirilmiş; kullanılmayan veya güncelliğini kaybeden frontend özellikleri ve endpointler temizlenmiştir.

Yapay zekâ ve RAG tarafında analiz servisleri RAG kaynaklarıyla bütünleştirilmiş, YouTube içeriklerinin bilgi tabanına alınabilmesi için ingestion pipeline ve yanıt servisi eklenmiştir. RAG kaynak yönetimi ve oturum işlemleri geliştirilmiş; fikir bazlı Mom Test soruları ve görüşme kanıtı analizi gibi AI özellikleri ürün akışına dahil edilmiştir.

Doğrulama akışının uzun süren işlemlerinde kullanıcıya anlık ilerleme bilgisi sunmak amacıyla gerçek zamanlı workflow progress tracking özelliği geliştirilmiştir. Ayrıca proje yaşam döngüsündeki sık kullanılan geliştirme komutlarını kolaylaştırmak amacıyla Makefile eklenmiştir.

Sprint 3 Milestone kapsamında yer alan 11 issue'nun tamamı kapatılmış ve milestone yüzde 100 tamamlanmıştır. Çalışmalar ayrı branch ve pull request'ler üzerinden ana branch'e aktarılmış; sprint sonunda ürünün temel kullanıcı akışı, analiz modülleri, raporlama özellikleri, testleri ve production ortamı için gerekli yapılandırmaları tamamlanmıştır.

Ürünün canlıya alınmasına yönelik teknik hazırlıklar yapılmış olmakla birlikte, canlı bağlantı ve nihai deployment bilgileri proje teslim süreci kapsamında ayrıca güncellenecektir.

### Sprint Hedefi

Sprint 3’ün temel hedefi, önceki sprintlerde geliştirilen backend, yapay zekâ ve RAG modüllerini frontend ile birleştirerek kullanıcı tarafından uçtan uca deneyimlenebilen, test edilebilir ve teslim edilebilir bir ürün ortaya çıkarmaktır.

Bu sprintte yeni ve bağımsız özellikler geliştirmekten çok, mevcut modüllerin tek bir doğrulama süreci altında birleştirilmesine, kullanıcı deneyiminin tamamlanmasına, hata durumlarının giderilmesine ve ürünün production ortamına hazırlanmasına öncelik verilmiştir.

Sprint 3 kapsamında hedeflenen ana çıktılar:

- Sprint 2’den aktarılan analiz sonuçlarını dashboard kullanıcı arayüzüne entegre etmek
- Fikir oluşturma, analiz başlatma ve analiz sonuçlarını görüntüleme adımlarını uçtan uca çalışan tek bir kullanıcı akışında birleştirmek
- Riskli varsayımlar, Mom Test soruları, MoSCoW kapsamı, doğrulama yol haritası ve diğer analiz modüllerini merkezi bir doğrulama workflow’u üzerinden yönetmek
- RAG kaynaklarını analiz servisleriyle bütünleştirerek yapay zekâ çıktılarının girişimcilik ve fikir doğrulama içerikleriyle desteklenmesini sağlamak
- Kullanıcının müşteri görüşme notlarını ekleyebilmesi, görüntüleyebilmesi, düzenleyebilmesi ve silebilmesi için backend ve frontend akışlarını geliştirmek
- Görüşme notlarından kanıt, içgörü ve tekrar eden problem analizleri oluşturmak
- Analiz sonuçları ile görüşme kanıtlarını bir araya getiren bütünleşik fikir doğrulama raporu hazırlamak
- Doğrulama raporunu PDF olarak dışa aktarılabilir hale getirmek
- Uzun süren analiz işlemlerinde kullanıcıya gerçek zamanlı ilerleme bilgisi göstermek
- Yüklenme, hata, boş durum ve responsive arayüz davranışlarını tamamlamak
- Kullanıcı sahipliği, yetkilendirme ve başarısız istek senaryolarını test etmek
- Hesap ayarları, e-posta doğrulama ve parola yönetimi gibi kullanıcı hesabı akışlarını tamamlamak
- Kullanılmayan frontend özelliklerini ve endpointleri temizleyerek ürün bütünlüğünü artırmak
- Projenin sık kullanılan geliştirme ve test komutlarını Makefile üzerinden kolaylaştırmak
- Production ortam değişkenlerini ve deployment yapılandırmasını hazırlamak
- Ürünün son kontrollerini, hata düzeltmelerini, dokümantasyonunu ve demo hazırlıklarını tamamlamak

Sprint sonunda hedeflenen ürün artımı; kullanıcının kayıt olarak bir iş fikri oluşturabildiği, bu fikir için yapay zekâ destekli doğrulama analizleri alabildiği, müşteri görüşme kanıtlarını sisteme ekleyebildiği ve tüm sonuçları bütünleşik bir rapor üzerinden inceleyebildiği çalışır bir MVP’dir.

### Sprint Backlog

Sprint 3 backlog'u, önceki sprintten aktarılan frontend entegrasyonunun tamamlanması, yapay zekâ ve RAG modüllerinin tek bir doğrulama akışında birleştirilmesi, müşteri görüşme kanıtlarının ürüne dahil edilmesi ve uygulamanın production ortamına hazırlanması hedefleri doğrultusunda oluşturulmuştur.

İşler; kullanıcı tarafından doğrudan deneyimlenen ürün akışları, bu akışları destekleyen backend ve yapay zekâ servisleri, yetkilendirme kontrolleri, arayüz durumları ve deployment hazırlıkları dikkate alınarak önceliklendirilmiştir.

Sprint kapsamındaki çalışmalar GitHub Issues, Sprint 3 Milestone, branch'ler, pull request'ler ve Project Board üzerinden takip edilmiştir.

| Issue | Çalışma | Sprint Sonu Durumu |
|---|---|---|
| #22 | Integrate Analysis Results into Dashboard UI | Sprint 2’den aktarıldı. Analiz sonuçları frontend kullanıcı akışına entegre edildi ve issue tamamlanarak kapatıldı. |
| #23 | Add Basic Test Scenarios for Sprint 2 MVP Flow | Sprint 2’den aktarıldı. Sprint sürecinde ayrı bir çalışma olarak devam ettirilmesinden vazgeçildi, kapsamdan çıkarıldı ve Project Board üzerinde `Block` durumuna alındı. Tamamlanmış bir çalışma olarak değerlendirilmedi. |
| #31 | Integrate RAG Sources into Analysis Services | RAG kaynakları yapay zekâ analiz servislerine entegre edildi ve issue tamamlanarak kapatıldı. |
| #32 | Orchestrate Validation Modules into a Single Workflow | Ayrı doğrulama modülleri tek bir merkezi workflow altında birleştirildi ve issue tamamlanarak kapatıldı. |
| #33 | Add Interview Notes Model and CRUD API | Müşteri görüşme notları için veri modeli ile oluşturma, listeleme, güncelleme ve silme API'leri geliştirildi ve issue tamamlanarak kapatıldı. |
| #34 | Generate Evidence and Insights from Interview Notes | Görüşme notlarından kanıt ve doğrulama içgörüleri üreten yapay zekâ servisi geliştirildi ve issue tamamlanarak kapatıldı. |
| #35 | Add Interview Notes and Evidence Insights UI | Görüşme notlarının eklenebildiği, düzenlenebildiği, silinebildiği ve ilgili içgörülerin görüntülenebildiği frontend akışı tamamlandı. |
| #36 | Build Consolidated Idea Validation Report | Farklı analiz ve kanıt sonuçlarını bir araya getiren bütünleşik fikir doğrulama raporu oluşturuldu ve issue tamamlanarak kapatıldı. |
| #37 | Finalize Loading, Error, Empty and Responsive UI States | Yüklenme, hata, boş durum ve responsive arayüz davranışları gözden geçirilerek tamamlandı. |
| #38 | Prepare Production Deployment and Environment Configuration | Production ortam değişkenleri ve deployment için gerekli yapılandırmalar hazırlandı ve issue tamamlanarak kapatıldı. |
| #39 | Add Authorization, Ownership and Failure Scenario Tests | Yetkilendirme, kullanıcı sahipliği ve başarısız istek senaryolarına yönelik testler tamamlandı ve issue kapatıldı. |

Sprint 3 Milestone kapsamında toplam 11 issue takip edilmiştir. Sprint sonunda milestone içerisindeki tüm issue'lar kapatılmış ve milestone GitHub üzerinde yüzde 100 tamamlanmış olarak görünmüştür.

Ancak kapatılan 11 işin tamamı geliştirilerek tamamlanmamıştır. On iş başarıyla tamamlanırken, #23 numaralı temel MVP test senaryoları çalışmasının ayrı bir backlog maddesi olarak devam ettirilmesinden vazgeçilmiş ve çalışma `Block` durumuna alınmıştır.

Sprint sırasında entegrasyon ve son ürün kontrolleri sonucunda ortaya çıkan ek ihtiyaçlar da ayrı branch ve pull request'ler üzerinden ele alınmıştır. Bu kapsamda tema sistemi, analiz geçmişi, gerçek kullanıcı fikirlerinin yüklenmesi, hesap ayarları, e-posta doğrulama, parola sıfırlama, mentor yanıtlarında Markdown desteği, Makefile, gerçek zamanlı workflow ilerleme takibi ve metin tabanlı PDF rapor çıktısı gibi tamamlayıcı geliştirmeler gerçekleştirilmiştir.

Sprint 3 teknik geliştirme milestone'u kapatıldıktan sonra final dokümantasyonu ve teslim süreci ayrı bir `Final Delivery` milestone'u üzerinden devam ettirilmiştir. Bu milestone altında yer alan #40 numaralı Sprint 3 ve final proje dokümantasyonu ile #41 numaralı demo videosu ve Bootcamp teslimi işleri sprint kapanışı sırasında `In Progress` durumundadır.

### Daily Scrum Notları

Sprint 3 boyunca ekip içi iletişim ve ilerleme takibi Slack, WhatsApp, GitHub Issues, pull request'ler ve Project Board üzerinden yürütülmüştür. Ekip üyeleri üzerinde çalıştıkları görevleri, tamamlanan geliştirmeleri, karşılaştıkları teknik sorunları ve sonraki adımlarını bu kanallar üzerinden paylaşmıştır.

Daily Scrum görüşmeleri ve yazılı durum güncellemelerinde ağırlıklı olarak aşağıdaki konular takip edilmiştir:

- Sprint 2’den aktarılan frontend ve backend entegrasyon çalışmalarının durumu
- Analiz sonuçlarının dashboard ve rapor ekranlarına bağlanması
- Farklı doğrulama modüllerinin tek bir workflow altında birleştirilmesi
- RAG kaynaklarının analiz servisleriyle entegrasyonu
- Müşteri görüşme notları için backend CRUD API ve frontend yönetim akışının geliştirilmesi
- Görüşme notlarından kanıt ve içgörü üretilmesi
- Fikir doğrulama raporunun oluşturulması ve PDF dışa aktarımının geliştirilmesi
- Yüklenme, hata, boş durum ve responsive arayüz kontrolleri
- Yetkilendirme, kullanıcı sahipliği ve başarısız istek senaryolarının kontrol edilmesi
- Kullanıcı hesabı, e-posta doğrulama ve parola sıfırlama akışlarının tamamlanması
- Gerçek zamanlı doğrulama ilerleme bilgisinin kullanıcıya gösterilmesi
- Kullanılmayan frontend özellikleri ve endpointlerin temizlenmesi
- Makefile ile geliştirme ve proje yaşam döngüsü komutlarının kolaylaştırılması
- Production ortamı ve deployment yapılandırmalarının hazırlanması
- Sprint 3 dokümantasyonu, demo videosu ve final teslim hazırlıkları

Sprintin ilk bölümünde temel öncelik, önceki sprintlerde ayrı ayrı geliştirilen backend, yapay zekâ ve frontend parçalarının birbiriyle uyumlu hale getirilmesi olmuştur. Entegrasyon sırasında ortaya çıkan eksik durumlar ve kullanıcı deneyimi sorunları ayrı commit ve pull request'ler üzerinden ele alınmıştır.

Sprint ilerledikçe görüşme notları, kanıt analizi, doğrulama raporu ve RAG entegrasyonu gibi çalışmalar tamamlanarak Project Board üzerinde `Done` durumuna taşınmıştır. Pull request açılan çalışmalar birleştirme öncesinde `In Review`, aktif olarak devam eden çalışmalar ise `In Progress` durumunda takip edilmiştir.

#23 numaralı temel MVP test senaryoları çalışmasının ayrı bir backlog maddesi olarak devam ettirilmemesine karar verilmiştir. Bu iş tamamlanmış olarak gösterilmemiş, Project Board üzerinde `Block` durumuna alınmıştır.

Sprint 3 teknik geliştirme işleri tamamlandıktan sonra #40 numaralı Sprint 3 ve final proje dokümantasyonu ile #41 numaralı demo videosu ve final Bootcamp teslimi çalışmaları ayrı `Final Delivery` milestone'u altında takip edilmeye başlanmıştır.

Sprint boyunca ortaya çıkan engeller ve entegrasyon sorunları ekip içinde değerlendirilmiş; gerekli düzeltmeler yeni branch, commit ve pull request'lerle ana geliştirme akışına dahil edilmiştir. Daily Scrum iletişimi yalnızca görev durumlarının paylaşılması için değil, frontend-backend bağımlılıklarının belirlenmesi, ürün kapsamının korunması ve final teslim önceliklerinin netleştirilmesi amacıyla da kullanılmıştır.

### Sprint Board Güncellemeleri

Sprint 3 boyunca görevlerin durumu GitHub Project Board üzerinden takip edilmiştir. Issue'lar geliştirme sürecindeki durumlarına göre `To Do`, `In Progress`, `In Review`, `Done` ve `Block` sütunları arasında güncellenmiştir.

Sprint başlangıcında Sprint 2’den aktarılan #22 ve #23 numaralı çalışmalar ile Sprint 3 Milestone kapsamında oluşturulan #31–#39 numaralı issue'lar board üzerinde takip edilmiştir. Geliştirmesine başlanan işler `In Progress`, pull request'i açılan ve birleştirme bekleyen işler `In Review`, geliştirmesi ve kontrolleri tamamlanan işler ise `Done` durumuna taşınmıştır.

Sprint sonunda board ve milestone üzerinde gerçekleştirilen başlıca güncellemeler aşağıdaki gibidir:

- **#22 – Integrate Analysis Results into Dashboard UI:** Sprint 2’den aktarılan çalışma tamamlanarak `Done` durumuna taşındı.
- **#23 – Add Basic Test Scenarios for Sprint 2 MVP Flow:** Ayrı bir backlog maddesi olarak devam ettirilmesinden vazgeçildi. Tamamlanmış olarak gösterilmeden `Block` durumuna alındı.
- **#31 – Integrate RAG Sources into Analysis Services:** Tamamlanarak `Done` durumuna taşındı.
- **#32 – Orchestrate Validation Modules into a Single Workflow:** Tamamlanarak `Done` durumuna taşındı.
- **#33 – Add Interview Notes Model and CRUD API:** Tamamlanarak `Done` durumuna taşındı.
- **#34 – Generate Evidence and Insights from Interview Notes:** Tamamlanarak `Done` durumuna taşındı.
- **#35 – Add Interview Notes and Evidence Insights UI:** Tamamlanarak `Done` durumuna taşındı.
- **#36 – Build Consolidated Idea Validation Report:** Tamamlanarak `Done` durumuna taşındı.
- **#37 – Finalize Loading, Error, Empty and Responsive UI States:** Tamamlanarak `Done` durumuna taşındı.
- **#38 – Prepare Production Deployment and Environment Configuration:** Tamamlanarak `Done` durumuna taşındı.
- **#39 – Add Authorization, Ownership and Failure Scenario Tests:** Tamamlanarak `Done` durumuna taşındı.

Sprint 3 Milestone içerisindeki 11 issue'nun tamamı kapatıldığı için milestone GitHub üzerinde yüzde 100 tamamlanmış olarak görünmektedir. Bununla birlikte kapatılan işlerden #23 tamamlanmış bir geliştirme değildir; kapsamdan çıkarıldığı için `Block` durumunda tutulmaktadır. Sprint 3 kapsamında planlanan diğer 10 çalışma tamamlanmıştır.

Sprint 3 teknik geliştirme süreci sonrasında final dokümantasyonu ve teslim hazırlıkları ayrı bir `Final Delivery` milestone'u altında takip edilmeye başlanmıştır:

- **#40 – Prepare Sprint 3 and final project documentation:** `In Progress`
- **#41 – Prepare demo video and final Bootcamp submission:** `In Progress`

Paylaşılan güncel Project Board görüntüsünde durum dağılımı aşağıdaki şekildedir:

- `To Do`: 0
- `In Progress`: 2
- `In Review`: 0
- `Done`: 29
- `Block`: 1

`Done` sütunundaki 29 iş yalnızca Sprint 3 çalışmalarını değil, proje boyunca önceki sprintlerde tamamlanan issue'ları da kapsamaktadır. `In Progress` sütunundaki iki çalışma final teslim hazırlıklarına, `Block` sütunundaki tek çalışma ise #23 numaralı kapsamdan çıkarılan işe aittir.

Sprint sonunda teknik geliştirme backlog'u kapatılmış; devam eden çalışmalar ürün geliştirmesinden ziyade dokümantasyon, demo videosu ve final Bootcamp teslimi üzerine yoğunlaşmıştır.

#### Sprint Board Ekran Görüntüsü

Sprint 3 sonundaki Project Board ve Milestone durumu `docs/sprint-3/screenshots/` klasörü altında paylaşılmaktadır.

### Ürün Durumu

Sprint 3 sonunda ürün, önceki sprintlerde ayrı ayrı geliştirilen backend, frontend, yapay zekâ ve RAG bileşenlerinin bir araya getirildiği, kullanıcı tarafından uçtan uca deneyimlenebilen bir MVP seviyesine ulaşmıştır.

Kullanıcı, uygulama üzerinden hesap oluşturabilmekte, e-posta adresini doğrulayabilmekte ve giriş yapabilmektedir. Parola sıfırlama, parola değiştirme ve kullanıcı profil bilgilerini güncelleme akışları da ürün içerisine dahil edilmiştir.

Giriş yapan kullanıcı kendisine ait iş fikirlerini oluşturabilmekte, listeleyebilmekte, görüntüleyebilmekte, güncelleyebilmekte ve silebilmektedir. Aktif fikir yönetimi iyileştirilmiş; silinen veya artık erişilemeyen bir fikrin analiz, mentor ve rapor ekranlarında hatalı istekler oluşturmasının önüne geçilmiştir.

Kullanıcının oluşturduğu fikir için aşağıdaki yapay zekâ destekli doğrulama çıktıları üretilebilmektedir:

- Fikrin temel analizi ve riskli varsayımları
- Mom Test yaklaşımına uygun müşteri görüşme soruları
- MoSCoW yöntemiyle MVP kapsam analizi
- Fikir doğrulama yol haritası
- Rakip ve pazar analizi
- Yatırımcı sunumu hazırlama desteği
- AI mentor üzerinden fikir odaklı yönlendirmeler

Bu analiz modülleri tek bir doğrulama workflow'u altında birleştirilmiştir. Uzun süren analiz işlemlerinde kullanıcıya işlemin hangi aşamada olduğu hakkında gerçek zamanlı ilerleme bilgisi gösterilmektedir.

RAG altyapısı analiz servisleriyle bütünleştirilmiş; girişimcilik ve fikir doğrulama kaynaklarının model yanıtlarında kullanılabilmesi sağlanmıştır. Ayrıca YouTube kaynaklarının sisteme alınması, parçalanması ve yanıt servisinde kullanılmasına yönelik RAG ingestion akışı geliştirilmiştir.

Müşteri görüşmelerinden elde edilen bilgilerin yalnızca kullanıcı tarafında tutulması yerine doğrulama sürecinin bir parçası haline getirilmesi sağlanmıştır. Kullanıcı görüşme notlarını ekleyebilmekte, düzenleyebilmekte ve silebilmektedir. Yapay zekâ servisi bu notlardan kanıtlar, içgörüler ve fikir doğrulamasında kullanılabilecek değerlendirmeler oluşturabilmektedir.

Fikir analizi, MVP kapsamı, doğrulama yol haritası, görüşme kanıtları ve diğer sonuçlar bütünleşik doğrulama raporu ekranında bir araya getirilmiştir. Rapor, metin tabanlı ve düzenlenmiş bir PDF çıktısı olarak dışa aktarılabilmektedir.

Frontend tarafında ürün bütünlüğünü ve kullanıcı deneyimini geliştirmek amacıyla aşağıdaki çalışmalar tamamlanmıştır:

- Gerçek kullanıcı fikirlerinin ve analiz geçmişinin yüklenmesi
- Açık ve koyu tema desteği
- Responsive ekran düzenlemeleri
- Yüklenme, hata ve boş durum ekranları
- Mentor mesajlarında Markdown gösterimi
- Formların klavye ile gönderilebilmesi
- Parola alanlarında görünürlük kontrolü
- Hesap ayarları ekranı
- Kullanılmayan frontend özelliklerinin ve endpointlerin temizlenmesi

Backend tarafında kullanıcı sahipliği ve yetkilendirme kontrolleri uygulanmıştır. Kullanıcıların başka kullanıcılara ait fikir, analiz ve görüşme notlarına erişmesi engellenmiş; başarısız istekler ve hata senaryoları için gerekli kontroller hazırlanmıştır.

Projenin geliştirme sürecini kolaylaştırmak amacıyla Makefile eklenmiş ve sık kullanılan proje yaşam döngüsü komutları merkezi hale getirilmiştir. Production ortam değişkenleri, e-posta ayarları, güvenlik yapılandırmaları ve deployment için gerekli teknik hazırlıklar gerçekleştirilmiştir.

Sprint sonunda ürünün temel özellikleri çalışır ve birbiriyle entegre durumdadır. Bununla birlikte ürün henüz canlı bir production adresinde yayınlanmamıştır. Canlıya alma, son dokümantasyon, demo videosu ve Bootcamp teslim işlemleri ayrı `Final Delivery` milestone'u altında devam etmektedir.


### Sprint Review

Sprint 3 sonunda takım; ürünün kullanıcı akışını, tamamlanan teknik geliştirmeleri, Sprint 3 Milestone durumunu ve final teslim hazırlıklarını değerlendirmiştir.

Bu sprintte temel amaç, önceki sprintlerde geliştirilen backend, frontend, yapay zekâ ve RAG bileşenlerini tek bir ürün akışı içerisinde birleştirmekti. Sprint sonunda kullanıcıların kayıt ve giriş işlemlerinden başlayarak fikir oluşturabildiği, yapay zekâ destekli doğrulama analizlerini çalıştırabildiği, müşteri görüşme notlarını yönetebildiği ve sonuçları bütünleşik rapor üzerinden inceleyebildiği uçtan uca MVP akışı oluşturulmuştur.

Sprint kapsamında tamamlanan başlıca çalışmalar şunlardır:

- Sprint 2’den aktarılan analiz sonuçlarının frontend kullanıcı arayüzüne entegrasyonu tamamlandı.
- Ayrı çalışan doğrulama modülleri merkezi bir workflow altında birleştirildi.
- RAG kaynakları yapay zekâ analiz servislerine entegre edildi.
- Müşteri görüşme notları için backend veri modeli ve CRUD API geliştirildi.
- Görüşme notlarının eklenmesi, düzenlenmesi ve silinmesi için frontend akışı hazırlandı.
- Görüşme notlarından kanıt ve içgörü üreten yapay zekâ servisi geliştirildi.
- Analiz ve görüşme sonuçlarını bir araya getiren bütünleşik fikir doğrulama raporu oluşturuldu.
- Doğrulama raporunun PDF olarak dışa aktarılması sağlandı.
- Yüklenme, hata, boş durum ve responsive arayüz davranışları iyileştirildi.
- Kullanıcı sahipliği, yetkilendirme ve başarısız istek senaryolarına yönelik kontroller tamamlandı.
- Hesap ayarları, e-posta doğrulama, parola değiştirme ve parola sıfırlama akışları ürüne dahil edildi.
- Kullanılmayan veya güncelliğini kaybeden frontend özellikleri ve endpointler temizlendi.
- Uzun süren doğrulama işlemleri için gerçek zamanlı ilerleme takibi eklendi.
- Sık kullanılan geliştirme, test ve proje yaşam döngüsü komutlarını kolaylaştırmak amacıyla Makefile hazırlandı.
- Production ortamı ve deployment için gerekli yapılandırmalar oluşturuldu.

Sprint 3 Milestone kapsamında takip edilen 11 issue'nun tamamı kapatılmıştır. Bu issue'lardan 10'u geliştirilerek tamamlanmış ve Project Board üzerinde `Done` durumuna taşınmıştır.

#23 numaralı temel MVP test senaryoları çalışmasının ise ayrı bir backlog maddesi olarak devam ettirilmesinden süreç içerisinde vazgeçilmiştir. Bu çalışma tamamlanmış gibi gösterilmemiş, Project Board üzerinde `Block` durumuna alınmıştır. Milestone'un GitHub üzerinde yüzde 100 görünmesi, milestone içerisindeki bütün issue'ların kapatılmış olmasından kaynaklanmaktadır.

Sprint Review sonucunda ürünün temel MVP kapsamının tamamlandığı ve kullanıcı tarafından uçtan uca deneyimlenebilir duruma geldiği değerlendirilmiştir. Önceki sprintlerde görülen frontend-backend entegrasyon eksikliği büyük ölçüde giderilmiş, ayrı geliştirilen modüller ürün bütünlüğü içerisinde birleştirilmiştir.

Sprint sonunda teknik geliştirme ağırlıklı Sprint 3 Milestone kapatılmıştır. Kalan çalışmalar ürünün temel fonksiyonlarının geliştirilmesinden ziyade aşağıdaki final teslim faaliyetlerine odaklanmaktadır:

- Sprint 3 ve final proje dokümantasyonunun tamamlanması
- Güncel ürün ekran görüntülerinin ve demo kayıtlarının hazırlanması
- Üç dakikalık proje tanıtım videosunun oluşturulması
- Final Bootcamp teslim formunun doldurulması
- Canlı ortam ve erişim bilgilerinin kesinleştirilmesi

Bu çalışmalar #40 ve #41 numaralı issue'lar üzerinden ayrı `Final Delivery` milestone'u altında takip edilmektedir.

Sprint Review sonunda ürünün yarışmaya sunulabilecek temel teknik seviyeye ulaştığı, final teslim öncesinde ise dokümantasyon, demo, canlı ortam kontrolleri ve sunum hazırlıklarının tamamlanması gerektiği sonucuna varılmıştır.

#### Sprint Retrospective

Sprint 3 sonunda takım; teknik geliştirme sürecini, entegrasyon çalışmalarını, görev yönetimini, ürün kapsamını ve final teslim hazırlıklarını birlikte değerlendirmiştir.

Bu sprintte önceki sprintlerden farklı olarak yalnızca bağımsız özelliklerin geliştirilmesine değil, geliştirilen bütün parçaların gerçek bir kullanıcı akışı içerisinde birlikte çalışmasına odaklanılmıştır. Frontend, backend, yapay zekâ ve RAG bileşenlerinin birleştirilmesi sırasında ortaya çıkan eksikler giderilmiş ve ürünün temel MVP akışı büyük ölçüde tamamlanmıştır.

#### İyi Giden Noktalar

- Sprint 2’den aktarılan analiz sonuçlarının frontend entegrasyonu tamamlandı.
- Ayrı ayrı geliştirilen analiz modülleri merkezi bir doğrulama workflow'u altında birleştirildi.
- RAG altyapısı analiz servisleriyle entegre edilerek ürün içerisinde işlevsel biçimde kullanılmaya başlandı.
- Müşteri görüşme notları için backend ve frontend tarafında bütünleşik bir yönetim akışı oluşturuldu.
- Görüşme notlarından kanıt ve içgörü üreten yapay zekâ özelliği doğrulama sürecine dahil edildi.
- Analiz sonuçlarını ve görüşme kanıtlarını bir araya getiren bütünleşik rapor ekranı hazırlandı.
- Raporların PDF olarak dışa aktarılması sağlandı.
- Yüklenme, hata, boş durum ve responsive arayüz davranışları iyileştirildi.
- E-posta doğrulama, parola sıfırlama, parola değiştirme ve hesap ayarları gibi kullanıcı hesabı akışları tamamlandı.
- Kullanıcı sahipliği, yetkilendirme ve başarısız istek senaryoları daha kapsamlı şekilde kontrol edildi.
- Gerçek zamanlı workflow ilerleme takibi sayesinde uzun süren analiz işlemleri kullanıcı açısından daha anlaşılır hale getirildi.
- Kullanılmayan frontend özellikleri ve eski endpointler temizlenerek ürün bütünlüğü artırıldı.
- Makefile eklenerek sık kullanılan geliştirme ve proje yaşam döngüsü komutlarının daha düzenli yönetilmesi sağlandı.
- Görevler issue, branch, commit, pull request, milestone ve Project Board üzerinden takip edildi.
- Sprint 3 kapsamında tamamlanan çalışmalar `Done`, kapsamdan çıkarılan çalışma ise `Block` durumunda açıkça gösterildi.

#### Karşılaşılan Zorluklar

- Önceki sprintlerde frontend ve backend çalışmalarının farklı hızlarda ilerlemesi, Sprint 3 içerisinde yoğun bir entegrasyon yükü oluşturdu.
- Ayrı geliştirilen modüllerin tek bir kullanıcı akışında birleştirilmesi sırasında beklenmeyen veri akışı ve durum yönetimi sorunları ortaya çıktı.
- Aktif fikir yönetimi, silinen fikirler, eski isteklerin sonuçları ve farklı sayfalardaki bağımlı API çağrıları ek düzenlemeler gerektirdi.
- Entegrasyon sırasında ilk backlog planında yer almayan kullanıcı hesabı, e-posta doğrulama, parola yönetimi ve arayüz iyileştirmeleri gibi tamamlayıcı ihtiyaçlar ortaya çıktı.
- Sprint kapsamının genişlemesi, dokümantasyon, demo ve final teslim çalışmalarının teknik geliştirmelerle paralel yürütülmesini zorlaştırdı.
- Production yapılandırmaları hazırlanmasına rağmen canlıya alma işlemi sprint kapanışı sırasında henüz kesinleştirilemedi.
- #23 numaralı temel MVP test senaryoları çalışmasının ayrı bir backlog maddesi olarak sürdürülmesinden vazgeçildi. Bu iş tamamlanmış kabul edilmeden `Block` durumuna alındı.
- Sprint milestone'unun yalnızca kapatılan issue sayısına göre yüzde 100 görünmesi, tamamlanan ve kapsamdan çıkarılan işlerin ayrıca açıklanması gerektiğini gösterdi.

#### Öğrenilenler

- Frontend ve backend entegrasyonu sprintin sonuna bırakılmamalı, özellikler tamamlandıkça küçük parçalar halinde doğrulanmalıdır.
- Bir özelliğin yalnızca backend veya frontend tarafında tamamlanması, ürün açısından tamamlandığı anlamına gelmemektedir.
- Issue açıklamalarında bağımlılıklar, beklenen API yapıları, hata durumları ve kabul kriterleri daha erken tanımlanmalıdır.
- Kullanıcı akışındaki yüklenme, boş durum, yetkilendirme ve silinmiş veri senaryoları geliştirme başlangıcından itibaren ele alınmalıdır.
- Sprint backlog'u hazırlanırken yalnızca yeni özellikler değil, entegrasyon, temizlik, test, dokümantasyon ve deployment çalışmaları için de zaman ayrılmalıdır.
- Kapatılan her issue'nun tamamlanmış olduğu varsayılmamalı; `Done` ve `Block` durumları ayrı biçimde raporlanmalıdır.
- Final dokümantasyonu ve demo hazırlıkları sprintin son günlerine bırakılmadan geliştirme süreciyle paralel yürütülmelidir.
- Projenin kurulum ve geliştirme komutlarının Makefile gibi merkezi bir yapı üzerinden sunulması ekip içi kullanım ve teslim kolaylığı sağlamaktadır.

#### Final Teslim İçin Aksiyonlar

- Sprint 3 ve final proje dokümantasyonu tamamlanacaktır.
- README içerisindeki ürün özellikleri, Product Backlog, proje yapısı, kullanılan teknolojiler ve kurulum adımları güncel proje yapısına göre yenilenecektir.
- Makefile içerisinde yer alan komutlar doğrulanarak kurulum ve geliştirme dokümantasyonuna eklenecektir.
- Güncel ürün ekran görüntüleri ve demo kayıtları `docs/sprint-3/` klasörüne eklenecektir.
- Üç dakikalık proje tanıtım videosu hazırlanacaktır.
- Final ürün akışı teslim öncesinde uçtan uca yeniden kontrol edilecektir.
- Public repository, proje videosu, canlı bağlantı ve teslim formu bilgileri kesinleştirilecektir.
- Deployment gerçekleştirilebilirse canlı bağlantı teslim dokümantasyonuna eklenecektir.
- #40 ve #41 numaralı final teslim çalışmaları `Final Delivery` milestone'u üzerinden tamamlanacaktır.

Sprint Retrospective sonucunda takım, ürünün temel MVP hedeflerine ulaştığını; ancak başarılı bir final teslim için dokümantasyon, demo videosu, son kullanıcı akışı kontrolleri ve deployment çalışmalarının tamamlanması gerektiğini değerlendirmiştir.

## Proje Teslim Bilgileri

| Teslim Kalemi | Durum |
|---|---|
| GitHub reposu | Hazır |
| Public repo | Hazır – <https://github.com/erenylldz/YZTA---Team-138> |
| Sprint 3 ürün durumu videosu | Çekildi, repository'ye yüklenmesi bekleniyor |
| Ürün demosu | Planlanıyor |
| Canlı link | Henüz bulunmuyor |
| Proje videosu | Hazırlanıyor |
| Final raporu ve dokümantasyon | Hazırlanıyor |

## Lisans

Belirlenecek.
