import { useState } from "react";
import {
  AlertCircle,
  Columns3,
  LoaderCircle,
} from "lucide-react";

import { StatusBadge } from "../components/common/Badges";
import { useIdeas } from "../hooks/useIdeas";
import {
  ApiError,
  compareIdeas,
  type IdeaComparisonResult,
} from "../lib/api";

const MAX_SELECTION = 3;

type CompareStatus = "idle" | "loading" | "ready" | "error";

export function ComparePage() {
  const { status: ideasStatus, data: ideas, error: ideasError } = useIdeas();

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [compareStatus, setCompareStatus] = useState<CompareStatus>("idle");
  const [compareError, setCompareError] = useState<string | null>(null);
  const [results, setResults] = useState<IdeaComparisonResult[]>([]);

  const toggleSelection = (ideaId: number) => {
    setSelectedIds((previous) => {
      if (previous.includes(ideaId)) {
        return previous.filter((id) => id !== ideaId);
      }
      if (previous.length >= MAX_SELECTION) {
        return previous;
      }
      return [...previous, ideaId];
    });
    setCompareStatus("idle");
  };

  const handleCompare = async () => {
    if (selectedIds.length < 2) return;

    setCompareStatus("loading");
    setCompareError(null);

    try {
      const res = await compareIdeas(selectedIds);
      setResults(res.ideas);
      setCompareStatus("ready");
    } catch (err) {
      setCompareError(
        err instanceof ApiError ? err.message : "Karşılaştırma yüklenemedi.",
      );
      setCompareStatus("error");
    }
  };

  const dateLabel = (value: string) => {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime())
      ? "—"
      : parsed.toLocaleDateString("tr-TR", {
          day: "numeric",
          month: "short",
          year: "numeric",
        });
  };

  return (
    <div
      className="hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto max-w-5xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-foreground">Fikir Karşılaştırma</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            2 veya 3 fikri seç, riskli varsayım, MVP kapsamı ve doğrulama durumlarını yan yana kıyasla.
          </p>
        </div>

        {ideasStatus === "loading" && (
          <div className="flex items-center justify-center gap-2 rounded-xl border border-border bg-card py-14 text-sm text-muted-foreground">
            <LoaderCircle size={17} className="animate-spin text-primary" />
            Fikirler yükleniyor...
          </div>
        )}

        {ideasStatus === "error" && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-5">
            <div className="flex items-start gap-3">
              <AlertCircle size={18} className="mt-0.5 flex-shrink-0 text-destructive" />
              <p className="text-sm text-destructive">{ideasError}</p>
            </div>
          </div>
        )}

        {ideasStatus === "ready" && (
          <>
            <div className="rounded-xl border border-border bg-card p-5">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-foreground">
                  Karşılaştırılacak fikirleri seç ({selectedIds.length}/{MAX_SELECTION})
                </h2>
                <button
                  type="button"
                  onClick={() => void handleCompare()}
                  disabled={selectedIds.length < 2 || compareStatus === "loading"}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground transition-all hover:bg-primary-hover disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <Columns3 size={13} />
                  {compareStatus === "loading" ? "Karşılaştırılıyor..." : "Karşılaştır"}
                </button>
              </div>

              {ideas.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Karşılaştırmak için önce en az iki fikir oluşturman gerekiyor.
                </p>
              ) : (
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {ideas.map((idea) => {
                    const checked = selectedIds.includes(idea.id);
                    const disabled = !checked && selectedIds.length >= MAX_SELECTION;
                    return (
                      <label
                        key={idea.id}
                        className={`flex items-start gap-2.5 rounded-xl border p-3 text-sm transition-all ${
                          checked
                            ? "border-primary/50 bg-primary/5"
                            : "border-border bg-muted/30"
                        } ${disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer hover:border-foreground/30"}`}
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          disabled={disabled}
                          onChange={() => toggleSelection(idea.id)}
                          className="mt-0.5"
                        />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate font-semibold text-foreground">
                            {idea.title}
                          </span>
                          <span className="mt-0.5 block text-xs text-muted-foreground">
                            {idea.sector || "Sektör belirtilmedi"}
                          </span>
                        </span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>

            {compareError && (
              <p className="mt-4 text-sm text-destructive">{compareError}</p>
            )}

            {compareStatus === "ready" && results.length > 0 && (
              <div className="mt-6 overflow-x-auto rounded-xl border border-border bg-card">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="w-40 px-4 py-3 text-left text-xs font-semibold text-muted-foreground">
                        Metrik
                      </th>
                      {results.map((idea) => (
                        <th key={idea.id} className="min-w-[180px] px-4 py-3 text-left">
                          <div className="text-sm font-bold text-foreground">{idea.title}</div>
                          <div className="mt-1">
                            <StatusBadge status={idea.analysis_status} />
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Sektör</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.sector || "—"}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Hedef Kitle</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.target_audience || "—"}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Oluşturulma</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {dateLabel(idea.created_at)}
                        </td>
                      ))}
                    </tr>

                    <tr className="bg-muted/30">
                      <td colSpan={results.length + 1} className="px-4 py-2 text-xs font-bold uppercase tracking-wide text-foreground">
                        Riskli Varsayımlar
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Toplam</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.risky_assumptions.total}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Doğrulandı</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 font-semibold text-success">
                          {idea.risky_assumptions.validated}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Çürütüldü</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 font-semibold text-destructive">
                          {idea.risky_assumptions.refuted}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Test edilmedi</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.risky_assumptions.untested}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Yüksek risk</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.risky_assumptions.high_risk}
                        </td>
                      ))}
                    </tr>

                    <tr className="bg-muted/30">
                      <td colSpan={results.length + 1} className="px-4 py-2 text-xs font-bold uppercase tracking-wide text-foreground">
                        MVP Kapsamı (MoSCoW)
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Must Have</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.moscow.must_have}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Should Have</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.moscow.should_have}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Could Have</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.moscow.could_have}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Won't Have</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.moscow.wont_have}
                        </td>
                      ))}
                    </tr>

                    <tr className="bg-muted/30">
                      <td colSpan={results.length + 1} className="px-4 py-2 text-xs font-bold uppercase tracking-wide text-foreground">
                        Doğrulama İlerlemesi
                      </td>
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Müşteri görüşme sorusu</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.mom_test_question_count}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Görüşme notu</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="px-4 py-3 text-foreground">
                          {idea.interview_note_count}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Rakip/pazar analizi</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="max-w-[260px] px-4 py-3 text-xs leading-relaxed text-foreground">
                          {idea.competitor_analysis_summary || (
                            <span className="text-muted-foreground">Henüz oluşturulmadı.</span>
                          )}
                        </td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 text-xs font-semibold text-muted-foreground">Genel değerlendirme</td>
                      {results.map((idea) => (
                        <td key={idea.id} className="max-w-[260px] px-4 py-3 text-xs leading-relaxed text-foreground">
                          {idea.general_evaluation_summary || (
                            <span className="text-muted-foreground">Henüz oluşturulmadı.</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
