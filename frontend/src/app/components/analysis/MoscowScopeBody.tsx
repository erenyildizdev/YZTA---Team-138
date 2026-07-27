import { RefreshCw, Sparkles } from "lucide-react";
import { useMoscowScope } from "../../hooks/useMoscowScope";

const CATEGORY_CONFIG = [
  { key: "must_have" as const, label: "Must Have", bg: "bg-red-900/20 border-red-800/30", lc: "text-red-700 dark:text-red-300", dot: "bg-red-500" },
  { key: "should_have" as const, label: "Should Have", bg: "bg-amber-900/20 border-amber-800/30", lc: "text-amber-700 dark:text-amber-300", dot: "bg-amber-500" },
  { key: "could_have" as const, label: "Could Have", bg: "bg-blue-900/20 border-blue-800/30", lc: "text-blue-700 dark:text-blue-300", dot: "bg-blue-500" },
  { key: "wont_have" as const, label: "Won't Have", bg: "bg-slate-800/30 border-slate-700/30", lc: "text-slate-700 dark:text-slate-300", dot: "bg-slate-500" },
];

export function MoscowScopeBody({ ideaId }: { ideaId: number }) {
  const { status, data, error, generate, reload } = useMoscowScope(ideaId);

  return (
    <div>
      {status === "loading" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-xl bg-muted/40 border border-border animate-pulse" />
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
          <div className="w-11 h-11 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-3">
            <Sparkles size={18} className="text-emerald-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz MVP kapsamı oluşturulmadı.
          </p>
          <button
            onClick={generate}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
          >
            <Sparkles size={13} />MVP Kapsamı Oluştur
          </button>
        </div>
      )}

      {status === "generating" && (
        <div className="text-center py-6">
          <RefreshCw size={18} className="text-emerald-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">MVP kapsamı oluşturuluyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div>
          <div className="flex items-start justify-between gap-3 mb-3">
            <p className="text-sm text-muted-foreground leading-relaxed">{data.summary}</p>
            <button
              onClick={generate}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400 hover:text-emerald-300 transition-colors flex-shrink-0"
            >
              <RefreshCw size={11} />Yeniden Oluştur
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {CATEGORY_CONFIG.map(({ key, label, bg, lc, dot }) => (
              <div key={key} className={`rounded-xl border p-3.5 ${bg}`}>
                <div className="flex items-center gap-1.5 mb-2.5">
                  <div className={`w-1.5 h-1.5 rounded-full ${dot}`} />
                  <span className={`text-xs font-bold ${lc}`}>{label}</span>
                </div>
                <ul className="space-y-1.5">
                  {data[key].map((item, i) => (
                    <li key={i} className="text-xs leading-relaxed text-foreground/80" title={item.reason}>
                      {item.title}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
