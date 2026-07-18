import { CheckCircle, Clock } from "lucide-react";
import type { IdeaStatus, RiskLevel } from "../../types";

export function RiskBadge({ level }: { level: RiskLevel }) {
  const cfg = {
    high:   { label: "Yüksek Risk", cls: "bg-red-900/30 text-red-400 border-red-800/40" },
    medium: { label: "Orta Risk",   cls: "bg-amber-900/30 text-amber-400 border-amber-800/40" },
    low:    { label: "Düşük Risk",  cls: "bg-emerald-900/30 text-emerald-400 border-emerald-800/40" },
  };
  const { label, cls } = cfg[level];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border flex-shrink-0 ${cls}`}>
      {label}
    </span>
  );
}

export function StatusBadge({ status }: { status: IdeaStatus }) {
  if (status === "complete") {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900/30 text-blue-400 border border-blue-800/40">
        <CheckCircle size={10} />Analiz Tamamlandı
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800/60 text-slate-400 border border-slate-700/40">
      <Clock size={10} />Taslak
    </span>
  );
}
