import {
  AlertCircle,
  BarChart3,
  LoaderCircle,
  Plus,
  Sparkles,
  TrendingUp,
} from "lucide-react";

import { IdeaListCard } from "../components/ideas/IdeaListCard";
import { useAuth } from "../context/AuthContext";
import { useActiveIdeaId } from "../hooks/useActiveIdeaId";
import { useIdeas } from "../hooks/useIdeas";

export function DashboardPage({
  onNew,
  onViewAll,
  onOpenDetail,
}: {
  onNew: () => void;
  onViewAll: () => void;
  onOpenDetail: () => void;
}) {
  const { status, data: ideas, error } = useIdeas();
  const { setActiveIdeaId } = useActiveIdeaId();
  const { user } = useAuth();
  const displayName = user?.first_name?.trim() || user?.email || "";
  const completedCount = ideas.filter(
    (idea) => idea.analysis_status === "completed",
  ).length;
  const stats = [
    {
      label: "Toplam Fikir",
      value: ideas.length,
      Icon: Sparkles,
      accent: "text-foreground",
      bg: "bg-accent",
      border: "border-border",
    },
    {
      label: "Analiz Edildi",
      value: completedCount,
      Icon: BarChart3,
      accent: "text-success",
      bg: "bg-success/10",
      border: "border-success/20",
    },
    {
      label: "Devam Eden",
      value: ideas.length - completedCount,
      Icon: TrendingUp,
      accent: "text-warning",
      bg: "bg-warning/10",
      border: "border-warning/20",
    },
  ];

  const openIdea = (ideaId: number) => {
    setActiveIdeaId(ideaId);
    onOpenDetail();
  };

  return (
    <div
      className="hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto max-w-4xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-10">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            {displayName ? `Hoş geldin, ${displayName}! 👋` : "Hoş geldin! 👋"}
          </h1>
          <p className="mt-2 max-w-lg text-sm leading-relaxed text-muted-foreground">
            AI destekli mentörünle fikrini uçtan uca doğrula: riskleri keşfet,
            rakiplerini analiz et, MVP&apos;ni netleştir ve yatırımcı sunumunu hazırla.
          </p>
          <button
            type="button"
            onClick={onNew}
            className="mt-5 inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-all hover:bg-primary-hover"
          >
            <Plus size={15} />
            Yeni Fikir Oluştur
          </button>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className={`rounded-xl border bg-card p-5 ${stat.border}`}
            >
              <div
                className={`mb-3 flex h-9 w-9 items-center justify-center rounded-xl border ${stat.bg} ${stat.border}`}
              >
                <stat.Icon size={17} className={stat.accent} />
              </div>
              <div className={`text-2xl font-bold ${stat.accent}`}>
                {status === "loading" ? "—" : stat.value}
              </div>
              <div className="mt-0.5 text-sm text-muted-foreground">
                {stat.label}
              </div>
            </div>
          ))}
        </div>

        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-foreground">Son Fikirler</h2>
            <button
              type="button"
              onClick={onViewAll}
              className="text-xs font-medium text-primary transition-colors hover:text-primary-hover"
            >
              Tümünü Gör
            </button>
          </div>

          {status === "loading" && (
            <div className="flex items-center gap-2 rounded-xl border border-border bg-card p-5 text-sm text-muted-foreground">
              <LoaderCircle size={16} className="animate-spin text-primary" />
              Son fikirler yükleniyor...
            </div>
          )}

          {status === "error" && (
            <div className="flex items-center gap-2 rounded-xl border border-destructive/30 bg-destructive/10 p-5 text-sm text-destructive">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          {status === "ready" && ideas.length === 0 && (
            <div className="rounded-xl border border-dashed border-border bg-card p-6 text-sm text-muted-foreground">
              Henüz bir fikir oluşturmadın.
            </div>
          )}

          {status === "ready" && ideas.length > 0 && (
            <div className="space-y-3">
              {ideas.slice(0, 3).map((idea) => (
                <IdeaListCard
                  key={idea.id}
                  idea={idea}
                  onOpen={openIdea}
                  compact
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
