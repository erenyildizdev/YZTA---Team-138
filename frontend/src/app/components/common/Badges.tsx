import { CheckCircle, Clock } from "lucide-react";
import type { IdeaStatus, RiskLevel } from "../../types";

export function RiskBadge({ level }: { level: RiskLevel }) {
  const cfg = {
    high:   { label: "Yüksek Risk", cls: "bg-destructive/10 text-destructive border-destructive/30" },
    medium: { label: "Orta Risk",   cls: "bg-warning/10 text-warning border-warning/30" },
    low:    { label: "Düşük Risk",  cls: "bg-success/10 text-success border-success/30" },
  };
  const { label, cls } = cfg[level];
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border flex-shrink-0 ${cls}`}>
      {label}
    </span>
  );
}

export function StatusBadge({ status }: { status: IdeaStatus }) {
  if (status === "completed") {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-success/10 text-success border border-success/30">
        <CheckCircle size={10} />Analiz Tamamlandı
      </span>
    );
  }
  if (status === "in_progress") {
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning/10 text-warning border border-warning/30">
        <Clock size={10} />Devam Ediyor
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-muted text-muted-foreground border border-border">
      <Clock size={10} />Taslak
    </span>
  );
}
