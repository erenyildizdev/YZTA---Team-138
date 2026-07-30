import re
import unicodedata
from contextlib import ExitStack
from io import BytesIO
from unittest.mock import patch
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pypdf import PdfReader
from rest_framework import status
from rest_framework.test import APITestCase

from apps.analyses.models import (
    MomTestQuestionsAnalysis,
    MoscowScopeAnalysis,
)
from apps.analyses.services.report_pdf import build_report_filename
from apps.ideas.models import (
    CompetitorAnalysis,
    GeneralEvaluation,
    Idea,
    InvestorPitch,
    RiskyAssumptions,
    ValidationRoadmap,
)


TURKISH_SENTINEL = "ÇĞİÖŞÜ çğıöşü — Iğdır ve İstanbul"
OTHER_USER_SECRET = "BASKA-KULLANICI-GIZLI-987654"

REPORT_SECTION_HEADINGS = (
    "Fikir Özeti",
    "Problem ve Hedef Kitle",
    "Riskli Varsayımlar",
    "Müşteri Görüşme Soruları",
    "MVP Kapsamı (MoSCoW)",
    "Doğrulama Yol Haritası",
    "Genel Değerlendirme",
    "Rakip / Pazar Analizi",
    "Yatırımcı Sunumu",
    "Kullanılan Kaynaklar",
)

ROADMAP_SECTION_KEYS = (
    "İlk görüşmeler",
    "Test edilecek varsayımlar",
    "MVP öncelikleri",
    "Başarı metrikleri",
    "Sonraki karar noktaları",
)


def normalized_text(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def dereference(value):
    return value.get_object() if hasattr(value, "get_object") else value


def content_disposition_filename(header):
    extended_match = re.search(
        r"filename\*\s*=\s*UTF-8''([^;]+)",
        header,
        flags=re.IGNORECASE,
    )
    if extended_match:
        return unquote(extended_match.group(1), encoding="utf-8")

    quoted_match = re.search(
        r'filename\s*=\s*"((?:[^"\\]|\\.)*)"',
        header,
        flags=re.IGNORECASE,
    )
    if quoted_match:
        return re.sub(r"\\(.)", r"\1", quoted_match.group(1))

    plain_match = re.search(
        r"filename\s*=\s*([^;]+)",
        header,
        flags=re.IGNORECASE,
    )
    if plain_match:
        return plain_match.group(1).strip()

    raise AssertionError(
        f"Content-Disposition has no filename: {header!r}"
    )


class ReportPdfFixtureMixin:
    @staticmethod
    def create_idea(
        user,
        *,
        title="Çevik Çözüm İstasyonu",
        description=None,
        target_audience=None,
        problem=None,
        solution=None,
        sector="Teknoloji",
        sources=None,
    ):
        return Idea.objects.create(
            user=user,
            title=title,
            description=(
                description
                or f"FİKİR-ÖZETİ: {TURKISH_SENTINEL}"
            ),
            target_audience=(
                target_audience
                or "HEDEF-KİTLE: Erken aşama girişimciler"
            ),
            problem=(
                problem
                or "PROBLEM-İÇERİĞİ: Dağınık doğrulama süreçleri"
            ),
            solution=solution or "Çözüm: tek ve ölçülebilir bir akış",
            sector=sector,
            rag_sources=(
                sources
                if sources is not None
                else [
                    {
                        "title": "KAYNAK-İÇERİĞİ: Mom Test Eğitimi",
                        "source_type": "youtube",
                        "source_url": "https://example.com/mom-test",
                        "chunk_id": 11,
                        "chunk_index": 0,
                        "distance": 0.1,
                    },
                    {
                        "title": "MVP Kapsamı Rehberi",
                        "source_type": "text",
                        "source_url": "https://example.com/mvp",
                        "chunk_id": 12,
                        "chunk_index": 1,
                        "distance": 0.2,
                    },
                ]
            ),
        )

    @staticmethod
    def seed_core_analyses(idea, *, compact=False):
        assumptions = [
            {
                "text": "RİSK-İÇERİĞİ: Kullanıcılar haftalık görüşme yapar",
                "level": "high",
                "status": "validated",
                "evidence_quote": (
                    "RİSK-KANITI: Görüşmeler düzenli yapılacak"
                ),
            },
        ]
        questions = [
            {
                "category": "problem_context",
                "question": (
                    "MOM-SORUSU: Son kez ne zaman bu sorunu yaşadınız?"
                ),
            },
        ]

        if not compact:
            assumptions.extend(
                {
                    "text": f"Riskli varsayım {index}",
                    "level": "medium",
                    "status": "untested",
                }
                for index in range(2, 6)
            )
            questions.extend(
                {
                    "category": f"category_{index}",
                    "question": f"Müşteri görüşme sorusu {index}?",
                }
                for index in range(2, 11)
            )

        RiskyAssumptions.objects.create(
            idea=idea,
            assumptions_data={"assumptions": assumptions},
        )
        MomTestQuestionsAnalysis.objects.create(
            idea=idea,
            questions=questions,
        )
        MoscowScopeAnalysis.objects.create(
            idea=idea,
            result={
                "summary": (
                    "MOSCOW-ÖZETİ: Önce temel doğrulama akışı kurulmalı"
                ),
                "must_have": [
                    {
                        "title": "MOSCOW-MUST: Fikir kaydı",
                        "reason": "Temel girdi gereklidir.",
                    }
                ],
                "should_have": [
                    {
                        "title": "MOSCOW-SHOULD: Analiz geçmişi",
                        "reason": "Karşılaştırma sağlar.",
                    }
                ],
                "could_have": [
                    {
                        "title": "MOSCOW-COULD: Ekip paylaşımı",
                        "reason": "İş birliği sağlar.",
                    }
                ],
                "wont_have": [
                    {
                        "title": "MOSCOW-WONT: Ödeme altyapısı",
                        "reason": "İlk sürüm kapsamında değildir.",
                    }
                ],
            },
            provider="test-provider",
            model_name="test-model",
        )

        phase_count = 1 if compact else 3
        ValidationRoadmap.objects.create(
            idea=idea,
            roadmap_data={
                "roadmap_type": "validation",
                "idea_title": idea.title,
                "phases": [
                    {
                        "week": week,
                        "title": (
                            f"ROADMAP-AŞAMA-{week}: Görüşme döngüsü"
                        ),
                        **{
                            key: [
                                (
                                    f"ROADMAP-İÇERİĞİ-{week}-{index}: "
                                    f"{key} maddesi"
                                )
                                for index in (
                                    range(1, 2)
                                    if compact
                                    else range(1, 3)
                                )
                            ]
                            for key in ROADMAP_SECTION_KEYS
                        },
                    }
                    for week in range(1, phase_count + 1)
                ],
            },
        )
        GeneralEvaluation.objects.create(
            idea=idea,
            evaluation_data={
                "strengths": [
                    "GENEL-GÜÇ: Net bir problem tanımı",
                ],
                "uncertainties": [
                    "GENEL-BELİRSİZLİK: Görüşme sıklığı",
                ],
                "next_action": (
                    "GENEL-AKSİYON: Beş kullanıcıyla görüş"
                ),
            },
        )

    @classmethod
    def seed_optional_analyses(cls, idea):
        CompetitorAnalysis.objects.create(
            idea=idea,
            analysis_data={
                "competitors": [
                    {
                        "name": "RAKİP-ADI: Doğrula AŞ",
                        "description": (
                            "RAKİP-TANIMI: Benzer doğrulama ürünü"
                        ),
                        "strengths": [
                            "RAKİP-GÜÇ: Yerleşik kullanıcı tabanı",
                        ],
                        "weaknesses": [
                            "RAKİP-ZAYIFLIK: Karmaşık iş akışı",
                        ],
                    },
                    {
                        "name": "İkinci Rakip",
                        "description": "Manuel çalışma sayfası",
                        "strengths": ["Kolay erişim"],
                        "weaknesses": ["Otomasyon eksikliği"],
                    },
                    {
                        "name": "Üçüncü Rakip",
                        "description": "Genel proje aracı",
                        "strengths": ["Esnek kullanım"],
                        "weaknesses": ["Doğrulama odağı yok"],
                    },
                ],
                "market_gap": (
                    "PAZAR-BOŞLUĞU: Türkçe rehberli akış eksik"
                ),
                "differentiation": (
                    "FARKLILAŞMA: Kanıta dayalı tek akış"
                ),
            },
        )
        InvestorPitch.objects.create(
            idea=idea,
            pitch_data={
                "elevator_pitch": (
                    "PITCH-ELEVATOR: Fikirleri kanıtla buluşturan platform"
                ),
                "slides": [
                    {
                        "title": f"PITCH-SLAYT-{index}",
                        "bullets": [
                            f"PITCH-MADDE-{index}-1",
                            f"PITCH-MADDE-{index}-2",
                        ],
                    }
                    for index in range(1, 7)
                ],
                "closing_ask": (
                    "PITCH-TALEP: Üç pilot müşteriyle tanışma"
                ),
            },
        )

    @classmethod
    def seed_complete_report(cls, idea):
        cls.seed_core_analyses(idea)
        cls.seed_optional_analyses(idea)

    @classmethod
    def create_long_report(cls, user):
        tokens = []
        token_index = 0

        def long_text(label):
            nonlocal token_index
            token_index += 1
            token = f"UZUN{token_index:04d}"
            tokens.append(token)
            return (
                f"{token} {label}: "
                + (
                    "Türkçe karakterlerle ölçülebilir doğrulama cümlesi "
                    "satıra güvenle sığmalıdır. "
                )
                * 3
            )

        idea = cls.create_idea(
            user,
            title="Uzun Çok Sayfalı Doğrulama Raporu",
            description=long_text("Fikir özeti"),
            problem=long_text("Problem"),
            target_audience=long_text("Hedef kitle"),
            solution="Uzun rapor test çözümü",
            sources=[],
        )

        RiskyAssumptions.objects.create(
            idea=idea,
            assumptions_data={
                "assumptions": [
                    {
                        "text": long_text(f"Risk {index}"),
                        "level": "high" if index < 3 else "medium",
                        "status": "validated",
                        "evidence_quote": long_text(
                            f"Risk kanıtı {index}"
                        ),
                    }
                    for index in range(1, 6)
                ]
            },
        )
        MomTestQuestionsAnalysis.objects.create(
            idea=idea,
            questions=[
                {
                    "category": f"category_{index}",
                    "question": long_text(f"Mom Test sorusu {index}"),
                }
                for index in range(1, 11)
            ],
        )
        MoscowScopeAnalysis.objects.create(
            idea=idea,
            result={
                "summary": long_text("MoSCoW özeti"),
                **{
                    category: [
                        {
                            "title": long_text(
                                f"{category} özellik {index}"
                            ),
                            "reason": "Uzun rapor gerekçesi",
                        }
                        for index in range(1, 3)
                    ]
                    for category in (
                        "must_have",
                        "should_have",
                        "could_have",
                        "wont_have",
                    )
                },
            },
            provider="test-provider",
            model_name="test-model",
        )
        ValidationRoadmap.objects.create(
            idea=idea,
            roadmap_data={
                "roadmap_type": "validation",
                "idea_title": idea.title,
                "phases": [
                    {
                        "week": week,
                        "title": long_text(f"Yol haritası {week}"),
                        **{
                            key: [
                                long_text(
                                    f"{key} {week}.{item_index}"
                                )
                                for item_index in range(1, 3)
                            ]
                            for key in ROADMAP_SECTION_KEYS
                        },
                    }
                    for week in range(1, 4)
                ],
            },
        )
        GeneralEvaluation.objects.create(
            idea=idea,
            evaluation_data={
                "strengths": [
                    long_text(f"Güçlü yön {index}")
                    for index in range(1, 4)
                ],
                "uncertainties": [
                    long_text(f"Belirsizlik {index}")
                    for index in range(1, 3)
                ],
                "next_action": long_text("Sonraki aksiyon"),
            },
        )
        CompetitorAnalysis.objects.create(
            idea=idea,
            analysis_data={
                "competitors": [
                    {
                        "name": long_text(f"Rakip {index}"),
                        "description": long_text(
                            f"Rakip açıklaması {index}"
                        ),
                        "strengths": [
                            long_text(
                                f"Rakip {index} güçlü {item_index}"
                            )
                            for item_index in range(1, 3)
                        ],
                        "weaknesses": [
                            long_text(
                                f"Rakip {index} zayıf {item_index}"
                            )
                            for item_index in range(1, 3)
                        ],
                    }
                    for index in range(1, 4)
                ],
                "market_gap": long_text("Pazar boşluğu"),
                "differentiation": long_text("Farklılaşma"),
            },
        )
        InvestorPitch.objects.create(
            idea=idea,
            pitch_data={
                "elevator_pitch": long_text("Elevator pitch"),
                "slides": [
                    {
                        "title": long_text(f"Sunum slaytı {index}"),
                        "bullets": [
                            long_text(
                                f"Slayt {index} madde {item_index}"
                            )
                            for item_index in range(1, 4)
                        ],
                    }
                    for index in range(1, 7)
                ],
                "closing_ask": long_text("Kapanış talebi"),
            },
        )

        final_token_text = long_text("Son kaynak")
        idea.rag_sources = [
            {
                "title": final_token_text,
                "source_type": "text",
                "source_url": "https://example.com/long-final-source",
                "chunk_id": 99,
                "chunk_index": 9,
                "distance": 0.05,
            }
        ]
        idea.save(update_fields=("rag_sources",))

        return idea, tokens


class ValidationReportPdfEndpointTests(
    ReportPdfFixtureMixin,
    APITestCase,
):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(
            username="pdf-owner",
            email="pdf-owner@example.com",
            password="StrongPass123!",
        )
        self.other_user = user_model.objects.create_user(
            username="pdf-other",
            email="pdf-other@example.com",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(self.owner)
        self.seed_complete_report(self.idea)
        self.other_idea = self.create_idea(
            self.other_user,
            title=OTHER_USER_SECRET,
            description=OTHER_USER_SECRET,
            target_audience=OTHER_USER_SECRET,
            problem=OTHER_USER_SECRET,
            solution=OTHER_USER_SECRET,
            sources=[
                {
                    "title": OTHER_USER_SECRET,
                    "source_type": "text",
                    "source_url": "https://example.com/private",
                    "chunk_id": 999,
                    "chunk_index": 0,
                    "distance": 0.01,
                }
            ],
        )
        self.seed_complete_report(self.other_idea)
        self.url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": self.idea.pk},
        )
        self.client.force_authenticate(user=self.owner)

    def parse_pdf_response(self, response):
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertGreater(len(response.content), 1_000)

        reader = PdfReader(BytesIO(response.content), strict=False)
        self.assertFalse(reader.is_encrypted)
        self.assertGreaterEqual(len(reader.pages), 1)
        text = "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )
        return reader, normalized_text(text)

    def assert_all_pages_are_a4(self, reader):
        for page_number, page in enumerate(reader.pages, start=1):
            with self.subTest(page=page_number):
                self.assertAlmostEqual(
                    float(page.mediabox.width),
                    595.28,
                    delta=1.0,
                )
                self.assertAlmostEqual(
                    float(page.mediabox.height),
                    841.89,
                    delta=1.0,
                )

    def assert_pdf_has_no_image_xobjects(self, reader):
        visited = set()

        def visit_resources(resources):
            resources = dereference(resources)
            if not resources:
                return

            xobjects = dereference(resources.get("/XObject"))
            if not xobjects:
                return

            for xobject_reference in xobjects.values():
                xobject = dereference(xobject_reference)
                object_key = getattr(
                    xobject_reference,
                    "idnum",
                    id(xobject),
                )
                if object_key in visited:
                    continue
                visited.add(object_key)

                subtype = str(xobject.get("/Subtype"))
                self.assertNotEqual(
                    subtype,
                    "/Image",
                    "Report PDF must contain selectable vector text, "
                    "not rasterized page content.",
                )
                if subtype == "/Form":
                    visit_resources(xobject.get("/Resources"))

        for page in reader.pages:
            visit_resources(page.get("/Resources"))

    def assert_pdf_has_no_active_content(self, reader):
        root = dereference(reader.trailer["/Root"])
        names = dereference(root.get("/Names"))
        if names:
            self.assertNotIn("/JavaScript", names)
            self.assertNotIn("/EmbeddedFiles", names)

        self.assertNotIn("/AA", root)

        for page in reader.pages:
            annotations = dereference(page.get("/Annots")) or []
            for annotation_reference in annotations:
                annotation = dereference(annotation_reference)
                action = dereference(annotation.get("/A"))
                if not action:
                    continue
                self.assertNotEqual(
                    str(action.get("/S")),
                    "/JavaScript",
                )
                uri = action.get("/URI")
                if uri is not None:
                    self.assertRegex(
                        str(uri),
                        r"^https?://",
                    )

    def test_owner_receives_parseable_selectable_complete_report(self):
        response = self.client.get(self.url)

        reader, text = self.parse_pdf_response(response)

        disposition = response["Content-Disposition"]
        self.assertTrue(disposition.lower().startswith("attachment;"))
        self.assertEqual(
            content_disposition_filename(disposition),
            build_report_filename(self.idea),
        )
        self.assert_all_pages_are_a4(reader)
        self.assert_pdf_has_no_image_xobjects(reader)
        self.assert_pdf_has_no_active_content(reader)
        self.assertEqual(
            reader.metadata.title,
            f"{self.idea.title} — Doğrulama Raporu",
        )
        self.assertEqual(reader.metadata.author, "FikirLab")
        self.assertEqual(
            reader.metadata.creator,
            "FikirLab ReportLab PDF Service",
        )
        self.assertEqual(
            reader.metadata.subject,
            "Fikir doğrulama ve analiz raporu",
        )
        self.assertTrue(reader.metadata.get("/CreationDate"))

        expected_content = (
            "Doğrulama Raporu",
            self.idea.title,
            TURKISH_SENTINEL,
            self.idea.problem,
            self.idea.target_audience,
            *REPORT_SECTION_HEADINGS,
            "RİSK-İÇERİĞİ",
            "RİSK-KANITI",
            "Yüksek Risk",
            "Doğrulandı",
            "MOM-SORUSU",
            "MOSCOW-ÖZETİ",
            "MOSCOW-MUST",
            "Must Have",
            "Should Have",
            "Could Have",
            "Won’t Have",
            "ROADMAP-AŞAMA-1",
            "ROADMAP-İÇERİĞİ-1-1",
            "GENEL-GÜÇ",
            "GENEL-BELİRSİZLİK",
            "GENEL-AKSİYON",
            "RAKİP-ADI",
            "RAKİP-TANIMI",
            "PAZAR-BOŞLUĞU",
            "FARKLILAŞMA",
            "PITCH-ELEVATOR",
            "PITCH-SLAYT-1",
            "PITCH-MADDE-1-1",
            "PITCH-TALEP",
            "KAYNAK-İÇERİĞİ",
        )
        for expected in expected_content:
            with self.subTest(expected=expected):
                self.assertIn(normalized_text(expected), text)

    def test_authentication_and_owner_scoping_are_enforced(self):
        self.client.force_authenticate(user=None)
        anonymous_response = self.client.get(self.url)
        self.assertEqual(
            anonymous_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.client.force_authenticate(user=self.owner)
        other_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": self.other_idea.pk},
        )
        other_response = self.client.get(other_url)
        self.assertEqual(
            other_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
        self.assertNotIn(
            OTHER_USER_SECRET,
            other_response.content.decode("utf-8", errors="ignore"),
        )

        missing_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": 999_999},
        )
        missing_response = self.client.get(missing_url)
        self.assertEqual(
            missing_response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_report_never_leaks_another_users_data(self):
        response = self.client.get(self.url)
        _, text = self.parse_pdf_response(response)

        self.assertNotIn(OTHER_USER_SECRET, text)

    def test_missing_competitor_and_pitch_use_compact_placeholders(self):
        compact_idea = self.create_idea(
            self.owner,
            title="Kompakt Eksik Analiz Raporu",
            sources=[],
        )
        self.seed_core_analyses(compact_idea, compact=True)
        compact_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": compact_idea.pk},
        )

        response = self.client.get(compact_url)
        reader, text = self.parse_pdf_response(response)

        self.assertIn(
            normalized_text(
                "Bu fikir için henüz rakip/pazar analizi oluşturulmadı."
            ),
            text,
        )
        self.assertIn(
            normalized_text(
                "Bu fikir için henüz yatırımcı sunumu oluşturulmadı."
            ),
            text,
        )
        self.assertLessEqual(
            len(reader.pages),
            4,
            "Missing optional analyses should not create mostly empty pages.",
        )

    def test_missing_and_malformed_core_sections_do_not_break_report(self):
        partial_idea = self.create_idea(
            self.owner,
            title="Eksik Bölümlü Rapor",
            sources={"unexpected": "mapping"},
        )
        RiskyAssumptions.objects.create(
            idea=partial_idea,
            assumptions_data={"assumptions": "not-a-list"},
        )
        MomTestQuestionsAnalysis.objects.create(
            idea=partial_idea,
            questions={"unexpected": "mapping"},
        )
        MoscowScopeAnalysis.objects.create(
            idea=partial_idea,
            result=[],
        )
        ValidationRoadmap.objects.create(
            idea=partial_idea,
            roadmap_data={"phases": "not-a-list"},
        )
        GeneralEvaluation.objects.create(
            idea=partial_idea,
            evaluation_data=[],
        )
        partial_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": partial_idea.pk},
        )

        response = self.client.get(partial_url)
        _, text = self.parse_pdf_response(response)

        for placeholder in (
            "Bu fikir için henüz riskli varsayım analizi oluşturulmadı.",
            "Bu fikir için henüz müşteri görüşme soruları oluşturulmadı.",
            "Bu fikir için henüz MVP kapsamı oluşturulmadı.",
            (
                "Bu fikir için henüz bir doğrulama yol haritası "
                "oluşturulmadı."
            ),
            "Bu fikir için henüz genel değerlendirme oluşturulmadı.",
            (
                "Bu fikir için henüz rakip/pazar analizi "
                "oluşturulmadı."
            ),
            "Bu fikir için henüz yatırımcı sunumu oluşturulmadı.",
        ):
            with self.subTest(placeholder=placeholder):
                self.assertIn(normalized_text(placeholder), text)

    def test_long_report_is_multipage_without_content_cutoff(self):
        long_idea, tokens = self.create_long_report(self.owner)
        long_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": long_idea.pk},
        )

        response = self.client.get(long_url)
        reader, text = self.parse_pdf_response(response)

        self.assertGreaterEqual(len(reader.pages), 3)
        self.assert_all_pages_are_a4(reader)
        self.assert_pdf_has_no_image_xobjects(reader)
        for token in tokens:
            with self.subTest(token=token):
                self.assertEqual(
                    text.count(token),
                    1,
                    f"{token} was omitted, duplicated, or cut off.",
                )

        last_page_text = normalized_text(
            reader.pages[-1].extract_text() or ""
        )
        self.assertIn(tokens[-1], last_page_text)

    def test_xml_markdown_and_pdf_syntax_are_rendered_as_literal_text(self):
        special_idea = self.create_idea(
            self.owner,
            title='Özel <script>alert("başlık")</script> & Rapor',
            description=(
                'XML-SENTINEL <tag attr="x">& değer</tag> '
                '<script>alert("PDF-XSS")</script>'
            ),
            problem=(
                "MARKDOWN-SENTINEL **kalın** _italik_ "
                "[kötü](javascript:alert(1))"
            ),
            target_audience=(
                r"PDF-SENTINEL %PDF-1.7 (parantez) \\ ters-eğik"
            ),
            sources=[],
        )
        self.seed_core_analyses(special_idea, compact=True)
        special_url = reverse(
            "analyses:validation-report-pdf",
            kwargs={"idea_id": special_idea.pk},
        )

        response = self.client.get(special_url)
        reader, text = self.parse_pdf_response(response)

        for expected in (
            'XML-SENTINEL <tag attr="x">& değer</tag>',
            '<script>alert("PDF-XSS")</script>',
            "MARKDOWN-SENTINEL **kalın** _italik_",
            "[kötü](javascript:alert(1))",
            r"PDF-SENTINEL %PDF-1.7 (parantez) \\ ters-eğik",
        ):
            with self.subTest(expected=expected):
                self.assertIn(normalized_text(expected), text)
        self.assert_pdf_has_no_active_content(reader)

    def test_response_uses_safe_bounded_filename(self):
        self.idea.title = (
            "  ../../CON\r\nX-Injected: yes "
            '/ Çılgın:*?"<>| '
            + ("İ" * 180)
        )
        self.idea.save(update_fields=("title",))

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        disposition = response["Content-Disposition"]
        filename = content_disposition_filename(disposition)
        self.assertEqual(filename, build_report_filename(self.idea))
        self.assertNotIn("\r", disposition)
        self.assertNotIn("\n", disposition)
        self.assertTrue(filename.lower().endswith(".pdf"))
        self.assertLessEqual(len(filename.encode("utf-8")), 255)
        self.assertFalse(filename.startswith((".", " ")))
        self.assertFalse(filename.endswith((".", " ")))
        self.assertNotIn("..", filename)
        self.assertFalse(
            set(filename).intersection('\\/:*?"<>|')
        )
        self.assertFalse(
            any(ord(character) < 32 or ord(character) == 127 for character in filename)
        )
        self.assertNotRegex(filename, r"[\u202a-\u202e\u2066-\u2069]")

    def test_report_generation_never_invokes_ai_generators(self):
        generator_names = (
            "generate_risky_assumptions_payload",
            "generate_validation_roadmap_payload",
            "generate_general_evaluation_payload",
            "generate_competitor_analysis_payload",
            "generate_investor_pitch_payload",
            "generate_mom_test_questions",
            "generate_moscow_scope",
        )
        source_targets = (
            "apps.ideas.services.generate_risky_assumptions_payload",
            "apps.ideas.services.generate_validation_roadmap_payload",
            "apps.ideas.services.generate_general_evaluation_payload",
            "apps.ideas.services.generate_competitor_analysis_payload",
            "apps.ideas.services.generate_investor_pitch_payload",
            (
                "apps.analyses.services.mom_test_questions."
                "generate_mom_test_questions"
            ),
            "apps.analyses.services.moscow_scope.generate_moscow_scope",
        )

        with ExitStack() as stack:
            mocks = [
                stack.enter_context(
                    patch(
                        target,
                        side_effect=AssertionError(
                            "PDF generation must not invoke AI."
                        ),
                    )
                )
                for target in source_targets
            ]
            local_mocks = [
                stack.enter_context(
                    patch(
                        (
                            "apps.analyses.services.report_pdf."
                            f"{generator_name}"
                        ),
                        create=True,
                        side_effect=AssertionError(
                            "PDF generation must not invoke AI."
                        ),
                    )
                )
                for generator_name in generator_names
            ]

            response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for generator_mock in (*mocks, *local_mocks):
            generator_mock.assert_not_called()

    @patch(
        "apps.analyses.views.build_report_pdf",
        side_effect=RuntimeError("RAW-PDF-SECRET"),
    )
    def test_unexpected_pdf_error_returns_sanitized_500(self, build_pdf):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertNotIn(
            "RAW-PDF-SECRET",
            response.content.decode("utf-8", errors="ignore"),
        )
        build_pdf.assert_called_once()


class ValidationReportFilenameTests(
    ReportPdfFixtureMixin,
    TestCase,
):
    def setUp(self):
        owner = get_user_model().objects.create_user(
            username="pdf-filename-owner",
            password="StrongPass123!",
        )
        self.idea = self.create_idea(owner)

    def test_filename_builder_handles_empty_reserved_and_unicode_titles(self):
        unsafe_titles = (
            "",
            "   ",
            "////\\\\",
            "..",
            "CON",
            "NUL.txt",
            "\x00\x01başlık\r\nX-Injected: yes",
            "\u202ekötü-ad.pdf",
            ("ÇĞİÖŞÜ çğıöşü " * 100),
        )

        for title in unsafe_titles:
            with self.subTest(title=repr(title)):
                self.idea.title = title
                filename = build_report_filename(self.idea)

                self.assertTrue(filename)
                self.assertTrue(filename.lower().endswith(".pdf"))
                self.assertLessEqual(
                    len(filename.encode("utf-8")),
                    255,
                )
                self.assertFalse(filename.startswith((".", " ")))
                self.assertFalse(filename.endswith((".", " ")))
                self.assertFalse(
                    set(filename).intersection('\\/:*?"<>|')
                )
                self.assertFalse(
                    any(
                        ord(character) < 32
                        or ord(character) == 127
                        for character in filename
                    )
                )
                self.assertNotRegex(
                    filename,
                    r"[\u202a-\u202e\u2066-\u2069]",
                )
