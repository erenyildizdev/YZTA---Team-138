import { AlertCircle, History, LoaderCircle, RefreshCw } from "lucide-react";

import { IdeaListCard } from "../components/ideas/IdeaListCard";
import {
  clearActiveIdeaIdIfMatches,
  useActiveIdeaId,
} from "../hooks/useActiveIdeaId";
import { useIdeas } from "../hooks/useIdeas";

export function HistoryPage({
  onOpen,
  onNew,
}: {
  onOpen: () => void;
  onNew: () => void;
}) {
  const { status, data: ideas, error, reload, removeIdea } = useIdeas();
  const { setActiveIdeaId } = useActiveIdeaId();

  const openIdea = (ideaId: number) => {
    setActiveIdeaId(ideaId);
    onOpen();
  };

  const deleteIdea = async (ideaId: number) => {
    await removeIdea(ideaId);
    clearActiveIdeaIdIfMatches(ideaId);
  };

  return (
    <div
      className="hide-scroll flex-1 overflow-y-auto"
      style={{ animation: "page-in 0.3s ease-out" }}
    >
      <div className="mx-auto max-w-4xl px-4 py-7 sm:px-7 sm:py-10">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-foreground">Geçmiş Fikirler</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Daha önce oluşturduğunuz tüm fikirler ve analiz durumları.
          </p>
        </div>

        {status === "loading" && (
          <div className="flex items-center justify-center gap-2 rounded-xl border border-border bg-card py-14 text-sm text-muted-foreground">
            <LoaderCircle size={17} className="animate-spin text-primary" />
            Fikirler yükleniyor...
          </div>
        )}

        {status === "error" && (
          <div className="rounded-xl border border-destructive/30 bg-destructive/10 p-5">
            <div className="flex items-start gap-3">
              <AlertCircle size={18} className="mt-0.5 flex-shrink-0 text-destructive" />
              <div>
                <p className="text-sm font-medium text-foreground">
                  Fikirler yüklenemedi
                </p>
                <p className="mt-1 text-sm text-destructive">{error}</p>
                <button
                  type="button"
                  onClick={() => void reload()}
                  className="mt-3 inline-flex items-center gap-1.5 rounded-lg bg-primary px-3.5 py-2 text-xs font-semibold text-primary-foreground hover:bg-primary-hover"
                >
                  <RefreshCw size={12} />
                  Yeniden dene
                </button>
              </div>
            </div>
          </div>
        )}

        {status === "ready" && ideas.length === 0 && (
          <div className="rounded-xl border border-dashed border-border bg-card px-6 py-14 text-center">
            <History size={24} className="mx-auto text-muted-foreground" />
            <h2 className="mt-3 text-sm font-semibold text-foreground">
              Henüz bir fikrin yok
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Oluşturduğun fikirler burada görünecek.
            </p>
            <button
              type="button"
              onClick={onNew}
              className="mt-4 rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-primary-hover"
            >
              Yeni Fikir Ekle
            </button>
          </div>
        )}

        {status === "ready" && ideas.length > 0 && (
          <div className="grid gap-4">
            {ideas.map((idea) => (
              <IdeaListCard
                key={idea.id}
                idea={idea}
                onOpen={openIdea}
                onDelete={deleteIdea}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
