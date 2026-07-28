import { Megaphone, RefreshCw, Sparkles, Target } from "lucide-react";
import { useInvestorPitch } from "../../hooks/useInvestorPitch";

export function InvestorPitchBody({
  ideaId,
  readOnly = false,
}: {
  ideaId: number;
  readOnly?: boolean;
}) {
  const { status, data, error, generate, reload } = useInvestorPitch(ideaId);

  return (
    <div>
      {status === "loading" && (
        <div data-pdf-block className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-14 rounded-xl bg-muted/40 border border-border animate-pulse" />
          ))}
        </div>
      )}

      {status === "error" && (
        <div data-pdf-block className="bg-red-900/10 border border-red-800/30 rounded-xl p-4">
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
        <div data-pdf-block className="text-center py-6">
          <div className="w-11 h-11 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto mb-3">
            <Megaphone size={18} className="text-amber-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz yatırımcı sunumu oluşturulmadı.
          </p>
          {!readOnly && (
            <button
              onClick={generate}
              className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
            >
              <Sparkles size={13} />Sunumu Oluştur
            </button>
          )}
        </div>
      )}

      {status === "generating" && (
        <div data-pdf-block className="text-center py-6">
          <RefreshCw size={18} className="text-amber-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">Yatırımcı sunumu hazırlanıyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div className="space-y-3">
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

          <div data-pdf-block className="rounded-xl border border-amber-800/30 bg-amber-900/10 p-3.5">
            <h4 className="text-xs font-bold text-foreground mb-1">Elevator Pitch</h4>
            <p className="text-sm text-foreground/90 leading-relaxed italic">
              "{data.elevator_pitch}"
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {data.slides.map((slide, i) => (
              <div key={i} data-pdf-block className="rounded-xl border border-border bg-muted/30 p-3.5">
                <div className="flex items-center gap-1.5 mb-2">
                  <span className="w-5 h-5 rounded-full bg-amber-500/10 text-amber-400 text-[10px] font-bold flex items-center justify-center border border-amber-500/20 flex-shrink-0">
                    {i + 1}
                  </span>
                  <h4 className="text-sm font-bold text-foreground">{slide.title}</h4>
                </div>
                <ul className="space-y-1">
                  {slide.bullets.map((b, idx) => (
                    <li key={idx} className="text-xs text-muted-foreground leading-relaxed">
                      · {b}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div data-pdf-block className="rounded-xl border border-border bg-muted/30 p-3.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Target size={12} className="text-foreground" />
              <h4 className="text-xs font-bold text-foreground">Kapanış / Talep</h4>
            </div>
            <p className="text-sm text-muted-foreground leading-relaxed">{data.closing_ask}</p>
          </div>
        </div>
      )}
    </div>
  );
}
