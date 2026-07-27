import { Download } from "lucide-react";

import { GeneralEvaluationBody } from "../components/analysis/GeneralEvaluationBody";
import { MomTestQuestionsBody } from "../components/analysis/MomTestQuestionsBody";
import { MoscowScopeBody } from "../components/analysis/MoscowScopeBody";
import { RiskyAssumptionsBody } from "../components/analysis/RiskyAssumptionsBody";
import { ValidationRoadmapBody } from "../components/analysis/ValidationRoadmapBody";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useIdea } from "../hooks/useIdea";

interface ReportPageProps {
  onBack: () => void;
}

export function ReportPage({ onBack }: ReportPageProps) {
  const [ideaId] = useActiveIdeaId();
  const { data: idea } = useIdea(ideaId);

  const Divider = ({ label }: { label: string }) => (
    <div className="mb-4 flex items-center gap-2">
      <div className="h-0.5 w-4 rounded-full bg-primary" />

      <h2 className="text-[10px] font-bold uppercase tracking-widest text-foreground">
        {label}
      </h2>
    </div>
  );

  return (
    <div
      className="hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto max-w-3xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="mb-1 text-xs uppercase tracking-widest text-muted-foreground">
              FikirLab — Doğrulama Raporu
            </div>

            <h1 className="text-2xl font-bold text-foreground">
              {idea?.title ?? "Yükleniyor..."}
            </h1>

            <p className="mt-1 text-sm text-muted-foreground">
              {idea
                ? `${new Date(idea.created_at).toLocaleDateString(
                    "tr-TR",
                  )} tarihli analiz`
                : ""}
            </p>
          </div>

          <button
            type="button"
            disabled
            title="Backend entegrasyonu sonrasında kullanılabilir"
            className="inline-flex cursor-not-allowed items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground opacity-45"
          >
            <Download size={14} />
            PDF İndir
          </button>
        </div>

        <button
          type="button"
          onClick={onBack}
          className="mb-6 text-xs font-semibold text-foreground transition-colors hover:text-muted-foreground"
        >
          ← Fikir analizine dön
        </button>

        <div className="space-y-9">
          <section>
            <Divider label="Fikir Özeti" />

            <p className="text-sm leading-relaxed text-muted-foreground">
              {idea?.description}
            </p>
          </section>

          <section>
            <Divider label="Problem ve Hedef Kitle" />

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Problem
                </h3>

                <p className="text-sm leading-relaxed text-muted-foreground">
                  {idea?.problem}
                </p>
              </div>

              <div className="rounded-xl border border-border bg-card p-5">
                <h3 className="mb-2 text-sm font-bold text-foreground">
                  Hedef Kitle
                </h3>

                <p className="text-sm leading-relaxed text-muted-foreground">
                  {idea?.target_audience}
                </p>
              </div>
            </div>
          </section>

          <section>
            <Divider label="Riskli Varsayımlar" />
            <RiskyAssumptionsBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Müşteri Görüşme Soruları" />
            <MomTestQuestionsBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="MVP Kapsamı (MoSCoW)" />
            <MoscowScopeBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Doğrulama Yol Haritası" />
            <ValidationRoadmapBody ideaId={ideaId} />
          </section>

          <section>
            <Divider label="Genel Değerlendirme" />
            <GeneralEvaluationBody ideaId={ideaId} />
          </section>
        </div>
      </div>
    </div>
  );
}