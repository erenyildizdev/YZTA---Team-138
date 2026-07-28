import { useRef, useState } from "react";
import { Download } from "lucide-react";
import html2canvas from "html2canvas-pro";
import jsPDF from "jspdf";

import { CompetitorAnalysisBody } from "../components/analysis/CompetitorAnalysisBody";
import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { MomTestQuestionsBody } from "../components/analysis/MomTestQuestionsBody";
import { MoscowScopeBody } from "../components/analysis/MoscowScopeBody";
import { RiskyAssumptionsBody } from "../components/analysis/RiskyAssumptionsBody";
import { ValidationRoadmapBody } from "../components/analysis/ValidationRoadmapBody";
import { ActiveIdeaPageState } from "../components/ideas/ActiveIdeaPageState";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useIdea } from "../hooks/useIdea";

interface RagSource {
  title: string;
  source_url?: string | null;
}

interface ReportPageProps {
  onBack: () => void;
}

export function ReportPage({ onBack }: ReportPageProps) {
  const { ideaId } = useActiveIdeaId();

  const {
    status: ideaStatus,
    data: idea,
    reload: reloadIdea,
  } = useIdea(ideaId);

  const reportRef = useRef<HTMLDivElement>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  const handleDownloadPdf = async () => {
    const element = reportRef.current;

    if (!element || isDownloading) {
      return;
    }

    setIsDownloading(true);
    setDownloadError(null);

    const hiddenEls = Array.from(
      element.querySelectorAll<HTMLElement>(".no-print"),
    );

    hiddenEls.forEach((el) => {
      el.style.visibility = "hidden";
    });

    const styleTag = document.createElement("style");

    styleTag.textContent =
      "*, *::before, *::after { animation: none !important; transition: none !important; }";

    document.head.appendChild(styleTag);

    try {
      const blockEls = Array.from(
        element.querySelectorAll<HTMLElement>("[data-pdf-block]"),
      );

      const pageWidth = 595.28;
      const pageHeight = 841.89;
      const margin = 24;
      const contentWidth = pageWidth - margin * 2;
      const usableHeight = pageHeight - margin * 2;
      const gap = 16;

      const pdf = new jsPDF({
        unit: "pt",
        format: "a4",
      });

      let cursorY = margin;
      let pageHasContent = false;

      for (const blockEl of blockEls) {
        const canvas = await html2canvas(blockEl, {
          scale: 1.5,
          useCORS: true,
          backgroundColor: "#ffffff",
        });

        const imgHeight = (canvas.height * contentWidth) / canvas.width;
        const imgData = canvas.toDataURL("image/jpeg", 0.85);

        if (imgHeight > usableHeight) {
          if (pageHasContent) {
            pdf.addPage();
          }

          let sliceOffset = 0;
          let heightLeft = imgHeight;

          pdf.addImage(
            imgData,
            "JPEG",
            margin,
            margin - sliceOffset,
            contentWidth,
            imgHeight,
          );

          heightLeft -= usableHeight;

          while (heightLeft > 0) {
            sliceOffset += usableHeight;

            pdf.addPage();

            pdf.addImage(
              imgData,
              "JPEG",
              margin,
              margin - sliceOffset,
              contentWidth,
              imgHeight,
            );

            heightLeft -= usableHeight;
          }

          cursorY = margin;
          pageHasContent = false;

          continue;
        }

        if (cursorY + imgHeight > pageHeight - margin) {
          pdf.addPage();
          cursorY = margin;
        }

        pdf.addImage(
          imgData,
          "JPEG",
          margin,
          cursorY,
          contentWidth,
          imgHeight,
        );

        cursorY += imgHeight + gap;
        pageHasContent = true;
      }

      const rawName = idea?.title?.trim() || "Fikir";

      const safeName = rawName
        .replace(/[\\/:*?"<>|]/g, "")
        .replace(/\s+/g, " ")
        .trim();

      const blob = pdf.output("blob");
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `${safeName} analiz raporu.pdf`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      URL.revokeObjectURL(url);
    } catch (error) {
      console.error(error);

      setDownloadError(
        "PDF oluşturulamadı. Lütfen tekrar dener misin?",
      );
    } finally {
      hiddenEls.forEach((el) => {
        el.style.visibility = "";
      });

      styleTag.remove();
      setIsDownloading(false);
    }
  };

  const Divider = ({ label }: { label: string }) => (
    <div className="mb-4 flex items-center gap-2">
      <div className="h-0.5 w-4 rounded-full bg-primary" />

      <h2 className="text-[10px] font-bold uppercase tracking-widest text-foreground">
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

  const sources: RagSource[] = idea.sources ?? [];

  const uniqueSources = Array.from(
    new Map(
      sources.map((source) => [
        source.source_url ?? source.title,
        source,
      ]),
    ).values(),
  );

  return (
    <div
      className="print-area hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div
        ref={reportRef}
        className="mx-auto max-w-3xl px-4 py-7 sm:px-7 sm:py-10"
      >
        <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div data-pdf-block>
            <div className="mb-1 text-xs uppercase tracking-widest text-muted-foreground">
              FikirLab — Doğrulama Raporu
            </div>

            <h1 className="text-2xl font-bold text-foreground">
              {idea.title}
            </h1>

            <p className="mt-1 text-sm text-muted-foreground">
              {`${new Date(idea.created_at).toLocaleDateString(
                "tr-TR",
              )} tarihli analiz`}
            </p>
          </div>

          <div className="no-print flex flex-col items-end gap-1.5">
            <button
              type="button"
              onClick={handleDownloadPdf}
              disabled={isDownloading}
              className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Download size={14} />

              {isDownloading ? "Hazırlanıyor..." : "PDF İndir"}
            </button>

            {downloadError && (
              <p className="text-xs text-destructive">
                {downloadError}
              </p>
            )}
          </div>
        </div>

        <button
          type="button"
          onClick={onBack}
          className="no-print mb-6 text-xs font-semibold text-foreground transition-colors hover:text-muted-foreground"
        >
          ← Fikir analizine dön
        </button>

        <div className="space-y-9">
          <section data-pdf-block>
            <Divider label="Fikir Özeti" />

            <p className="text-sm leading-relaxed text-muted-foreground">
              {idea.description}
            </p>
          </section>

          <section data-pdf-block>
            <Divider label="Problem ve Hedef Kitle" />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Problem
                </h3>

                <p className="text-sm leading-relaxed text-muted-foreground">
                  {idea.problem}
                </p>
              </div>

              <div className="rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Hedef Kitle
                </h3>

                <p className="text-sm leading-relaxed text-muted-foreground">
                  {idea.target_audience}
                </p>
              </div>
            </div>
          </section>

          <section data-pdf-block>
            <Divider label="Riskli Varsayımlar" />

            <RiskyAssumptionsBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-block>
            <Divider label="Müşteri Görüşme Soruları" />

            <MomTestQuestionsBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-block>
            <Divider label="MVP Kapsamı (MoSCoW)" />

            <MoscowScopeBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section>
            <div data-pdf-block>
              <Divider label="Doğrulama Yol Haritası" />
            </div>

            <ValidationRoadmapBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-block>
            <Divider label="Genel Değerlendirme" />

            <GeneralEvaluationBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section>
            <div data-pdf-block>
              <Divider label="Rakip / Pazar Analizi" />
            </div>

            <CompetitorAnalysisBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          {uniqueSources.length > 0 && (
            <section data-pdf-block>
              <Divider label="Kullanılan Kaynaklar" />

              <div className="rounded-xl border border-border bg-card p-5">
                <p className="mb-4 text-sm text-muted-foreground">
                  Bu analiz hazırlanırken aşağıdaki eğitim içerikleri
                  referans alınmıştır.
                </p>

                <ul className="space-y-3">
                  {uniqueSources.map((source, index) => (
                    <li
                      key={`${source.source_url ?? source.title}-${index}`}
                      className="flex flex-col gap-1"
                    >
                      <span className="text-sm font-semibold text-foreground">
                        {source.title}
                      </span>

                      {source.source_url && (
                        <a
                          href={source.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="no-print w-fit text-xs font-medium text-primary hover:underline"
                        >
                          Kaynağı görüntüle
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