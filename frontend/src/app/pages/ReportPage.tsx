import { useState } from "react";
import { pdf } from "@react-pdf/renderer";
import { Download } from "lucide-react";

import { CompetitorAnalysisBody } from "../components/analysis/CompetitorAnalysisBody";
import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { InvestorPitchBody } from "../components/analysis/InvestorPitchBody";
import { MomTestQuestionsBody } from "../components/analysis/MomTestQuestionsBody";
import { MoscowScopeBody } from "../components/analysis/MoscowScopeBody";
import { RiskyAssumptionsBody } from "../components/analysis/RiskyAssumptionsBody";
import { ValidationRoadmapBody } from "../components/analysis/ValidationRoadmapBody";
import { ActiveIdeaPageState } from "../components/ideas/ActiveIdeaPageState";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useCompetitorAnalysis } from "../hooks/useCompetitorAnalysis";
import { useGeneralEvaluation } from "../hooks/useGeneralEvaluation";
import { useIdea } from "../hooks/useIdea";
import { useInvestorPitch } from "../hooks/useInvestorPitch";
import { useMomTestQuestions } from "../hooks/useMomTestQuestions";
import { useMoscowScope } from "../hooks/useMoscowScope";
import { useRiskyAssumptions } from "../hooks/useRiskyAssumptions";
import { useValidationRoadmap } from "../hooks/useValidationRoadmap";
import { ReportDocument } from "../pdf/ReportDocument";

interface RagSource {
  title: string;
  source_url?: string | null;
}

interface ReportPageProps {
  onBack: () => void;
}

function isPending(status: string): boolean {
  return status === "loading" || status === "generating";
}

function createSafePdfName(title: string): string {
  return title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/ı/g, "i")
    .replace(/İ/g, "I")
    .replace(/[\\/:*?"<>|]/g, "")
    .replace(/\s+/g, "_")
    .trim();
}

export function ReportPage({ onBack }: ReportPageProps) {
  const { ideaId } = useActiveIdeaId();

  const {
    status: ideaStatus,
    data: idea,
    reload: reloadIdea,
  } = useIdea(ideaId);

  const riskyAssumptions = useRiskyAssumptions(ideaId ?? 0);
  const momQuestions = useMomTestQuestions(ideaId ?? 0);
  const moscow = useMoscowScope(ideaId ?? 0);
  const roadmap = useValidationRoadmap(ideaId ?? 0);
  const evaluation = useGeneralEvaluation(ideaId ?? 0);
  const competitor = useCompetitorAnalysis(ideaId ?? 0);
  const pitch = useInvestorPitch(ideaId ?? 0);

  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const sources: RagSource[] = idea?.sources ?? [];

  const uniqueSources = Array.from(
    new Map(
      sources.map((source) => [
        source.source_url ?? source.title,
        source,
      ]),
    ).values(),
  );

  const anyPending =
    isPending(riskyAssumptions.status) ||
    isPending(momQuestions.status) ||
    isPending(moscow.status) ||
    isPending(roadmap.status) ||
    isPending(evaluation.status) ||
    isPending(competitor.status) ||
    isPending(pitch.status);

  const handleDownloadPdf = async () => {
    if (!idea || isDownloading || anyPending) {
      return;
    }

    setIsDownloading(true);
    setDownloadError(null);

    try {
      const reportBlob = await pdf(
        <ReportDocument
          idea={{
            title: idea.title,
            createdAt: idea.created_at,
            description: idea.description,
            problem: idea.problem,
            targetAudience: idea.target_audience,
            sources: uniqueSources,
          }}
          riskyAssumptions={
            riskyAssumptions.status === "ready"
              ? riskyAssumptions.data
              : null
          }
          momQuestions={
            momQuestions.status === "ready"
              ? momQuestions.data
              : null
          }
          moscow={
            moscow.status === "ready"
              ? moscow.data
              : null
          }
          roadmap={
            roadmap.status === "ready"
              ? roadmap.data
              : null
          }
          evaluation={
            evaluation.status === "ready"
              ? evaluation.data
              : null
          }
          competitor={
            competitor.status === "ready"
              ? competitor.data
              : null
          }
          pitch={
            pitch.status === "ready"
              ? pitch.data
              : null
          }
        />,
      ).toBlob();

      const rawName = idea.title?.trim() || "Fikir";
      const safeName = createSafePdfName(rawName) || "Fikir";

      const url = URL.createObjectURL(reportBlob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `${safeName}_FikirLab_Dogrulama_Raporu.pdf`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 1000);
    } catch (error) {
      console.error("PDF oluşturma hatası:", error);
      setDownloadError(
        "PDF oluşturulamadı. Lütfen tekrar dener misin?",
      );
    } finally {
      setIsDownloading(false);
    }
  };

  const Divider = ({ label }: { label: string }) => (
    <div className="mb-4 flex items-center gap-2">
      <div className="h-[3px] w-5 rounded-full bg-primary" />

      <h2 className="text-[11px] font-bold uppercase tracking-[0.14em] text-foreground">
        {label}
      </h2>
    </div>
  );

  if (ideaStatus === "loading") {
    return <ActiveIdeaPageState mode="loading" />;
  }

  if (
    ideaId === null ||
    ideaStatus === "idle" ||
    ideaStatus === "not_found"
  ) {
    return <ActiveIdeaPageState mode="empty" />;
  }

  if (ideaStatus === "error") {
    return (
      <ActiveIdeaPageState
        mode="error"
        onRetry={() => void reloadIdea()}
      />
    );
  }

  if (!idea || idea.id !== ideaId) {
    return <ActiveIdeaPageState mode="loading" />;
  }

  return (
    <div
      className="print-area hide-scroll flex-1 overflow-y-auto bg-background"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto w-full max-w-[860px] px-4 py-7 sm:px-7 sm:py-10">
        <div className="no-print mb-6 flex flex-wrap items-center justify-between gap-3">
          <button
            type="button"
            onClick={onBack}
            className="text-xs font-semibold text-foreground transition-colors hover:text-muted-foreground"
          >
            ← Fikir analizine dön
          </button>

          <div className="flex flex-col items-end gap-1.5">
            <button
              type="button"
              onClick={() => void handleDownloadPdf()}
              disabled={isDownloading || anyPending}
              className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Download size={14} />

              {isDownloading
                ? "Hazırlanıyor..."
                : anyPending
                  ? "İçerik yükleniyor..."
                  : "PDF İndir"}
            </button>

            {downloadError && (
              <p className="text-xs text-destructive">
                {downloadError}
              </p>
            )}
          </div>
        </div>

        <div className="space-y-9 rounded-2xl bg-white px-5 py-7 shadow-sm ring-1 ring-black/5 sm:px-10 sm:py-10">
          <header className="border-b border-border pb-7">
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              FikirLab · Doğrulama Raporu
            </div>

            <h1 className="max-w-2xl text-3xl font-bold leading-tight tracking-tight text-foreground">
              {idea.title}
            </h1>

            <p className="mt-2 text-sm text-muted-foreground">
              {new Date(idea.created_at).toLocaleDateString("tr-TR", {
                day: "2-digit",
                month: "long",
                year: "numeric",
              })}
            </p>
          </header>

          <section>
            <Divider label="Fikir Özeti" />

            <div className="rounded-xl border border-border bg-card px-5 py-4">
              <p className="text-sm leading-6 text-muted-foreground">
                {idea.description}
              </p>
            </div>
          </section>

          <section>
            <Divider label="Problem ve Hedef Kitle" />

            <div className="grid grid-cols-1 items-stretch gap-4 sm:grid-cols-2">
              <article className="h-full rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Problem
                </h3>

                <p className="text-sm leading-6 text-muted-foreground">
                  {idea.problem}
                </p>
              </article>

              <article className="h-full rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Hedef Kitle
                </h3>

                <p className="text-sm leading-6 text-muted-foreground">
                  {idea.target_audience}
                </p>
              </article>
            </div>
          </section>

          <section>
            <Divider label="Riskli Varsayımlar" />
            <RiskyAssumptionsBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="Müşteri Görüşme Soruları" />
            <MomTestQuestionsBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="MVP Kapsamı (MoSCoW)" />
            <MoscowScopeBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="Doğrulama Yol Haritası" />
            <ValidationRoadmapBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="Genel Değerlendirme" />
            <GeneralEvaluationBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="Rakip / Pazar Analizi" />
            <CompetitorAnalysisBody ideaId={ideaId} readOnly />
          </section>

          <section>
            <Divider label="Yatırımcı Sunumu" />
            <InvestorPitchBody ideaId={ideaId} readOnly />
          </section>

          {uniqueSources.length > 0 && (
            <section>
              <Divider label="Kullanılan Kaynaklar" />

              <div className="rounded-xl border border-border bg-card p-5">
                <p className="mb-5 text-sm leading-6 text-muted-foreground">
                  Bu analiz hazırlanırken aşağıdaki eğitim içerikleri
                  referans alınmıştır.
                </p>

                <ul className="divide-y divide-border">
                  {uniqueSources.map((source, index) => (
                    <li
                      key={`${source.source_url ?? source.title}-${index}`}
                      className="flex flex-col gap-1 py-3 first:pt-0 last:pb-0"
                    >
                      <span className="text-sm font-semibold text-foreground">
                        {source.title}
                      </span>

                      {source.source_url && (
                        <a
                          href={source.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="w-fit break-all text-xs font-medium text-primary hover:underline"
                        >
                          {source.source_url}
                        </a>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}