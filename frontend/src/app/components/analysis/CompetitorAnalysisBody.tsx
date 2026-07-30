import { CheckCircle2, RefreshCw, Sparkles, TrendingUp, XCircle } from "lucide-react";
import { useCompetitorAnalysis } from "../../hooks/useCompetitorAnalysis";

export function CompetitorAnalysisBody({
  ideaId,
  readOnly = false,
}: {
  ideaId: number;
  readOnly?: boolean;
}) {
  const { status, data, error, generate, reload } = useCompetitorAnalysis(ideaId);

  return (
    <div>
      {status === "loading" && (
        <div className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-16 rounded-xl bg-muted/40 border border-border animate-pulse" />
          ))}
        </div>
      )}

      {status === "error" && (
        <div className="bg-red-900/10 border border-red-800/30 rounded-xl p-4">
          <p className="text-xs text-red-400 mb-2.5">{error}</p>
          <button
            onClick={reload}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border border-red-800/40 text-red-400 hover:bg-red-900/20 transition-all"
          >
            <RefreshCw size={12} />Tekrar Dene
          </button>
        </div>
      )}

      {status === "empty" && (
        <div className="text-center py-6">
          <div className="w-11 h-11 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mx-auto mb-3">
            <TrendingUp size={18} className="text-violet-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz rakip/pazar analizi oluşturulmadı.
          </p>
          {!readOnly && (
            <button
              onClick={generate}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
            >
              <Sparkles size={13} />Rakip Analizi Oluştur
            </button>
          )}
        </div>
      )}

      {status === "generating" && (
        <div className="text-center py-6">
          <RefreshCw size={18} className="text-violet-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">Rakip analizi oluşturuluyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div className="space-y-3">
          {!readOnly && (
            <div className="flex items-center justify-end">
              <button
                onClick={generate}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-violet-400 hover:text-violet-300 transition-colors"
              >
                <RefreshCw size={11} />Yeniden Oluştur
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {data.competitors.map((c, i) => (
              <div key={i} className="rounded-xl border border-border bg-muted/30 p-3.5">
                <h4 className="text-sm font-bold text-foreground">{c.name}</h4>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">{c.description}</p>

                <div className="mt-2.5 space-y-1">
                  {c.strengths.map((s, idx) => (
                    <div key={idx} className="flex items-start gap-1.5">
                      <CheckCircle2 size={11} className="mt-0.5 flex-shrink-0 text-emerald-400" />
                      <span className="text-xs text-muted-foreground">{s}</span>
                    </div>
                  ))}
                  {c.weaknesses.map((w, idx) => (
                    <div key={idx} className="flex items-start gap-1.5">
                      <XCircle size={11} className="mt-0.5 flex-shrink-0 text-red-400" />
                      <span className="text-xs text-muted-foreground">{w}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="rounded-xl border border-border bg-muted/30 p-3.5">
            <h4 className="text-xs font-bold text-foreground mb-1">Pazar Boşluğu</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">{data.market_gap}</p>
          </div>

          <div className="rounded-xl border border-violet-800/30 bg-violet-900/10 p-3.5">
            <h4 className="text-xs font-bold text-foreground mb-1">Farklılaşma Noktanız</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">{data.differentiation}</p>
          </div>
        </div>
      )}
    </div>
  );
}
