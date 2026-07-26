import { AlertTriangle, RefreshCw, Sparkles } from "lucide-react";
import { RiskBadge } from "../common/Badges";
import { useRiskyAssumptions } from "../../hooks/useRiskyAssumptions";

export function RiskyAssumptionsBody({ ideaId }: { ideaId: number }) {
  const { status, data, error, generate, reload } = useRiskyAssumptions(ideaId);

  return (
    <div>
      {status === "loading" && (
        <div className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-10 rounded-xl bg-muted/40 border border-border animate-pulse" />
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
          <div className="w-11 h-11 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-3">
            <AlertTriangle size={18} className="text-red-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz riskli varsayımlar oluşturulmadı.
          </p>
          <button
            onClick={generate}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
          >
            <Sparkles size={13} />Riskli Varsayımlar Oluştur
          </button>
        </div>
      )}

      {status === "generating" && (
        <div className="text-center py-6">
          <RefreshCw size={18} className="text-red-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">Riskli varsayımlar oluşturuluyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div>
          <div className="flex items-center justify-end mb-3">
            <button
              onClick={generate}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-400 hover:text-red-300 transition-colors"
            >
              <RefreshCw size={11} />Yeniden Oluştur
            </button>
          </div>

          <div className="space-y-3">
            {data.assumptions.map((item, i) => (
              <div key={i} className="flex items-start gap-3">
                <RiskBadge level={item.level} />
                <p className="text-sm text-muted-foreground leading-relaxed">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
