import { CheckCircle, HelpCircle, RefreshCw, Sparkles, Zap } from "lucide-react";
import { useGeneralEvaluation } from "../../hooks/useGeneralEvaluation";

export function GeneralEvaluationBody({
  ideaId,
  readOnly = false,
}: {
  ideaId: number;
  readOnly?: boolean;
}) {
  const { status, data, error, generate, reload } = useGeneralEvaluation(ideaId);

  return (
    <div>
      {status === "loading" && (
        <div className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-8 rounded-xl bg-muted/40 border border-border animate-pulse" />
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
          <div className="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto mb-3">
            <Sparkles size={18} className="text-amber-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz genel değerlendirme oluşturulmadı.
          </p>
          {!readOnly && (
            <button
              onClick={generate}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
            >
              <Sparkles size={13} />Değerlendirme Oluştur
            </button>
          )}
        </div>
      )}

      {status === "generating" && (
        <div className="text-center py-6">
          <RefreshCw size={18} className="text-amber-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">Değerlendirme oluşturuluyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div className="space-y-4">
          {!readOnly && (
            <div className="flex items-center justify-end">
              <button
                onClick={generate}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-amber-400 hover:text-amber-300 transition-colors"
              >
                <RefreshCw size={11} />Yeniden Oluştur
              </button>
            </div>
          )}

          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <CheckCircle size={12} className="text-emerald-400" />
              <span className="text-xs font-bold text-foreground">Güçlü Yönler</span>
            </div>
            <ul className="space-y-1.5">
              {data.strengths.map((s, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-emerald-500 mt-0.5">·</span>{s}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <div className="flex items-center gap-1.5 mb-2">
              <HelpCircle size={12} className="text-amber-400" />
              <span className="text-xs font-bold text-foreground">Belirsiz Noktalar</span>
            </div>
            <ul className="space-y-1.5">
              {data.uncertainties.map((u, i) => (
                <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                  <span className="text-amber-500 mt-0.5">·</span>{u}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-blue-900/20 border border-blue-800/30 rounded-xl p-4">
            <div className="flex items-center gap-1.5 mb-1.5">
              <Zap size={12} className="text-foreground" />
              <span className="text-xs font-bold text-foreground">İlk Yapılacak Aksiyon</span>
            </div>
            <p className="text-sm text-foreground/80 leading-relaxed">{data.next_action}</p>
          </div>
        </div>
      )}
    </div>
  );
}
