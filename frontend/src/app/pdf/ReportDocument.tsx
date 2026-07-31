import {
    Document,
    Font,
    Link,
    Page,
    StyleSheet,
    Text,
    View,
} from "@react-pdf/renderer";

Font.register({
    family: "NotoSans",
    fonts: [
        {
            src: "/fonts/NotoSans-Regular.ttf",
            fontWeight: 400,
        },
        {
            src: "/fonts/NotoSans-Bold.ttf",
            fontWeight: 700,
        },
        {
            src: "/fonts/NotoSans-Italic.ttf",
            fontWeight: 400,
            fontStyle: "italic",
        },
    ],
});

// ---------------------------------------------------------------------------
// Veri tipleri — her biri ilgili hook'un `data` alanına birebir karşılık gelir
// ---------------------------------------------------------------------------

export interface ReportIdeaData {
    title: string;
    createdAt: string;
    description: string;
    problem: string;
    targetAudience: string;
    sources: { title: string; source_url?: string | null }[];
}

export type RiskLevel = "high" | "medium" | "low" | string;
export type RiskyAssumptionStatus = "validated" | "refuted" | "untested";

export interface RiskyAssumptionItem {
    level: RiskLevel;
    status?: RiskyAssumptionStatus;
    text: string;
    evidence_quote?: string;
}

export interface RiskyAssumptionsData {
    assumptions: RiskyAssumptionItem[];
}

export interface MomTestQuestion {
    question: string;
}

export interface MoscowItem {
    title: string;
    reason?: string;
}

export interface MoscowScopeData {
    summary: string;
    must_have: MoscowItem[];
    should_have: MoscowItem[];
    could_have: MoscowItem[];
    wont_have: MoscowItem[];
}

export interface RoadmapPhase {
    week?: number;
    phase?: number;
    title?: string;
    "İlk görüşmeler"?: string[];
    "Test edilecek varsayımlar"?: string[];
    "MVP öncelikleri"?: string[];
    "Başarı metrikleri"?: string[];
    "Sonraki karar noktaları"?: string[];
}

export interface ValidationRoadmapData {
    roadmap_type: "weekly" | "phase" | string;
    phases: RoadmapPhase[];
}

export interface GeneralEvaluationData {
    strengths: string[];
    uncertainties: string[];
    next_action: string;
}

export interface Competitor {
    name: string;
    description: string;
    strengths: string[];
    weaknesses: string[];
}

export interface CompetitorAnalysisData {
    competitors: Competitor[];
    market_gap: string;
    differentiation: string;
}

export interface PitchSlide {
    title: string;
    bullets: string[];
}

export interface InvestorPitchData {
    elevator_pitch: string;
    slides: PitchSlide[];
    closing_ask: string;
}

export interface ReportDocumentProps {
    idea: ReportIdeaData;
    riskyAssumptions?: RiskyAssumptionsData | null;
    momQuestions?: MomTestQuestion[] | null;
    moscow?: MoscowScopeData | null;
    roadmap?: ValidationRoadmapData | null;
    evaluation?: GeneralEvaluationData | null;
    competitor?: CompetitorAnalysisData | null;
    pitch?: InvestorPitchData | null;
}

// ---------------------------------------------------------------------------
// Stiller
// ---------------------------------------------------------------------------

const colors = {
    background: "#FFFFFF",
    card: "#F8F8F6",
    foreground: "#202020",
    muted: "#666666",
    border: "#D9D9D4",
    primary: "#202020",
};

const riskConfig: Record<string, { label: string; color: string; bg: string; border: string }> = {
    high: { label: "Yüksek Risk", color: "#B91C1C", bg: "#FEF2F2", border: "#FECACA" },
    medium: { label: "Orta Risk", color: "#B45309", bg: "#FFFBEB", border: "#FDE68A" },
    low: { label: "Düşük Risk", color: "#047857", bg: "#ECFDF5", border: "#A7F3D0" },
};

const statusConfig: Record<RiskyAssumptionStatus, { label: string; color: string; bg: string; border: string }> = {
    validated: { label: "Doğrulandı", color: "#047857", bg: "#ECFDF5", border: "#A7F3D0" },
    refuted: { label: "Çürütüldü", color: "#B91C1C", bg: "#FEF2F2", border: "#FECACA" },
    untested: { label: "Test edilmedi", color: colors.muted, bg: "#F1F5F9", border: colors.border },
};

const moscowCategories: { key: keyof MoscowScopeData; label: string; color: string; bg: string }[] = [
    { key: "must_have", label: "Must Have", color: "#B91C1C", bg: "#FEF2F2" },
    { key: "should_have", label: "Should Have", color: "#B45309", bg: "#FFFBEB" },
    { key: "could_have", label: "Could Have", color: "#1D4ED8", bg: "#EFF6FF" },
    { key: "wont_have", label: "Won't Have", color: "#475569", bg: "#F1F5F9" },
];

const roadmapSectionKeys: {
    key: keyof RoadmapPhase;
    label: string;
}[] = [
        { key: "İlk görüşmeler", label: "İlk Görüşmeler" },
        { key: "Test edilecek varsayımlar", label: "Test Edilecek Varsayımlar" },
        { key: "MVP öncelikleri", label: "MVP Öncelikleri" },
        { key: "Başarı metrikleri", label: "Başarı Metrikleri" },
        { key: "Sonraki karar noktaları", label: "Sonraki Karar Noktaları" },
    ];

const styles = StyleSheet.create({
    page: {
        paddingTop: 30,
        paddingRight: 30,
        paddingBottom: 50,
        paddingLeft: 30,
        backgroundColor: colors.background,
        color: colors.foreground,
        fontFamily: "NotoSans",
        fontSize: 9.1,
        lineHeight: 1.48,
    },
    cover: {
        marginBottom: 27,
        paddingBottom: 18,
    },
    eyebrow: {
        marginBottom: 9,
        color: "#555555",
        fontSize: 7.3,
        fontWeight: 700,
        letterSpacing: 1.25,
        textTransform: "uppercase",
    },
    title: {
        marginBottom: 7,
        color: colors.foreground,
        fontSize: 20.5,
        fontWeight: 700,
        lineHeight: 1.16,
    },
    date: {
        color: "#656565",
        fontSize: 8.8,
    },
    section: {
        marginBottom: 14,
    },
    sectionHeadingRow: {
        flexDirection: "row",
        alignItems: "center",
        marginBottom: 9,
    },
    sectionAccent: {
        width: 16,
        height: 2.4,
        marginRight: 7,
        borderRadius: 2,
        backgroundColor: "#202020",
    },
    sectionHeading: {
        flexGrow: 1,
        color: "#252525",
        fontSize: 8.4,
        fontWeight: 700,
        letterSpacing: 1.05,
        textTransform: "uppercase",
    },
    card: {
        paddingTop: 12,
        paddingRight: 14,
        paddingBottom: 12,
        paddingLeft: 14,
        borderWidth: 0.8,
        borderColor: colors.border,
        borderRadius: 11,
        backgroundColor: colors.card,
    },
    bodyText: {
        color: colors.muted,
        fontSize: 9.1,
        lineHeight: 1.5,
    },
    grid: {
        flexDirection: "row",
        flexWrap: "wrap",
    },
    gridCol2: {
        width: "48.7%",
        marginRight: "2.6%",
        marginBottom: 9,
        minHeight: 68,
    },
    gridCol2Last: {
        width: "48.7%",
        marginBottom: 9,
        minHeight: 68,
    },
    subCardTitle: {
        marginBottom: 5,
        color: colors.foreground,
        fontSize: 9.2,
        fontWeight: 700,
    },

    // Riskli varsayımlar
    assumptionRow: {
        flexDirection: "row",
        alignItems: "flex-start",
        marginBottom: 9,
    },
    assumptionBadgeRow: {
        width: 148,
        flexDirection: "row",
        alignItems: "center",
        marginRight: 9,
        paddingTop: 1,
    },
    assumptionContent: {
        flex: 1,
    },
    badge: {
        paddingTop: 2,
        paddingBottom: 2,
        paddingLeft: 6,
        paddingRight: 6,
        borderRadius: 9,
        borderWidth: 0.8,
        marginRight: 5,
        fontSize: 6.9,
        fontWeight: 700,
    },
    assumptionText: {
        color: colors.muted,
        fontSize: 8.8,
        lineHeight: 1.48,
    },
    evidenceText: {
        marginTop: 3,
        color: colors.muted,
        fontSize: 7.8,
        fontStyle: "italic",
    },

    // Müşteri görüşme soruları
    numberedRow: {
        flexDirection: "row",
        alignItems: "flex-start",
        marginBottom: 6,
    },
    numberBadge: {
        width: 14,
        height: 14,
        borderRadius: 7,
        backgroundColor: "#EFF6FF",
        borderWidth: 0.7,
        borderColor: "#BFDBFE",
        color: "#3390E8",
        fontSize: 7,
        fontWeight: 700,
        textAlign: "center",
        marginRight: 7,
        marginTop: 0.5,
        paddingTop: 2.1,
    },
    numberedText: {
        flex: 1,
        color: colors.muted,
        fontSize: 8.8,
        lineHeight: 1.45,
    },

    // Liste satırları
    bulletLine: {
        flexDirection: "row",
        alignItems: "flex-start",
        marginBottom: 3,
    },
    bulletMark: {
        width: 10,
        color: "#58CDB4",
        fontSize: 8.5,
        fontWeight: 700,
    },
    bulletText: {
        flex: 1,
        color: colors.muted,
        fontSize: 8.3,
        lineHeight: 1.42,
    },

    // Yol haritası
    phaseCard: {
        marginBottom: 10,
        borderWidth: 0.8,
        borderColor: colors.border,
        borderRadius: 10,
        backgroundColor: "#FAFAF9",
        paddingTop: 10,
        paddingBottom: 10,
        paddingLeft: 12,
        paddingRight: 12,
    },
    phaseHeaderRow: {
        flexDirection: "row",
        alignItems: "center",
        marginBottom: 8,
    },
    phaseNumber: {
        width: 18,
        height: 18,
        borderRadius: 9,
        backgroundColor: "#EFEFEA",
        borderWidth: 0.7,
        borderColor: colors.border,
        color: colors.foreground,
        fontSize: 7.6,
        fontWeight: 700,
        textAlign: "center",
        paddingTop: 4,
        marginRight: 8,
    },
    phaseTitle: {
        flex: 1,
        color: colors.foreground,
        fontSize: 9.3,
        fontWeight: 700,
    },
    phaseTag: {
        paddingTop: 2,
        paddingBottom: 2,
        paddingLeft: 6,
        paddingRight: 6,
        borderRadius: 7,
        backgroundColor: "#EFEFEA",
        borderWidth: 0.6,
        borderColor: colors.border,
        color: "#666666",
        fontSize: 6.7,
        fontWeight: 700,
    },
    phaseSubBox: {
        width: "48.7%",
        marginRight: "2.6%",
        marginBottom: 7,
        borderWidth: 0.7,
        borderColor: colors.border,
        borderRadius: 8,
        backgroundColor: "#F1F2F2",
        paddingTop: 8,
        paddingBottom: 8,
        paddingLeft: 9,
        paddingRight: 9,
        minHeight: 82,
    },
    phaseSubBoxLast: {
        width: "48.7%",
        marginBottom: 7,
        borderWidth: 0.7,
        borderColor: colors.border,
        borderRadius: 8,
        backgroundColor: "#F1F2F2",
        paddingTop: 8,
        paddingBottom: 8,
        paddingLeft: 9,
        paddingRight: 9,
        minHeight: 82,
    },
    phaseSubBoxTitle: {
        marginBottom: 4,
        color: colors.foreground,
        fontSize: 7.7,
        fontWeight: 700,
    },

    // Genel değerlendirme
    listItemRow: {
        flexDirection: "row",
        alignItems: "flex-start",
        marginBottom: 4,
    },
    listDot: {
        width: 10,
        color: "#5CCDB6",
        fontSize: 9,
    },
    warningDot: {
        width: 10,
        color: "#E5C248",
        fontSize: 9,
    },
    listItemText: {
        flex: 1,
        color: colors.muted,
        fontSize: 8.8,
        lineHeight: 1.46,
    },
    evaluationLabel: {
        marginBottom: 5,
        color: colors.foreground,
        fontSize: 8.2,
        fontWeight: 700,
    },
    calloutBox: {
        borderWidth: 0.8,
        borderColor: "#9AADE8",
        backgroundColor: "#DDE3F4",
        borderRadius: 9,
        paddingTop: 10,
        paddingBottom: 10,
        paddingLeft: 12,
        paddingRight: 12,
        marginTop: 8,
    },
    calloutLabel: {
        marginBottom: 3,
        color: colors.foreground,
        fontSize: 8.1,
        fontWeight: 700,
    },
    calloutText: {
        color: colors.foreground,
        fontSize: 8.8,
        lineHeight: 1.45,
    },

    // Kaynaklar ve bağlantılar
    link: {
        color: "#252525",
        textDecoration: "none",
        fontSize: 8.1,
        marginTop: 2,
        fontWeight: 700,
    },
    sourceRow: {
        marginBottom: 8,
        paddingBottom: 8,
        borderBottomWidth: 0.7,
        borderBottomColor: colors.border,
    },
    sourceTitle: {
        color: colors.foreground,
        fontSize: 9,
        fontWeight: 700,
    },

    // Yatırımcı sunumu boş durumu
    emptyPitch: {
        alignItems: "center",
        justifyContent: "center",
        minHeight: 115,
        paddingTop: 15,
        paddingBottom: 15,
    },
    emptyPitchIcon: {
        width: 28,
        height: 28,
        borderRadius: 9,
        borderWidth: 0.8,
        borderColor: "#F4D9A6",
        backgroundColor: "#FFF8EA",
        color: "#E5A800",
        fontSize: 13,
        textAlign: "center",
        paddingTop: 6,
        marginBottom: 8,
    },
    emptyPitchText: {
        width: 190,
        color: "#707070",
        fontSize: 8.8,
        lineHeight: 1.45,
        textAlign: "center",
    },

    footer: {
        position: "absolute",
        right: 30,
        bottom: 15,
        left: 30,
        paddingTop: 6,
        borderTopWidth: 0.6,
        borderTopColor: "#EEEEEC",
        flexDirection: "row",
        justifyContent: "space-between",
        color: "#7A8494",
        fontSize: 6.8,
    },
});

function formatDate(value: string): string {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
        return value;
    }
    return new Intl.DateTimeFormat("tr-TR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
    }).format(date);
}

// ---------------------------------------------------------------------------
// Ortak küçük bileşenler
// ---------------------------------------------------------------------------

function SectionShell({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}) {
    return (
        <View style={styles.section}>
            <View
                style={styles.sectionHeadingRow}
                minPresenceAhead={90}
            >
                <View style={styles.sectionAccent} />

                <Text style={styles.sectionHeading}>
                    {title}
                </Text>
            </View>

            {children}
        </View>
    );
}

function Bullets({ items }: { items: string[] }) {
    return (
        <>
            {items.map((item, idx) => (
                <View key={idx} style={styles.bulletLine} wrap={false}>
                    <Text style={styles.bulletMark}>·</Text>
                    <Text style={styles.bulletText}>{item}</Text>
                </View>
            ))}
        </>
    );
}

// ---------------------------------------------------------------------------
// Bölüm bileşenleri
// ---------------------------------------------------------------------------

function SummarySection({ description }: { description: string }) {
    return (
        <SectionShell title="Fikir Özeti">
            <View style={styles.card}>
                <Text style={styles.bodyText}>{description}</Text>
            </View>
        </SectionShell>
    );
}

function ProblemAudienceSection({
    problem,
    targetAudience,
}: {
    problem: string;
    targetAudience: string;
}) {
    return (
        <SectionShell title="Problem ve Hedef Kitle">
            <View style={styles.grid}>
                <View style={[styles.card, styles.gridCol2]}>
                    <Text style={styles.subCardTitle}>Problem</Text>
                    <Text style={styles.bodyText}>{problem}</Text>
                </View>
                <View style={[styles.card, styles.gridCol2Last]}>
                    <Text style={styles.subCardTitle}>Hedef Kitle</Text>
                    <Text style={styles.bodyText}>{targetAudience}</Text>
                </View>
            </View>
        </SectionShell>
    );
}

function RiskyAssumptionsSection({ data }: { data: RiskyAssumptionsData }) {
    return (
        <SectionShell title="Riskli Varsayımlar">
            <View>
                {data.assumptions.map((item, idx) => {
                    const risk = riskConfig[item.level] ?? riskConfig.medium;
                    const status = item.status ? statusConfig[item.status] : null;
                    return (
                        <View key={idx} style={styles.assumptionRow} wrap={false}>
                            <View style={styles.assumptionBadgeRow}>
                                <Text
                                    style={[
                                        styles.badge,
                                        {
                                            color: risk.color,
                                            backgroundColor: risk.bg,
                                            borderColor: risk.border,
                                        },
                                    ]}
                                >
                                    {risk.label}
                                </Text>

                                {status && (
                                    <Text
                                        style={[
                                            styles.badge,
                                            {
                                                color: status.color,
                                                backgroundColor: status.bg,
                                                borderColor: status.border,
                                            },
                                        ]}
                                    >
                                        {status.label}
                                    </Text>
                                )}
                            </View>

                            <View style={styles.assumptionContent}>
                                <Text style={styles.assumptionText}>
                                    {item.text}
                                </Text>

                                {item.evidence_quote && (
                                    <Text style={styles.evidenceText}>
                                        &ldquo;{item.evidence_quote}&rdquo;
                                    </Text>
                                )}
                            </View>
                        </View>
                    );
                })}
            </View>
        </SectionShell>
    );
}

function MomTestQuestionsSection({ data }: { data: MomTestQuestion[] }) {
    return (
        <SectionShell title="Müşteri Görüşme Soruları">
            <View>
                {data.map((q, idx) => (
                    <View key={idx} style={styles.numberedRow} wrap={false}>
                        <Text style={styles.numberBadge}>{idx + 1}</Text>
                        <Text style={styles.numberedText}>{q.question}</Text>
                    </View>
                ))}
            </View>
        </SectionShell>
    );
}

function MoscowScopeSection({ data }: { data: MoscowScopeData }) {
    return (
        <SectionShell title="MVP Kapsamı (MoSCoW)">
            <Text style={[styles.bodyText, { marginBottom: 10 }]}>
                {data.summary}
            </Text>
            <View style={styles.grid}>
                {moscowCategories.map(({ key, label, color, bg }, idx) => {
                    const items = data[key] as MoscowItem[];
                    const isRightCol = idx % 2 === 1;
                    return (
                        <View
                            key={key as string}
                            style={[
                                styles.card,
                                isRightCol ? styles.gridCol2Last : styles.gridCol2,
                                { backgroundColor: bg },
                            ]}
                            wrap={false}
                        >
                            <Text style={[styles.subCardTitle, { color }]}>{label}</Text>
                            {items.map((item, i) => (
                                <Text key={i} style={[styles.bodyText, { marginBottom: 3 }]}>
                                    · {item.title}
                                </Text>
                            ))}
                        </View>
                    );
                })}
            </View>
        </SectionShell>
    );
}

function ValidationRoadmapSection({ data }: { data: ValidationRoadmapData }) {
    return (
        <SectionShell title="Doğrulama Yol Haritası">
            <Text style={[styles.bodyText, { marginBottom: 10 }]}>
                {data.phases.length}{" "}
                {data.roadmap_type === "weekly" ? "haftalık aşama" : "aşama"}
            </Text>
            {data.phases.map((phase, i) => {
                const order = phase.week ?? phase.phase ?? i + 1;
                const label =
                    data.roadmap_type === "weekly" ? `Hafta ${order}` : `Aşama ${order}`;

                const visibleSections = roadmapSectionKeys.filter(({ key }) => {
                    const items = phase[key];
                    return Array.isArray(items) && items.length > 0;
                });

                return (
                    <View key={i} style={styles.phaseCard} wrap={false}>
                        <View style={styles.phaseHeaderRow}>
                            <Text style={styles.phaseNumber}>{order}</Text>

                            <Text style={styles.phaseTitle}>
                                {phase.title ?? label}
                            </Text>

                            <Text style={styles.phaseTag}>{label}</Text>
                        </View>
                        <View style={styles.grid}>
                            {visibleSections.map(({ key, label: sectionLabel }, idx) => {
                                const items = phase[key] as string[];
                                const isRightCol = idx % 2 === 1;
                                return (
                                    <View
                                        key={key as string}
                                        style={
                                            isRightCol
                                                ? styles.phaseSubBoxLast
                                                : styles.phaseSubBox
                                        }
                                    >
                                        <Text style={styles.phaseSubBoxTitle}>
                                            {sectionLabel}
                                        </Text>
                                        {items.map((line, li) => (
                                            <Text
                                                key={li}
                                                style={[styles.bodyText, { marginBottom: 2, fontSize: 8.5 }]}
                                            >
                                                · {line}
                                            </Text>
                                        ))}
                                    </View>
                                );
                            })}
                        </View>
                    </View>
                );
            })}
        </SectionShell>
    );
}

function GeneralEvaluationSection({ data }: { data: GeneralEvaluationData }) {
    return (
        <SectionShell title="Genel Değerlendirme">
            <View style={{ marginBottom: 10 }}>
                <Text style={styles.evaluationLabel}>Güçlü Yönler</Text>
                {data.strengths.map((s, i) => (
                    <View key={i} style={styles.listItemRow} wrap={false}>
                        <Text style={styles.listDot}>·</Text>
                        <Text style={styles.listItemText}>{s}</Text>
                    </View>
                ))}
            </View>
            <View style={{ marginBottom: 4 }}>
                <Text style={styles.evaluationLabel}>Belirsiz Noktalar</Text>
                {data.uncertainties.map((u, i) => (
                    <View key={i} style={styles.listItemRow} wrap={false}>
                        <Text style={styles.warningDot}>·</Text>
                        <Text style={styles.listItemText}>{u}</Text>
                    </View>
                ))}
            </View>
            <View style={styles.calloutBox} wrap={false}>
                <Text style={styles.calloutLabel}>İlk Yapılacak Aksiyon</Text>
                <Text style={styles.calloutText}>{data.next_action}</Text>
            </View>
        </SectionShell>
    );
}

function CompetitorAnalysisSection({ data }: { data: CompetitorAnalysisData }) {
    return (
        <SectionShell title="Rakip / Pazar Analizi">
            <View style={styles.grid}>
                {data.competitors.map((c, i) => {
                    const isRightCol = i % 2 === 1;
                    return (
                        <View
                            key={i}
                            style={[
                                styles.card,
                                isRightCol ? styles.gridCol2Last : styles.gridCol2,
                            ]}
                            wrap={false}
                        >
                            <Text style={styles.subCardTitle}>{c.name}</Text>
                            <Text style={[styles.bodyText, { marginBottom: 6 }]}>
                                {c.description}
                            </Text>
                            <Bullets items={c.strengths} />
                            <Bullets items={c.weaknesses} />
                        </View>
                    );
                })}
            </View>
            <View style={[styles.card, { marginBottom: 10 }]} wrap={false}>
                <Text style={styles.subCardTitle}>Pazar Boşluğu</Text>
                <Text style={styles.bodyText}>{data.market_gap}</Text>
            </View>
            <View
                style={[
                    styles.card,
                    { backgroundColor: "#F5F3FF", borderColor: "#DDD6FE" },
                ]}
                wrap={false}
            >
                <Text style={styles.subCardTitle}>Farklılaşma Noktanız</Text>
                <Text style={styles.bodyText}>{data.differentiation}</Text>
            </View>
        </SectionShell>
    );
}

function InvestorPitchSection({ data }: { data: InvestorPitchData }) {
    return (
        <SectionShell title="Yatırımcı Sunumu">
            <View
                style={[
                    styles.card,
                    { backgroundColor: "#FFFBEB", borderColor: "#FDE68A", marginBottom: 10 },
                ]}
                wrap={false}
            >
                <Text style={styles.subCardTitle}>Elevator Pitch</Text>
                <Text style={[styles.bodyText, { fontStyle: "italic" }]}>
                    &ldquo;{data.elevator_pitch}&rdquo;
                </Text>
            </View>
            <View style={styles.grid}>
                {data.slides.map((slide, i) => {
                    const isRightCol = i % 2 === 1;
                    return (
                        <View
                            key={i}
                            style={[
                                styles.card,
                                isRightCol ? styles.gridCol2Last : styles.gridCol2,
                            ]}
                            wrap={false}
                        >
                            <Text style={styles.subCardTitle}>
                                {i + 1}. {slide.title}
                            </Text>
                            <Bullets items={slide.bullets} />
                        </View>
                    );
                })}
            </View>
            <View style={styles.card} wrap={false}>
                <Text style={styles.subCardTitle}>Kapanış / Talep</Text>
                <Text style={styles.bodyText}>{data.closing_ask}</Text>
            </View>
        </SectionShell>
    );
}

function InvestorPitchEmptySection() {
    return (
        <SectionShell title="Yatırımcı Sunumu">
            <View style={styles.emptyPitch}>
                <Text style={styles.emptyPitchIcon}>›</Text>

                <Text style={styles.emptyPitchText}>
                    Bu fikir için henüz yatırımcı sunumu oluşturulmadı.
                </Text>
            </View>
        </SectionShell>
    );
}

function SourcesSection({
    sources,
}: {
    sources: { title: string; source_url?: string | null }[];
}) {
    if (sources.length === 0) return null;
    return (
        <SectionShell title="Kullanılan Kaynaklar">
            <View style={styles.card}>
                <Text style={[styles.bodyText, { marginBottom: 10 }]}>
                    Bu analiz hazırlanırken aşağıdaki eğitim içerikleri referans
                    alınmıştır.
                </Text>
                {sources.map((source, idx) => (
                    <View
                        key={`${source.source_url ?? source.title}-${idx}`}
                        style={styles.sourceRow}
                        wrap={false}
                    >
                        <Text style={styles.sourceTitle}>{source.title}</Text>
                        {source.source_url && (
                            <Link src={source.source_url} style={styles.link}>
                                {source.source_url}
                            </Link>
                        )}
                    </View>
                ))}
            </View>
        </SectionShell>
    );
}

// ---------------------------------------------------------------------------
// Ana doküman
// ---------------------------------------------------------------------------

export function ReportDocument({
    idea,
    riskyAssumptions,
    momQuestions,
    moscow,
    roadmap,
    evaluation,
    competitor,
    pitch,
}: ReportDocumentProps) {
    return (
        <Document
            title={`${idea.title} - FikirLab Doğrulama Raporu`}
            author="FikirLab"
            subject="Fikir doğrulama raporu"
            creator="FikirLab"
        >
            <Page size="A4" style={styles.page} wrap>
                <View style={styles.cover}>
                    <Text style={styles.eyebrow}>FikirLab · Doğrulama Raporu</Text>
                    <Text style={styles.title}>{idea.title}</Text>
                    <Text style={styles.date}>{formatDate(idea.createdAt)}</Text>
                </View>

                <SummarySection description={idea.description} />

                <ProblemAudienceSection
                    problem={idea.problem}
                    targetAudience={idea.targetAudience}
                />

                {riskyAssumptions && riskyAssumptions.assumptions.length > 0 && (
                    <RiskyAssumptionsSection data={riskyAssumptions} />
                )}

                {momQuestions && momQuestions.length > 0 && (
                    <MomTestQuestionsSection data={momQuestions} />
                )}

                {moscow && <MoscowScopeSection data={moscow} />}

                {roadmap && roadmap.phases.length > 0 && (
                    <ValidationRoadmapSection data={roadmap} />
                )}

                {evaluation && <GeneralEvaluationSection data={evaluation} />}

                {competitor && <CompetitorAnalysisSection data={competitor} />}

                {pitch ? (
                    <InvestorPitchSection data={pitch} />
                ) : (
                    <InvestorPitchEmptySection />
                )}

                {idea.sources.length > 0 && (
                    <View break>
                        <SourcesSection sources={idea.sources} />
                    </View>
                )}

                <View style={styles.footer} fixed>
                    <Text>FikirLab · Doğrulama Raporu</Text>
                    <Text
                        render={({ pageNumber, totalPages }) =>
                            `${pageNumber} / ${totalPages}`
                        }
                    />
                </View>
            </Page>
        </Document>
    );
}