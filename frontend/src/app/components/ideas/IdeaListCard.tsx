import { Calendar, ChevronRight, Tag, Users } from "lucide-react";

import type { IdeaResponse } from "../../lib/api";
import { StatusBadge } from "../common/Badges";

interface IdeaListCardProps {
  idea: IdeaResponse;
  onOpen: (ideaId: number) => void;
  compact?: boolean;
}

export function IdeaListCard({ idea, onOpen, compact = false }: IdeaListCardProps) {
  const createdAt = new Date(idea.created_at);
  const dateLabel = Number.isNaN(createdAt.getTime())
    ? "Tarih belirtilmedi"
    : createdAt.toLocaleDateString("tr-TR", {
        day: "numeric",
        month: "short",
        year: "numeric",
      });

  return (
    <div className="group rounded-xl border border-border bg-card p-5 transition-all hover:border-foreground/30">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center gap-2">
            <StatusBadge status={idea.analysis_status} />
            <span className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar size={10} />
              {dateLabel}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-foreground">{idea.title}</h3>
          <p
            className={`mt-1 text-sm leading-relaxed text-muted-foreground ${
              compact ? "line-clamp-1" : ""
            }`}
          >
            {idea.description}
          </p>
          <div className="mt-2.5 flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Tag size={10} />
              {idea.sector || "Sektör belirtilmedi"}
            </span>
            <span className="text-border">·</span>
            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
              <Users size={10} />
              {idea.target_audience || "Hedef kitle belirtilmedi"}
            </span>
          </div>
        </div>
        <button
          type="button"
          onClick={() => onOpen(idea.id)}
          className="inline-flex flex-shrink-0 items-center gap-1.5 rounded-xl border border-border bg-muted px-3.5 py-2 text-xs font-semibold text-muted-foreground transition-all hover:border-foreground/30 hover:bg-hover hover:text-foreground"
        >
          Detaya Git
          <ChevronRight size={12} />
        </button>
      </div>
    </div>
  );
}
