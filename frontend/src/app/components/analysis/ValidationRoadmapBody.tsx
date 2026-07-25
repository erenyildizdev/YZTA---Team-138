import { AlertTriangle, ArrowRight, Map, MessageSquare, RefreshCw, Sparkles, Target, TrendingUp } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "../ui/accordion";
import { useValidationRoadmap } from "../../hooks/useValidationRoadmap";

const SECTION_CONFIG: { key: string; label: string; icon: any; color: "cyan" | "red" | "emerald" | "amber" | "violet" }[] = [
  { key: "İlk görüşmeler", label: "İlk Görüşmeler", icon: MessageSquare, color: "cyan" },
  { key: "Test edilecek varsayımlar", label: "Test Edilecek Varsayımlar", icon: AlertTriangle, color: "red" },
  { key: "MVP öncelikleri", label: "MVP Öncelikleri", icon: Target, color: "emerald" },
  { key: "Başarı metrikleri", label: "Başarı Metrikleri", icon: TrendingUp, color: "amber" },
  { key: "Sonraki karar noktaları", label: "Sonraki Karar Noktaları", icon: ArrowRight, color: "violet" },
];

const COLOR_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  cyan: { bg: "bg-cyan-500/10", text: "text-cyan-400", border: "border-cyan-500/20" },
  red: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20" },
  emerald: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/20" },
  amber: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/20" },
  violet: { bg: "bg-violet-500/10", text: "text-violet-400", border: "border-violet-500/20" },
};

export function ValidationRoadmapBody({
  ideaId,
  onIdeaIdChange,
}: {
  ideaId: number;
  onIdeaIdChange?: (id: number) => void;
}) {
  const { status, data, error, generate, reload } = useValidationRoadmap(ideaId);

  return (
    <div>
      {onIdeaIdChange && (
        <div className="flex items-center justify-end gap-2 mb-3">
          <label className="text-[11px] text-muted-foreground">Fikir ID</label>
          <input
            type="number"
            min={1}
            value={ideaId}
            onChange={(e) => onIdeaIdChange(Number(e.target.value))}
            className="w-16 bg-muted border border-border rounded-lg px-2 py-1 text-xs text-foreground focus:outline-none focus:border-primary/50"
          />
        </div>
      )}

      {status === "loading" && (
        <div className="space-y-2.5">
          {[0, 1, 2].map((i) => (
            <div key={i} className="h-14 rounded-xl bg-muted/40 border border-border animate-pulse" />
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
            <Map size={18} className="text-violet-400" />
          </div>
          <p className="text-sm text-muted-foreground mb-4 max-w-xs mx-auto leading-relaxed">
            Bu fikir için henüz bir doğrulama yol haritası oluşturulmadı.
          </p>
          <button
            onClick={generate}
            className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-semibold bg-primary text-white hover:bg-blue-600 transition-all"
          >
            <Sparkles size={13} />Yol Haritası Oluştur
          </button>
        </div>
      )}

      {status === "generating" && (
        <div className="text-center py-6">
          <RefreshCw size={18} className="text-violet-400 mx-auto mb-3 animate-spin" />
          <p className="text-xs text-muted-foreground">Yol haritası oluşturuluyor...</p>
        </div>
      )}

      {status === "ready" && data && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] text-muted-foreground">
              {data.phases.length} {data.roadmap_type === "weekly" ? "haftalık aşama" : "aşama"}
            </span>
            <button
              onClick={generate}
              className="inline-flex items-center gap-1 text-[11px] font-semibold text-violet-400 hover:text-violet-300 transition-colors"
            >
              <RefreshCw size={11} />Yeniden Oluştur
            </button>
          </div>

          <Accordion type="multiple" defaultValue={["phase-0"]} className="space-y-2.5">
            {data.phases.map((phase, i) => {
              const order = phase.week ?? phase.phase ?? i + 1;
              const label = data.roadmap_type === "weekly" ? `Hafta ${order}` : `Aşama ${order}`;

              return (
                <AccordionItem
                  key={i}
                  value={`phase-${i}`}
                  className="bg-muted/30 border border-border rounded-xl px-4 border-b"
                >
                  <AccordionTrigger className="hover:no-underline py-3">
                    <div className="flex items-center gap-2.5 text-left">
                      <span className="w-6 h-6 rounded-full bg-violet-500/10 text-violet-400 text-[11px] font-bold flex items-center justify-center border border-violet-500/20 flex-shrink-0">
                        {order}
                      </span>
                      <div>
                        <span className="text-sm font-semibold text-foreground">{phase.title ?? label}</span>
                        <span className="ml-2 text-[10px] text-muted-foreground px-1.5 py-0.5 bg-secondary rounded-full border border-border">
                          {label}
                        </span>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {SECTION_CONFIG.map(({ key, label: sectionLabel, icon: Icon, color }) => {
                        const items = phase[key];
                        if (!Array.isArray(items) || items.length === 0) return null;
                        const c = COLOR_STYLES[color];

                        return (
                          <div key={key} className={`rounded-lg border p-3 ${c.bg} ${c.border}`}>
                            <div className="flex items-center gap-1.5 mb-2">
                              <Icon size={11} className={c.text} />
                              <span className={`text-[11px] font-bold ${c.text}`}>{sectionLabel}</span>
                            </div>
                            <ul className="space-y-1">
                              {items.map((item, idx) => (
                                <li key={idx} className={`text-xs leading-relaxed ${c.text} opacity-80`}>
                                  · {String(item)}
                                </li>
                              ))}
                            </ul>
                          </div>
                        );
                      })}
                    </div>
                  </AccordionContent>
                </AccordionItem>
              );
            })}
          </Accordion>
        </div>
      )}
    </div>
  );
}
