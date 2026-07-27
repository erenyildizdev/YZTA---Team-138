import { AlertTriangle, CheckCircle2, HelpCircle, RefreshCw, Sparkles, XCircle } from "lucide-react";
import { RiskBadge } from "../common/Badges";
import { useRiskyAssumptions } from "../../hooks/useRiskyAssumptions";

const STATUS_CONFIG = {
  validated: { label: "Doğrulandı", cls: "text-emerald-400 border-emerald-800/40 bg-emerald-900/10", Icon: CheckCircle2 },
  refuted: { label: "Çürütüldü", cls: "text-red-400 border-red-800/40 bg-red-900/10", Icon: XCircle },
  untested: { label: "Test edilmedi", cls: "text-muted-foreground border-border bg-secondary", Icon: HelpCircle },
} as const;

export function RiskyAssumptionsBody({
  ideaId,
  readOnly = false,
}: {
  ideaId: number;
  readOnly?: boolean;
}) {
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
          {!readOnly && (
            <button
              onClick={generate}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
            >
              <Sparkles size={13} />Riskli Varsayımlar Oluştur
            </button>
          )}
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
          {!readOnly && (
            <div className="flex items-center justify-end mb-3">
              <button
                onClick={generate}
                className="inline-flex items-center gap-1 text-[11px] font-semibold text-red-400 hover:text-red-300 transition-colors"
              >
                <RefreshCw size={11} />Yeniden Oluştur
              </button>
            </div>
          )}

          <div className="space-y-3">
            {data.assumptions.map((item, i) => {
              const statusConfig = item.status ? STATUS_CONFIG[item.status] : null;
              return (
                <div key={i} className="flex items-start gap-3 flex-wrap">
                  <RiskBadge level={item.level} />
                  {statusConfig && (
                    <span
                      className={`inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full border flex-shrink-0 ${statusConfig.cls}`}
                    >
                      <statusConfig.Icon size={10} />
                      {statusConfig.label}
                    </span>
                  )}
                  <div className="flex-1 min-w-[200px]">
                    <p className="text-sm text-muted-foreground leading-relaxed">{item.text}</p>
                    {item.evidence_quote && (
                      <p className="text-xs text-muted-foreground/70 italic mt-1">"{item.evidence_quote}"</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
