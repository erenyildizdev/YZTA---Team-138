import { useRef, useState } from "react";
import { Download } from "lucide-react";
import html2canvas from "html2canvas-pro";
import jsPDF from "jspdf";

import { CompetitorAnalysisBody } from "../components/analysis/CompetitorAnalysisBody";
import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { InvestorPitchBody } from "../components/analysis/InvestorPitchBody";
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

const PDF_RENDER_WIDTH = 794;

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
    const sourceElement = reportRef.current;

    if (!sourceElement || isDownloading) {
      return;
    }

    const closedAccordionButtons = Array.from(
      sourceElement.querySelectorAll<HTMLButtonElement>(
        '[data-pdf-expand-all] button[aria-expanded="false"]',
      ),
    );

    setIsDownloading(true);
    setDownloadError(null);

    closedAccordionButtons.forEach((button) => {
      button.click();
    });

    await new Promise<void>((resolve) => {
      window.setTimeout(resolve, 350);
    });

    await new Promise<void>((resolve) => {
      requestAnimationFrame(() => {
        requestAnimationFrame(() => resolve());
      });
    });

    const styleTag = document.createElement("style");

    styleTag.textContent = `
      *, *::before, *::after {
        animation: none !important;
        transition: none !important;
        caret-color: transparent !important;
      }

      [data-pdf-render-root] {
        width: ${PDF_RENDER_WIDTH}px !important;
        min-width: ${PDF_RENDER_WIDTH}px !important;
        max-width: ${PDF_RENDER_WIDTH}px !important;
        margin: 0 !important;
        padding: 48px !important;
        box-sizing: border-box !important;
        overflow: visible !important;
        background: #ffffff !important;
        color: #111827 !important;
      }

      [data-pdf-render-root] .no-print {
        display: none !important;
      }

      [data-pdf-render-root] [data-pdf-section] {
        width: 100% !important;
        max-width: none !important;
        box-sizing: border-box !important;
      }

      [data-pdf-render-root] .sm\\:grid-cols-2 {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      }

      [data-pdf-render-root] .sm\\:flex-row {
        flex-direction: row !important;
      }

      [data-pdf-render-root] .sm\\:items-start {
        align-items: flex-start !important;
      }

      [data-pdf-render-root] .sm\\:justify-between {
        justify-content: space-between !important;
      }

      [data-pdf-render-root] .sm\\:px-7 {
        padding-left: 1.75rem !important;
        padding-right: 1.75rem !important;
      }

      [data-pdf-render-root] .sm\\:py-10 {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
      }

      [data-pdf-render-root] button {
        box-shadow: none !important;
      }

      [data-pdf-render-root] [data-pdf-expand-all] [data-state="open"] {
        animation: none !important;
        transition: none !important;
      }

      [data-pdf-render-root] [data-pdf-expand-all] [data-state="open"][role="region"] {
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
      }

      [data-pdf-render-root] a {
        text-decoration: none !important;
      }
    `;

    document.head.appendChild(styleTag);

    const renderHost = document.createElement("div");

    renderHost.setAttribute("aria-hidden", "true");
    renderHost.style.position = "fixed";
    renderHost.style.left = "-100000px";
    renderHost.style.top = "0";
    renderHost.style.width = `${PDF_RENDER_WIDTH}px`;
    renderHost.style.background = "#ffffff";
    renderHost.style.pointerEvents = "none";
    renderHost.style.zIndex = "-1";

    const clonedReport = sourceElement.cloneNode(true) as HTMLDivElement;

    clonedReport.setAttribute("data-pdf-render-root", "");
    clonedReport.removeAttribute("ref");

    renderHost.appendChild(clonedReport);
    document.body.appendChild(renderHost);

    try {
      if (document.fonts?.ready) {
        await document.fonts.ready;
      }

      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => resolve());
        });
      });

      const sectionEls = Array.from(
        clonedReport.querySelectorAll<HTMLElement>(
          ":scope > [data-pdf-section]",
        ),
      );

      if (sectionEls.length === 0) {
        throw new Error("PDF'e aktarılacak rapor bölümü bulunamadı.");
      }

      const pageWidth = 595.28;
      const pageHeight = 841.89;
      const marginX = 34;
      const marginTop = 34;
      const marginBottom = 44;
      const sectionGap = 14;

      const contentWidth = pageWidth - marginX * 2;
      const usableHeight = pageHeight - marginTop - marginBottom;

      const pdf = new jsPDF({
        unit: "pt",
        format: "a4",
        orientation: "portrait",
        compress: true,
      });

      let cursorY = marginTop;
      let pageHasContent = false;

      const addNewPage = () => {
        pdf.addPage();
        cursorY = marginTop;
        pageHasContent = false;
      };

      for (const sectionEl of sectionEls) {
        const canvas = await html2canvas(sectionEl, {
          scale: 2,
          useCORS: true,
          allowTaint: false,
          backgroundColor: "#ffffff",
          logging: false,
          width: sectionEl.scrollWidth,
          height: sectionEl.scrollHeight,
          windowWidth: PDF_RENDER_WIDTH,
          scrollX: 0,
          scrollY: 0,
        });

        if (canvas.width === 0 || canvas.height === 0) {
          continue;
        }

        const renderedHeight =
          (canvas.height * contentWidth) / canvas.width;

        const imageData = canvas.toDataURL("image/png");

        if (renderedHeight <= usableHeight) {
          if (
            pageHasContent &&
            cursorY + renderedHeight > pageHeight - marginBottom
          ) {
            addNewPage();
          }

          pdf.addImage(
            imageData,
            "PNG",
            marginX,
            cursorY,
            contentWidth,
            renderedHeight,
            undefined,
            "FAST",
          );

          cursorY += renderedHeight + sectionGap;
          pageHasContent = true;

          continue;
        }

        if (pageHasContent) {
          addNewPage();
        }

        let sourceY = 0;
        let lastSliceHeightInPdf = 0;

        const sourcePageHeight =
          (usableHeight * canvas.width) / contentWidth;

        while (sourceY < canvas.height) {
          const currentSliceHeight = Math.min(
            sourcePageHeight,
            canvas.height - sourceY,
          );

          const sliceCanvas = document.createElement("canvas");
          const sliceContext = sliceCanvas.getContext("2d");

          if (!sliceContext) {
            throw new Error("PDF sayfa parçası oluşturulamadı.");
          }

          sliceCanvas.width = canvas.width;
          sliceCanvas.height = Math.ceil(currentSliceHeight);

          sliceContext.fillStyle = "#ffffff";
          sliceContext.fillRect(
            0,
            0,
            sliceCanvas.width,
            sliceCanvas.height,
          );

          sliceContext.drawImage(
            canvas,
            0,
            sourceY,
            canvas.width,
            currentSliceHeight,
            0,
            0,
            canvas.width,
            currentSliceHeight,
          );

          lastSliceHeightInPdf =
            (currentSliceHeight * contentWidth) / canvas.width;

          pdf.addImage(
            sliceCanvas.toDataURL("image/png"),
            "PNG",
            marginX,
            marginTop,
            contentWidth,
            lastSliceHeightInPdf,
            undefined,
            "FAST",
          );

          sourceY += currentSliceHeight;

          if (sourceY < canvas.height) {
            addNewPage();
          }
        }

        cursorY = marginTop + lastSliceHeightInPdf + sectionGap;
        pageHasContent = true;
      }

      const totalPages = pdf.getNumberOfPages();

      for (let pageNumber = 1; pageNumber <= totalPages; pageNumber += 1) {
        pdf.setPage(pageNumber);

        pdf.setDrawColor(226, 232, 240);
        pdf.setLineWidth(0.6);
        pdf.line(
          marginX,
          pageHeight - 29,
          pageWidth - marginX,
          pageHeight - 29,
        );

        pdf.setFont("helvetica", "normal");
        pdf.setFontSize(8);
        pdf.setTextColor(100, 116, 139);

        pdf.text(
          "FikirLab · Rapor",
          marginX,
          pageHeight - 16,
        );

        pdf.text(
          `${pageNumber} / ${totalPages}`,
          pageWidth - marginX,
          pageHeight - 16,
          { align: "right" },
        );
      }

      const rawName = idea?.title?.trim() || "Fikir";

      const safeName = rawName
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/ı/g, "i")
        .replace(/İ/g, "I")
        .replace(/[\\/:*?"<>|]/g, "")
        .replace(/\s+/g, "_")
        .trim();

      const blob = pdf.output("blob");
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");

      link.href = url;
      link.download = `${safeName}_Fikirlab_Dogrulama_Raporu.pdf`;

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      window.setTimeout(() => {
        URL.revokeObjectURL(url);
      }, 1000);
    } catch (error) {
      console.error(error);

      setDownloadError(
        "PDF oluşturulamadı. Lütfen tekrar dener misin?",
      );
    } finally {
      renderHost.remove();
      styleTag.remove();

      closedAccordionButtons.forEach((button) => {
        if (button.getAttribute("aria-expanded") === "true") {
          button.click();
        }
      });

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

        <div
          ref={reportRef}
          className="space-y-9 rounded-2xl bg-white px-5 py-7 shadow-sm ring-1 ring-black/5 sm:px-10 sm:py-10"
        >
          <header
            data-pdf-section
            className="border-b border-border pb-7"
          >
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

          <section data-pdf-section>
            <Divider label="Fikir Özeti" />

            <div className="rounded-xl border border-border bg-card px-5 py-4">
              <p className="text-sm leading-6 text-muted-foreground">
                {idea.description}
              </p>
            </div>
          </section>

          <section data-pdf-section>
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

          <section data-pdf-section>
            <Divider label="Riskli Varsayımlar" />

            <RiskyAssumptionsBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-section>
            <Divider label="Müşteri Görüşme Soruları" />

            <MomTestQuestionsBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-section>
            <Divider label="MVP Kapsamı (MoSCoW)" />

            <MoscowScopeBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section
            data-pdf-section
            data-pdf-expand-all
          >
            <Divider label="Doğrulama Yol Haritası" />

            <ValidationRoadmapBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-section>
            <Divider label="Genel Değerlendirme" />

            <GeneralEvaluationBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-section>
            <Divider label="Rakip / Pazar Analizi" />

            <CompetitorAnalysisBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          <section data-pdf-section>
            <Divider label="Yatırımcı Sunumu" />

            <InvestorPitchBody
              ideaId={ideaId}
              readOnly
            />
          </section>

          {uniqueSources.length > 0 && (
            <section data-pdf-section>
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